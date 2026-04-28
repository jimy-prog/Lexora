from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db, Lesson, Group, Attendance, Student

router = APIRouter(prefix="/lessons")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def list_lessons(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    lessons = db.query(Lesson).filter(
        Lesson.date >= week_start, Lesson.date <= week_end
    ).order_by(Lesson.date, Lesson.time).all()
    groups = db.query(Group).all()
    upcoming = db.query(Lesson).filter(Lesson.date > today).order_by(Lesson.date, Lesson.time).limit(15).all()
    return templates.TemplateResponse("lessons.html", {
        "request": request, "lessons": lessons, "groups": groups,
        "today": today, "week_start": week_start, "week_end": week_end,
        "upcoming": upcoming, "active_page": "lessons"
    })

@router.post("/add")
def add_lesson(
    group_id: int = Form(...),
    date_str: str = Form(...),
    time: str = Form(""),
    status: str = Form("Held"),
    topic: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    lesson_date = date.fromisoformat(date_str)
    lesson = Lesson(group_id=group_id, date=lesson_date, time=time,
                    status=status, topic=topic, notes=notes)
    db.add(lesson); db.commit(); db.refresh(lesson)
    if status == "Held":
        students = db.query(Student).filter(
            Student.group_id == group_id, Student.active == True
        ).all()
        for s in students:
            db.add(Attendance(lesson_id=lesson.id, student_id=s.id, status="Present"))
        db.commit()
    return RedirectResponse("/lessons/", status_code=303)

@router.post("/{lid}/status")
def update_status(lid: int, status: str = Form(...), db: Session = Depends(get_db)):
    l = db.query(Lesson).get(lid)
    if l: l.status = status; db.commit()
    return RedirectResponse("/lessons/", status_code=303)

@router.post("/{lid}/delete")
def delete_lesson(lid: int, db: Session = Depends(get_db)):
    l = db.query(Lesson).get(lid)
    if l: db.delete(l); db.commit()
    return RedirectResponse("/lessons/", status_code=303)

@router.get("/{lid}")
def lesson_detail(lid: int, request: Request, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).get(lid)
    records = db.query(Attendance).filter(Attendance.lesson_id == lid).all()
    students = db.query(Student).filter(
        Student.group_id == lesson.group_id, Student.active == True
    ).all()
    attended = {r.student_id: r for r in records}
    return templates.TemplateResponse("lesson_detail.html", {
        "request": request, "lesson": lesson, "records": records,
        "students": students, "attended": attended, "active_page": "lessons"
    })

@router.post("/{lid}/save")
async def save_lesson(lid: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    lesson = db.query(Lesson).get(lid)
    if not lesson:
        return RedirectResponse("/lessons/", status_code=303)
    lesson.topic = form.get("topic", "")
    lesson.homework = form.get("homework", "")
    lesson.notes = form.get("notes", "")
    lesson.status = form.get("status", lesson.status)
    for key, val in form.items():
        if key.startswith("att_"):
            sid = int(key.replace("att_", ""))
            rec = db.query(Attendance).filter(
                Attendance.lesson_id == lid, Attendance.student_id == sid
            ).first()
            if rec:
                rec.status = val
            else:
                db.add(Attendance(lesson_id=lid, student_id=sid, status=val))
    db.commit()
    return RedirectResponse(f"/lessons/{lid}", status_code=303)
