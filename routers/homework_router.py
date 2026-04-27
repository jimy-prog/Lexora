from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from datetime import date, datetime
from database import get_db, Base, Group, Student, Lesson

router = APIRouter(prefix="/homework")
templates = Jinja2Templates(directory="templates")

# ── Homework models (created inline, safe to add) ────────────────────────────
class Homework(Base):
    __tablename__ = "homework"
    __table_args__ = {"extend_existing": True}
    id          = Column(Integer, primary_key=True)
    lesson_id   = Column(Integer, ForeignKey("lessons.id"))
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    due_date    = Column(Date, nullable=True)
    completed   = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    lesson      = relationship("Lesson")
    submissions = relationship("HomeworkSubmission", back_populates="homework", cascade="all, delete-orphan")

class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"
    __table_args__ = {"extend_existing": True}
    id          = Column(Integer, primary_key=True)
    homework_id = Column(Integer, ForeignKey("homework.id"))
    student_id  = Column(Integer, ForeignKey("students.id"))
    submitted   = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    homework    = relationship("Homework", back_populates="submissions")
    student     = relationship("Student")

# Create tables


def _enrich(hw, today):
    subs = hw.submissions
    hw.submitted = sum(1 for s in subs if s.submitted)
    hw.total     = len(subs)
    hw.is_overdue = hw.due_date and hw.due_date < today and not hw.completed
    return hw

@router.get("/")
def homework_list(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    active    = db.query(Homework).filter(Homework.completed == False).order_by(Homework.created_at.desc()).all()
    completed = db.query(Homework).filter(Homework.completed == True).order_by(Homework.created_at.desc()).limit(20).all()
    for hw in active + completed: _enrich(hw, today)

    groups = db.query(Group).filter(Group.status == "active").all()

    # Lessons by group for JS dropdown
    lessons_by_group = {}
    for g in groups:
        ls = db.query(Lesson).filter(Lesson.group_id == g.id, Lesson.status == "Held").order_by(Lesson.date.desc()).limit(30).all()
        lessons_by_group[str(g.id)] = [{"id": l.id, "date": str(l.date), "time": l.time or "", "topic": l.topic or ""} for l in ls]

    return templates.TemplateResponse("homework.html", {
        "request": request, "active": active, "completed": completed,
        "groups": groups, "lessons_by_group": lessons_by_group,
        "active_page": "homework"
    })

@router.post("/add")
def add_homework(
    title: str = Form(...), lesson_id: int = Form(...),
    group_id: int = Form(...), description: str = Form(""),
    due_date: str = Form(""), db: Session = Depends(get_db)
):
    hw = Homework(
        lesson_id=int(lesson_id), title=title, description=description,
        due_date=date.fromisoformat(due_date) if due_date else None
    )
    db.add(hw); db.flush()
    students = db.query(Student).filter(Student.group_id == int(group_id), Student.active == True).all()
    for s in students:
        db.add(HomeworkSubmission(homework_id=hw.id, student_id=s.id, submitted=False))
    db.commit()
    return RedirectResponse("/homework/", status_code=303)

@router.post("/{hid}/complete")
def complete_hw(hid: int, db: Session = Depends(get_db)):
    hw = db.query(Homework).get(hid)
    if hw: hw.completed = True; db.commit()
    return RedirectResponse("/homework/", status_code=303)

@router.post("/{hid}/reopen")
def reopen_hw(hid: int, db: Session = Depends(get_db)):
    hw = db.query(Homework).get(hid)
    if hw: hw.completed = False; db.commit()
    return RedirectResponse("/homework/", status_code=303)

@router.post("/{hid}/update-submissions")
async def update_submissions(hid: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    for key, val in form.items():
        if key.startswith("sub_"):
            sub_id = int(key.replace("sub_", ""))
            sub = db.query(HomeworkSubmission).get(sub_id)
            if sub: sub.submitted = (val == "1")
    db.commit()
    return RedirectResponse("/homework/", status_code=303)

@router.get("/api/lessons/{group_id}")
def get_lessons(group_id: int, db: Session = Depends(get_db)):
    ls = db.query(Lesson).filter(Lesson.group_id == group_id, Lesson.status == "Held").order_by(Lesson.date.desc()).limit(30).all()
    return JSONResponse([{"id": l.id, "date": str(l.date), "time": l.time or "", "topic": l.topic or ""} for l in ls])
