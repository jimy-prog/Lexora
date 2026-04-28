import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/routers/profile.py"
with open(file_path, "r") as f:
    content = f.read()

# Add master_database import
if "from master_database import User, SessionMaster" not in content:
    content = content.replace(
        "from datetime import datetime",
        "from datetime import datetime\nfrom master_database import User, SessionMaster"
    )

# Fix the user query
old_query = "users    = db.query(User).order_by(User.created_at.asc()).all()"
new_query = """
    users = []
    if getattr(request.state, "current_user", None):
        mdb = SessionMaster()
        try:
            users_list = mdb.query(User).filter_by(tenant_id=request.state.current_user.tenant_id).order_by(User.created_at.asc()).all()
            for u in users_list: mdb.expunge(u)
            users = users_list
        finally:
            mdb.close()
"""
content = content.replace(old_query, new_query)

with open(file_path, "w") as f:
    f.write(content)

print("profile.py patched")
