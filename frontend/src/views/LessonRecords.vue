<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">记上课</el-button>
    </div>
    <el-table :data="list" size="small" border>
      <el-table-column prop="enrollment.student.name" label="学员" />
      <el-table-column prop="enrollment.course.name" label="课程" />
      <el-table-column prop="enrollment.course.teacher.name" label="课表教师" width="100">
        <template #default="{ row }">{{ row.enrollment?.course?.teacher?.name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="actual_teacher.name" label="上课教师" width="100">
        <template #default="{ row }">
          <span :class="{ 'substitute': row.actual_teacher_id && row.actual_teacher_id !== row.enrollment?.course?.teacher_id }">
            {{ row.actual_teacher?.name || row.enrollment?.course?.teacher?.name || '-' }}
          </span>
          <el-tag v-if="row.actual_teacher_id && row.actual_teacher_id !== row.enrollment?.course?.teacher_id" size="small" type="warning" style="margin-left: 4px">代课</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lesson_date" label="上课日期" width="110">
        <template #default="{ row }">{{ fmtDate(row.lesson_date) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'attended' ? 'success' : 'danger'" size="small">{{ row.status === 'attended' ? '出勤' : '缺勤' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="上课内容" />
      <el-table-column prop="homework" label="作业" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" text @click="openDialog(row)">编辑</el-button>
          <el-button size="small" text type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑上课记录' : '记上课'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="报名记录">
          <el-select v-model="form.enrollment_id" filterable style="width: 100%" @change="onEnrollmentChange">
            <el-option v-for="e in activeEnrollments" :key="e.id" :label="e.student?.name + ' - ' + e.course?.name + ' (' + e.course?.teacher?.name + ')' " :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期">
          <el-date-picker v-model="form.lesson_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="上课教师">
          <el-select v-model="form.actual_teacher_id" placeholder="默认为课表教师" clearable style="width: 100%">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name + ' (' + t.instrument + ')'" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联代课申请">
          <el-select v-model="form.substitute_request_id" placeholder="选择代课申请（自动填充代课教师）" clearable style="width: 100%" @change="onSubstituteChange">
            <el-option v-for="sr in approvedSubstitutes" :key="sr.id" :label="sr.schedule?.course?.name + ': ' + sr.original_teacher?.name + ' -> ' + sr.substitute_teacher?.name" :value="sr.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="出勤" value="attended" />
            <el-option label="缺勤" value="absent" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课内容"><el-input v-model="form.content" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="作业"><el-input v-model="form.homework" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listLessonRecords, createLessonRecord, updateLessonRecord, deleteLessonRecord } from '../api/lessonRecord.js'
import { listEnrollments } from '../api/enrollment.js'
import { listTeachers } from '../api/teacher.js'
import { listSubstituteRequests } from '../api/substituteRequest.js'

const list = ref([])
const enrollments = ref([])
const teachers = ref([])
const substituteRequests = ref([])
const dialogVisible = ref(false)
const form = ref({})

const activeEnrollments = computed(() => {
  return enrollments.value.filter(e => e.status === 'active')
})

const approvedSubstitutes = computed(() => {
  return substituteRequests.value.filter(sr => sr.status === 'approved' && sr.substitute_teacher_id)
})

function fmtDate(d) {
  if (!d) return '-'
  return d.split('T')[0]
}

async function load() {
  list.value = await listLessonRecords()
  enrollments.value = await listEnrollments()
  teachers.value = await listTeachers()
  substituteRequests.value = await listSubstituteRequests()
}

function onEnrollmentChange() {
  const enrollment = activeEnrollments.value.find(e => e.id === form.value.enrollment_id)
  if (enrollment && !form.value.actual_teacher_id) {
    form.value.actual_teacher_id = enrollment.course?.teacher_id || null
  }
}

function onSubstituteChange() {
  const sr = approvedSubstitutes.value.find(s => s.id === form.value.substitute_request_id)
  if (sr) {
    form.value.actual_teacher_id = sr.substitute_teacher_id
  }
}

function openDialog(row = null) {
  form.value = row ? { ...row } : { status: 'attended' }
  dialogVisible.value = true
}

async function submit() {
  const data = { ...form.value }
  if (data.id) {
    await updateLessonRecord(data.id, data)
  } else {
    await createLessonRecord(data)
  }
  dialogVisible.value = false
  await load()
}

async function remove(id) {
  await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' })
  await deleteLessonRecord(id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
.substitute { color: #e6a23c; }
</style>