import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/auth.py"
with open(file_path, "r") as f:
    content = f.read()

content = content.replace(
    "from database import SessionLocal, User, AuthSession",
    "from master_database import SessionMaster, User, AuthSession, PlatformTenant"
)

content = content.replace(
    "db = SessionLocal()",
    "db = SessionMaster()"
)

# Fix ensure_owner_account
owner_block = """def ensure_owner_account():
    db = SessionMaster()
    try:
        if db.query(User).count() > 0:
            return
        initial_hash = get_stored_hash()
        owner = User(
            username=OWNER_USERNAME.strip().lower(),
            email=OWNER_EMAIL.strip().lower(),
            full_name=OWNER_FULL_NAME.strip(),
            role="owner",
            password_hash=initial_hash,
            is_active=True,
        )
        db.add(owner)
        db.commit()
    finally:
        db.close()"""

new_owner_block = """def ensure_owner_account():
    db = SessionMaster()
    try:
        if db.query(User).count() > 0:
            return
            
        import master_database
        master_database.init_master_db()
            
        tenant = PlatformTenant(slug="lexora_admin", db_filename="tenant_1.db")
        db.add(tenant)
        db.flush()
        
        initial_hash = get_stored_hash()
        owner = User(
            tenant_id=tenant.id,
            username=OWNER_USERNAME.strip().lower(),
            email=OWNER_EMAIL.strip().lower(),
            full_name=OWNER_FULL_NAME.strip(),
            role="owner",
            password_hash=initial_hash,
            is_active=True,
        )
        db.add(owner)
        db.commit()
    finally:
        db.close()"""

content = content.replace(owner_block, new_owner_block)

with open(file_path, "w") as f:
    f.write(content)

print("auth.py patched")
