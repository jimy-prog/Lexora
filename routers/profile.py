from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
from master_database import User, SessionMaster
from database import get_db, Base, Settings, Group
import os, shutil

router = APIRouter(prefix="/profile")
templates = Jinja2Templates(directory="templates")
os.makedirs("./uploads/profile", exist_ok=True)

class TeacherProfile(Base):
    __tablename__ = "teacher_profile"
    __table_args__ = {"extend_existing": True}
    id=Column(Integer,primary_key=True); name=Column(String,default="")
    title=Column(String,default=""); bio=Column(Text,default="")
    phone=Column(String,default=""); email=Column(String,default="")
    school_name=Column(String,default="")
    bank_details=Column(Text,default=""); photo_path=Column(String,default="")
    created_at=Column(DateTime,default=datetime.utcnow)



def get_profile(db, current_user=None):
    p = db.query(TeacherProfile).first()
    if not p:
        p = TeacherProfile(
            name=current_user.full_name if current_user else "",
            title="",
            school_name=""
        )
        db.add(p)
        db.commit()
        db.refresh(p)
    else:
        # Clean up legacy placeholders if they exist
        modified = False
        if p.name == "Jamshid" and current_user:
            p.name = current_user.full_name
            modified = True
        elif not p.name and current_user:
            p.name = current_user.full_name
            modified = True
            
        if p.title == "English Teacher":
            p.title = ""
            modified = True
        if p.school_name == "Language Vision":
            p.school_name = ""
            modified = True
            
        if modified:
            db.commit()
            db.refresh(p)
    return p

@router.get("/")
def profile_page(request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "current_user", None)
    profile  = get_profile(db, current_user)
    settings = {s.key: s for s in db.query(Settings).all()}
    groups   = db.query(Group).order_by(Group.name).all()
    
    users = []
    if current_user:
        mdb = SessionMaster()
        try:
            users_list = mdb.query(User).filter_by(tenant_id=current_user.tenant_id).order_by(User.created_at.asc()).all()
            for u in users_list: mdb.expunge(u)
            users = users_list
        finally:
            mdb.close()

    tab      = request.query_params.get("tab", "profile")
    if current_user:
        if tab == "finance" and current_user.role not in ["owner", "teacher"]:
            tab = "profile"
        elif tab == "system" and current_user.role != "owner":
            tab = "profile"
            
    return templates.TemplateResponse("settings_page.html", {
        "request":request, "profile":profile, "settings":settings,
        "groups":groups, "users":users, "tab":tab, "active_page":"settings",
        "current_user": current_user,
    })

@router.post("/update")
async def update_profile(request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "current_user", None)
    form = await request.form()
    p = get_profile(db, current_user)
    for f in ["name","title","bio","phone","email","school_name","bank_details"]:
        if f in form: setattr(p, f, form[f])
    db.commit()
    return RedirectResponse("/profile/?tab=profile&saved=1", status_code=303)

@router.post("/upload-photo")
async def upload_photo(request: Request, photo: UploadFile = File(...), db: Session = Depends(get_db)):
    current_user = getattr(request.state, "current_user", None)
    p = get_profile(db, current_user)
    if photo.filename:
        ext = photo.filename.rsplit(".",1)[-1]
        path = f"./uploads/profile/teacher_photo.{ext}"
        with open(path,"wb") as f: shutil.copyfileobj(photo.file, f)
        p.photo_path = f"/uploads/profile/teacher_photo.{ext}"
        db.commit()
    return RedirectResponse("/profile/?tab=profile", status_code=303)
