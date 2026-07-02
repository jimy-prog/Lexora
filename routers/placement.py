from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import random

from database import get_db, PlacementQuestion, PlacementSession, Group, Student
from auth import require_teacher_or_owner

router = APIRouter(prefix="/placement", tags=["placement"])
templates = Jinja2Templates(directory="templates")

# Helper to register student on the Waitlist upon passing or manual override
def create_waitlist_from_session(db: Session, session: PlacementSession):
    from routers.waitlist import WaitlistEntry
    level_map = {
        'beginner': 'Beginner',
        'elementary': 'A2',
        'pre-intermediate': 'B1',
        'intermediate': 'B1',
        'upper-intermediate': 'B2',
        'advanced': 'C1'
    }
    cefr_level = level_map.get(session.target_level.lower(), session.target_level.upper())
    
    existing = db.query(WaitlistEntry).filter_by(name=session.student_name, phone=session.phone).first()
    if existing:
        return existing
        
    entry = WaitlistEntry(
        name=session.student_name,
        phone=session.phone,
        parent_phone=session.parent_phone,
        level=cefr_level,
        notes=f"{session.notes}\n[Passed placement test for {session.target_level.upper()} level with score {session.score}/{session.total_questions} on {datetime.utcnow().date()}]".strip(),
        status="new",
        desired_group_id=None
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

# -------------------------------------------------------------
# ADMIN ROUTERS (Restricted to Teacher or Owner)
# -------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def placement_dashboard(request: Request, db: Session = Depends(get_db), current_user = Depends(require_teacher_or_owner)):
    active_sessions = db.query(PlacementSession).filter(PlacementSession.status.in_(["pending", "active"])).order_by(PlacementSession.id.desc()).all()
    completed_sessions = db.query(PlacementSession).filter(PlacementSession.status == "completed").order_by(PlacementSession.completed_at.desc()).all()
    questions = db.query(PlacementQuestion).order_by(PlacementQuestion.level, PlacementQuestion.id).all()
    
    show_pin = request.query_params.get("show_pin", "")
    show_name = request.query_params.get("name", "")
    
    return templates.TemplateResponse("placement_dashboard.html", {
        "request": request,
        "user": current_user,
        "active_sessions": active_sessions,
        "completed_sessions": completed_sessions,
        "questions": questions,
        "active_page": "placement",
        "show_pin": show_pin,
        "show_name": show_name
    })

@router.post("/session/create")
async def create_session(
    request: Request,
    student_name: str = Form(...),
    target_level: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    student_name = student_name.strip()
    target_level = target_level.lower().strip()
    
    # Generate unique 4-digit code
    while True:
        code = f"{random.randint(1000, 9999)}"
        existing = db.query(PlacementSession).filter_by(access_code=code, status="pending").first()
        if not existing:
            break
            
    # Count total questions for this level
    total_q = db.query(PlacementQuestion).filter_by(level=target_level).count()
    
    session = PlacementSession(
        student_name=student_name,
        target_level=target_level,
        access_code=code,
        status="pending",
        total_questions=total_q
    )
    db.add(session)
    db.commit()
    
    return RedirectResponse(f"/placement/?show_pin={code}&name={student_name}", status_code=303)

@router.post("/session/initiate")
async def initiate_placement_session(
    request: Request,
    name: str = Form(...),
    level: str = Form(...),
    group_id: int = Form(...),
    phone: str = Form(""),
    parent_phone: str = Form(""),
    email: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    student_name = name.strip()
    target_level = level.lower().strip()
    
    # Generate unique 4-digit code
    while True:
        code = f"{random.randint(1000, 9999)}"
        existing = db.query(PlacementSession).filter_by(access_code=code, status="pending").first()
        if not existing:
            break
            
    # Count total questions for this level
    total_q = db.query(PlacementQuestion).filter_by(level=target_level).count()
    
    session = PlacementSession(
        student_name=student_name,
        target_level=target_level,
        access_code=code,
        status="pending",
        total_questions=total_q,
        group_id=group_id,
        phone=phone.strip(),
        parent_phone=parent_phone.strip(),
        email=email.strip(),
        notes=notes.strip()
    )
    db.add(session)
    db.commit()
    
    return RedirectResponse(f"/placement/?show_pin={code}&name={student_name}", status_code=303)

@router.post("/session/initiate-json")
async def initiate_placement_json(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    try:
        data = await request.json()
    except Exception:
        # Fallback to form parameters
        form = await request.form()
        data = {
            "name": form.get("name", ""),
            "level": form.get("level", ""),
            "group_id": form.get("group_id", None),
            "phone": form.get("phone", ""),
            "parent_phone": form.get("parent_phone", ""),
            "email": form.get("email", ""),
            "notes": form.get("notes", "")
        }
        
    student_name = data.get("name", "").strip()
    target_level = data.get("level", "").lower().strip()
    
    if not student_name:
        student_name = "New Client"
        
    # Generate unique 4-digit code
    while True:
        code = f"{random.randint(1000, 9999)}"
        existing = db.query(PlacementSession).filter_by(access_code=code, status="pending").first()
        if not existing:
            break
            
    # Count total questions for this level
    total_q = db.query(PlacementQuestion).filter_by(level=target_level).count()
    
    group_id_val = data.get("group_id")
    try:
        group_id = int(group_id_val) if group_id_val else None
    except Exception:
        group_id = None
        
    session = PlacementSession(
        student_name=student_name,
        target_level=target_level,
        access_code=code,
        status="pending",
        total_questions=total_q,
        group_id=group_id,
        phone=data.get("phone", "").strip(),
        parent_phone=data.get("parent_phone", "").strip(),
        email=data.get("email", "").strip(),
        notes=data.get("notes", "").strip()
    )
    db.add(session)
    db.commit()
    
    return JSONResponse(content={"success": True, "pin": code})

@router.post("/session/{session_id}/override")
async def override_and_register(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    session = db.query(PlacementSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Manually register the student on the Waitlist
    create_waitlist_from_session(db, session)
    
    session.passed = True
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    
    return RedirectResponse("/waitlist/?override=success", status_code=303)

@router.post("/question/add")
async def add_placement_question(
    request: Request,
    level: str = Form(...),
    prompt: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    q = PlacementQuestion(
        level=level.lower().strip(),
        prompt=prompt.strip(),
        option_a=option_a.strip(),
        option_b=option_b.strip(),
        option_c=option_c.strip(),
        option_d=option_d.strip(),
        correct_option=correct_option.upper().strip()
    )
    db.add(q)
    db.commit()
    return RedirectResponse("/placement/?qadded=success", status_code=303)

@router.post("/session/{session_id}/delete")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_teacher_or_owner)
):
    session = db.query(PlacementSession).filter_by(id=session_id).first()
    if session:
        db.delete(session)
        db.commit()
    return RedirectResponse("/placement/", status_code=303)

# -------------------------------------------------------------
# PUBLIC CLIENT ROUTERS (Tablet / iPad View - Bypass Auth)
# -------------------------------------------------------------

@router.get("/take", response_class=HTMLResponse)
async def take_placement_portal(request: Request):
    return templates.TemplateResponse("placement_take.html", {
        "request": request,
        "step": "enter_code",
        "error": None
    })

@router.post("/take/start")
async def start_placement_test(
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    code = code.strip()
    session = db.query(PlacementSession).filter_by(access_code=code).first()
    
    if not session:
        return templates.TemplateResponse("placement_take.html", {
            "request": request,
            "step": "enter_code",
            "error": "Invalid access code. Please ask the administrator."
        })
        
    if session.status == "completed":
        return templates.TemplateResponse("placement_take.html", {
            "request": request,
            "step": "enter_code",
            "error": "This test has already been completed."
        })
        
    # Mark as active
    session.status = "active"
    session.started_at = datetime.utcnow()
    db.commit()
    
    questions = db.query(PlacementQuestion).filter_by(level=session.target_level).all()
    
    return templates.TemplateResponse("placement_take.html", {
        "request": request,
        "step": "test",
        "session": session,
        "questions": questions
    })

@router.post("/take/submit")
async def submit_placement_test(
    request: Request,
    session_id: int = Form(...),
    db: Session = Depends(get_db)
):
    session = db.query(PlacementSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    form = await request.form()
    questions = db.query(PlacementQuestion).filter_by(level=session.target_level).all()
    
    correct_count = 0
    for q in questions:
        answer = form.get(f"q_{q.id}", "").upper().strip()
        if answer == q.correct_option:
            correct_count += 1
            
    session.score = correct_count
    session.total_questions = len(questions)
    
    pct = (correct_count / len(questions)) if len(questions) > 0 else 0
    passed = (pct >= 0.60)
    
    if passed:
        # Candidate passed the current target level!
        session.passed = True
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        
        # Auto-create Waitlist Entry
        create_waitlist_from_session(db, session)
        db.commit()
        
        return templates.TemplateResponse("placement_take.html", {
            "request": request,
            "step": "done",
            "session": session,
            "passed": True,
            "was_registered": True
        })
    else:
        # Candidate failed. Let's find the next lower level:
        level_order = ["advanced", "upper-intermediate", "intermediate", "pre-intermediate", "elementary"]
        try:
            curr_idx = level_order.index(session.target_level.lower())
        except ValueError:
            curr_idx = len(level_order) # not in order
            
        if curr_idx < len(level_order) - 1:
            # There is a lower level test available!
            next_level = level_order[curr_idx + 1]
            
            # Update session to use the next lower level
            session.target_level = next_level
            session.score = 0
            session.total_questions = db.query(PlacementQuestion).filter_by(level=next_level).count()
            session.status = "active"
            db.commit()
            
            next_questions = db.query(PlacementQuestion).filter_by(level=next_level).all()
            
            return templates.TemplateResponse("placement_take.html", {
                "request": request,
                "step": "test",
                "session": session,
                "questions": next_questions,
                "failed_previous": True,
                "previous_level": level_order[curr_idx].upper()
            })
        else:
            # Failed even Elementary! So they are Beginner.
            session.target_level = "beginner"
            session.passed = True # Beginner doesn't need to pass a test, so they are marked as completed/passed beginner
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            
            # Auto-create Waitlist Entry at Beginner level
            create_waitlist_from_session(db, session)
            db.commit()
            
            return templates.TemplateResponse("placement_take.html", {
                "request": request,
                "step": "done",
                "session": session,
                "passed": False,
                "is_beginner": True,
                "was_registered": True
            })
