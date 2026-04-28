"""Full system connectivity check - run on Mac"""
from database import SessionLocal, Group, Lesson, Student, Attendance
from datetime import date
from config import DATABASE_FILE, DEFAULT_DB_FILENAME

db = SessionLocal()
today = date.today()

print(f"=== TODAY: {today} ===\n")

print("=== GROUPS STATUS ===")
for g in db.query(Group).all():
    future = db.query(Lesson).filter(
        Lesson.group_id==g.id, Lesson.date>today
    ).count()
    future_held = db.query(Lesson).filter(
        Lesson.group_id==g.id, Lesson.date>today,
        Lesson.status=="Held"
    ).count()
    mode = getattr(g, 'mode', 'in-person')
    print(f"{g.name} | {g.status} | mode:{mode} | future_lessons:{future} | future_marked_held:{future_held}")

print("\n=== FUTURE LESSONS FOR ARCHIVED GROUPS ===")
for g in db.query(Group).filter(Group.status=="archived").all():
    fl = db.query(Lesson).filter(
        Lesson.group_id==g.id, Lesson.date>today
    ).all()
    if fl:
        print(f"  {g.name}: {len(fl)} future lessons still exist!")
        for l in fl[:3]:
            print(f"    -> {l.date} | {l.status}")

print("\n=== PAYMENTS CHECK ===")
from database import Payment
ms = today.replace(day=1)
payments = db.query(Payment).filter(Payment.month==today.strftime("%Y-%m")).all()
print(f"Payments recorded this month: {len(payments)}")

print("\n=== ONLINE COLUMNS CHECK ===")
import sqlite3
db_path = str(DATABASE_FILE) if DATABASE_FILE is not None else DEFAULT_DB_FILENAME
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("PRAGMA table_info(groups)")
cols = [r[1] for r in cur.fetchall()]
online_cols = ['mode','company_name','rate_type','rate_amount','lesson_duration','zoom_link']
for c in online_cols:
    print(f"  groups.{c}: {'✓' if c in cols else '✗ MISSING'}")
conn.close()

db.close()
