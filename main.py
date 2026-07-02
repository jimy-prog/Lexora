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
from routers import owner
from routers import classes
from routers import reviews
from routers import placement

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
    "/placement/take",
    "/auth",
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



from fastapi.responses import JSONResponse

@app.post("/login")
async def login_post(request: Request):
    content_type = request.headers.get("content-type", "")
    
    identifier = None
    password = None
    next_url = "/dashboard"
    
    if "application/json" in content_type:
        try:
            data = await request.json()
            identifier = data.get("identifier")
            password = data.get("password")
            next_url = data.get("next", "/dashboard")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            identifier = form.get("identifier")
            password = form.get("password")
            next_url = form.get("next", "/dashboard")
        except Exception:
            pass
            
    if not identifier or not password:
        if "application/json" in content_type:
            return JSONResponse(status_code=422, content={"detail": "Missing identifier or password"})
        return templates.TemplateResponse("login.html", {
            "request": request, "next": next_url,
            "error": "Username/Email and Password are required."
        })
        
    user = authenticate_user(identifier, password)
    if user:
        token = create_session(user.id)
        dest = next_url if next_url.startswith("/") else "/dashboard"
        if dest == "/":
            dest = "/dashboard"
            
        if "application/json" in content_type:
            response = JSONResponse(content={"success": True, "redirect": dest})
        else:
            response = RedirectResponse(dest, status_code=302)
            
        response.set_cookie(SESSION_KEY, token, httponly=True,
                            max_age=60*60*24*30, samesite="lax")
        return response
        
    if "application/json" in content_type:
        return JSONResponse(status_code=401, content={"detail": "Incorrect login or password. Try again."})
        
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next_url,
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
    return templates.TemplateResponse("register.html", {"request": request, "step": "1", "channel": "email"})

import random
import secrets
from datetime import datetime, timedelta
from master_database import SessionMaster, EmailOTP, PhoneOTP, PlatformTenant, User, TeacherProfile, StudentProfile
from auth import hash_pw

@app.post("/register/send-otp", response_class=HTMLResponse)
async def register_send_otp(request: Request, email: str = Form(...)):
    db = SessionMaster()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email.strip().lower()).first()
        if existing:
            return templates.TemplateResponse("register.html", {
                "request": request, "step": "1", "channel": "email", "error": "Email already in use."
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
            "request": request, "step": "2", "channel": "email", "email": email.strip().lower()
        })
    finally:
        db.close()

