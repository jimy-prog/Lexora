from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db, Group, Student, Lesson, Attendance, Notification, Payment, WeeklyPerformance
from scheduler import generate_month_lessons, check_unmarked_lessons, fix_archived_future_lessons
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
    month_str = today.strftime("%Y-%m")
    last_ms = (ms - timedelta(days=1)).replace(day=1)
    last_me = ms

    if user.role == "student":
        student = db.query(Student).filter(
            (Student.email == user.email) | (Student.phone == user.phone) | (Student.name == user.full_name)
        ).first()
        
        group = None
        leaderboard = []
        perf_list = []
        att_rate = 0
        att_trend = 0
        held_count = 0
        lessons_expected = 0
        lessons_pct = 0
        
        if student and student.group_id:
            group = db.query(Group).filter(Group.id == student.group_id, Group.status == "active").first()
            if group:
                # Lessons
                held_count = db.query(Lesson).filter(Lesson.group_id == group.id, Lesson.date >= ms, Lesson.status == "Held").count()
                lessons_expected = group.lessons_per_week * group.weeks_per_month
                lessons_pct = round(held_count / lessons_expected * 100) if lessons_expected else 0

                # Attendance
                total_rec = db.query(Attendance).join(Lesson).filter(Lesson.date >= ms, Attendance.student_id == student.id, Lesson.group_id == group.id).count()
                present_rec = db.query(Attendance).join(Lesson).filter(Lesson.date >= ms, Attendance.student_id == student.id, Attendance.status == "Present", Lesson.group_id == group.id).count()
                att_rate = round(present_rec / total_rec * 100) if total_rec else 0

                # Trend
                last_total = db.query(Attendance).join(Lesson).filter(Lesson.date >= last_ms, Lesson.date < last_me, Attendance.student_id == student.id, Lesson.group_id == group.id).count()
                last_present = db.query(Attendance).join(Lesson).filter(Lesson.date >= last_ms, Lesson.date < last_me, Attendance.status == "Present", Attendance.student_id == student.id, Lesson.group_id == group.id).count()
                last_rate = round(last_present / last_total * 100) if last_total else 0
                att_trend = att_rate - last_rate

                # Weekly Performance
                perf_list = db.query(WeeklyPerformance).filter(WeeklyPerformance.student_id == student.id, WeeklyPerformance.month == month_str).order_by(WeeklyPerformance.week_num).all()

                # Leaderboard
                group_students = db.query(Student).filter(Student.group_id == group.id, Student.active == True, Student.archived == False, Student.banned == False).all()
                for s in group_students:
                    s_total = db.query(Attendance).join(Lesson).filter(Lesson.date >= ms, Attendance.student_id == s.id, Lesson.group_id == group.id).count()
                    s_present = db.query(Attendance).join(Lesson).filter(Lesson.date >= ms, Attendance.student_id == s.id, Attendance.status == "Present", Lesson.group_id == group.id).count()
                    s_att_rate = round(s_present / s_total * 100) if s_total else 0
                    
                    s_perf = db.query(WeeklyPerformance).filter(WeeklyPerformance.student_id == s.id, WeeklyPerformance.month == month_str).all()
                    scores = []
                    for wp in s_perf:
                        for v in [wp.grammar, wp.activity, wp.vocabulary]:
                            if v is not None:
                                scores.append(v)
                    s_perf_avg = round(sum(scores) / len(scores), 1) if scores else 0.0
                    
                    att_score = (s_att_rate / 10)
                    perf_score = (s_perf_avg / 3) * 10
                    overall = round((att_score + perf_score) / 2, 1) if (s_total or scores) else 0.0
                    
                    parts = s.name.strip().split()
                    display_name = s.name
                    if len(parts) > 1:
                        display_name = f"{parts[0]} {parts[1][0]}."
                    
                    leaderboard.append({
                        "name": display_name,
                        "is_self": s.id == student.id,
                        "att_rate": s_att_rate,
                        "perf_avg": s_perf_avg,
                        "overall": overall
                    })
                leaderboard.sort(key=lambda x: x["overall"], reverse=True)

        todays_lessons = db.query(Lesson).filter(Lesson.date == today, Lesson.group_id == (group.id if group else -1)).order_by(Lesson.time).all()
        upcoming_lessons = db.query(Lesson).filter(Lesson.date > today, Lesson.date <= today + timedelta(days=7), Lesson.group_id == (group.id if group else -1)).order_by(Lesson.date, Lesson.time).all()

        return templates.TemplateResponse("dashboard_student.html", {
            "request": request, "user": user, "student": student, "group": group,
            "att_rate": att_rate, "att_trend": att_trend,
            "held_count": held_count, "lessons_expected": lessons_expected, "lessons_pct": lessons_pct,
            "perf_list": perf_list, "leaderboard": leaderboard,
            "todays_lessons": todays_lessons, "upcoming_lessons": upcoming_lessons,
            "active_page": "dashboard"
        })

    generate_month_lessons(db, today.year, today.month)
    fix_archived_future_lessons(db)
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

    # Today's lessons - ACTIVE groups only
    todays = db.query(Lesson).join(Group).filter(
        Lesson.date==today,
        Group.status == "active"
    ).order_by(Lesson.time).all()
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
    upcoming      = db.query(Lesson).join(Group).filter(
        Lesson.date>today, Lesson.date<=today+timedelta(days=7),
        Group.status == "active"
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
