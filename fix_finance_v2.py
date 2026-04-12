"""
Fixes:
1. Adds epl_override column to groups table
2. Each group can have its own per-lesson rate
Run: python3 fix_finance_v2.py
"""
import sqlite3
from config import DATABASE_FILE, DEFAULT_DB_FILENAME

db_path = str(DATABASE_FILE) if DATABASE_FILE is not None else DEFAULT_DB_FILENAME
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add epl_override column
try:
    cur.execute("ALTER TABLE groups ADD COLUMN epl_override REAL DEFAULT 0")
    print("✓ Added groups.epl_override")
except:
    print("— groups.epl_override already exists")

conn.commit()
conn.close()
print("\n✓ Done. Restart the app:")
print("  launchctl stop com.lexora.app && launchctl start com.lexora.app")
