from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Group, Student, Lesson, Attendance

router = APIRouter(prefix="/archive")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def archive_view(request: Request, db: Session = Depends(get_db)):
    archived_groups  = db.query(Group).filter(Group.status=="archived").order_by(Group.archived_date.desc()).all()
    archived_students = db.query(Student).filter(Student.archived==True, Student.banned==False).order_by(Student.end_date.desc()).all()
    return templates.TemplateResponse("archive.html", {
        "request": request,
        "archived_groups": archived_groups,
        "archived_students": archived_students,
        "active_page": "archive"
    })

@router.post("/group/{gid}/restore")
def restore_group(gid: int, db: Session = Depends(get_db)):
    g = db.query(Group).get(gid)
    if g:
        g.status = "active"
        g.archived_date = None
        db.commit()
    return RedirectResponse("/archive/", status_code=303)

@router.post("/student/{sid}/restore")
def restore_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        s.archived = False
        s.active = True
        s.end_date = None
        db.commit()
    return RedirectResponse("/archive/", status_code=303)
