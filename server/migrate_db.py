import sqlite3

def migrate():
    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    
    print("Starting migration...")
    
    # Add columns to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN account_type TEXT DEFAULT 'student'")
        print("Added account_type to users")
    except sqlite3.OperationalError as e:
        print(f"Skipping account_type: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN study_focus TEXT DEFAULT ''")
        print("Added study_focus to users")
    except sqlite3.OperationalError as e:
        print(f"Skipping study_focus: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_public_teacher BOOLEAN DEFAULT 0")
        print("Added is_public_teacher to users")
    except sqlite3.OperationalError as e:
        print(f"Skipping is_public_teacher: {e}")

    # Ensure student_id in mock_attempts is a ForeignKey to users (SQLite doesn't support easy ALTER for FK, but we can ensure the column exists)
    # Actually, it was already student_id, just needed to be linked in ORM.
    
    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
