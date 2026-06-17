from dotenv import load_dotenv
load_dotenv()
from app.core.database import SessionLocal, engine
from app.models.models import Base, User, Teacher, Student, Course, Classroom, CourseSchedule, Enrollment, LessonRecord, ExamRecord, Instrument
from app.core.security import get_password_hash
from datetime import date

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

db.add(User(username='admin', password_hash=get_password_hash('admin123'), real_name='管理员', phone='13800138000', role='admin'))
db.add(User(username='teacher1', password_hash=get_password_hash('admin123'), real_name='王老师', phone='13800138001', role='teacher'))
db.add(User(username='manager1', password_hash=get_password_hash('admin123'), real_name='李经理', phone='13800138002', role='manager'))

db.add(Teacher(name='王老师', phone='13811112222', instrument='钢琴', level='senior', bio='十年钢琴教学经验', hire_date=date(2019, 3, 1)))
db.add(Teacher(name='陈老师', phone='13822223333', instrument='小提琴', level='senior', bio='音乐学院毕业', hire_date=date(2020, 6, 15)))
db.add(Teacher(name='张老师', phone='13833334444', instrument='吉他', level='intermediate', bio='民谣吉他教学', hire_date=date(2021, 9, 10)))
db.add(Teacher(name='刘老师', phone='13844445555', instrument='古筝', level='senior', bio='古筝演奏级', hire_date=date(2018, 1, 20)))

db.add(Student(name='小明', phone='13900001111', parent_name='李先生', parent_phone='13900001112', birthday=date(2015, 4, 10), level='beginner'))
db.add(Student(name='小红', phone='13900002222', parent_name='王女士', parent_phone='13900002223', birthday=date(2014, 7, 22), level='intermediate'))
db.add(Student(name='小华', phone='13900003333', parent_name='张先生', parent_phone='13900003334', birthday=date(2016, 1, 5), level='beginner'))
db.add(Student(name='小丽', phone='13900004444', parent_name='赵女士', parent_phone='13900004445', birthday=date(2013, 11, 18), level='advanced'))

db.add(Classroom(name='钢琴房A', capacity=2, piano_count=1, status='available'))
db.add(Classroom(name='钢琴房B', capacity=2, piano_count=1, status='available'))
db.add(Classroom(name='小提琴室', capacity=4, piano_count=0, status='available'))
db.add(Classroom(name='综合教室', capacity=6, piano_count=1, status='available'))

db.commit()

db.add(Course(name='少儿钢琴启蒙班', instrument='钢琴', duration_minutes=45, price=200.00, max_students=1, teacher_id=1, description='适合零基础儿童'))
db.add(Course(name='小提琴进阶班', instrument='小提琴', duration_minutes=60, price=260.00, max_students=2, teacher_id=2, description='二级以上水平'))
db.add(Course(name='民谣吉他速成班', instrument='吉他', duration_minutes=45, price=150.00, max_students=3, teacher_id=3, description='成人零基础速成'))
db.add(Course(name='古筝考级班', instrument='古筝', duration_minutes=60, price=220.00, max_students=2, teacher_id=4, description='备战三级考级'))

db.commit()

db.add(CourseSchedule(course_id=1, classroom_id=1, teacher_id=1, weekday=5, start_time='16:00', end_time='16:45', start_date=date(2026, 6, 1), end_date=date(2026, 12, 31)))
db.add(CourseSchedule(course_id=1, classroom_id=2, teacher_id=1, weekday=6, start_time='10:00', end_time='10:45', start_date=date(2026, 6, 1), end_date=date(2026, 12, 31)))
db.add(CourseSchedule(course_id=2, classroom_id=3, teacher_id=2, weekday=5, start_time='18:00', end_time='19:00', start_date=date(2026, 6, 1), end_date=date(2026, 12, 31)))
db.add(CourseSchedule(course_id=3, classroom_id=4, teacher_id=3, weekday=6, start_time='14:00', end_time='14:45', start_date=date(2026, 6, 1), end_date=date(2026, 12, 31)))
db.add(CourseSchedule(course_id=4, classroom_id=4, teacher_id=4, weekday=0, start_time='09:00', end_time='10:00', start_date=date(2026, 6, 1), end_date=date(2026, 12, 31)))

db.commit()

db.add(Enrollment(student_id=1, course_id=1, schedule_id=1, total_lessons=24, used_lessons=8, amount=4800.00, status='active'))
db.add(Enrollment(student_id=2, course_id=2, schedule_id=3, total_lessons=12, used_lessons=3, amount=3120.00, status='active'))
db.add(Enrollment(student_id=3, course_id=3, schedule_id=4, total_lessons=12, used_lessons=1, amount=1800.00, status='active'))
db.add(Enrollment(student_id=4, course_id=4, schedule_id=5, total_lessons=16, used_lessons=5, amount=3520.00, status='active'))

db.commit()

db.add(LessonRecord(enrollment_id=1, lesson_date=date(2026, 6, 9), status='attended', content='复习C大调音阶，学习二分音符', homework='每天练琴20分钟'))
db.add(LessonRecord(enrollment_id=2, lesson_date=date(2026, 6, 9), status='attended', content='练习空弦，学习D大调', homework='练习空弦10分钟'))
db.add(LessonRecord(enrollment_id=3, lesson_date=date(2026, 6, 8), status='absent'))
db.add(LessonRecord(enrollment_id=4, lesson_date=date(2026, 6, 8), status='attended', content='古筝摇指技法', homework='复习《渔舟唱晚》前半段'))

db.commit()

db.add(ExamRecord(student_id=2, exam_name='2026年夏季小提琴考级', instrument='小提琴', level='三级', exam_date=date(2026, 7, 15), result='pending'))
db.add(ExamRecord(student_id=4, exam_name='2026年古筝考级', instrument='古筝', level='四级', exam_date=date(2026, 8, 10), result='pending'))

db.commit()

db.add(Instrument(name='三角钢琴', brand='Yamaha', model='GB1K', serial_no='YP2024001', status='available', purchase_date=date(2024, 1, 10), price=68000.00))
db.add(Instrument(name='立式钢琴', brand='Kawai', model='KU-S10', serial_no='KP2024002', status='available', purchase_date=date(2024, 2, 15), price=32000.00))
db.add(Instrument(name='小提琴', brand='Suzuki', model='No.280', serial_no='VN2024001', status='available', purchase_date=date(2024, 3, 1), price=2800.00, remark='教学用琴'))
db.add(Instrument(name='古筝', brand='敦煌', model='694KK', serial_no='GZ2024001', status='repair', purchase_date=date(2023, 6, 20), price=5600.00, remark='琴码需维修'))

db.commit()
db.close()
print('Database initialized successfully')