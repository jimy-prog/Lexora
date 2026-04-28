from fastapi import APIRouter, Request, Depends, Form, Header, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Boolean, or_
from sqlalchemy.orm import Session, relationship
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
import os
import ssl
import csv
import io
import re
from urllib.parse import quote, urlparse, parse_qs
from urllib.request import urlopen, Request as UrlRequest
from database import get_db, Base, Group, Student, Settings
from student_history import log_student_event

router = APIRouter(prefix="/waitlist")
templates = Jinja2Templates(directory="templates")

class WaitlistEntry(Base):
    __tablename__ = "waitlist"
    __table_args__ = {"extend_existing": True}
    id                 = Column(Integer, primary_key=True)
    name               = Column(String, nullable=False)
    phone              = Column(String, default="")
    parent_phone       = Column(String, default="")
    desired_group_id   = Column(Integer, ForeignKey("groups.id"), nullable=True)
    preferred_schedule = Column(String, default="")
    how_found          = Column(String, default="")
    learning_goal      = Column(Text, default="")
    notes              = Column(Text, default="")
    status             = Column(String, default="new")  # new/contacted/trial/enrolled
    mode               = Column(String, default="in-person")  # in-person/online
    trial_date         = Column(Date, nullable=True)
    trial_done         = Column(Boolean, default=False)
    enquiry_date       = Column(Date, default=date.today)
    created_at         = Column(DateTime, default=datetime.utcnow)
    desired_group      = relationship("Group")



STATUS_LABELS = {
    "new":       ("New Enquiry",   "pill-orange"),
    "contacted": ("Contacted",     "pill-blue"),
    "trial":     ("Trial Lesson",  "pill-yellow"),
    "enrolled":  ("Enrolled",      "pill-green"),
}
HOW_FOUND = ["Instagram","Friend/Referral","Telegram","Google","Company","Other"]

DEFAULT_WAITLIST_SHEET_ID = "1pdQkS1LT6QfzXTZv0a4gOHdOzi5Ttd5oqExlu6XuBI0"
DEFAULT_WAITLIST_SHEET_NAME = "Form_Responses"
DEFAULT_WAITLIST_SHEET_GID = "573437932"

def _get_setting(db: Session, key: str, default: str = "") -> str:
    s = db.query(Settings).filter(Settings.key == key).first()
    return s.value if s and s.value is not None else default


def _set_setting(db: Session, key: str, value: str):
    s = db.query(Settings).filter(Settings.key == key).first()
    if s:
        s.value = value
    else:
        db.add(Settings(key=key, value=value, label=key, category="integrations"))


def _norm_header(v: str) -> str:
    return re.sub(r"[^a-zа-я0-9]", "", (v or "").strip().lower())


def _pick(row: dict, aliases: set) -> str:
    for k, v in row.items():
        if _norm_header(k) in aliases and str(v or "").strip():
            return str(v).strip()
    return ""


def _parse_mode(raw: str) -> str:
    v = (raw or "").strip().lower()
    if "online" in v or "онлайн" in v:
        return "online"
    return "in-person"


def _normalize_csv_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if "/pubhtml" in u:
        return u.replace("/pubhtml", "/pub?output=csv")
    if u.endswith("/pub"):
        return u + "?output=csv"
    return u


def _is_probably_csv(body: str) -> bool:
    s = (body or "").lstrip().lower()
    if not s:
        return False
    if s.startswith("<"):
        return False
    first_line = (body.splitlines()[0] if body.splitlines() else "").lower()
    if "<html" in first_line or "<!doctype" in first_line:
        return False
    return "," in first_line


def _extract_sheet_id_and_gid(value: str):
    value = (value or "").strip()
    if not value:
        return "", ""
    if value.startswith("http"):
        try:
            u = urlparse(value)
            parts = [p for p in u.path.split("/") if p]
            sid = ""
            if "d" in parts:
                i = parts.index("d")
                if i + 1 < len(parts):
                    sid = parts[i + 1]
            gid = ""
            q = parse_qs(u.query)
            if "gid" in q and q["gid"]:
                gid = q["gid"][0]
            if not gid and u.fragment.startswith("gid="):
                gid = u.fragment.replace("gid=", "", 1)
            return sid, gid
        except Exception:
            return "", ""
    return value, ""


class GoogleWaitlistPayload(BaseModel):
    name: str
    phone: str = ""
    parent_phone: str = ""
    desired_group_id: Optional[int] = None
    preferred_schedule: str = ""
    how_found: str = "Google Form"
    learning_goal: str = ""
    notes: str = ""
    mode: str = "in-person"

@router.post("/from-google-form")
def add_from_google_form(
    payload: GoogleWaitlistPayload,
    x_webhook_token: str = Header(default=""),
    token: str = "",
    db: Session = Depends(get_db)
):
    secret = os.getenv("WAITLIST_WEBHOOK_TOKEN", "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="Webhook token is not configured")

    provided = (x_webhook_token or token or "").strip()
    if provided != secret:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="name is required")

    mode = (payload.mode or "in-person").strip().lower()
    if mode not in {"in-person", "online"}:
        mode = "in-person"

    desired_group_id = payload.desired_group_id
    if desired_group_id:
        exists = db.query(Group).filter(Group.id == desired_group_id).first()
        if not exists:
            desired_group_id = None

    phone = (payload.phone or "").strip()
    duplicate = db.query(WaitlistEntry).filter(
        WaitlistEntry.name == name,
        WaitlistEntry.phone == phone,
        WaitlistEntry.status != "enrolled",
        WaitlistEntry.enquiry_date == date.today()
    ).first()
    if duplicate:
        return {"ok": True, "status": "duplicate", "entry_id": duplicate.id}

    entry = WaitlistEntry(
        name=name,
        phone=phone,
        parent_phone=(payload.parent_phone or "").strip(),
        desired_group_id=desired_group_id,
        preferred_schedule=(payload.preferred_schedule or "").strip(),
        how_found=(payload.how_found or "Google Form").strip(),
        learning_goal=(payload.learning_goal or "").strip(),
        notes=(payload.notes or "").strip(),
        mode=mode,
        status="new",
        enquiry_date=date.today(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"ok": True, "status": "created", "entry_id": entry.id}

@router.get("/")
def waitlist_view(request: Request, db: Session = Depends(get_db)):
    entries = db.query(WaitlistEntry).filter(
        WaitlistEntry.status != "enrolled"
    ).order_by(WaitlistEntry.enquiry_date.desc()).all()
    groups = db.query(Group).filter(Group.status == "active").all()
    sheet_id = _get_setting(db, "waitlist_sheet_id", DEFAULT_WAITLIST_SHEET_ID)
    sheet_name = _get_setting(db, "waitlist_sheet_name", DEFAULT_WAITLIST_SHEET_NAME)
    imported_rows = _get_setting(db, "waitlist_sheet_last_index", "0")
    sheet_gid = _get_setting(db, "waitlist_sheet_gid", DEFAULT_WAITLIST_SHEET_GID)
    last_import_error = _get_setting(db, "waitlist_sheet_last_error", "")
    sheet_csv_url = _get_setting(db, "waitlist_sheet_csv_url", "")
    return templates.TemplateResponse("waitlist.html", {
        "request": request, "entries": entries,
        "groups": groups, "status_labels": STATUS_LABELS,
        "how_found_options": HOW_FOUND,
        "sheet_id": sheet_id,
        "sheet_name": sheet_name,
        "imported_rows": imported_rows,
        "sheet_gid": sheet_gid,
        "last_import_error": last_import_error,
        "sheet_csv_url": sheet_csv_url,
        "active_page": "waitlist"
    })

@router.post("/import-google-sheet")
def import_google_sheet(
    sheet_id: str = Form(""),
    sheet_name: str = Form(""),
    sheet_gid: str = Form(""),
    reset_cursor: str = Form(""),
    db: Session = Depends(get_db)
):
    configured_id = _get_setting(db, "waitlist_sheet_id", DEFAULT_WAITLIST_SHEET_ID)
    configured_name = _get_setting(db, "waitlist_sheet_name", DEFAULT_WAITLIST_SHEET_NAME)
    configured_gid = _get_setting(db, "waitlist_sheet_gid", DEFAULT_WAITLIST_SHEET_GID)
    configured_csv_url = _get_setting(db, "waitlist_sheet_csv_url", "")

    raw_sheet_id = (sheet_id or configured_id or "").strip()
    parsed_id, parsed_gid = _extract_sheet_id_and_gid(raw_sheet_id)

    sheet_id = (parsed_id or raw_sheet_id or DEFAULT_WAITLIST_SHEET_ID).strip()
    sheet_name = (sheet_name or configured_name or DEFAULT_WAITLIST_SHEET_NAME).strip()
    sheet_gid = (sheet_gid or parsed_gid or configured_gid or DEFAULT_WAITLIST_SHEET_GID).strip()

    if not sheet_gid and parsed_gid:
        sheet_gid = parsed_gid

    sheet_csv_url = _normalize_csv_url(configured_csv_url or "")

    _set_setting(db, "waitlist_sheet_id", sheet_id)
    _set_setting(db, "waitlist_sheet_name", sheet_name)
    _set_setting(db, "waitlist_sheet_gid", sheet_gid)
    _set_setting(db, "waitlist_sheet_csv_url", sheet_csv_url)

    if reset_cursor == "1":
        last_index = 0
    else:
        try:
            last_index = int(_get_setting(db, "waitlist_sheet_last_index", "0") or 0)
        except Exception:
            last_index = 0

    candidates = []
    if sheet_csv_url.startswith("http"):
        candidates.append(sheet_csv_url)
    candidates.append(f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={quote(sheet_name)}")
    if sheet_gid:
        candidates.append(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_gid}")
    candidates.append(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

    body = ""
    last_error = ""
    default_ctx = ssl.create_default_context()
    loose_ctx = ssl._create_unverified_context()

    for url in candidates:
        req = UrlRequest(url, headers={
            "User-Agent": "Mozilla/5.0 (TeacherAdmin Waitlist Import)",
            "Accept": "text/csv,*/*",
        })
        for ctx in (default_ctx, loose_ctx):
            try:
                with urlopen(req, timeout=20, context=ctx) as resp:
                    body = resp.read().decode("utf-8-sig")
                    if _is_probably_csv(body):
                        break
                    body = ""
            except Exception as e:
                last_error = str(e)
        if _is_probably_csv(body):
            break

    if not body:
        msg = (last_error or "Unknown network/auth error or non-CSV response")[:240]
        _set_setting(db, "waitlist_sheet_last_error", msg)
        db.commit()
        print(f"[Waitlist Import] Failed. id={sheet_id} name={sheet_name} gid={sheet_gid} err={msg}")
        return RedirectResponse("/waitlist/?import_err=sheet_unavailable", status_code=303)

    rows = list(csv.DictReader(io.StringIO(body)))
    total = len(rows)
    if total <= last_index:
        _set_setting(db, "waitlist_sheet_last_index", str(total))
        _set_setting(db, "waitlist_sheet_last_error", "")
        db.commit()
        return RedirectResponse("/waitlist/?import_ok=1&imported=0", status_code=303)

    new_rows = rows[last_index:]
    created = 0

    name_keys = {"fullname", "fullname*", "fullnamerequired", "имя", "фио"}
    phone_keys = {"phone", "phonenumber", "номер", "телефон"}
    parent_phone_keys = {"parentphone", "родительскийтелефон", "parent"}
    mode_keys = {"mode", "формат", "modeonlineinperson"}
    schedule_keys = {"preferredschedule", "schedule", "предпочтительноерасписание", "расписание"}
    how_found_keys = {"howfound", "источник", "откудаузнали"}
    goal_keys = {"goalnotes", "goal", "learninggoal", "цель", "заметки"}

    for row in new_rows:
        name = _pick(row, name_keys)
        if not name:
            continue
        phone = _pick(row, phone_keys)
        parent_phone = _pick(row, parent_phone_keys)
        mode = _parse_mode(_pick(row, mode_keys))
        preferred_schedule = _pick(row, schedule_keys)
        how_found = _pick(row, how_found_keys) or "Google Form"
        learning_goal = _pick(row, goal_keys)

        duplicate = db.query(WaitlistEntry).filter(
            WaitlistEntry.name == name,
            WaitlistEntry.phone == phone,
            WaitlistEntry.status != "enrolled",
            WaitlistEntry.enquiry_date == date.today()
        ).first()
        if duplicate:
            continue

        db.add(WaitlistEntry(
            name=name,
            phone=phone,
            parent_phone=parent_phone,
            preferred_schedule=preferred_schedule,
            how_found=how_found,
            learning_goal=learning_goal,
            notes="Imported from Google Sheet",
            mode=mode,
            status="new",
            enquiry_date=date.today(),
        ))
        created += 1

    _set_setting(db, "waitlist_sheet_last_index", str(total))
    _set_setting(db, "waitlist_sheet_last_error", "")
    db.commit()
    return RedirectResponse(f"/waitlist/?import_ok=1&imported={created}", status_code=303)

@router.post("/add")
def add_entry(
    name: str = Form(...), phone: str = Form(""),
    parent_phone: str = Form(""), desired_group_id: str = Form(""),
    preferred_schedule: str = Form(""), how_found: str = Form(""),
    learning_goal: str = Form(""), notes: str = Form(""),
    mode: str = Form("in-person"),
    db: Session = Depends(get_db)
):
    if phone.strip():
        banned_match = db.query(Student).filter(
            Student.banned == True,
            or_(
                Student.phone == phone.strip(),
                Student.parent_phone == phone.strip()
            )
        ).first()
        if banned_match:
            return RedirectResponse("/waitlist/?err=banned_phone", status_code=303)

    db.add(WaitlistEntry(
        name=name, phone=phone, parent_phone=parent_phone,
        desired_group_id=int(desired_group_id) if desired_group_id else None,
        preferred_schedule=preferred_schedule, how_found=how_found,
        learning_goal=learning_goal, notes=notes,
        mode=mode, status="new", enquiry_date=date.today()
    ))
    db.commit()
    return RedirectResponse("/waitlist/", status_code=303)

@router.post("/{eid}/status")
def update_status(eid: int, status: str = Form(...),
                  db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if e: e.status = status; db.commit()
    return RedirectResponse("/waitlist/", status_code=303)

@router.post("/{eid}/trial")
def set_trial(eid: int, trial_date: str = Form(...),
              db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if e:
        e.trial_date = date.fromisoformat(trial_date)
        e.status = "trial"
        db.commit()
    return RedirectResponse("/waitlist/", status_code=303)

@router.post("/{eid}/trial-done")
def trial_done(eid: int, db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if e: e.trial_done = True; db.commit()
    return RedirectResponse("/waitlist/", status_code=303)

@router.post("/{eid}/enroll")
def enroll_student(eid: int, group_id: int = Form(...),
                   level: str = Form(""),
                   db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if not e:
        return RedirectResponse("/waitlist/", status_code=303)
    banned_match = None
    if (e.phone or "").strip():
        banned_match = db.query(Student).filter(
            Student.banned == True,
            or_(
                Student.phone == e.phone.strip(),
                Student.parent_phone == e.phone.strip()
            )
        ).first()
    if banned_match:
        return RedirectResponse("/waitlist/?err=banned_phone", status_code=303)

    s = Student(
        name=e.name, group_id=group_id, phone=e.phone,
        parent_phone=e.parent_phone, level=level,
        notes=e.learning_goal, active=True, archived=False,
        start_date=date.today()
    )
    db.add(s)
    db.flush()
    log_student_event(
        db, student=s, event_type="created", source="waitlist",
        details=(
            f"Enrolled from waitlist entry #{e.id}. "
            f"Mode={e.mode}, Preferred schedule={e.preferred_schedule or '-'}, "
            f"How found={e.how_found or '-'}, Goal={e.learning_goal or '-'}"
        )
    )
    e.status = "enrolled"
    db.commit()
    return RedirectResponse("/students/", status_code=303)

@router.post("/{eid}/log-call")
def log_call_waitlist(eid: int, db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if e:
        # Keep lightweight event trail even before full enrollment.
        db.add(Settings(
            key=f"waitlist_call_log_{eid}_{datetime.utcnow().timestamp()}",
            value=f"{e.name}|{e.phone}|{date.today()}",
            label="waitlist_call_log",
            category="audit"
        ))
        db.commit()
    return JSONResponse({"ok": True})

@router.post("/{eid}/delete")
def delete_entry(eid: int, db: Session = Depends(get_db)):
    e = db.query(WaitlistEntry).get(eid)
    if e: db.delete(e); db.commit()
    return RedirectResponse("/waitlist/", status_code=303)
