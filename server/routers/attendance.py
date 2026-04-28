from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Attendance, Lesson, Student, Group

router = APIRouter(prefix="/attendance")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def attendance_view(request: Request, month: str = None, db: Session = Depends(get_db)):
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        month_start = date(y, m, 1)
    else:
        month_start = today.replace(day=1)
    
    if month_start.month == 12:
        month_end = date(month_start.year + 1, 1, 1)
    else:
        month_end = date(month_start.year, month_start.month + 1, 1)

    lessons = db.query(Lesson).filter(
        Lesson.date >= month_start, Lesson.date < month_end
    ).order_by(Lesson.date).all()

    groups = db.query(Group).all()
    students = db.query(Student).filter(Student.active == True).all()

    # Build matrix: student -> lesson -> status
    all_att = db.query(Attendance).join(Lesson).filter(
        Lesson.date >= month_start, Lesson.date < month_end
    ).all()
    matrix = {}
    for a in all_att:
        matrix[(a.student_id, a.lesson_id)] = a.status

    return templates.TemplateResponse("attendance.html", {
        "request": request,
        "lessons": lessons, "students": students, "groups": groups,
        "matrix": matrix, "month_start": month_start,
        "month_str": month_start.strftime("%Y-%m"),
        "active_page": "attendance"
    })

@router.post("/update")
def update_attendance(
    lesson_id: int = Form(...),
    student_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    rec = db.query(Attendance).filter(
        Attendance.lesson_id == lesson_id,
        Attendance.student_id == student_id
    ).first()
    if rec:
        rec.status = status
    else:
        db.add(Attendance(lesson_id=lesson_id, student_id=student_id, status=status))
    db.commit()
    return {"ok": True}
