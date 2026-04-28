from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Group, Student, Lesson, Attendance, WeeklyPerformance
from finance_rules import get_group_epl, get_default_group_values

router = APIRouter(prefix="/groups")
templates = Jinja2Templates(directory="templates")

def nm(d):
    if d.month == 12: return date(d.year+1,1,1)
    return date(d.year, d.month+1, 1)

@router.get("/")
def groups_list(request: Request, db: Session = Depends(get_db)):
    groups = db.query(Group).filter(Group.status == "active").all()
    for g in groups:
        g.student_count = db.query(Student).filter(
            Student.group_id==g.id, Student.archived==False, Student.banned==False
        ).count()
        g.epl = get_group_epl(db, g)
    return templates.TemplateResponse("groups.html", {
        "request": request, "groups": groups, "active_page": "groups"
    })

@router.post("/add")
async def add_group(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    group_type = form.get("group_type", "group")
    defaults = get_default_group_values(db, group_type)

    g = Group(
        name=form.get("name", ""),
        group_type=group_type,
        color=form.get("color", "#4c6ef5"),
        price_monthly=float(form.get("price_monthly", defaults["price_monthly"]) or defaults["price_monthly"]),
        teacher_pct=float(form.get("teacher_pct", defaults["teacher_pct"]) or defaults["teacher_pct"]) / 100,
        lessons_per_week=int(form.get("lessons_per_week", 3) or 3),
        weeks_per_month=int(form.get("weeks_per_month", 4) or 4),
        schedule=form.get("schedule", ""),
        notes=form.get("notes", ""),
        status="active",
        mode=form.get("mode", "in-person"),
        finance_mode=form.get("finance_mode", defaults["finance_mode"]),
        epl_override=float(form.get("epl_override") or 0),
        company_name=form.get("company_name", ""),
        rate_type=form.get("rate_type", "per_lesson"),
        rate_amount=float(form.get("rate_amount") or 0),
        lesson_duration=int(form.get("lesson_duration") or 60),
        zoom_link=form.get("zoom_link", ""),
    )
    db.add(g)
    db.commit()
    return RedirectResponse("/groups/", status_code=303)

@router.get("/{gid}")
def group_detail(gid: int, request: Request, month: str = None,
                 db: Session = Depends(get_db)):
    g = db.query(Group).get(gid)
    if not g:
        return RedirectResponse("/groups/", status_code=303)
    today = date.today()
    if month:
        y, m = map(int, month.split("-"))
        month_start = date(y, m, 1)
    else:
        month_start = today.replace(day=1)
    month_end = nm(month_start)

    students_active = db.query(Student).filter(
        Student.group_id==gid, Student.archived==False, Student.banned==False
    ).all()
    students_alumni = []

    # Lessons this month
    lessons = db.query(Lesson).filter(
        Lesson.group_id==gid,
        Lesson.date>=month_start, Lesson.date<month_end
    ).order_by(Lesson.date).all()

    # Attendance matrix
    att_map = {}
    for l in lessons:
        for a in l.attendance:
            att_map[(a.student_id, l.id)] = a.status

    # Finance — only past/today held lessons
    held_past = db.query(Lesson).filter(
        Lesson.group_id==gid,
        Lesson.date>=month_start, Lesson.date<=today,
        Lesson.date<month_end, Lesson.status=="Held"
    ).count()
    countable = db.query(Attendance).join(Lesson).filter(
        Lesson.group_id==gid,
        Lesson.date>=month_start, Lesson.date<=today,
        Lesson.date<month_end, Lesson.status=="Held",
        Attendance.status.in_(["Present","Absent"])
    ).count()
    epl = get_group_epl(db, g)
    income = round(countable * epl)

    # Performance
    perf_month = month_start.strftime("%Y-%m")
    perf_data = []
    for s in students_active:
        weeks = {wp.week_num: wp for wp in db.query(WeeklyPerformance).filter_by(
            student_id=s.id, month=perf_month).all()}
        perf_data.append({"student": s, "weeks": weeks})

    # Monthly history
    history = []
    for i in range(11, -1, -1):
        m2 = month_start.month - i
        y2 = month_start.year
        while m2 <= 0: m2 += 12; y2 -= 1
        hms = date(y2,m2,1); hme = nm(hms)
        hl = db.query(Lesson).filter(
            Lesson.group_id==gid, Lesson.date>=hms,
            Lesson.date<hme, Lesson.status=="Held"
        ).count()
        hp = db.query(Attendance).join(Lesson).filter(
            Lesson.group_id==gid, Lesson.date>=hms,
            Lesson.date<hme, Lesson.status=="Held",
            Attendance.status=="Present"
        ).count()
        ha = db.query(Attendance).join(Lesson).filter(
            Lesson.group_id==gid, Lesson.date>=hms,
            Lesson.date<hme, Lesson.status=="Held",
            Attendance.status=="Absent"
        ).count()
        total_att = db.query(Attendance).join(Lesson).filter(
            Lesson.group_id==gid, Lesson.date>=hms,
            Lesson.date<hme, Lesson.status=="Held"
        ).count()
        rate = round(hp/total_att*100) if total_att else 0
        history.append({
            "month": hms.strftime("%Y-%m"), "lessons": hl,
            "present": hp, "absent": ha, "rate": rate
        })

    return templates.TemplateResponse("group_detail.html", {
        "request": request, "group": g,
        "students_active": students_active,
        "students_alumni": students_alumni,
        "lessons": lessons, "att_map": att_map,
        "month_start": month_start,
        "month_str": month_start.strftime("%Y-%m"),
        "held_count": held_past,
        "countable": countable,
        "income": income,
        "epl": epl,
        "history": history,
        "perf_data": perf_data,
        "perf_month": perf_month,
        "active_page": "groups"
    })
