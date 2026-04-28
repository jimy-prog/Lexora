from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
import calendar
from database import get_db, Group, Lesson, Attendance

router = APIRouter(prefix="/calendar")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def calendar_view(request: Request, month: str = None, db: Session = Depends(get_db)):
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        month_start = date(y, m, 1)
    else:
        month_start = today.replace(day=1)

    if month_start.month == 12:
        month_end = date(month_start.year + 1, 1, 1)
        next_ms = date(month_start.year + 1, 1, 1)
    else:
        month_end = date(month_start.year, month_start.month + 1, 1)
        next_ms = month_end

    prev_ms = (month_start - timedelta(days=1)).replace(day=1)

    # All lessons this month
    lessons = db.query(Lesson).filter(
        Lesson.date >= month_start, Lesson.date < month_end
    ).order_by(Lesson.time).all()
    lessons_by_date = {}
    for l in lessons:
        lessons_by_date.setdefault(l.date, []).append(l)

    # Build calendar weeks (Mon-Sun)
    cal = calendar.monthcalendar(month_start.year, month_start.month)
    first_weekday = month_start.weekday()
    # Get all days to show including padding
    first_day = month_start - timedelta(days=first_weekday)
    calendar_weeks = []
    d = first_day
    while d < month_end or len(calendar_weeks) == 0 or d.weekday() != 0:
        week = []
        for _ in range(7):
            day_lessons = lessons_by_date.get(d, [])
            is_holiday = any(l.status == "Holiday" for l in day_lessons)
            non_holiday = [l for l in day_lessons if l.status != "Holiday"]
            week.append({
                "date": d,
                "in_month": d.month == month_start.month,
                "is_today": d == today,
                "lessons": non_holiday,
                "is_holiday": is_holiday
            })
            d += timedelta(days=1)
            if d >= month_end and d.weekday() == 0:
                break
        calendar_weeks.append(week)
        if d >= month_end and d.weekday() == 0:
            break

    # Income & lesson counts per group this month
    groups = db.query(Group).filter(Group.status != "archived").all()
    group_lesson_counts = {}
    group_income = {}
    for g in groups:
        cnt = db.query(Attendance).join(Lesson).filter(
            Lesson.group_id == g.id, Lesson.date >= month_start,
            Lesson.date < month_end, Lesson.status == "Held",
            Attendance.status == "Present"
        ).count()
        lpm = g.lessons_per_week * g.weeks_per_month
        epl = (g.price_monthly / lpm * g.teacher_pct) if lpm else 0
        group_lesson_counts[g.id] = db.query(Lesson).filter(
            Lesson.group_id == g.id, Lesson.date >= month_start,
            Lesson.date < month_end, Lesson.status == "Held"
        ).count()
        group_income[g.id] = round(cnt * epl)

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "month_start": month_start,
        "today": today,
        "today_month": today.strftime("%Y-%m"),
        "prev_month": prev_ms.strftime("%Y-%m"),
        "next_month": next_ms.strftime("%Y-%m"),
        "calendar_weeks": calendar_weeks,
        "groups": groups,
        "group_lesson_counts": group_lesson_counts,
        "group_income": group_income,
        "active_page": "calendar"
    })
