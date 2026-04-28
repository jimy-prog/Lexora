import os, shutil

# Create directory
os.makedirs("/Users/jamshidmahkamov/Desktop/teacher_admin/database_tenants", exist_ok=True)

try:
    import sys
    sys.path.append("/Users/jamshidmahkamov/Desktop/teacher_admin")
    
    from master_database import init_master_db
    from auth import ensure_owner_account
    
    # 1. Initialize Master DB schema
    init_master_db()
    print("Master DB initialized")
    
    # 2. Ensure owner account exists - this creates tenant_1.db reference!
    ensure_owner_account()
    print("Owner account initialized in Master DB")
    
    # 3. Copy the old database.db to tenant_1.db to preserve his data!
    db_source = "/Users/jamshidmahkamov/Desktop/teacher_admin/database.db"
    db_dest = "/Users/jamshidmahkamov/Desktop/teacher_admin/database_tenants/tenant_1.db"
    if os.path.exists(db_source) and not os.path.exists(db_dest):
        shutil.copy(db_source, db_dest)
        print("Data migrated! Copied database.db -> tenant_1.db")
    else:
        print("db_source does not exist or db_dest already exists. Skipping copy.")
        
except Exception as e:
    print("Error during migration:", str(e))
