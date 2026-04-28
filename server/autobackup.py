"""Runs on every app startup — silently saves a dated backup of the database."""
import shutil
import os
from datetime import date
from config import BACKUP_DIR, DATABASE_FILE, DEFAULT_DB_FILENAME, LEGACY_DB_FILENAME

def run_backup():
    if DATABASE_FILE is not None:
        src = str(DATABASE_FILE)
    else:
        src = DEFAULT_DB_FILENAME
    if not os.path.exists(src):
        return
    backup_dir = str(BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)
    # Keep last 30 daily backups
    db_label = DEFAULT_DB_FILENAME.replace(".db", "")
    if os.path.basename(src) == LEGACY_DB_FILENAME:
        db_label = LEGACY_DB_FILENAME.replace(".db", "")
    dst = os.path.join(backup_dir, f"{db_label}_{date.today()}.db")
    if not os.path.exists(dst):  # Only backup once per day
        shutil.copy2(src, dst)
        print(f"[Backup] Saved: {dst}")
    # Clean up backups older than 30 days
    backups = sorted(os.listdir(backup_dir))
    while len(backups) > 30:
        os.remove(os.path.join(backup_dir, backups.pop(0)))
