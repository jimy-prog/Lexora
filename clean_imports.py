import os, glob, re

router_files = glob.glob("/Users/jamshidmahkamov/Desktop/teacher_admin/routers/*.py")

for file in router_files:
    with open(file, "r") as f:
        content = f.read()

    # Find the line like: from database import get_db, Base, Group, User
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    for line in lines:
        if line.startswith('from database import '):
            if ', User' in line:
                line = line.replace(', User', '')
                modified = True
            if ', AuthSession' in line:
                line = line.replace(', AuthSession', '')
                modified = True
                
        new_lines.append(line)

    if modified:
        with open(file, "w") as f:
            f.write('\n'.join(new_lines))
        print(f"Cleaned {file}")

