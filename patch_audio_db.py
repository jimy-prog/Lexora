import sqlite3

def patch_db():
    conn = sqlite3.connect('master.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE mock_exams ADD COLUMN audio_url VARCHAR")
        print("Added audio_url to mock_exams")
    except sqlite3.OperationalError as e:
        print("Skipped audio_url:", e)
        
    try:
        cursor.execute("ALTER TABLE mock_questions ADD COLUMN correct_answer_text VARCHAR DEFAULT ''")
        print("Added correct_answer_text to mock_questions")
    except sqlite3.OperationalError as e:
        print("Skipped correct_answer_text:", e)
        
    try:
        cursor.execute("ALTER TABLE mock_attempts ADD COLUMN band_score FLOAT")
        print("Added band_score to mock_attempts")
    except sqlite3.OperationalError as e:
        print("Skipped band_score:", e)
        
    conn.commit()
    conn.close()
    print("Database patched successfully.")

if __name__ == "__main__":
    patch_db()
