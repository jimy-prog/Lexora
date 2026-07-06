from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import random
import string
from master_database import SessionMaster, User, PublicClass, ClassMember, ClassTask, ClassMessage, ClassTimelineEvent
from auth import get_current_user

router = APIRouter(prefix="/classes", tags=["classes"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.get("/", response_class=HTMLResponse)
async def my_classes(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    if user.role in ("teacher", "owner"):
        if user.role == "owner":
            classes = db.query(PublicClass).all()
        else:
            classes = db.query(PublicClass).filter(PublicClass.teacher_id == user.id).all()
        return templates.TemplateResponse("teacher_classes.html", {
            "request": request,
            "user": user,
            "classes": classes,
            "active_page": "classes"
        })
    elif user.role == "student":
        memberships = db.query(ClassMember).filter(ClassMember.student_id == user.id).all()
        return templates.TemplateResponse("student_classes.html", {
            "request": request,
            "user": user,
            "memberships": memberships,
            "active_page": "classes"
        })
    else:
        return RedirectResponse("/dashboard", status_code=302)

@router.post("/create")
async def create_class(request: Request, name: str = Form(...), description: str = Form(""), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create classes")
        
    code = generate_invite_code()
    # Ensure uniqueness
    while db.query(PublicClass).filter(PublicClass.invite_code == code).first():
        code = generate_invite_code()
        
    new_class = PublicClass(teacher_id=user.id, name=name, description=description, invite_code=code)
    db.add(new_class)
    db.commit()
    
    return RedirectResponse("/classes/", status_code=303)

@router.post("/join")
async def join_class(request: Request, code: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can join classes")
        
    code = code.upper().strip()
    target_class = db.query(PublicClass).filter(PublicClass.invite_code == code).first()
    if not target_class:
        # For simplicity, redirect back with error in future iterations
        return RedirectResponse("/classes/?error=Invalid+Code", status_code=303)
        
    # Check if already a member
    existing = db.query(ClassMember).filter(ClassMember.class_id == target_class.id, ClassMember.student_id == user.id).first()
    if not existing:
        member = ClassMember(class_id=target_class.id, student_id=user.id)
        db.add(member)
        db.commit()
        
    return RedirectResponse("/classes/", status_code=303)

@router.post("/{class_id}/delete")
async def delete_class(request: Request, class_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role not in ("teacher", "owner"):
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    if user.role == "owner":
        target = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    else:
        target = db.query(PublicClass).filter(PublicClass.id == class_id, PublicClass.teacher_id == user.id).first()
        
    if target:
        db.delete(target)
        db.commit()
        
    return RedirectResponse("/classes/", status_code=303)


@router.get("/{class_id}", response_class=HTMLResponse)
async def class_details(class_id: int, request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    is_authorized = False
    if user.role == "owner" or (user.role == "teacher" and target_class.teacher_id == user.id):
        is_authorized = True
    elif user.role == "student":
        member = db.query(ClassMember).filter(ClassMember.class_id == class_id, ClassMember.student_id == user.id).first()
        if member:
            is_authorized = True
            
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Unauthorized access to this class")
        
    members = db.query(ClassMember).filter(ClassMember.class_id == class_id).all()
    tasks = db.query(ClassTask).filter(ClassTask.class_id == class_id).order_by(ClassTask.created_at.desc()).all()
    messages = db.query(ClassMessage).filter(ClassMessage.class_id == class_id).order_by(ClassMessage.created_at.asc()).all()
    timeline = db.query(ClassTimelineEvent).filter(ClassTimelineEvent.class_id == class_id).order_by(ClassTimelineEvent.event_date_str.asc()).all()
    
    from master_database import MockExam
    all_exams = db.query(MockExam).all() if user.role in ("teacher", "owner") else []
    
    return templates.TemplateResponse("class_details.html", {
        "request": request,
        "user": user,
        "klass": target_class,
        "members": members,
        "tasks": tasks,
        "messages": messages,
        "timeline": timeline,
        "all_exams": all_exams,
        "active_page": "classes"
    })


@router.post("/{class_id}/add-student")
async def add_student_to_class(class_id: int, request: Request, username: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role not in ("teacher", "owner"):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class or (user.role == "teacher" and target_class.teacher_id != user.id):
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    student = db.query(User).filter(User.username == username.strip()).first()
    if not student:
        return RedirectResponse(f"/classes/{class_id}?error=Student+not+found", status_code=303)
        
    if student.role != "student":
        return RedirectResponse(f"/classes/{class_id}?error=User+is+not+a+student", status_code=303)
        
    existing = db.query(ClassMember).filter(ClassMember.class_id == class_id, ClassMember.student_id == student.id).first()
    if not existing:
        member = ClassMember(class_id=class_id, student_id=student.id)
        db.add(member)
        db.commit()
        
    return RedirectResponse(f"/classes/{class_id}?msg=Student+added+successfully", status_code=303)


@router.post("/{class_id}/remove-student/{student_id}")
async def remove_student_from_class(class_id: int, student_id: int, request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role not in ("teacher", "owner"):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class or (user.role == "teacher" and target_class.teacher_id != user.id):
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    member = db.query(ClassMember).filter(ClassMember.class_id == class_id, ClassMember.student_id == student_id).first()
    if member:
        db.delete(member)
        db.commit()
        
    return RedirectResponse(f"/classes/{class_id}?msg=Student+removed", status_code=303)


@router.post("/{class_id}/add-task")
async def add_class_task(
    class_id: int, 
    request: Request, 
    title: str = Form(...), 
    description: str = Form(""), 
    mock_exam_id: str = Form(None), 
    deadline_str: str = Form(""), 
    db: SessionMaster = Depends(get_mdb)
):
    user = get_current_user(request)
    if not user or user.role not in ("teacher", "owner"):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class or (user.role == "teacher" and target_class.teacher_id != user.id):
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    exam_id = int(mock_exam_id) if mock_exam_id and mock_exam_id.isdigit() else None
    
    task = ClassTask(
        class_id=class_id,
        title=title,
        description=description,
        mock_exam_id=exam_id,
        deadline_str=deadline_str
    )
    db.add(task)
    db.commit()
    
    return RedirectResponse(f"/classes/{class_id}?msg=Task+created", status_code=303)


@router.post("/{class_id}/send-message")
async def send_class_message(class_id: int, request: Request, message: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    is_authorized = False
    if user.role == "owner" or (user.role == "teacher" and target_class.teacher_id == user.id):
        is_authorized = True
    elif user.role == "student":
        member = db.query(ClassMember).filter(ClassMember.class_id == class_id, ClassMember.student_id == user.id).first()
        if member:
            is_authorized = True
            
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    msg = ClassMessage(
        class_id=class_id,
        sender_id=user.id,
        message=message.strip()
    )
    db.add(msg)
    db.commit()
    
    return RedirectResponse(f"/classes/{class_id}#chatBox", status_code=303)


@router.post("/{class_id}/add-timeline-event")
async def add_timeline_event(
    class_id: int, 
    request: Request, 
    title: str = Form(...), 
    description: str = Form(""), 
    event_date_str: str = Form(...), 
    db: SessionMaster = Depends(get_mdb)
):
    user = get_current_user(request)
    if not user or user.role not in ("teacher", "owner"):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    target_class = db.query(PublicClass).filter(PublicClass.id == class_id).first()
    if not target_class or (user.role == "teacher" and target_class.teacher_id != user.id):
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    event = ClassTimelineEvent(
        class_id=class_id,
        title=title,
        description=description,
        event_date_str=event_date_str
    )
    db.add(event)
    db.commit()
    
    return RedirectResponse(f"/classes/{class_id}?msg=Timeline+event+added", status_code=303)
