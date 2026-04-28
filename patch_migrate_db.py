import os
import re

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/database.py"
with open(file_path, "r") as f:
    content = f.read()

# Replace the complicated migrate_db function with a simple pass
pattern = re.compile(r"def migrate_db\(db=None\):.*?def init_tenant_db\(engine\):", re.DOTALL)

new_code = "def migrate_db(db=None):\n    pass\n\ndef init_tenant_db(engine):"

content = pattern.sub(new_code, content)

with open(file_path, "w") as f:
    f.write(content)

print(f"Patched migrate_db in {file_path}")
