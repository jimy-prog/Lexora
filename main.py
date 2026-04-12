from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn, os

from config import APP_NAME, SECRET_KEY, STATIC_DIR, UPLOADS_DIR
from database import init_db
from autobackup import run_backup
from auth import check_password, create_session, is_authenticated, logout, SESSION_KEY, set_password
from scheduler import fix_archived_future_lessons

from routers import (dashboard, students, groups, lessons, attendance,
                     finance, reports, payments, backup, settings_router)
from routers import (calendar_router, timetable_router, homework_router,
                     performance, reportcard)
from routers import courses, waitlist, profile as profile_router
from routers import monthly_report, timetable_export
from routers import holidays as holidays_router
from routers import online as online_router
from routers import archive as archive_router

app = FastAPI(title=APP_NAME)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

templates = Jinja2Templates(directory="templates")

PUBLIC_PATHS = {"/login", "/static", "/favicon.ico", "/waitlist/from-google-form"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)
    if not is_authenticated(request):
        return RedirectResponse(f"/login?next={path}", status_code=302)
    return await call_next(request)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next, "error": None
    })

@app.post("/login")
async def login_post(request: Request,
                     password: str = Form(...),
                     next: str = Form("/")):
    if check_password(password):
        token = create_session()
        response = RedirectResponse(next if next.startswith("/") else "/",
                                    status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True,
                            max_age=60*60*24*30, samesite="lax")
        return response
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next,
        "error": "Incorrect password. Try again."
    })

@app.get("/logout")
async def logout_route(request: Request):
    logout(request)
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(SESSION_KEY)
    return response

@app.post("/settings/change-password")
async def change_password(request: Request,
                          current_pw: str = Form(...),
                          new_pw: str = Form(...)):
    if not check_password(current_pw):
        return RedirectResponse("/profile/?tab=security&error=wrong_password", status_code=302)
    set_password(new_pw)
    return RedirectResponse("/profile/?tab=security&success=password_changed", status_code=302)

for r in [dashboard.router, students.router, groups.router, lessons.router,
          attendance.router, finance.router, reports.router, payments.router,
          backup.router, settings_router.router, calendar_router.router,
          timetable_router.router, homework_router.router, performance.router,
          reportcard.router, courses.router, waitlist.router,
          profile_router.router, monthly_report.router,
          timetable_export.router, holidays_router.router,
          online_router.router, archive_router.router]:
    app.include_router(r)

@app.on_event("startup")
def startup():
    from sqlalchemy.orm import Session
    from database import SessionLocal
    init_db()
    run_backup()
    # Fix: remove future lessons from archived groups
    db = SessionLocal()
    removed = fix_archived_future_lessons(db)
    if removed:
        print(f"[Startup] Removed {removed} future lessons from archived groups")
    db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
