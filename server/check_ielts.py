"""Check IELTS New attendance for March 2026"""
from database import SessionLocal, Group, Lesson, Attendance, Student
from datetime import date

db = SessionLocal()
g = db.query(Group).filter(Group.name=="IELTS New").first()
print(f"Group: {g.name} | status: {g.status}")
print()

# Students
students = db.query(Student).filter(Student.group_id==g.id).all()
print("Students:")
for s in students:
    print(f"  {s.name} | archived:{s.archived} | start:{s.start_date} | end:{s.end_date}")
print()

# March 2026 lessons
ms = date(2026,3,1); me = date(2026,4,1)
lessons = db.query(Lesson).filter(
    Lesson.group_id==g.id,
    Lesson.date>=ms, Lesson.date<me
).all()
print(f"March 2026 lessons: {len(lessons)}")
for l in lessons:
    print(f"  {l.date} | {l.status} | attendance: {len(l.attendance)}")
    for a in l.attendance:
        print(f"    -> {a.student.name} | {a.status}")
db.close()
