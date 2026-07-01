from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from master_database import SessionMaster, User, ReviewRequest, MockAttempt, ClassMember, PublicClass
from auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

@router.get("/inbox", response_class=HTMLResponse)
async def review_inbox(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "teacher":
        return RedirectResponse("/login", status_code=302)
        
    requests = db.query(ReviewRequest).filter(ReviewRequest.teacher_id == user.id).order_by(ReviewRequest.status.desc(), ReviewRequest.created_at.desc()).all()
    
    return templates.TemplateResponse("teacher_reviews.html", {
        "request": request,
        "user": user,
        "review_requests": requests,
        "active_page": "reviews"
    })

@router.post("/submit")
async def submit_review_request(request: Request, attempt_id: int = Form(...), teacher_id: int = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit for review")
        
    # Check if request already exists
    existing = db.query(ReviewRequest).filter_by(attempt_id=attempt_id, student_id=user.id).first()
    if existing:
        return RedirectResponse(f"/mock/results/{attempt_id}?msg=Already+Submitted", status_code=303)
        
    new_req = ReviewRequest(attempt_id=attempt_id, student_id=user.id, teacher_id=teacher_id)
    db.add(new_req)
    db.commit()
    
    return RedirectResponse(f"/mock/results/{attempt_id}?msg=Review+Requested", status_code=303)

@router.get("/{review_id}", response_class=HTMLResponse)
async def review_detail(request: Request, review_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    req = db.query(ReviewRequest).filter(ReviewRequest.id == review_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Review request not found")
        
    # Security: Only involved student or teacher
    if user.id != req.student_id and user.id != req.teacher_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    return templates.TemplateResponse("review_detail.html", {
        "request": request,
        "user": user,
        "review": req
    })

@router.post("/{review_id}/grade")
async def grade_review(request: Request, review_id: int, score: float = Form(...), feedback: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "teacher":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    req = db.query(ReviewRequest).filter(ReviewRequest.id == review_id, ReviewRequest.teacher_id == user.id).first()
    if req:
        req.score = score
        req.feedback = feedback
        req.status = "reviewed"
        req.reviewed_at = datetime.utcnow()
        db.commit()
        
    return RedirectResponse("/reviews/inbox", status_code=303)
