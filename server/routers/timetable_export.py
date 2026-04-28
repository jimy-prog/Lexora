from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db, Group, Lesson, Attendance, Student, WeeklyPerformance
from routers.holidays import get_holidays_dict, seed_holidays
from finance_rules import get_group_epl

router = APIRouter(prefix="/timetable-export")
templates = Jinja2Templates(directory="templates")

def nm(d):
    if d.month == 12: return date(d.year+1,1,1)
    return date(d.year, d.month+1, 1)

def filter_groups(groups, show):
    if show == "active":   return [g for g in groups if g.status == "active"]
    if show == "archived": return [g for g in groups if g.status == "archived"]
    return groups

@router.get("/")
def export_view(request: Request,
                view: str = "monthly",
                month: str = None,
                week: str = None,
                d: str = None,
                show: str = "all",
                db: Session = Depends(get_db)):
    today = date.today()
    seed_holidays(db)
    holidays = get_holidays_dict(db)

    # Date range
    if view == "monthly":
        if month:
            y, m = map(int, month.split("-"))
            ms = date(y, m, 1)
        else:
            ms = today.replace(day=1)
        me = nm(ms)
        date_label = ms.strftime("%B %Y")
    elif view == "weekly":
        if week:
            parts = week.split("-")
            ws = date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            ws = today - timedelta(days=today.weekday())
        we = ws + timedelta(days=6)
        ms, me = ws, we + timedelta(days=1)
        date_label = f"{ws.strftime('%d %b')} – {we.strftime('%d %b %Y')}"
    else:
        vd = date.fromisoformat(d) if d else today
        ms, me = vd, vd + timedelta(days=1)
        date_label = vd.strftime("%A, %d %B %Y")

    all_lessons = db.query(Lesson).filter(
        Lesson.date >= ms, Lesson.date < me
    ).order_by(Lesson.date, Lesson.time).all()

    all_groups = db.query(Group).all()
    groups = filter_groups(all_groups, show)
    active_ids = {l.group_id for l in all_lessons}
    groups = [g for g in groups if g.id in active_ids]

    group_data = []
    total_income = 0

    for g in groups:
        g_lessons = sorted([l for l in all_lessons if l.group_id == g.id], key=lambda x: x.date)

        # Only HELD lessons count for finance (not future, not cancelled, not holiday without lesson_held)
        held = [l for l in g_lessons if l.status == "Held"]
        cancelled = [l for l in g_lessons if l.status == "Cancelled"]

        # Build lesson date columns — only lessons that actually exist for this group
        lesson_dates = []
        for l in g_lessons:
            h = holidays.get(l.date)
            is_holiday = h is not None and not (h.lesson_held)
            lesson_dates.append({
                "date": l.date,
                "lesson": l,
                "is_holiday": h is not None,
                "lesson_held": h.lesson_held if h else False,
                "holiday_name": h.name if h else "",
                "status": l.status,
            })

        # Students — include those who were active at any point in period
        students = db.query(Student).filter(Student.group_id == g.id).all()
        active_s = [s for s in students if
                    s.end_date is None or s.end_date >= ms]

        # Per-lesson rate — fixed per lesson for display
        lpm = len(held) if held else (g.lessons_per_week * g.weeks_per_month)
        epl = (g.price_monthly * g.teacher_pct / lpm) if lpm else 0

        student_att = []
        total_countable = 0
        today = date.today()

        for s in active_s:
            # Only get attendance for PAST/TODAY held lessons — not future
            atts = db.query(Attendance).join(Lesson).filter(
                Attendance.student_id == s.id,
                Lesson.group_id == g.id,
                Lesson.date >= ms, Lesson.date < me,
                Lesson.date <= today,
                Lesson.status == "Held"
            ).all()
            att_by_date = {a.lesson.date: a.status for a in atts}
            present  = sum(1 for a in atts if a.status == "Present")
            absent   = sum(1 for a in atts if a.status == "Absent")
            # Present + Absent count; Excused does NOT
            countable = present + absent
            total_countable += countable
            student_att.append({
                "name": s.name,
                "att": att_by_date,
                "start_date": s.start_date,
                "end_date": s.end_date,
            })

        # Finance: use effective per-group rule (standard/custom/override)
        epl = get_group_epl(db, g)
        income = round(total_countable * epl)
        total_income += income

        # Performance
        perf_rows = []
        if view == "monthly":
            pm = ms.strftime("%Y-%m")
            for s in active_s:
                wps = db.query(WeeklyPerformance).filter_by(
                    student_id=s.id, month=pm
                ).order_by(WeeklyPerformance.week_num).all()
                if wps:
                    scores = [v for wp in wps
                             for v in [wp.grammar, wp.activity, wp.vocabulary] if v]
                    avg = round(sum(scores)/len(scores), 1) if scores else None
                    # Per-skill averages for radar
                    g_scores = [wp.grammar for wp in wps if wp.grammar]
                    a_scores = [wp.activity for wp in wps if wp.activity]
                    v_scores = [wp.vocabulary for wp in wps if wp.vocabulary]
                    perf_rows.append({
                        "name": s.name,
                        "weeks": {wp.week_num: wp for wp in wps},
                        "avg": avg,
                        "g_avg": round(sum(g_scores)/len(g_scores),1) if g_scores else 0,
                        "a_avg": round(sum(a_scores)/len(a_scores),1) if a_scores else 0,
                        "v_avg": round(sum(v_scores)/len(v_scores),1) if v_scores else 0,
                    })

        group_data.append({
            "group": g,
            "lesson_dates": lesson_dates,
            "student_att": student_att,
            "held": len(held),
            "cancelled": len(cancelled),
            "total_countable": total_countable,
            "income": income,
            "epl": round(epl),
            "perf_rows": perf_rows,
        })

    return templates.TemplateResponse("timetable_export.html", {
        "request": request,
        "view": view, "show": show,
        "date_label": date_label,
        "group_data": group_data,
        "total_income": total_income,
        "generated": today,
        "ms": ms, "me": me,
    })
