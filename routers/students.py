from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import date
import re

from database import get_db, Student, Group, Attendance, Lesson, TestResult, StudentEvent
from student_history import log_student_event

router = APIRouter(prefix="/students")
templates = Jinja2Templates(directory="templates")


def _norm_phone(v: str) -> str:
    return re.sub(r"\D", "", (v or "").strip())


@router.get("/")
def list_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).filter(
        Student.archived == False,
        Student.banned == False,
        Student.active == True
    ).all()
    groups = db.query(Group).all()

    for s in students:
        s.att_count = db.query(Attendance).filter(
            Attendance.student_id == s.id,
            Attendance.status == "Present"
        ).count()
        s.total = db.query(Attendance).filter(Attendance.student_id == s.id).count()
        s.rate = round(s.att_count / s.total * 100) if s.total else 0

    err = request.query_params.get("error", "")
    warn = request.query_params.get("warn", "")
    msg_name = request.query_params.get("name", "")

    return templates.TemplateResponse("students.html", {
        "request": request,
        "students": students,
        "groups": groups,
        "active_page": "students",
        "error_code": err,
        "warn_code": warn,
        "message_name": msg_name,
    })


@router.get("/banned")
def banned_students_page(request: Request, db: Session = Depends(get_db)):
    banned = db.query(Student).filter(Student.banned == True).order_by(Student.banned_date.desc()).all()
    for s in banned:
        s.att_count = db.query(Attendance).filter(
            Attendance.student_id == s.id,
            Attendance.status == "Present"
        ).count()
        s.total = db.query(Attendance).filter(Attendance.student_id == s.id).count()
        s.rate = round(s.att_count / s.total * 100) if s.total else 0
    return templates.TemplateResponse("students_banned.html", {
        "request": request,
        "banned": banned,
        "active_page": "students",
    })


@router.get("/phone-check")
def check_phone(phone: str = "", db: Session = Depends(get_db)):
    np = _norm_phone(phone)
    if not np:
        return JSONResponse({"ok": True, "known": False, "banned": False, "matches": []})

    matches = db.query(Student).filter(
        or_(
            Student.phone.like(f"%{np}%"),
            Student.parent_phone.like(f"%{np}%")
        )
    ).all()

    payload = [{
        "id": s.id,
        "name": s.name,
        "banned": bool(s.banned),
        "archived": bool(s.archived),
        "phone": s.phone or "",
        "parent_phone": s.parent_phone or "",
    } for s in matches]

    return JSONResponse({
        "ok": True,
        "known": len(matches) > 0,
        "banned": any(s.banned for s in matches),
        "matches": payload,
    })


@router.post("/add")
def add_student(
    name: str = Form(...),
    group_id: int = Form(...),
    phone: str = Form(""),
    parent_phone: str = Form(""),
    email: str = Form(""),
    level: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    np = _norm_phone(phone)
    known_match = None
    if np:
        banned_match = db.query(Student).filter(
            Student.banned == True,
            or_(
                Student.phone.like(f"%{np}%"),
                Student.parent_phone.like(f"%{np}%")
            )
        ).first()
        if banned_match:
            return RedirectResponse(f"/students/?error=banned_phone&name={banned_match.name}", status_code=303)

        known_match = db.query(Student).filter(
            or_(
                Student.phone.like(f"%{np}%"),
                Student.parent_phone.like(f"%{np}%")
            )
        ).first()
        if known_match:
            log_student_event(
                db,
                student=known_match,
                event_type="reused_phone_detected",
                source="students",
                details=f"New registration attempted with same phone for '{name}'",
            )

    s = Student(
        name=name,
        group_id=group_id,
        phone=phone,
        parent_phone=parent_phone,
        email=email,
        notes=notes,
        level=level,
        start_date=date.today(),
        active=True,
        archived=False,
        banned=False,
    )
    db.add(s)
    db.flush()
    log_student_event(
        db,
        student=s,
        event_type="created",
        source="manual",
        details=f"Registered manually into group_id={group_id}",
    )
    db.commit()

    if np and known_match:
        return RedirectResponse(f"/students/?warn=known_phone&name={known_match.name}", status_code=303)

    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/archive")
def archive_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        s.archived = True
        s.active = False
        s.banned = False
        s.end_date = date.today()
        log_student_event(db, student=s, event_type="archived", source="students", details="Moved to archive")
        db.commit()
    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/restore")
def restore_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        s.archived = False
        s.banned = False
        s.active = True
        s.end_date = None
        log_student_event(db, student=s, event_type="restored", source="students", details="Restored to active list")
        db.commit()
    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/transfer")
def transfer_student(sid: int, group_id: int = Form(...), db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    g = db.query(Group).get(group_id)
    if s and g and not s.banned:
        old = s.group.name if s.group else "No Group"
        s.group_id = group_id
        s.active = True
        s.archived = False
        log_student_event(
            db,
            student=s,
            event_type="transfer",
            source="students",
            details=f"Transferred from '{old}' to '{g.name}'",
        )
        db.commit()
    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/exclude")
def exclude_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        old = s.group.name if s.group else "No Group"
        s.group_id = None
        s.active = True
        log_student_event(
            db,
            student=s,
            event_type="excluded",
            source="students",
            details=f"Excluded from group '{old}'",
        )
        db.commit()
    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/ban")
def ban_student(sid: int, reason: str = Form(""), db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        old_group = s.group.name if s.group else "No Group"
        s.banned = True
        s.active = False
        s.archived = False
        s.group_id = None
        s.banned_reason = reason or "No reason provided"
        s.banned_date = date.today()
        log_student_event(
            db,
            student=s,
            event_type="banned",
            source="students",
            details=f"Banned. Reason: {s.banned_reason}. Auto-excluded from '{old_group}'",
        )
        db.commit()
    return RedirectResponse("/students/", status_code=303)


@router.post("/{sid}/unban")
def unban_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        s.banned = False
        s.active = False
        s.group_id = None
        log_student_event(db, student=s, event_type="unbanned", source="students", details="Removed from banned list")
        db.commit()
    return RedirectResponse("/students/banned", status_code=303)


@router.post("/{sid}/log-call")
def log_call_student(sid: int, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if s:
        log_student_event(db, student=s, event_type="call", source="students", details="Call button used")
        db.commit()
    return JSONResponse({"ok": True})


@router.post("/{sid}/update")
def update_student(
    sid: int,
    phone: str = Form(""),
    parent_phone: str = Form(""),
    email: str = Form(""),
    notes: str = Form(""),
    level: str = Form(""),
    progress_notes: str = Form(""),
    strengths: str = Form(""),
    weaknesses: str = Form(""),
    db: Session = Depends(get_db),
):
    s = db.query(Student).get(sid)
    if s:
        s.phone = phone
        s.parent_phone = parent_phone
        s.email = email
        s.notes = notes
        s.level = level
        s.progress_notes = progress_notes
        s.strengths = strengths
        s.weaknesses = weaknesses
        db.commit()
    return RedirectResponse(f"/students/{sid}", status_code=303)


@router.post("/{sid}/add-test")
def add_test(
    sid: int,
    test_date: str = Form(...),
    grammar: float = Form(None),
    vocabulary: float = Form(None),
    activity: float = Form(None),
    comments: str = Form(""),
    db: Session = Depends(get_db),
):
    scores = [x for x in [grammar, vocabulary, activity] if x is not None]
    total = round(sum(scores) / len(scores), 1) if scores else None
    t = TestResult(
        student_id=sid,
        test_date=date.fromisoformat(test_date),
        month=test_date[:7],
        grammar=grammar,
        vocabulary=vocabulary,
        activity=activity,
        total=total,
        comments=comments,
    )
    db.add(t)
    db.commit()
    return RedirectResponse(f"/students/{sid}", status_code=303)


@router.post("/{sid}/delete-test/{tid}")
def delete_test(sid: int, tid: int, db: Session = Depends(get_db)):
    t = db.query(TestResult).get(tid)
    if t:
        db.delete(t)
        db.commit()
    return RedirectResponse(f"/students/{sid}", status_code=303)


@router.get("/search")
def search(q: str = "", db: Session = Depends(get_db)):
    if not q:
        return JSONResponse([])
    results = db.query(Student).filter(Student.name.ilike(f"%{q}%")).limit(10).all()
    return JSONResponse([
        {"id": s.id, "name": s.name, "group": s.group.name if s.group else ""}
        for s in results
    ])


@router.get("/{sid}")
def student_detail(sid: int, request: Request, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if not s:
        raise HTTPException(404)
    records = db.query(Attendance).filter(Attendance.student_id == sid).join(Lesson).order_by(Lesson.date.desc()).all()
    present = sum(1 for r in records if r.status == "Present")
    absent = sum(1 for r in records if r.status == "Absent")
    excused = sum(1 for r in records if r.status == "Excused")
    rate = round(present / len(records) * 100) if records else 0
    tests = db.query(TestResult).filter(TestResult.student_id == sid).order_by(TestResult.test_date.desc()).all()

    from collections import defaultdict

    monthly = defaultdict(lambda: {"present": 0, "absent": 0, "excused": 0})
    for r in records:
        m = r.lesson.date.strftime("%Y-%m")
        if r.status == "Present":
            monthly[m]["present"] += 1
        elif r.status == "Absent":
            monthly[m]["absent"] += 1
        else:
            monthly[m]["excused"] += 1
    monthly_list = sorted(monthly.items(), reverse=True)

    events = db.query(StudentEvent).filter(StudentEvent.student_id == sid).order_by(StudentEvent.created_at.desc()).all()
    return templates.TemplateResponse("student_detail.html", {
        "request": request,
        "student": s,
        "records": records,
        "present": present,
        "absent": absent,
        "excused": excused,
        "rate": rate,
        "monthly_list": monthly_list,
        "tests": tests,
        "events": events,
        "month_str": date.today().strftime("%Y-%m"),
        "active_page": "students",
    })


@router.get("/{sid}/history")
def student_history_popup(sid: int, request: Request, db: Session = Depends(get_db)):
    s = db.query(Student).get(sid)
    if not s:
        raise HTTPException(404)
    events = db.query(StudentEvent).filter(StudentEvent.student_id == sid).order_by(StudentEvent.created_at.desc()).all()
    return templates.TemplateResponse("student_history_popup.html", {
        "request": request,
        "student": s,
        "events": events,
    })
