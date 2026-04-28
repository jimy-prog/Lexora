from fastapi import APIRouter
from fastapi.responses import FileResponse
import shutil, os
from datetime import date
from config import DATABASE_FILE, DEFAULT_DB_FILENAME, LEGACY_DB_FILENAME

router = APIRouter(prefix="/backup")

@router.get("/download")
def download_backup():
    src = str(DATABASE_FILE) if DATABASE_FILE is not None else DEFAULT_DB_FILENAME
    prefix = "lexora_backup"
    if os.path.basename(src) == LEGACY_DB_FILENAME:
        prefix = "teacher_admin_backup"
    name = f"{prefix}_{date.today()}.db"
    dst  = f"/tmp/{name}"
    shutil.copy2(src, dst)
    return FileResponse(dst, filename=name, media_type="application/octet-stream")
