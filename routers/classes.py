from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import random
import string
from master_database import SessionMaster, User, PublicClass, ClassMember
from auth import get_current_user

router = APIRouter(prefix="/classes", tags=["classes"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.get("/", response_class=HTMLResponse)
async def my_classes(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    if user.role == "teacher":
        classes = db.query(PublicClass).filter(PublicClass.teacher_id == user.id).all()
        return templates.TemplateResponse("teacher_classes.html", {
            "request": request,
            "user": user,
            "classes": classes,
            "active_page": "classes"
        })
    elif user.role == "student":
        memberships = db.query(ClassMember).filter(ClassMember.student_id == user.id).all()
        return templates.TemplateResponse("student_classes.html", {
            "request": request,
            "user": user,
            "memberships": memberships,
            "active_page": "classes"
        })
    else:
        return RedirectResponse("/dashboard", status_code=302)

@router.post("/create")
async def create_class(request: Request, name: str = Form(...), description: str = Form(""), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create classes")
        
    code = generate_invite_code()
    # Ensure uniqueness
    while db.query(PublicClass).filter(PublicClass.invite_code == code).first():
        code = generate_invite_code()
        
    new_class = PublicClass(teacher_id=user.id, name=name, description=description, invite_code=code)
    db.add(new_class)
    db.commit()
    
    return RedirectResponse("/classes/", status_code=303)

@router.post("/join")
async def join_class(request: Request, code: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can join classes")
        
    code = code.upper().strip()
    target_class = db.query(PublicClass).filter(PublicClass.invite_code == code).first()
    if not target_class:
        # For simplicity, redirect back with error in future iterations
        return RedirectResponse("/classes/?error=Invalid+Code", status_code=303)
        
    # Check if already a member
    existing = db.query(ClassMember).filter(ClassMember.class_id == target_class.id, ClassMember.student_id == user.id).first()
    if not existing:
        member = ClassMember(class_id=target_class.id, student_id=user.id)
        db.add(member)
        db.commit()
        
    return RedirectResponse("/classes/", status_code=303)

@router.post("/{class_id}/delete")
async def delete_class(request: Request, class_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    target = db.query(PublicClass).filter(PublicClass.id == class_id, PublicClass.teacher_id == user.id).first()
    if target:
        db.delete(target)
        db.commit()
        
    return RedirectResponse("/classes/", status_code=303)
