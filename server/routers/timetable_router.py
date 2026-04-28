from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db, Group, Lesson, Attendance, Student

router = APIRouter(prefix="/timetable")
templates = Jinja2Templates(directory="templates")

def nm(d):
    if d.month == 12: return date(d.year+1,1,1)
    return date(d.year, d.month+1, 1)

def disp(lesson, today):
    if lesson.status in ("Holiday","Cancelled","Rescheduled"): return lesson.status
    if lesson.date > today: return "Upcoming"
    if lesson.date == today: return "Today"
    return "Held"

def get_students(db, lesson):
    sts = db.query(Student).filter(Student.group_id == lesson.group_id).all()
    active = [s for s in sts if not s.archived and
              (s.start_date is None or s.start_date <= lesson.date) and
              (s.end_date is None or s.end_date >= lesson.date)]
    return active if active else [s for s in sts if not s.archived]

def filter_lessons(lessons, show):
    if show == "active":
        return [l for l in lessons if l.group and l.group.status == "active"]
    if show == "archived":
        return [l for l in lessons if l.group and l.group.status == "archived"]
    return lessons  # "all"

@router.get("/")
def daily(request: Request, d: str = None, show: str = "all", db: Session = Depends(get_db)):
    today = date.today()
    vd = date.fromisoformat(d) if d else today
    all_lessons = db.query(Lesson).filter(Lesson.date == vd).order_by(Lesson.time).all()
    lessons = filter_lessons(all_lessons, show)
    day_data = []
    for l in lessons:
        sts = get_students(db, l)
        att_map = {a.student_id: a for a in l.attendance}
        day_data.append({
            "lesson": l, "students": sts, "att_map": att_map,
            "marked": len(l.attendance) > 0,
            "display_status": disp(l, today),
            "is_past": l.date < today,
            "is_today": l.date == today,
            "is_future": l.date > today,
        })
    return templates.TemplateResponse("timetable.html", {
        "request": request, "view": "daily",
        "view_date": vd, "today": today,
        "day_data": day_data,
        "prev_date": (vd - timedelta(days=1)).isoformat(),
        "next_date": (vd + timedelta(days=1)).isoformat(),
        "show": show, "active_page": "timetable"
    })

@router.get("/weekly")
def weekly(request: Request, week: str = None, show: str = "all", db: Session = Depends(get_db)):
    today = date.today()
    if week:
        parts = week.split("-")
        ws = date(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        ws = today - timedelta(days=today.weekday())
    we = ws + timedelta(days=6)
    all_lessons = db.query(Lesson).filter(Lesson.date >= ws, Lesson.date <= we).order_by(Lesson.date, Lesson.time).all()
    lessons = filter_lessons(all_lessons, show)
    times = sorted(set(l.time for l in lessons if l.time)) or ["14:30","16:00","17:30","18:00","19:00"]
    days = []
    for i in range(7):
        d2 = ws + timedelta(days=i)
        dl = [l for l in lessons if l.date == d2]
        bt = {}
        for l in dl: bt.setdefault(l.time or "—", []).append(l)
        days.append({
            "name": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][i],
            "date": d2, "is_today": d2 == today,
            "is_past": d2 < today, "lessons_by_time": bt
        })
    return templates.TemplateResponse("timetable.html", {
        "request": request, "view": "weekly", "today": today,
        "week_start": ws, "week_end": we, "week_days": days, "time_slots": times,
        "prev_week": (ws - timedelta(days=7)).isoformat(),
        "next_week": (ws + timedelta(days=7)).isoformat(),
        "show": show, "active_page": "timetable"
    })

@router.get("/monthly")
def monthly(request: Request, month: str = None, show: str = "all", db: Session = Depends(get_db)):
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        ms = date(y, m, 1)
    else:
        ms = today.replace(day=1)
    me = nm(ms)

    # Simple direct query — no complex filters
    all_lessons = db.query(Lesson).filter(
        Lesson.date >= ms,
        Lesson.date < me
    ).order_by(Lesson.time).all()

    lessons = filter_lessons(all_lessons, show)

    lbd = {}
    for l in lessons:
        lbd.setdefault(l.date, []).append(l)

    # Standard calendar grid
    first_day = ms - timedelta(days=ms.weekday())
    weeks = []
    d2 = first_day
    while d2 < me or (len(weeks) < 4):
        week = []
        for _ in range(7):
            week.append({
                "date": d2,
                "in_month": d2.month == ms.month,
                "is_today": d2 == today,
                "is_past": d2 < today,
                "lessons": [l for l in lbd.get(d2, []) if l.status != "Holiday"],
                "is_holiday": any(l.status == "Holiday" for l in lbd.get(d2, [])),
            })
            d2 += timedelta(days=1)
        weeks.append(week)
        if d2 >= me and d2.weekday() == 0:
            break
        if len(weeks) >= 6:
            break

    groups = db.query(Group).all()
    prev_m = (ms - timedelta(days=1)).replace(day=1).strftime("%Y-%m")
    next_m = me.strftime("%Y-%m")

    return templates.TemplateResponse("timetable.html", {
        "request": request, "view": "monthly", "today": today,
        "month_start": ms, "month_str": ms.strftime("%Y-%m"),
        "weeks": weeks, "groups": groups,
        "prev_month": prev_m, "next_month": next_m,
        "show": show, "active_page": "timetable"
    })

@router.post("/lesson/{lid}/status")
def set_status(lid: int, status: str = Form(...),
               redirect_to: str = Form("/timetable/"),
               db: Session = Depends(get_db)):
    l = db.query(Lesson).get(lid)
    if l: l.status = status; db.commit()
    return RedirectResponse(redirect_to, status_code=303)

@router.post("/attendance/quick")
async def quick_att(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    rec = db.query(Attendance).filter_by(
        lesson_id=data["lesson_id"], student_id=data["student_id"]).first()
    if rec: rec.status = data["status"]
    else: db.add(Attendance(lesson_id=data["lesson_id"],
                            student_id=data["student_id"], status=data["status"]))
    db.commit()
    return JSONResponse({"ok": True})

@router.post("/mark-all/{lid}")
def mark_all(lid: int, db: Session = Depends(get_db)):
    l = db.query(Lesson).get(lid)
    if not l: return JSONResponse({"ok": False})
    for s in get_students(db, l):
        rec = db.query(Attendance).filter_by(lesson_id=lid, student_id=s.id).first()
        if rec: rec.status = "Present"
        else: db.add(Attendance(lesson_id=lid, student_id=s.id, status="Present"))
    db.commit()
    return JSONResponse({"ok": True})
