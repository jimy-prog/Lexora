from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db, Group, Student, Lesson, Attendance, Notification, Payment
from scheduler import generate_month_lessons, check_unmarked_lessons
from auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def _nm(d):
    if d.month == 12: return date(d.year+1,1,1)
    return date(d.year, d.month+1, 1)

@router.get("/dashboard")
def dashboard(request: Request, show_marked: int = 0, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
        
    today = date.today()
    ms = today.replace(day=1)
    me = _nm(ms)

    generate_month_lessons(db, today.year, today.month)
    check_unmarked_lessons(db)

    # Show active groups on dashboard (status=active only)
    active_groups = db.query(Group).filter(Group.status == "active").all()
    active_ids    = [g.id for g in active_groups]

    total_students = db.query(Student).filter(
        Student.active==True, Student.archived==False, Student.banned==False
    ).count()

    held_count = db.query(Lesson).filter(
        Lesson.date>=ms, Lesson.status=="Held"
    ).count()

    # Present + Absent both count; Excused does NOT
    countable = db.query(Attendance).join(Lesson).filter(
        Lesson.date>=ms, Lesson.status=="Held",
        Attendance.status.in_(["Present","Absent"])
    ).count()

    # Income + max — from ALL groups that had lessons this month
    income = 0
    income_max = 0
    groups_data = []
    groups_this_month = db.query(Group).join(Lesson).filter(
        Lesson.date>=ms, Lesson.date<me
    ).distinct().all()
    for g in groups_this_month:
        gc = db.query(Attendance).join(Lesson).filter(
            Lesson.date>=ms, Lesson.status=="Held",
            Attendance.status.in_(["Present","Absent"]),
            Lesson.group_id==g.id
        ).count()
        lpm = g.lessons_per_week * g.weeks_per_month
        teacher_max = g.price_monthly * g.teacher_pct
        epl = teacher_max / lpm if lpm else 0
        inc = round(gc * epl)
        income += inc
        income_max += round(teacher_max)
        groups_data.append({"group": g, "countable": gc, "income": inc})

    income_pct = round(income / income_max * 100) if income_max else 0

    # Lessons expected this month
    lessons_expected = sum(g.lessons_per_week * g.weeks_per_month for g in active_groups)
    lessons_pct = round(held_count / lessons_expected * 100) if lessons_expected else 0

    # Attendance rate
    total_rec   = db.query(Attendance).join(Lesson).filter(Lesson.date>=ms, Lesson.group_id.in_(active_ids)).count() if active_ids else 0
    present_rec = db.query(Attendance).join(Lesson).filter(Lesson.date>=ms, Attendance.status=="Present", Lesson.group_id.in_(active_ids)).count() if active_ids else 0
    att_rate = round(present_rec / total_rec * 100) if total_rec else 0

    # Attendance trend vs last month
    last_ms = (ms - timedelta(days=1)).replace(day=1)
    last_me = ms
    last_total   = db.query(Attendance).join(Lesson).filter(Lesson.date>=last_ms, Lesson.date<last_me, Lesson.group_id.in_(active_ids)).count() if active_ids else 0
    last_present = db.query(Attendance).join(Lesson).filter(Lesson.date>=last_ms, Lesson.date<last_me, Attendance.status=="Present", Lesson.group_id.in_(active_ids)).count() if active_ids else 0
    last_rate = round(last_present / last_total * 100) if last_total else 0
    att_trend = att_rate - last_rate

    # Payments
    month_str = today.strftime("%Y-%m")
    paid_ids   = {p.student_id for p in db.query(Payment).filter(Payment.month==month_str).all()}
    active_sids= [s.id for s in db.query(Student).filter(Student.active==True, Student.archived==False, Student.banned==False, Student.group_id.in_(active_ids)).all()] if active_ids else []
    paid_count   = len([s for s in active_sids if s in paid_ids])
    unpaid_count = len([s for s in active_sids if s not in paid_ids])

    # Today's lessons - ALL groups
    todays = db.query(Lesson).filter(Lesson.date==today).order_by(Lesson.time).all()
    todays_data = []
    for lesson in todays:
        if not lesson.group: continue
        students = db.query(Student).filter(
            Student.group_id==lesson.group_id
        ).filter(
            (Student.end_date==None) | (Student.end_date>=today)
        ).filter(
            (Student.start_date==None) | (Student.start_date<=today)
        ).filter(
            Student.archived==False, Student.banned==False
        ).all()
        if not students:
            students = db.query(Student).filter(
                Student.group_id==lesson.group_id,
                Student.archived==False,
                Student.banned==False
            ).all()
        att_map = {a.student_id: a for a in lesson.attendance}
        marked = (lesson.status == "Held" and len(students) > 0 and len(lesson.attendance) >= len(students))
        if show_marked != 1 and marked and lesson.status == "Held":
            continue
        todays_data.append({"lesson":lesson,"students":students,"att_map":att_map,"marked":marked})

    notifications = db.query(Notification).filter(Notification.read==False).order_by(Notification.created_at.desc()).limit(6).all()
    upcoming      = db.query(Lesson).filter(
        Lesson.date>today, Lesson.date<=today+timedelta(days=7)
    ).order_by(Lesson.date, Lesson.time).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "today": today,
        "total_students": total_students, "total_groups": len(active_groups),
        "held_count": held_count, "lessons_expected": lessons_expected, "lessons_pct": lessons_pct,
        "countable": countable, "income": round(income),
        "income_max": income_max, "income_pct": income_pct,
        "att_rate": att_rate, "att_trend": att_trend,
        "paid_count": paid_count, "unpaid_count": unpaid_count,
        "todays_data": todays_data, "notifications": notifications,
        "upcoming": upcoming, "groups_data": groups_data,
        "show_marked": show_marked,
        "active_page": "dashboard"
    })

@router.post("/mark-all-present/{lesson_id}")
def mark_all_present(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).get(lesson_id)
    if not lesson: return JSONResponse({"ok":False})
    for s in db.query(Student).filter(
        Student.group_id==lesson.group_id, Student.active==True, Student.archived==False, Student.banned==False
    ).all():
        rec = db.query(Attendance).filter_by(lesson_id=lesson_id, student_id=s.id).first()
        if rec: rec.status = "Present"
        else: db.add(Attendance(lesson_id=lesson_id, student_id=s.id, status="Present"))
    db.commit()
    return JSONResponse({"ok":True})

@router.post("/notifications/dismiss/{nid}")
def dismiss(nid: int, db: Session = Depends(get_db)):
    n = db.query(Notification).get(nid)
    if n: n.read = True; db.commit()
    return RedirectResponse("/dashboard", status_code=303)

@router.post("/notifications/dismiss-all")
def dismiss_all(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.read==False).update({"read":True})
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)
