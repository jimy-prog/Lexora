from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from master_database import SessionMaster, User, MockExam, MockAttempt, TeacherProfile, StudentProfile
from auth import get_current_user

router = APIRouter(prefix="/owner", tags=["owner"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def owner_dashboard(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        return RedirectResponse("/login", status_code=302)
        
    stats = {
        "total_teachers": db.query(User).filter(User.role == "teacher").count(),
        "total_students": db.query(User).filter(User.role == "student").count(),
        "total_mocks": db.query(MockExam).count(),
        "total_attempts": db.query(MockAttempt).count(),
    }
    
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse("owner_dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "recent_users": recent_users,
        "active_page": "owner_dashboard"
    })

@router.get("/users", response_class=HTMLResponse)
async def manage_users(request: Request, role: str = None, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        return RedirectResponse("/login", status_code=302)
        
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
        
    users = query.order_by(User.created_at.desc()).all()
    
    return templates.TemplateResponse("owner_users.html", {
        "request": request,
        "user": user,
        "users": users,
        "active_role": role,
        "active_page": "owner_users"
    })

@router.post("/users/{target_id}/ban")
async def ban_user(request: Request, target_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    target = db.query(User).filter(User.id == target_id).first()
    if target:
        target.is_banned = not target.is_banned
        db.commit()
        
    return RedirectResponse(request.headers.get("referer", "/owner/users"), status_code=303)

@router.post("/users/{target_id}/delete")
async def delete_user(request: Request, target_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    target = db.query(User).filter(User.id == target_id).first()
    if target:
        db.delete(target)
        db.commit()
        
    return RedirectResponse("/owner/users", status_code=303)


from fastapi import UploadFile, File
import shutil
import os
from config import DATA_DIR

@router.post("/database/restore")
async def restore_database(request: Request, db_file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    tenants_dir = os.path.join(DATA_DIR, "database_tenants")
    os.makedirs(tenants_dir, exist_ok=True)
    target_path = os.path.join(tenants_dir, "tenant_1.db")
    
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(db_file.file, buffer)
        
    return RedirectResponse("/owner/?restored=success", status_code=303)
