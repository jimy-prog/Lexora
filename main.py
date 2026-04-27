from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn, os

from config import APP_NAME, SECRET_KEY, STATIC_DIR, UPLOADS_DIR
from master_database import init_master_db
from autobackup import run_backup
from auth import (
    authenticate_user,
    create_session,
    ensure_owner_account,
    get_current_user,
    is_authenticated,
    logout,
    SESSION_KEY,
)
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
from routers import api_auth
from routers import mock_platform

app = FastAPI(title=APP_NAME)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
LANDING_IMAGES_DIR = STATIC_DIR / "landing_images"
os.makedirs(LANDING_IMAGES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/images", StaticFiles(directory=str(LANDING_IMAGES_DIR)), name="landing_images")

templates = Jinja2Templates(directory="templates")

PUBLIC_PREFIXES = (
    "/api/auth",
    "/login",
    "/static",
    "/favicon.ico",
    "/waitlist/from-google-form",
    "/register",
    "/images",
    "/healthz",
)


def _is_public_path(path: str) -> bool:
    if path == "/":
        return True
    return any(path.startswith(p) for p in PUBLIC_PREFIXES)


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if _is_public_path(path):
        return await call_next(request)
    current_user = get_current_user(request)
    request.state.current_user = current_user
    if not current_user:
        return RedirectResponse(f"/login?next={path}", status_code=302)
    return await call_next(request)


@app.get("/")
async def root(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/static/landing/index.html", status_code=302)


@app.get("/register")
async def register_redirect():
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/dashboard"):
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next, "error": None
    })

@app.post("/login")
async def login_post(request: Request,
                     identifier: str = Form(...),
                     password: str = Form(...),
                     next: str = Form("/dashboard")):
    user = authenticate_user(identifier, password)
    if user:
        token = create_session(user.id)
        dest = next if next.startswith("/") else "/dashboard"
        if dest == "/":
            dest = "/dashboard"
        response = RedirectResponse(dest, status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True,
                            max_age=60*60*24*30, samesite="lax")
        return response
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next,
        "error": "Incorrect login or password. Try again."
    })

@app.get("/logout")
async def logout_route(request: Request):
    logout(request)
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(SESSION_KEY)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "step": "1"})

import random
from master_database import SessionMaster, EmailOTP, PlatformTenant, User
from auth import hash_pw

@app.post("/register/send-otp", response_class=HTMLResponse)
async def register_send_otp(request: Request, email: str = Form(...)):
    db = SessionMaster()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email.strip().lower()).first()
        if existing:
            return templates.TemplateResponse("register.html", {
                "request": request, "step": "1", "error": "Email already in use."
            })
            
        code = str(random.randint(100000, 999999))
        print(f"=====================================")
        print(f"MOCK EMAIL SENT TO {email}: OTP IS {code}")
        print(f"=====================================")
        
        otp_entry = EmailOTP(
            email=email.strip().lower(),
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(otp_entry)
        db.commit()
        
        return templates.TemplateResponse("register.html", {
            "request": request, "step": "2", "email": email.strip().lower()
        })
    finally:
        db.close()

@app.post("/register/verify")
async def register_verify(request: Request, email: str = Form(...), otp: str = Form(...), 
                          full_name: str = Form(...), password: str = Form(...), 
                          account_type: str = Form(...), study_focus: str = Form(...)):
    db = SessionMaster()
    try:
        email = email.strip().lower()
        # Verify OTP
        otp_entry = db.query(EmailOTP).filter(
            EmailOTP.email == email, 
            EmailOTP.code == otp.strip()
        ).order_by(EmailOTP.id.desc()).first()
        
        if not otp_entry or otp_entry.expires_at < datetime.utcnow():
            return templates.TemplateResponse("register.html", {
                "request": request, "step": "2", "email": email, "error": "Invalid or expired verification code."
            })
            
        # Check if already registered
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return templates.TemplateResponse("register.html", {
                "request": request, "step": "1", "error": "Account already exists."
            })
            
        # 1. Create a unique isolated database tenant
        # Give it a safe slug based on email prefix + random
        slug_base = email.split("@")[0].replace(".", "_")
        tenant_slug = f"{slug_base}_{random.randint(1000,9999)}"
        tenant = PlatformTenant(
            slug=tenant_slug,
            db_filename=f"tenant_{tenant_slug}.db"
        )
        db.add(tenant)
        db.flush() # get tenant.id
        
        # 2. Create User linked to the tenant
        new_user = User(
            tenant_id=tenant.id,
            username=tenant_slug, # Username is slug by default
            email=email,
            full_name=full_name.strip(),
            password_hash=hash_pw(password),
            role="owner", # They are the owner of their own tenant
            account_type=account_type,
            study_focus=study_focus,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 3. Log them in automatically
        token = create_session(new_user.id)
        response = RedirectResponse("/dashboard" if account_type == "teacher" else "/mock", status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax")
        return response
    finally:
        db.close()

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("support.html", {
        "request": request,
        "user": user,
        "active_page": "support"
    })

for r in [dashboard.router, students.router, groups.router, lessons.router,
          attendance.router, finance.router, reports.router, payments.router,
          backup.router, settings_router.router, calendar_router.router,
          timetable_router.router, homework_router.router, performance.router,
          reportcard.router, courses.router, waitlist.router,
          profile_router.router, monthly_report.router,
          timetable_export.router, holidays_router.router,
          online_router.router, archive_router.router,
          mock_platform.router]:
    app.include_router(r)
app.include_router(api_auth.router, prefix="/api")

@app.on_event("startup")
def startup():
    from master_database import init_master_db
    init_master_db()
    ensure_owner_account()
    run_backup()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
