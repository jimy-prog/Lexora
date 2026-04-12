"""Simple session-based auth. Single teacher login."""
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
import hashlib, secrets
from config import DEFAULT_ADMIN_PASSWORD, PASSWORD_FILE, LEGACY_PASSWORD_FILE, SESSION_COOKIE_NAME

# Default password — teacher changes this in settings
DEFAULT_PASSWORD = DEFAULT_ADMIN_PASSWORD
SESSION_KEY = SESSION_COOKIE_NAME
_sessions: set = set()

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_stored_hash() -> str:
    if PASSWORD_FILE.exists():
        return PASSWORD_FILE.read_text().strip()
    if LEGACY_PASSWORD_FILE.exists():
        legacy_hash = LEGACY_PASSWORD_FILE.read_text().strip()
        PASSWORD_FILE.write_text(legacy_hash)
        return legacy_hash
    # First run — create default
    h = hash_pw(DEFAULT_PASSWORD)
    PASSWORD_FILE.write_text(h)
    return h

def set_password(new_password: str):
    PASSWORD_FILE.write_text(hash_pw(new_password))

def check_password(pw: str) -> bool:
    return hash_pw(pw) == get_stored_hash()

def create_session() -> str:
    token = secrets.token_hex(32)
    _sessions.add(token)
    return token

def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(SESSION_KEY)
    return token in _sessions if token else False

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=307,
            headers={"Location": f"/login?next={request.url.path}"})

def logout(request: Request):
    token = request.cookies.get(SESSION_KEY)
    if token and token in _sessions:
        _sessions.discard(token)
