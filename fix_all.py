"""
Fixes:
1. Removes future lessons from archived groups (CEFR)
2. Adds missing waitlist columns
Run: python3 fix_all.py
"""
import sqlite3
from database import SessionLocal, Lesson, Group
from datetime import date
from config import DATABASE_FILE, DEFAULT_DB_FILENAME

print("=== Fix 1: Remove future lessons from archived groups ===")
db = SessionLocal()
today = date.today()
archived = db.query(Group).filter(Group.status.in_(["archived","paused"])).all()
removed = 0
for g in archived:
    future = db.query(Lesson).filter(
        Lesson.group_id == g.id,
        Lesson.date > today
    ).all()
    for l in future:
        for a in l.attendance:
            db.delete(a)
        db.delete(l)
        removed += 1
db.commit()
db.close()
print(f"  ✓ Removed {removed} future lessons from archived groups")

print("\n=== Fix 2: Add missing waitlist columns ===")
db_path = str(DATABASE_FILE) if DATABASE_FILE is not None else DEFAULT_DB_FILENAME
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cols_to_add = [
    ("waitlist", "mode",       "TEXT DEFAULT 'in-person'"),
    ("waitlist", "trial_date", "TEXT"),
    ("waitlist", "trial_done", "INTEGER DEFAULT 0"),
]
for table, col, defn in cols_to_add:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
        print(f"  ✓ Added {table}.{col}")
    except Exception as e:
        print(f"  — {table}.{col} already exists")
conn.commit()
conn.close()

print("\n✓ All fixes done. Restart the app:")
print("  launchctl stop com.lexora.app && launchctl start com.lexora.app")
