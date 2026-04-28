"""
Moves student start_date and end_date forward 1 year where they're in 2024 or 2025.
Run once: python3 fix_student_dates.py
"""
from database import SessionLocal, Student
from datetime import date

db = SessionLocal()
students = db.query(Student).all()
fixed = 0

for s in students:
    changed = False
    if s.start_date and s.start_date.year in (2024, 2025):
        old = s.start_date
        s.start_date = date(old.year + 1, old.month, old.day)
        print(f"  {s.name} start: {old} → {s.start_date}")
        changed = True
    if s.end_date and s.end_date.year in (2024, 2025):
        old = s.end_date
        s.end_date = date(old.year + 1, old.month, old.day)
        print(f"  {s.name} end:   {old} → {s.end_date}")
        changed = True
    if changed:
        fixed += 1

db.commit()
print(f"\n✓ Fixed {fixed} students.")
db.close()
