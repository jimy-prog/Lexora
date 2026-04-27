from __future__ import annotations
"""Database-backed multi-user auth with owner/admin roles."""
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
import base64
import hashlib
import hmac
import secrets
from config import (
    DEFAULT_ADMIN_PASSWORD,
    LEGACY_PASSWORD_FILE,
    OWNER_EMAIL,
    OWNER_FULL_NAME,
    OWNER_USERNAME,
    PASSWORD_FILE,
    SESSION_COOKIE_NAME,
)
from master_database import SessionMaster, User, AuthSession, PlatformTenant

DEFAULT_PASSWORD = DEFAULT_ADMIN_PASSWORD
SESSION_KEY = SESSION_COOKIE_NAME
SESSION_DAYS = 30

def hash_pw(pw: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 200000
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    )

def _legacy_hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(pw: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2_sha256$"):
        _, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            pw.encode(),
            base64.b64decode(salt_b64.encode()),
            int(iterations),
        )
        return hmac.compare_digest(base64.b64encode(digest).decode(), digest_b64)
    return hmac.compare_digest(_legacy_hash_pw(pw), stored_hash)

def get_stored_hash() -> str:
    if PASSWORD_FILE.exists():
        return PASSWORD_FILE.read_text().strip()
    if LEGACY_PASSWORD_FILE.exists():
        legacy_hash = LEGACY_PASSWORD_FILE.read_text().strip()
        PASSWORD_FILE.write_text(legacy_hash)
        return legacy_hash
    h = hash_pw(DEFAULT_PASSWORD)
    PASSWORD_FILE.write_text(h)
    return h

def set_password(new_password: str, user: User | None = None):
    new_hash = hash_pw(new_password)
    db = SessionMaster()
    try:
        target = user
        if target is None:
            target = db.query(User).filter(User.username == OWNER_USERNAME).first()
        elif getattr(target, "id", None):
            target = db.query(User).filter(User.id == target.id).first()
        if target:
            target.password_hash = new_hash
            if target.role == "owner":
                PASSWORD_FILE.write_text(new_hash)
            db.commit()
        elif user is None:
            PASSWORD_FILE.write_text(new_hash)
    finally:
        db.close()

def check_password(pw: str) -> bool:
    return verify_pw(pw, get_stored_hash())

def _find_user(db, identifier: str):
    ident = (identifier or "").strip().lower()
    if not ident:
        return None
    return db.query(User).filter(
        (User.username == ident) | (User.email == ident)
    ).first()

def ensure_owner_account():
    db = SessionMaster()
    try:
        if db.query(User).count() > 0:
            return
            
        import master_database
        master_database.init_master_db()
            
        tenant = PlatformTenant(slug="lexora_admin", db_filename="tenant_1.db")
        db.add(tenant)
        db.flush()
        
        initial_hash = get_stored_hash()
        owner = User(
            tenant_id=tenant.id,
            username=OWNER_USERNAME.strip().lower(),
            email=OWNER_EMAIL.strip().lower(),
            full_name=OWNER_FULL_NAME.strip(),
            role="owner",
            password_hash=initial_hash,
            is_active=True,
        )
        db.add(owner)
        db.commit()
    finally:
        db.close()

def authenticate_user(identifier: str, password: str):
    db = SessionMaster()
    try:
        user = _find_user(db, identifier)
        if not user or not user.is_active:
            return None
        if not verify_pw(password, user.password_hash):
            return None
        if not user.password_hash.startswith("pbkdf2_sha256$"):
            user.password_hash = hash_pw(password)
            PASSWORD_FILE.write_text(user.password_hash)
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def check_user_password(user: User, password: str) -> bool:
    return verify_pw(password, user.password_hash)

def create_session(user_id: int) -> str:
    db = SessionMaster()
    try:
        token = secrets.token_hex(32)
        db.add(AuthSession(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=SESSION_DAYS),
        ))
        db.commit()
        return token
    finally:
        db.close()

def get_current_user(request: Request):
    token = request.cookies.get(SESSION_KEY)
    if not token:
        return None
    db = SessionMaster()
    try:
        session = db.query(AuthSession).filter(AuthSession.token == token).first()
        if not session:
            return None
        if session.expires_at and session.expires_at < datetime.utcnow():
            db.delete(session)
            db.commit()
            return None
        user = db.query(User).filter(User.id == session.user_id, User.is_active == True).first()
        if not user:
            return None
        return user
    finally:
        db.close()

def is_authenticated(request: Request) -> bool:
    return get_current_user(request) is not None

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=307,
            headers={"Location": f"/login?next={request.url.path}"})

def require_owner(request: Request):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return user

def logout(request: Request):
    token = request.cookies.get(SESSION_KEY)
    if not token:
        return
    db = SessionMaster()
    try:
        session = db.query(AuthSession).filter(AuthSession.token == token).first()
        if session:
            db.delete(session)
            db.commit()
    finally:
        db.close()
