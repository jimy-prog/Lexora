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
    id=Column(Integer,primary_key=True); name=Column(String,default="Jamshid")
    title=Column(String,default="English Teacher"); bio=Column(Text,default="")
    phone=Column(String,default=""); email=Column(String,default="")
    school_name=Column(String,default="Language Vision")
    bank_details=Column(Text,default=""); photo_path=Column(String,default="")
    created_at=Column(DateTime,default=datetime.utcnow)



def get_profile(db):
    p = db.query(TeacherProfile).first()
    if not p:
        p = TeacherProfile(); db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("/")
def profile_page(request: Request, db: Session = Depends(get_db)):
    profile  = get_profile(db)
    settings = {s.key: s for s in db.query(Settings).all()}
    groups   = db.query(Group).order_by(Group.name).all()
    
    users = []
    if getattr(request.state, "current_user", None):
        mdb = SessionMaster()
        try:
            users_list = mdb.query(User).filter_by(tenant_id=request.state.current_user.tenant_id).order_by(User.created_at.asc()).all()
            for u in users_list: mdb.expunge(u)
            users = users_list
        finally:
            mdb.close()

    tab      = request.query_params.get("tab", "profile")
    return templates.TemplateResponse("settings_page.html", {
        "request":request, "profile":profile, "settings":settings,
        "groups":groups, "users":users, "tab":tab, "active_page":"settings",
        "current_user": getattr(request.state, "current_user", None),
    })

@router.post("/update")
async def update_profile(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    p = get_profile(db)
    for f in ["name","title","bio","phone","email","school_name","bank_details"]:
        if f in form: setattr(p, f, form[f])
    db.commit()
    return RedirectResponse("/profile/?tab=profile&saved=1", status_code=303)

@router.post("/upload-photo")
async def upload_photo(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    p = get_profile(db)
    if photo.filename:
        ext = photo.filename.rsplit(".",1)[-1]
        path = f"./uploads/profile/teacher_photo.{ext}"
        with open(path,"wb") as f: shutil.copyfileobj(photo.file, f)
        p.photo_path = f"/uploads/profile/teacher_photo.{ext}"
        db.commit()
    return RedirectResponse("/profile/?tab=profile", status_code=303)
