from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel

import string, random
from master_database import SessionMaster, PlatformTenant, User
from auth import hash_pw

from auth import authenticate_user, create_session, SESSION_KEY, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    identifier: str
    password: str

@router.post("/login")
async def login_api(req: LoginRequest, response: Response):
    user = authenticate_user(req.identifier, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user.id)
    # Set the cookie for the frontend
    response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax", path="/")
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/logout")
async def logout_api(response: Response):
    response.delete_cookie(SESSION_KEY, path="/")
    return {"success": True}

@router.get("/me")
async def get_me(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

class RegisterRequest(BaseModel):
    email: str
    password: str
    school_name: str

@router.post("/register")
async def register_api(req: RegisterRequest, response: Response):
    db = SessionMaster()
    try:
        email = req.email.strip().lower()
        if db.query(User).filter_by(email=email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Generate tenant slug and filename
        base_slug = "".join(x for x in req.school_name.lower() if x.isalnum())[:10]
        rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        slug = f"{base_slug}_{rand_suffix}"
        db_filename = f"tenant_{slug}.db"
        
        tenant = PlatformTenant(slug=slug, db_filename=db_filename)
        db.add(tenant)
        db.flush()
        
        user = User(
            tenant_id=tenant.id,
            username=email, # Using email as username
            email=email,
            full_name=req.school_name,
            role="owner",
            password_hash=hash_pw(req.password),
            is_active=True
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
        
    # Auto login after register
    user = authenticate_user(req.email, req.password)
    token = create_session(user.id)
    response.set_cookie(SESSION_KEY, token, httponly=True, max_age=60*60*24*30, samesite="lax", path="/")
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }
