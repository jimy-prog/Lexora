import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = os.getenv("APP_NAME", "Lexora")
APP_TAGLINE = os.getenv("APP_TAGLINE", "English Learning Platform")

DEFAULT_DB_FILENAME = "lexora.db"
LEGACY_DB_FILENAME = "teacher_admin.db"

_db_env = os.getenv("DATABASE_URL", "").strip()
if _db_env:
    DATABASE_URL = _db_env
    DATABASE_FILE = None
else:
    lexora_db = BASE_DIR / DEFAULT_DB_FILENAME
    legacy_db = BASE_DIR / LEGACY_DB_FILENAME
    active_db = lexora_db if lexora_db.exists() or not legacy_db.exists() else legacy_db
    DATABASE_FILE = active_db
    DATABASE_URL = f"sqlite:///{active_db}"

SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "lexora-dev-secret-change-me")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "lexora_session")

DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "change-me")

PASSWORD_FILE = BASE_DIR / "lexora_auth_password.txt"
LEGACY_PASSWORD_FILE = BASE_DIR / "auth_password.txt"

BACKUP_DIR = BASE_DIR / "backups"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

LOG_FILENAME = os.getenv("APP_LOG_FILENAME", "lexora.log")
