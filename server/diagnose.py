"""Full diagnostic — run this and paste output"""
from database import SessionLocal, Group, Lesson, Attendance, Student
from datetime import date

db = SessionLocal()
today = date.today()
print(f"Today: {today}\n")

print("=== GROUPS ===")
for g in db.query(Group).all():
    lessons = db.query(Lesson).filter(Lesson.group_id==g.id).all()
    held = [l for l in lessons if l.status=="Held"]
    future_held = [l for l in held if l.date > today]
    print(f"{g.name} | {g.status} | archived:{g.archived_date}")
    print(f"  Total lessons:{len(lessons)} | Held:{len(held)} | Future marked Held:{len(future_held)}")
    if future_held:
        for l in future_held[:3]:
            print(f"    -> {l.date} marked as Held (should be Scheduled!)")
    # Finance check
    lpm = g.lessons_per_week * g.weeks_per_month
    epl_ind = g.price_monthly * g.teacher_pct / lpm
    epl_grp = 25000
    print(f"  Price:{g.price_monthly} | Teacher%:{g.teacher_pct} | lpm:{lpm}")
    print(f"  EPL if individual: {epl_ind:.0f} | EPL if group: {epl_grp}")
    print()

print("=== MARCH 2026 LESSONS FOR CEFR (post-archive) ===")
ms = date(2026,3,1); me = date(2026,4,1)
cefr = db.query(Group).filter(Group.name=="CEFR Group").first()
if cefr:
    lessons = db.query(Lesson).filter(
        Lesson.group_id==cefr.id,
        Lesson.date>=ms, Lesson.date<me
    ).order_by(Lesson.date).all()
    print(f"CEFR archived_date: {cefr.archived_date}")
    print(f"March 2026 lessons: {len(lessons)}")
    for l in lessons:
        att_count = len(l.attendance)
        print(f"  {l.date} | {l.status} | att:{att_count}")

db.close()
