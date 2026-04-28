"""
Shifts all lessons before 2026 forward by exactly 1 year.
2024-11 → 2025-11
2024-12 → 2025-12
2025-01 → 2026-01
2025-02 → 2026-02
2025-03 → 2026-03
2026-03 stays as-is (already correct)

Run once: python3 fix_all_years.py
"""
from database import SessionLocal, Lesson
from datetime import date

db = SessionLocal()

lessons = db.query(Lesson).filter(
    Lesson.date < date(2026, 1, 1)
).all()

print(f"Found {len(lessons)} lessons to shift forward 1 year\n")

counts = {}
for l in lessons:
    old_date = l.date
    new_date = date(old_date.year + 1, old_date.month, old_date.day)
    l.date = new_date
    key = f"{old_date.year}-{old_date.month:02d} → {new_date.year}-{new_date.month:02d}"
    counts[key] = counts.get(key, 0) + 1

for k, v in sorted(counts.items()):
    print(f"  {k}: {v} lessons")

db.commit()
print(f"\n✓ Done. {len(lessons)} lessons moved forward 1 year.")
db.close()
