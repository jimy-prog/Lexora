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

@router.get("/")
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "current_user", None)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    settings = {s.key: s for s in db.query(Settings).all()}
    groups   = db.query(Group).order_by(Group.name).all()
    
    # We use the current_user object as the 'profile'
    profile = user
    
    users = []
    mdb = SessionMaster()
    try:
        users_list = mdb.query(User).filter_by(tenant_id=user.tenant_id).order_by(User.created_at.asc()).all()
        for u in users_list: mdb.expunge(u)
        users = users_list
    finally:
        mdb.close()

    tab      = request.query_params.get("tab", "profile")
    return templates.TemplateResponse("settings_page.html", {
        "request":request, "profile":profile, "settings":settings,
        "groups":groups, "users":users, "tab":tab, "active_page":"settings",
        "current_user": user,
    })

@router.post("/update")
async def update_profile(request: Request):
    user = getattr(request.state, "current_user", None)
    if not user: return RedirectResponse("/login")
    
    form = await request.form()
    mdb = SessionMaster()
    try:
        db_user = mdb.query(User).filter(User.id == user.id).first()
        if db_user:
            db_user.full_name = form.get("name", db_user.full_name)
            db_user.title = form.get("title", db_user.title)
            db_user.bio = form.get("bio", db_user.bio)
            db_user.phone = form.get("phone", db_user.phone)
            db_user.school_name = form.get("school_name", db_user.school_name)
            db_user.bank_details = form.get("bank_details", db_user.bank_details)
            mdb.commit()
    finally:
        mdb.close()
        
    return RedirectResponse("/profile/?tab=profile&saved=1", status_code=303)

@router.post("/upload-photo")
async def upload_photo(request: Request, photo: UploadFile = File(...)):
    user = getattr(request.state, "current_user", None)
    if not user: return RedirectResponse("/login")
    
    if photo.filename:
        ext = photo.filename.rsplit(".",1)[-1]
        filename = f"user_{user.id}.{ext}"
        path = f"./uploads/profile/{filename}"
        with open(path,"wb") as f: shutil.copyfileobj(photo.file, f)
        
        mdb = SessionMaster()
        try:
            db_user = mdb.query(User).filter(User.id == user.id).first()
            if db_user:
                db_user.photo_path = f"/uploads/profile/{filename}"
                mdb.commit()
        finally:
            mdb.close()
            
    return RedirectResponse("/profile/?tab=profile", status_code=303)
