from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from master_database import SessionMaster, User, PlatformTenant
from auth import get_current_user
from sqlalchemy import or_

router = APIRouter(prefix="/owner", tags=["owner"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, q: str = "", role: str = "", db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        return RedirectResponse("/login")
        
    query = db.query(User)
    if q:
        query = query.filter(or_(User.username.contains(q), User.email.contains(q), User.full_name.contains(q)))
    if role:
        query = query.filter(User.account_type == role)
        
    users = query.order_by(User.id.desc()).all()
    
    return templates.TemplateResponse("owner_users.html", {
        "request": request,
        "user": user,
        "users": users,
        "q": q,
        "role": role,
        "active_page": "users"
    })

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, db: SessionMaster = Depends(get_mdb), request: Request = None):
    owner = get_current_user(request)
    if not owner or owner.role != "owner":
        raise HTTPException(status_code=403)
        
    u = db.query(User).filter(User.id == user_id).first()
    if u:
        u.is_active = not u.is_active
        db.commit()
    return RedirectResponse("/owner/users", status_code=303)

@router.post("/users/{user_id}/delete")
async def delete_user(user_id: int, db: SessionMaster = Depends(get_mdb), request: Request = None):
    owner = get_current_user(request)
    if not owner or owner.role != "owner":
        raise HTTPException(status_code=403)
        
    u = db.query(User).filter(User.id == user_id).first()
    if u and u.role != "owner":
        db.delete(u)
        db.commit()
    return RedirectResponse("/owner/users", status_code=303)
