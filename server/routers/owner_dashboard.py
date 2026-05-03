from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from master_database import SessionMaster, User, MockExam, MockAttempt, PlatformTenant, ClassRoom
from auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/owner", tags=["owner"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
async def owner_dashboard(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    if user.role != "owner":
        return RedirectResponse("/dashboard") # Teachers go to their own dashboard

    # Global Stats
    total_teachers = db.query(User).filter(User.account_type == "teacher").count()
    total_students = db.query(User).filter(User.account_type == "student", User.role != "owner").count()
    total_exams = db.query(MockExam).count()
    total_attempts = db.query(MockAttempt).count()
    total_tenants = db.query(PlatformTenant).count()
    total_classes = db.query(ClassRoom).count()

    # Recent Activity
    recent_attempts = db.query(MockAttempt).order_by(MockAttempt.started_at.desc()).limit(5).all()
    recent_teachers = db.query(User).filter(User.account_type == "teacher").order_by(User.id.desc()).limit(5).all()

    # Attempts per day (last 7 days)
    today = datetime.utcnow().date()
    stats_7d = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = db.query(MockAttempt).filter(
            MockAttempt.started_at >= datetime.combine(day, datetime.min.time()),
            MockAttempt.started_at < datetime.combine(next_day, datetime.min.time())
        ).count()
        stats_7d.append({"date": day.strftime("%b %d"), "count": count})

    return templates.TemplateResponse("owner_dashboard.html", {
        "request": request,
        "user": user,
        "active_page": "dashboard",
        "stats": {
            "teachers": total_teachers,
            "students": total_students,
            "exams": total_exams,
            "attempts": total_attempts,
            "tenants": total_tenants,
            "classes": total_classes
        },
        "recent_attempts": recent_attempts,
        "recent_teachers": recent_teachers,
        "stats_7d": stats_7d
    })
