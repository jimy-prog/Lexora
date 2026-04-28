from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Group, Student, Lesson, Attendance, WeeklyPerformance
from finance_rules import get_group_epl

router = APIRouter(prefix="/monthly-report")
templates = Jinja2Templates(directory="templates")

def nm(d):
    if d.month == 12: return date(d.year+1,1,1)
    return date(d.year, d.month+1, 1)

@router.get("/")
def monthly_report(request: Request, month: str = None, db: Session = Depends(get_db)):
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        ms = date(y, m, 1)
    else:
        ms = today.replace(day=1)
    me = nm(ms)

    # All groups that had ANY lesson this month
    groups_with_lessons = db.query(Group).join(Lesson).filter(
        Lesson.date >= ms, Lesson.date < me
    ).distinct().all()

    report_data = []
    total_income = 0

    for g in groups_with_lessons:
        lessons = db.query(Lesson).filter(
            Lesson.group_id == g.id,
            Lesson.date >= ms, Lesson.date < me
        ).order_by(Lesson.date).all()

        held = [l for l in lessons if l.status == "Held"]
        cancelled = [l for l in lessons if l.status == "Cancelled"]
        holiday = [l for l in lessons if l.status == "Holiday"]

        # Students who attended this group this month
        students = db.query(Student).filter(Student.group_id == g.id).all()
        # Include anyone active at any point during this month
        active_students = [s for s in students if
                          s.end_date is None or s.end_date >= ms]

        # Attendance per student
        student_data = []
        total_countable = 0
        for s in active_students:
            records = db.query(Attendance).join(Lesson).filter(
                Attendance.student_id == s.id,
                Lesson.group_id == g.id,
                Lesson.date >= ms, Lesson.date < me,
                Lesson.status == "Held"
            ).all()
            if not records:
                continue
            present = sum(1 for r in records if r.status == "Present")
            absent  = sum(1 for r in records if r.status == "Absent")
            excused = sum(1 for r in records if r.status == "Excused")
            # Present + Absent count for salary; Excused does NOT
            countable_att = present + absent
            rate    = round(countable_att / len(records) * 100) if records else 0
            total_countable += countable_att
            student_data.append({
                "student": s, "present": present,
                "absent": absent, "excused": excused,
                "total": len(records), "rate": rate
            })

        # Finance
        epl = get_group_epl(db, g)
        income = round(total_countable * epl)
        total_income += income

        if (getattr(g, "finance_mode", "standard") or "standard") == "standard" and (getattr(g, "epl_override", 0) or 0) <= 0:
            finance_formula = f"{total_countable} countable × {round(epl)} UZS (standard rate)"
        else:
            held_for_formula = len(held) if len(held) > 0 else (g.lessons_per_week * g.weeks_per_month or 12)
            finance_formula = (
                f"{round(g.price_monthly):,} UZS × {int(g.teacher_pct * 100)}% ÷ {held_for_formula} lessons"
                f" = {round(epl):,} UZS/lesson × {total_countable} countable"
            )

        # Performance
        perf_month = ms.strftime("%Y-%m")
        perf_data = []
        for s in active_students:
            wps = db.query(WeeklyPerformance).filter_by(
                student_id=s.id, month=perf_month
            ).order_by(WeeklyPerformance.week_num).all()
            if wps:
                scores = [v for wp in wps
                         for v in [wp.grammar, wp.activity, wp.vocabulary] if v]
                avg = round(sum(scores)/len(scores), 1) if scores else None
                perf_data.append({"student": s, "weeks": wps, "avg": avg})

        report_data.append({
            "group": g,
            "lessons": lessons,
            "held": len(held),
            "cancelled": len(cancelled),
            "holiday": len(holiday),
            "student_data": student_data,
            "total_countable": total_countable,
            "income": income,
            "earn_per_lesson": round(epl),
            "finance_formula": finance_formula,
            "perf_data": perf_data,
        })

    return templates.TemplateResponse("monthly_report.html", {
        "request": request,
        "month_start": ms,
        "report_data": report_data,
        "total_income": total_income,
        "generated": today,
        "active_page": None
    })
