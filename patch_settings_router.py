import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/routers/settings_router.py"
with open(file_path, "r") as f:
    content = f.read()

if "from master_database import SessionMaster, User" not in content:
    content = content.replace(
        "from database import get_db, Settings, Group",
        "from database import get_db, Settings, Group\nfrom master_database import SessionMaster, User"
    )

old_current_user = """def _current_user(request: Request, db: Session):
    user = getattr(request.state, "current_user", None)
    if user and getattr(user, "id", None):
        return db.query(User).filter(User.id == user.id).first()
    return None"""

new_current_user = """def _current_user(request: Request):
    user = getattr(request.state, "current_user", None)
    if user and getattr(user, "id", None):
        mdb = SessionMaster()
        try:
            u = mdb.query(User).filter(User.id == user.id).first()
            if u: mdb.expunge(u)
            return u
        finally:
            mdb.close()
    return None"""

content = content.replace(old_current_user, new_current_user)

old_user_query_1 = "user = _current_user(request, db)"
new_user_query_1 = "user = _current_user(request)"
content = content.replace(old_user_query_1, new_user_query_1)

old_create_user = """def create_user(request: Request,
                      username: str = Form(...),
                      email: str = Form(...),
                      full_name: str = Form(""),
                      role: str = Form("admin"),
                      password: str = Form(...),
                      db: Session = Depends(get_db)):
    actor = _current_user(request)
    if not actor or actor.role != "owner":
        return RedirectResponse("/profile/?tab=security&error=owner_only", status_code=302)
    username = username.strip().lower()
    email = email.strip().lower()
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        return RedirectResponse("/profile/?tab=security&error=user_exists", status_code=302)
    db.add(User(
        username=username,
        email=email,
        full_name=full_name.strip(),
        role=role if role in {"owner", "admin"} else "admin",
        password_hash=hash_pw(password),
        is_active=True,
    ))
    db.commit()"""

new_create_user = """def create_user(request: Request,
                      username: str = Form(...),
                      email: str = Form(...),
                      full_name: str = Form(""),
                      role: str = Form("admin"),
                      password: str = Form(...),
                      db: Session = Depends(get_db)):
    actor = _current_user(request)
    if not actor or actor.role != "owner":
        return RedirectResponse("/profile/?tab=security&error=owner_only", status_code=302)
    username = username.strip().lower()
    email = email.strip().lower()
    mdb = SessionMaster()
    try:
        if mdb.query(User).filter((User.username == username) | (User.email == email)).first():
            return RedirectResponse("/profile/?tab=security&error=user_exists", status_code=302)
        mdb.add(User(
            tenant_id=actor.tenant_id,
            username=username,
            email=email,
            full_name=full_name.strip(),
            role=role if role in {"owner", "admin"} else "admin",
            password_hash=hash_pw(password),
            is_active=True,
        ))
        mdb.commit()
    finally:
        mdb.close()"""
content = content.replace(old_create_user, new_create_user)

old_toggle = """def toggle_user(request: Request, uid: int, db: Session = Depends(get_db)):
    actor = _current_user(request)
    if not actor or actor.role != "owner":
        return RedirectResponse("/profile/?tab=security&error=owner_only", status_code=302)
    user = db.query(User).filter(User.id == uid).first()
    if user and user.id != actor.id:
        user.is_active = not user.is_active
        db.commit()"""

new_toggle = """def toggle_user(request: Request, uid: int, db: Session = Depends(get_db)):
    actor = _current_user(request)
    if not actor or actor.role != "owner":
        return RedirectResponse("/profile/?tab=security&error=owner_only", status_code=302)
    mdb = SessionMaster()
    try:
        user = mdb.query(User).filter(User.id == uid).first()
        if user and user.id != actor.id and user.tenant_id == actor.tenant_id:
            user.is_active = not user.is_active
            mdb.commit()
    finally:
        mdb.close()"""
content = content.replace(old_toggle, new_toggle)

with open(file_path, "w") as f:
    f.write(content)

print("settings_router patched")
