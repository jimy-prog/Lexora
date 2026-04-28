"""Run this to see all lesson date ranges per group"""
from database import SessionLocal, Lesson, Group
from datetime import date

db = SessionLocal()
groups = db.query(Group).all()
print("=== LESSON DATE RANGES PER GROUP ===\n")
for g in groups:
    lessons = db.query(Lesson).filter(Lesson.group_id==g.id).order_by(Lesson.date).all()
    if not lessons:
        print(f"{g.name}: NO LESSONS")
        continue
    first = lessons[0].date
    last  = lessons[-1].date
    # Show distinct months
    months = sorted(set(f"{l.date.year}-{l.date.month:02d}" for l in lessons))
    print(f"{g.name} ({g.status})")
    print(f"  First: {first} | Last: {last} | Total: {len(lessons)}")
    print(f"  Months: {', '.join(months)}")
    print()
db.close()
