from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import date
from database import get_db, Group, Student, WeeklyPerformance

router = APIRouter(prefix="/performance")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def performance_view(request: Request, month: str = None, group_id: int = None, db: Session = Depends(get_db)):
    today = date.today()
    month_str = month or today.strftime("%Y-%m")
    groups = db.query(Group).filter(Group.status.in_(["active","paused"])).all()
    sel_group = db.query(Group).get(group_id) if group_id else (groups[0] if groups else None)

    data = []
    if sel_group:
        students = db.query(Student).filter(
            Student.group_id == sel_group.id, Student.archived == False
        ).all()
        for s in students:
            weeks = {wp.week_num: wp for wp in
                     db.query(WeeklyPerformance).filter_by(
                         student_id=s.id, month=month_str).all()}
            # All-time trend for line chart
            all_perf = db.query(WeeklyPerformance).filter_by(
                student_id=s.id).order_by(
                WeeklyPerformance.month, WeeklyPerformance.week_num).all()
            trend = []
            for wp in all_perf:
                scores = [v for v in [wp.grammar, wp.activity, wp.vocabulary] if v]
                if scores:
                    trend.append({"month": wp.month, "week": wp.week_num,
                                  "avg": round(sum(scores)/len(scores), 1)})
            data.append({"student": s, "weeks": weeks, "trend": trend})

    return templates.TemplateResponse("performance.html", {
        "request": request, "groups": groups, "sel_group": sel_group,
        "month_str": month_str, "data": data,
        "weeks": [1,2,3,4], "active_page": "performance"
    })

@router.post("/quick-save")
async def quick_save(request: Request, db: Session = Depends(get_db)):
    d = await request.json()
    wp = db.query(WeeklyPerformance).filter_by(
        student_id=d["student_id"], month=d["month"], week_num=d["week"]).first()
    if not wp:
        wp = WeeklyPerformance(student_id=d["student_id"],
                               month=d["month"], week_num=d["week"])
        db.add(wp)
    setattr(wp, d["field"], d.get("value"))
    db.commit()
    return JSONResponse({"ok": True})
