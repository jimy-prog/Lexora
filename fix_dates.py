"""
Moves Feb 2025 and Mar 2025 lessons to Feb 2026 and Mar 2026.
Run once: python3 fix_dates.py
"""
from database import SessionLocal, Lesson
from datetime import date

db = SessionLocal()

lessons = db.query(Lesson).filter(
    Lesson.date >= date(2025, 2, 1),
    Lesson.date < date(2025, 4, 1)
).all()

print(f"Found {len(lessons)} lessons to move from 2025 → 2026")

for l in lessons:
    old = l.date
    l.date = date(2026, l.date.month, l.date.day)
    print(f"  {old} → {l.date} | {l.group.name}")

db.commit()
print(f"\nDone. {len(lessons)} lessons moved to 2026.")
db.close()
