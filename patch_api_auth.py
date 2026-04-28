import os
import re

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/routers/api_auth.py"
with open(file_path, "r") as f:
    content = f.read()

new_imports = """
import string, random
from master_database import SessionMaster, PlatformTenant, User
from auth import hash_pw
"""

content = content.replace(
    "from auth import authenticate_user",
    new_imports + "\nfrom auth import authenticate_user"
)

register_endpoint = """
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
"""

content += register_endpoint

with open(file_path, "w") as f:
    f.write(content)

print("api_auth.py patched")
