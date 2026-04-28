import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/main.py"
with open(file_path, "r") as f:
    content = f.read()

content = content.replace("from database import init_db", "from master_database import init_master_db")

content = content.replace("    init_db()", "    init_master_db()")

with open(file_path, "w") as f:
    f.write(content)

print("main.py patched")