@app.post("/register/send-otp-phone", response_class=HTMLResponse)
async def register_send_otp_phone(request: Request, phone: str = Form(...)):
    db = SessionMaster()
    try:
        phone_num = phone.strip()
        # Check if user already exists
        existing = db.query(User).filter(User.phone == phone_num).first()
        if existing:
            return templates.TemplateResponse("register.html", {
                "request": request, "step": "1", "channel": "phone", "phone": phone_num, "error": "Phone number already in use."
            })
            
        code = str(random.randint(100000, 999999))
        print(f"=====================================")
        print(f"MOCK SMS SENT TO {phone_num}: OTP IS {code}")
        print(f"=====================================")
        
        otp_entry = PhoneOTP(
            phone=phone_num,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(otp_entry)
        db.commit()
        
        return templates.TemplateResponse("register.html", {
            "request": request, "step": "2", "channel": "phone", "phone": phone_num
        })
    finally:
        db.close()

@app.post("/register/verify")
async def register_verify(request: Request, email: str = Form(""), phone: str = Form(""),
                          channel: str = Form("email"), otp: str = Form(...), 
                          full_name: str = Form(...), password: str = Form(...), 
                          account_type: str = Form(...), study_focus: str = Form(...)):
    db = SessionMaster()
    try:
        if channel == "phone":
            phone = phone.strip()
            # Verify OTP
            otp_entry = db.query(PhoneOTP).filter(
                PhoneOTP.phone == phone, 
                PhoneOTP.code == otp.strip()
            ).order_by(PhoneOTP.id.desc()).first()
            
            if not otp_entry or otp_entry.expires_at < datetime.utcnow():
                return templates.TemplateResponse("register.html", {
                    "request": request, "step": "2", "phone": phone, "channel": "phone", "error": "Invalid or expired verification code."
                })
                
            # Check if already registered
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                return templates.TemplateResponse("register.html", {
                    "request": request, "step": "1", "channel": "phone", "error": "Account already exists."
                })
                
            email = f"{phone.replace('+', '')}@phone.lexora"
        else:
            email = email.strip().lower()
            # Verify OTP
            otp_entry = db.query(EmailOTP).filter(
                EmailOTP.email == email, 
                EmailOTP.code == otp.strip()
            ).order_by(EmailOTP.id.desc()).first()
            
            if not otp_entry or otp_entry.expires_at < datetime.utcnow():
                return templates.TemplateResponse("register.html", {
                    "request": request, "step": "2", "email": email, "channel": "email", "error": "Invalid or expired verification code."
                })
                
            # Check if already registered
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return templates.TemplateResponse("register.html", {
                    "request": request, "step": "1", "channel": "email", "error": "Account already exists."
                })
            phone = ""
            
        # 1. Fetch the default tenant
        tenant = db.query(PlatformTenant).filter(PlatformTenant.slug == "lexora_admin").first()
        if not tenant:
            tenant = PlatformTenant(
                slug="lexora_admin",
                db_filename="tenant_1.db"
            )
            db.add(tenant)
            db.flush()
        
        role = account_type.strip().lower()
        if role not in {"teacher", "student"}:
            role = "student"
            
        prefix = email.split("@")[0].replace(".", "_")
        username = f"{prefix}_{random.randint(1000, 9999)}"
        
        # 2. Create User linked to the default tenant
        new_user = User(
            tenant_id=tenant.id,
            username=username,
            email=email,
            phone=phone if phone else None,
            full_name=full_name.strip(),
            password_hash=hash_pw(password),
            role=role,
            is_active=True
        )
        db.add(new_user)
        db.flush() # get new_user.id
        
        # 3. Create Profile in Master DB
        if role == "teacher":
            profile = TeacherProfile(user_id=new_user.id, phone=phone)
            db.add(profile)
        else:
            profile = StudentProfile(user_id=new_user.id, phone=phone)
            db.add(profile)
            
            # Also add to waitlist in tenant database (tenant_1.db)
            from database import get_tenant_engine, sessionmaker as tenant_sessionmaker
            from routers.waitlist import WaitlistEntry
            try:
                engine = get_tenant_engine("tenant_1.db")
                SessionTenant = tenant_sessionmaker(bind=engine)
                tenant_db = SessionTenant()
                entry = WaitlistEntry(
                    name=full_name.strip(),
                    phone=phone,
                    status="new"
                )
                tenant_db.add(entry)
                tenant_db.commit()
                tenant_db.close()
            except Exception as e:
                print("Error writing student to tenant waitlist:", e)
                
        db.commit()
        db.refresh(new_user)
        
        # 4. Log them in automatically
        token = create_session(new_user.id)
        response = RedirectResponse("/dashboard" if role == "teacher" else "/mock", status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax")
        return response
    finally:
        db.close()

@app.get("/auth/google", response_class=HTMLResponse)
async def mock_google_oauth_page(request: Request):
    return templates.TemplateResponse("auth_google_mock.html", {"request": request})

@app.get("/auth/google/callback")
async def mock_google_oauth_callback(
    request: Request, 
    email: str, 
    name: str,
    role: str = "student",
    avatar: str = ""
):
    master_db = SessionMaster()
    try:
        email = email.strip().lower()
        user = master_db.query(User).filter(User.email == email).first()
        
        if not user:
            # Fetch the default tenant
            tenant = master_db.query(PlatformTenant).filter(PlatformTenant.slug == "lexora_admin").first()
            if not tenant:
                tenant = PlatformTenant(slug="lexora_admin", db_filename="tenant_1.db")
                master_db.add(tenant)
                master_db.flush()
                
            role = role.strip().lower()
            if role not in {"teacher", "student"}:
                role = "student"
                
            prefix = email.split("@")[0].replace(".", "_")
            username = f"{prefix}_{random.randint(1000, 9999)}"
            
            user = User(
                tenant_id=tenant.id,
                username=username,
                email=email,
                full_name=name.strip(),
                password_hash=hash_pw(secrets.token_hex(16)),
                role=role,
                avatar_url=avatar,
                is_active=True
            )
            master_db.add(user)
            master_db.flush()
            
            if role == "teacher":
                profile = TeacherProfile(user_id=user.id)
                master_db.add(profile)
            else:
                profile = StudentProfile(user_id=user.id)
                master_db.add(profile)
                
                # Also add student to the CRM waitlist in tenant_1.db
                from database import get_tenant_engine, sessionmaker as tenant_sessionmaker
                from routers.waitlist import WaitlistEntry
                try:
                    engine = get_tenant_engine("tenant_1.db")
                    SessionTenant = tenant_sessionmaker(bind=engine)
                    tenant_db = SessionTenant()
                    entry = WaitlistEntry(
                        name=name.strip(),
                        status="new"
                    )
                    tenant_db.add(entry)
                    tenant_db.commit()
                    tenant_db.close()
                except Exception as e:
                    print("Error writing Google student to tenant waitlist:", e)
                    
            master_db.commit()
            master_db.refresh(user)
            
        token = create_session(user.id)
        dest = "/dashboard" if user.role in {"owner", "teacher"} else "/mock"
        response = RedirectResponse(dest, status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax")
        return response
    finally:
        master_db.close()

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
          mock_platform.router, owner.router, classes.router, reviews.router, placement.router]:
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
