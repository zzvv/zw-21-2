<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">提交申请</el-button>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 140px; margin-left: 12px;">
        <el-option label="待处理" value="pending" />
        <el-option label="已批准" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
    </div>
    <el-table :data="list" size="small" border>
      <el-table-column prop="id" label="编号" width="60" />
      <el-table-column prop="schedule.course.name" label="课程" width="120" />
      <el-table-column prop="original_teacher.name" label="原教师" width="90" />
      <el-table-column prop="substitute_teacher.name" label="代课教师" width="90">
        <template #default="{ row }">{{ row.substitute_teacher?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="请假时间" width="200">
        <template #default="{ row }">{{ fmtDate(row.start_date) }} ~ {{ fmtDate(row.end_date) }}</template>
      </el-table-column>
      <el-table-column prop="reason" label="请假原因" width="150" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" width="100" show-overflow-tooltip />
      <el-table-column prop="created_at" label="提交时间" width="150">
        <template #default="{ row }">{{ fmtDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" text type="success" @click="openAssignDialog(row)">指派代课</el-button>
            <el-button size="small" text type="danger" @click="reject(row)">拒绝</el-button>
          </template>
          <template v-else>
            <el-button size="small" text type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑申请' : '提交代课申请'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择排课">
          <el-select v-model="form.schedule_id" filterable style="width: 100%" placeholder="选择排课">
            <el-option v-for="s in mySchedules" :key="s.id" :label="scheduleLabel(s)" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="请假原因">
          <el-input v-model="form.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="指派代课教师" width="480px">
      <el-form :model="assignForm" label-width="100px">
        <el-form-item label="代课教师">
          <el-select v-model="assignForm.substitute_teacher_id" filterable style="width: 100%" placeholder="选择代课教师">
            <el-option v-for="t in availableTeachers" :key="t.id" :label="t.name + ' (' + t.instrument + ')'" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="assignForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doAssign">确认指派</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listSubstituteRequests, createSubstituteRequest, assignSubstitute, rejectSubstitute, deleteSubstituteRequest } from '../api/substituteRequest.js'
import { listSchedules } from '../api/schedule.js'
import { listTeachers } from '../api/teacher.js'
import { useUserStore } from '../stores/user.js'

const userStore = useUserStore()
const list = ref([])
const schedules = ref([])
const teachers = ref([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const form = ref({})
const assignForm = ref({ substitute_teacher_id: '', remark: '' })
const currentRequestId = ref(null)

const filteredList = computed(() => {
  if (!filterStatus.value) return list.value
  return list.value.filter(r => r.status === filterStatus.value)
})

const mySchedules = computed(() => {
  return schedules.value.filter(s => s.is_active)
})

const availableTeachers = computed(() => {
  return teachers.value.filter(t => t.is_active)
})

function statusText(s) {
  const map = { pending: '待处理', approved: '已批准', rejected: '已拒绝' }
  return map[s] || s
}

function statusTagType(s) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[s] || ''
}

function fmtDate(d) {
  if (!d) return '-'
  return d.split('T')[0]
}

function fmtDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ')
}

function scheduleLabel(s) {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${s.course?.name} - ${weekdays[s.weekday]} ${s.start_time}-${s.end_time}`
}

async function load() {
  list.value = await listSubstituteRequests({ status: filterStatus.value || undefined })
  schedules.value = await listSchedules()
  teachers.value = await listTeachers()
}

function openDialog(row = null) {
  form.value = row ? { ...row } : {}
  dialogVisible.value = true
}

async function submit() {
  const data = { ...form.value }
  if (!data.schedule_id || !data.start_date || !data.end_date || !data.reason) {
    ElMessage.warning('请填写完整信息')
    return
  }
  await createSubstituteRequest(data)
  dialogVisible.value = false
  await load()
  ElMessage.success('申请已提交')
}

function openAssignDialog(row) {
  currentRequestId.value = row.id
  assignForm.value = { substitute_teacher_id: '', remark: '' }
  assignDialogVisible.value = true
}

async function doAssign() {
  if (!assignForm.value.substitute_teacher_id) {
    ElMessage.warning('请选择代课教师')
    return
  }
  await assignSubstitute(currentRequestId.value, assignForm.value)
  assignDialogVisible.value = false
  await load()
  ElMessage.success('代课教师已指派')
}

async function reject(row) {
  const { value: remark } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝申请', {
    inputPlaceholder: '请输入拒绝原因',
    confirmButtonText: '确认拒绝',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await rejectSubstitute(row.id, remark)
  await load()
  ElMessage.success('申请已拒绝')
}

async function remove(id) {
  await ElMessageBox.confirm('确认删除该申请？', '提示', { type: 'warning' })
  await deleteSubstituteRequest(id)
  await load()
  ElMessage.success('已删除')
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>