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

    # New columns for Mock overhaul
    try:
        cursor.execute("ALTER TABLE mock_attempts ADD COLUMN feedback_preference TEXT")
        print("Added feedback_preference to mock_attempts")
    except sqlite3.OperationalError as e:
        print(f"Skipping feedback_preference: {e}")

    try:
        cursor.execute("ALTER TABLE mock_attempts ADD COLUMN selected_teacher_id INTEGER")
        print("Added selected_teacher_id to mock_attempts")
    except sqlite3.OperationalError as e:
        print(f"Skipping selected_teacher_id: {e}")

    try:
        cursor.execute("ALTER TABLE mock_attempt_answers ADD COLUMN audio_url TEXT")
        print("Added audio_url to mock_attempt_answers")
    except sqlite3.OperationalError as e:
        print(f"Skipping audio_url: {e}")

    try:
        cursor.execute("ALTER TABLE mock_attempt_answers ADD COLUMN file_url TEXT")
        print("Added file_url to mock_attempt_answers")
    except sqlite3.OperationalError as e:
        print(f"Skipping file_url: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
