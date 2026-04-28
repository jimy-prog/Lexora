from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Group, Student, Lesson, Attendance

router = APIRouter(prefix="/online")
templates = Jinja2Templates(directory="templates")

def get_mode(g): return getattr(g, 'mode', 'in-person') or 'in-person'
def get_rate_type(g): return getattr(g, 'rate_type', 'per_lesson') or 'per_lesson'
def get_rate_amount(g): return float(getattr(g, 'rate_amount', 0) or 0)
def get_duration(g): return int(getattr(g, 'lesson_duration', 60) or 60)
def get_zoom(g): return getattr(g, 'zoom_link', '') or ''
def get_company(g): return getattr(g, 'company_name', '') or ''

def calc_income(db, group, ms, me):
    held = db.query(Lesson).filter(
        Lesson.group_id==group.id, Lesson.date>=ms,
        Lesson.date<me, Lesson.status=="Held"
    ).count()
    rate_type = get_rate_type(group)
    rate_amount = get_rate_amount(group)
    duration = get_duration(group)
    if rate_type == 'per_lesson':
        income = held * rate_amount
    elif rate_type == 'per_hour':
        income = held * rate_amount * (duration / 60)
    else:
        income = 0
    return {"held": held, "income": round(income),
            "rate_type": rate_type, "rate_amount": rate_amount,
            "duration": duration}

@router.get("/")
def online_view(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    ms = today.replace(day=1)
    me = date(ms.year, ms.month+1, 1) if ms.month < 12 else date(ms.year+1, 1, 1)

    # Show only active groups in online section
    all_groups = db.query(Group).filter(Group.status == "active").all()
    online_groups = [g for g in all_groups if get_mode(g) == 'online']

    group_data = []
    total_income = 0
    for g in online_groups:
        stats = calc_income(db, g, ms, me)
        total_income += stats["income"]
        students = db.query(Student).filter(
            Student.group_id==g.id, Student.archived==False
        ).all()
        group_data.append({
            **stats, "group": g,
            "students": students,
            "student_count": len(students),
            "company": get_company(g),
            "zoom_link": get_zoom(g),
            "mode": get_mode(g),
        })

    todays = db.query(Lesson).filter(Lesson.date == today).all()
    todays_online = [
        l for l in todays
        if l.group and l.group.status == "active" and get_mode(l.group) == 'online'
    ]

    return templates.TemplateResponse("online.html", {
        "request": request,
        "group_data": group_data,
        "total_income": total_income,
        "todays_online": todays_online,
        "today": today,
        "month_str": ms.strftime("%B %Y"),
        "active_page": "online"
    })

@router.post("/group/{gid}/settings")
async def update_settings(gid: int, request: Request,
                           db: Session = Depends(get_db)):
    form = await request.form()
    g = db.query(Group).get(gid)
    if not g:
        return RedirectResponse("/online/", status_code=303)
    g.mode            = form.get("mode", "in-person")
    g.company_name    = form.get("company_name", "")
    g.rate_type       = form.get("rate_type", "per_lesson")
    g.rate_amount     = float(form.get("rate_amount", 0) or 0)
    g.lesson_duration = int(form.get("lesson_duration", 60) or 60)
    g.zoom_link       = form.get("zoom_link", "")
    db.commit()
    return RedirectResponse("/online/", status_code=303)
