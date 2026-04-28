import os, glob

router_files = glob.glob("/Users/jamshidmahkamov/Desktop/teacher_admin/routers/*.py")

for file in router_files:
    with open(file, "r") as f:
        content = f.read()

    modified = False
    
    if "Base.metadata.create_all(bind=engine)" in content:
        content = content.replace("Base.metadata.create_all(bind=engine)", "")
        modified = True
        
    if "from database import get_db, Base, engine" in content:
        content = content.replace("from database import get_db, Base, engine", "from database import get_db, Base")
        modified = True

    if "from database import get_db, Base, Group, engine" in content:
        content = content.replace("from database import get_db, Base, Group, engine", "from database import get_db, Base, Group")
        modified = True

    if "from database import get_db, Base, engine, Settings, Group, User" in content:
        content = content.replace("from database import get_db, Base, engine, Settings, Group, User", "from database import get_db, Base, Settings, Group")
        modified = True

    if "from database import get_db, Base, Group, Student, Lesson, engine" in content:
        content = content.replace("from database import get_db, Base, Group, Student, Lesson, engine", "from database import get_db, Base, Group, Student, Lesson")
        modified = True

    if "from database import get_db, Base, Group, Student, engine, Settings" in content:
        content = content.replace("from database import get_db, Base, Group, Student, engine, Settings", "from database import get_db, Base, Group, Student, Settings")
        modified = True
        
    if "from database import get_db, Settings, Group, User" in content:
        content = content.replace("from database import get_db, Settings, Group, User", "from database import get_db, Settings, Group")
        modified = True

    if modified:
        with open(file, "w") as f:
            f.write(content)

print("Routers cleaned.")
