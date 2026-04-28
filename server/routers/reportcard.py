from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Student, Group, Attendance, Lesson, WeeklyPerformance, Payment

router = APIRouter(prefix="/reportcard")
templates = Jinja2Templates(directory="templates")

@router.get("/{sid}")
def report_card(sid: int, request: Request, month: str = None, db: Session = Depends(get_db)):
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        ms = date(y, m, 1)
    else:
        ms = today.replace(day=1)
    me = date(ms.year, ms.month+1, 1) if ms.month < 12 else date(ms.year+1, 1, 1)

    s = db.query(Student).get(sid)
    if not s:
        return HTMLResponse("Student not found", 404)

    # Attendance this month
    records = db.query(Attendance).join(Lesson).filter(
        Attendance.student_id == sid,
        Lesson.date >= ms, Lesson.date < me
    ).order_by(Lesson.date).all()

    present  = sum(1 for r in records if r.status == "Present")
    absent   = sum(1 for r in records if r.status == "Absent")
    excused  = sum(1 for r in records if r.status == "Excused")
    total    = len(records)
    att_rate = round(present / total * 100) if total else 0

    # All-time attendance
    all_records = db.query(Attendance).filter(Attendance.student_id == sid).all()
    all_present = sum(1 for r in all_records if r.status == "Present")
    all_total   = len(all_records)
    all_rate    = round(all_present / all_total * 100) if all_total else 0

    # Performance this month
    perf = db.query(WeeklyPerformance).filter(
        WeeklyPerformance.student_id == sid,
        WeeklyPerformance.month == ms.strftime("%Y-%m")
    ).order_by(WeeklyPerformance.week_num).all()

    # Payment status
    payment = db.query(Payment).filter(
        Payment.student_id == sid,
        Payment.month == ms.strftime("%Y-%m")
    ).first()

    # Monthly history (last 6 months)
    monthly = []
    for i in range(5, -1, -1):
        m2 = ms.month - i
        y2 = ms.year
        while m2 <= 0: m2 += 12; y2 -= 1
        hms = date(y2, m2, 1)
        hme = date(y2, m2+1, 1) if m2 < 12 else date(y2+1, 1, 1)
        recs = db.query(Attendance).join(Lesson).filter(
            Attendance.student_id == sid,
            Lesson.date >= hms, Lesson.date < hme
        ).all()
        if recs:
            p = sum(1 for r in recs if r.status == "Present")
            monthly.append({
                "month": hms.strftime("%b %Y"),
                "present": p, "total": len(recs),
                "rate": round(p/len(recs)*100) if recs else 0
            })

    SCORE_EMOJI = {1: "🔴", 2: "🟡", 3: "🟢", None: "—"}
    SCORE_LABEL = {1: "Needs Work", 2: "Needs Revision", 3: "Good", None: "—"}

    return templates.TemplateResponse("reportcard.html", {
        "request": request,
        "student": s, "month_start": ms,
        "records": records,
        "present": present, "absent": absent, "excused": excused,
        "att_rate": att_rate, "all_rate": all_rate,
        "perf": perf, "payment": payment,
        "monthly": monthly,
        "score_emoji": SCORE_EMOJI, "score_label": SCORE_LABEL,
        "generated": today
    })
