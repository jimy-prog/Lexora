"""
Removes duplicate lessons — keeps only ONE lesson per group+date+time.
Keeps the one with attendance data, or the most recent if no attendance.
Run once: python3 fix_duplicates.py
"""
from database import SessionLocal, Lesson, Attendance
from sqlalchemy import func

db = SessionLocal()

# Find all group+date+time combinations that have more than 1 lesson
from collections import defaultdict
all_lessons = db.query(Lesson).order_by(Lesson.date, Lesson.time).all()

# Group by (group_id, date, time)
groups = defaultdict(list)
for l in all_lessons:
    key = (l.group_id, l.date, l.time or "")
    groups[key].append(l)

duplicates_removed = 0
for key, lessons in groups.items():
    if len(lessons) <= 1:
        continue
    # Sort: keep the one with most attendance records
    lessons.sort(key=lambda l: len(l.attendance), reverse=True)
    keeper = lessons[0]
    to_delete = lessons[1:]
    print(f"Duplicate: {key[1]} {keeper.group.name} {key[2]} — keeping id:{keeper.id}, deleting {[l.id for l in to_delete]}")
    for l in to_delete:
        # Delete attendance first
        db.query(Attendance).filter(Attendance.lesson_id == l.id).delete()
        db.delete(l)
        duplicates_removed += 1

db.commit()
print(f"\n✓ Removed {duplicates_removed} duplicate lessons.")
db.close()
