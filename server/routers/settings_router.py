from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, Settings, Group
from master_database import SessionMaster, User
from auth import check_user_password, set_password, hash_pw

router = APIRouter(prefix="/settings")
templates = Jinja2Templates(directory="templates")

def _current_user(request: Request):
    user = getattr(request.state, "current_user", None)
    if user and getattr(user, "id", None):
        mdb = SessionMaster()
        try:
            u = mdb.query(User).filter(User.id == user.id).first()
            if u: mdb.expunge(u)
            return u
        finally:
            mdb.close()
    return None

@router.get("/")
def settings_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse("/profile/", status_code=302)

@router.post("/update")
async def update_settings(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    for key, value in form.items():
        s = db.query(Settings).filter(Settings.key == key).first()
        if s: s.value = value
        else: db.add(Settings(key=key, value=value))
    db.commit()
    return RedirectResponse("/profile/?tab=finance", status_code=303)

@router.post("/group/{gid}/update")
async def update_group(gid: int, request: Request, db: Session = Depends(get_db)):
    g = db.query(Group).get(gid)
    if not g:
        return RedirectResponse("/groups/", status_code=303)
    form = await request.form()
    try:
        if "price_monthly"    in form: g.price_monthly    = float(form["price_monthly"])
        if "teacher_pct"      in form: g.teacher_pct      = float(form["teacher_pct"]) / 100
        if "lessons_per_week" in form: g.lessons_per_week = int(form["lessons_per_week"])
        if "weeks_per_month"  in form: g.weeks_per_month  = int(form["weeks_per_month"])
        if "schedule"         in form: g.schedule         = form["schedule"]
        if "notes"            in form: g.notes            = form["notes"]
        if "epl_override"     in form: g.epl_override     = float(form.get("epl_override") or 0)
        if "finance_mode"     in form: g.finance_mode     = form.get("finance_mode","standard")
        # Online fields
        if "mode"             in form: g.mode             = form["mode"]
        if "company_name"     in form: g.company_name     = form.get("company_name","")
        if "rate_type"        in form: g.rate_type        = form.get("rate_type","per_lesson")
        if "rate_amount"      in form: g.rate_amount      = float(form.get("rate_amount") or 0)
        if "lesson_duration"  in form: g.lesson_duration  = int(form.get("lesson_duration") or 60)
        if "zoom_link"        in form: g.zoom_link        = form.get("zoom_link","")
        db.commit()
    except Exception as e:
        print(f"Error updating group {gid}: {e}")
    return RedirectResponse("/groups/", status_code=303)

@router.post("/group/{gid}/archive")
def archive_group(gid: int, db: Session = Depends(get_db)):
    from datetime import date
    g = db.query(Group).get(gid)
    if g:
        g.status = "archived"
        g.archived_date = date.today()
        for s in g.students:
            if not s.archived:
                s.active = False; s.archived = True; s.end_date = date.today()
        db.commit()
    return RedirectResponse("/groups/", status_code=303)

@router.post("/group/{gid}/pause")
def pause_group(gid: int, db: Session = Depends(get_db)):
    g = db.query(Group).get(gid)
    if g:
        g.status = "paused" if g.status == "active" else "active"
        db.commit()
    return RedirectResponse("/groups/", status_code=303)

@router.post("/group/{gid}/restore")
def restore_group(gid: int, db: Session = Depends(get_db)):
    g = db.query(Group).get(gid)
    if g:
        g.status = "active"; g.archived_date = None
        db.commit()
    return RedirectResponse("/groups/", status_code=303)

@router.post("/change-password")
async def change_password(request: Request,
                          current_pw: str = Form(...),
                          new_pw: str = Form(...),
                          db: Session = Depends(get_db)):
    user = _current_user(request)
    if not user or not check_user_password(user, current_pw):
        return RedirectResponse("/profile/?tab=security&error=wrong_password", status_code=302)
    set_password(new_pw, user=user)
    return RedirectResponse("/profile/?tab=security&success=password_changed", status_code=302)

@router.post("/users/create")
async def create_user(request: Request,
                      username: str = Form(...),
                      email: str = Form(...),
                      full_name: str = Form(""),
                      role: str = Form("admin"),
                      password: str = Form(...),
                      db: Session = Depends(get_db)):
    actor = _current_user(request, db)
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
    db.commit()
    return RedirectResponse("/profile/?tab=security&success=user_created", status_code=302)

@router.post("/users/{uid}/toggle")
async def toggle_user(request: Request, uid: int, db: Session = Depends(get_db)):
    actor = _current_user(request, db)
    if not actor or actor.role != "owner":
        return RedirectResponse("/profile/?tab=security&error=owner_only", status_code=302)
    user = db.query(User).filter(User.id == uid).first()
    if user and user.id != actor.id:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse("/profile/?tab=security&success=user_updated", status_code=302)
