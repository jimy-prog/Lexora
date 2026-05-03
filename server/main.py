from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn, os, random
from datetime import datetime, timedelta
from master_database import SessionMaster, EmailOTP, PlatformTenant, User, PasswordResetToken
from auth import hash_pw
import secrets
from email_service import send_otp_email, send_password_reset_email

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
from routers import owner_dashboard
from routers import owner_users

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
    "/uploads",
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


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/forgot-password")
async def forgot_password_post(request: Request, email: str = Form(...)):
    db = SessionMaster()
    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if user:
            # Generate token
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(minutes=30)
            
            # Save token
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires
            )
            db.add(reset_token)
            db.commit()
            
            # Send email
            reset_link = f"{request.base_url}reset-password?token={token}"
            send_password_reset_email(user.email, reset_link)
            
        return templates.TemplateResponse("forgot_password.html", {
            "request": request, 
            "success": "If an account with that email exists, a password reset link has been sent."
        })
    finally:
        db.close()

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    db = SessionMaster()
    try:
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            return templates.TemplateResponse("forgot_password.html", {
                "request": request, 
                "error": "Invalid or expired reset token."
            })
            
        return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})
    finally:
        db.close()

@app.post("/reset-password")
async def reset_password_post(request: Request, token: str = Form(...), password: str = Form(...)):
    db = SessionMaster()
    try:
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            return templates.TemplateResponse("forgot_password.html", {
                "request": request, 
                "error": "Invalid or expired reset token."
            })
            
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if user:
            user.password_hash = hash_pw(password)
            reset_token.used = True
            db.commit()
            return RedirectResponse("/login?reset=success", status_code=302)
        
        return RedirectResponse("/login", status_code=302)
    finally:
        db.close()

@app.post("/register/direct")
async def register_direct(request: Request, email: str = Form(...), 
                            full_name: str = Form(...), password: str = Form(...), 
                            account_type: str = Form(...), study_focus: str = Form(...)):
    db = SessionMaster()
    try:
        email = email.strip().lower()
        # Check if already registered
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return templates.TemplateResponse("register.html", {
                "request": request, "error": "Account with this email already exists."
            })
            
        # Create User
        new_user = User(
            tenant_id=1,
            username=email.split("@")[0].replace(".", "_") + "_" + str(random.randint(1000,9999)),
            email=email,
            full_name=full_name.strip(),
            password_hash=hash_pw(password),
            role="admin",
            account_type=account_type,
            study_focus=study_focus,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log them in automatically
        token = create_session(new_user.id)
        dest = "/dashboard" if account_type == "teacher" else "/mock"
        response = RedirectResponse(dest, status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax")
        return response
    finally:
        db.close()

from master_database import SupportTicket

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request, success: bool = False):
    user = get_current_user(request)
    return templates.TemplateResponse("support.html", {
        "request": request,
        "user": user,
        "active_page": "support",
        "success": success
    })

@app.post("/support")
async def support_post(request: Request, category: str = Form(...), 
                       subject: str = Form(...), message: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    db = SessionMaster()
    try:
        # 1. Save to database
        ticket = SupportTicket(
            user_id=user.id,
            category=category,
            subject=subject,
            message=message
        )
        db.add(ticket)
        db.commit()
        
        # 2. Notify Owner via Email
        from config import OWNER_EMAIL
        notification_body = f"""
        <html>
        <body>
            <h2>New Support Ticket: {subject}</h2>
            <p><strong>From:</strong> {user.full_name} ({user.email})</p>
            <p><strong>Category:</strong> {category}</p>
            <hr>
            <p style="white-space: pre-wrap;">{message}</p>
        </body>
        </html>
        """
        
        from email_service import send_custom_email
        send_custom_email(OWNER_EMAIL, f"[Lexora Support] {category.upper()}: {subject}", notification_body)
        
        return RedirectResponse("/support?success=true", status_code=303)
    finally:
        db.close()

@app.get("/support/inquiries", response_class=HTMLResponse)
async def support_inquiries(request: Request):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    db = SessionMaster()
    try:
        from master_database import SupportTicket
        tickets = db.query(SupportTicket).order_by(SupportTicket.created_at.desc()).all()
        return templates.TemplateResponse("support_inquiries.html", {
            "request": request,
            "user": user,
            "tickets": tickets,
            "active_page": "support_inquiries"
        })
    finally:
        db.close()

@app.get("/dashboard")
async def dashboard_redirect(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if user.role == "owner":
        return RedirectResponse("/owner/dashboard", status_code=302)
    # Default teacher dashboard
    return RedirectResponse("/teacher/dashboard", status_code=302)

for r in [dashboard.router, students.router, groups.router, lessons.router,
          attendance.router, finance.router, reports.router, payments.router,
          backup.router, settings_router.router, calendar_router.router,
          timetable_router.router, homework_router.router, performance.router,
          reportcard.router, courses.router, waitlist.router,
          profile_router.router, monthly_report.router,
          timetable_export.router, holidays_router.router,
          online_router.router, archive_router.router,
          mock_platform.router,
          owner_dashboard.router,
          owner_users.router]:
    app.include_router(r)
from firebase_config import verify_id_token

@app.post("/api/auth/firebase-login")
async def firebase_login(request: Request, id_token: str = Form(...)):
    decoded = verify_id_token(id_token)
    if not decoded:
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Invalid Firebase token."
        })
    
    email = decoded.get("email", "").lower()
    full_name = decoded.get("name", "")
    
    db = SessionMaster()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # First time Google login = Auto-registration
            # Use default Lexora tenant
            new_user = User(
                tenant_id=1,
                username=email.split("@")[0] + "_" + str(random.randint(1000, 9999)),
                email=email,
                full_name=full_name,
                password_hash="FIREBASE_AUTH", # No password stored for Google users
                role="admin",
                account_type="student", # Default to student, they can change later
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
            
        # Create session
        token = create_session(user.id)
        # Redirect based on account type
        dest = "/dashboard" if user.account_type == "teacher" else "/mock"
        response = RedirectResponse(dest, status_code=302)
        response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax")
        return response
    finally:
        db.close()

app.include_router(api_auth.router, prefix="/api")

@app.on_event("startup")
def startup():
    from master_database import init_master_db
    init_master_db()
    ensure_owner_account()
    run_backup()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
