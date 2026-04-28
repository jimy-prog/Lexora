"""
Adds online teaching columns to existing database.
Run once: python3 migrate_online.py
"""
import sqlite3
from config import DATABASE_FILE, DEFAULT_DB_FILENAME

db_path = str(DATABASE_FILE) if DATABASE_FILE is not None else DEFAULT_DB_FILENAME
conn = sqlite3.connect(db_path)
cur = conn.cursor()

migrations = [
    # Groups
    ("groups", "mode",          "TEXT DEFAULT 'in-person'"),   # in-person / online
    ("groups", "company_name",  "TEXT DEFAULT ''"),
    ("groups", "rate_type",     "TEXT DEFAULT 'monthly'"),     # monthly / per_lesson / per_hour
    ("groups", "rate_amount",   "REAL DEFAULT 0"),
    ("groups", "lesson_duration","INTEGER DEFAULT 60"),        # minutes
    ("groups", "zoom_link",     "TEXT DEFAULT ''"),
    # Students
    ("students", "mode",        "TEXT DEFAULT 'in-person'"),
]

for table, col, definition in migrations:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
        print(f"  ✓ Added {table}.{col}")
    except Exception as e:
        print(f"  — {table}.{col} already exists")

conn.commit()
conn.close()
print("\n✓ Migration complete.")
