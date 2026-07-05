from fastapi import APIRouter, Request, Depends, HTTPException, Form, UploadFile, File
import shutil
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.ai_extractor import extract_ielts_exam_from_pdf
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from master_database import SessionMaster, MockExam, ExamSection, QuestionBlock, Question, AnswerOption, MockAttempt, AttemptAnswer, User, ClassMember, ReviewRequest
from auth import get_current_user

router = APIRouter(prefix="/mock", tags=["mock"])
templates = Jinja2Templates(directory="templates")

def get_mdb():
    db = SessionMaster()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def mock_dashboard(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login?next=/mock", status_code=302)
        
    if user.role == "owner":
        exams = db.query(MockExam).all()
    else:
        exams = db.query(MockExam).filter(MockExam.is_published == True).all()
    
    return templates.TemplateResponse("mock_dashboard.html", {
        "request": request,
        "active_page": "mock",
        "user": user,
        "exams": exams
    })

@router.get("/manage", response_class=HTMLResponse)
async def manage_mocks(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    if user.role != "owner":
        return RedirectResponse("/mock/", status_code=302)
        
    exams = db.query(MockExam).order_by(MockExam.id.desc()).all()
    
    return templates.TemplateResponse("manage_mocks.html", {
        "request": request,
        "active_page": "manage_mocks",
        "user": user,
        "exams": exams
    })

@router.post("/create")
async def create_mock(request: Request, title: str = Form(...), exam_type: str = Form("IELTS"), test_scope: str = Form("Full Test"), test_mode: str = Form("Exam Mode"), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can create exams")
        
    exam = MockExam(title=title, exam_type=exam_type, test_scope=test_scope, test_mode=test_mode)
    db.add(exam)
    db.commit()
    db.refresh(exam)
    
    return RedirectResponse(f"/mock/{exam.id}/build", status_code=302)

@router.post("/{exam_id}/update-settings")
async def update_settings(request: Request, exam_id: int, title: str = Form(...), test_scope: str = Form(...), test_mode: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    exam.title = title
    exam.test_scope = test_scope
    exam.test_mode = test_mode
    db.commit()
    
    return RedirectResponse(f"/mock/{exam.id}/build", status_code=303)

@router.post("/{exam_id}/add-section")
async def add_section(request: Request, exam_id: int, section_type: str = Form(...), time_limit_minutes: int = Form(...), passage_text: str = Form(""), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    section = ExamSection(exam_id=exam.id, section_type=section_type, time_limit_minutes=time_limit_minutes)
    db.add(section)
    db.flush()
    
    if passage_text:
        # Create a block automatically to hold the passage text
        block = QuestionBlock(section_id=section.id, passage_text=passage_text, instructions="")
        db.add(block)
        
    db.commit()
    return RedirectResponse(f"/mock/{exam.id}/build", status_code=303)

@router.post("/{exam_id}/add-question")
async def add_question(request: Request, exam_id: int, section_id: int = Form(...), instructions: str = Form(""), q_type: str = Form(...), prompt: str = Form(...), correct_answer_text: str = Form(""), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    section = db.query(ExamSection).filter(ExamSection.id == section_id, ExamSection.exam_id == exam_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    # Get or create a block to hold this question
    # We'll just attach it to the last block in the section, or create one if none exists
    block = db.query(QuestionBlock).filter(QuestionBlock.section_id == section.id).order_by(QuestionBlock.id.desc()).first()
    if not block:
        block = QuestionBlock(section_id=section.id, passage_text="", instructions=instructions)
        db.add(block)
        db.flush()
    elif instructions and instructions != block.instructions:
        # If they provided new instructions, create a new block
        block = QuestionBlock(section_id=section.id, passage_text="", instructions=instructions)
        db.add(block)
        db.flush()
        
    question_num = db.query(Question).join(QuestionBlock).join(ExamSection).filter(ExamSection.exam_id == exam_id).count() + 1
    
    question = Question(
        block_id=block.id,
        q_type=q_type,
        question_number=str(question_num),
        prompt=prompt,
        correct_answer_text=correct_answer_text,
        points=1
    )
    db.add(question)
    db.commit()
    
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.get("/{exam_id}/build", response_class=HTMLResponse)
async def mock_builder(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can build exams")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    return templates.TemplateResponse("mock_builder.html", {
        "request": request,
        "active_page": "mock",
        "user": user,
        "exam": exam
    })

@router.post("/{exam_id}/publish")
async def publish_exam(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    exam.is_published = True
    db.commit()
    
    return RedirectResponse("/mock/", status_code=303)

@router.post("/{exam_id}/delete")
async def delete_exam(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    db.delete(exam)
    db.commit()
    
    return RedirectResponse("/mock/manage", status_code=303)

@router.get("/{exam_id}/start", response_class=HTMLResponse)
async def take_mock_start(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Check if exam has writing or speaking sections that require review
    has_graded_sections = any(
        s.section_type.lower() in {"writing", "speaking", "writing task 1", "writing task 2"}
        for s in exam.sections
    )
    
    class_teachers = []
    public_teachers = []
    
    if has_graded_sections:
        # Get teachers from classes the student has joined
        if user.role == "student":
            memberships = db.query(ClassMember).filter(ClassMember.student_id == user.id).all()
            # Deduplicate class teachers
            seen_ids = set()
            for m in memberships:
                if m.public_class and m.public_class.teacher:
                    t = m.public_class.teacher
                    if t.id not in seen_ids:
                        class_teachers.append(t)
                        seen_ids.add(t.id)
            
            # Get public teachers (all registered teachers except class teachers)
            all_teachers = db.query(User).filter(User.role == "teacher").all()
            for t in all_teachers:
                if t.id not in seen_ids:
                    public_teachers.append(t)
        else:
            # Fallback for admins/teachers taking exams
            public_teachers = db.query(User).filter(User.role == "teacher").all()
            
    return templates.TemplateResponse("mock_start.html", {
        "request": request,
        "user": user,
        "exam": exam,
        "has_graded_sections": has_graded_sections,
        "class_teachers": class_teachers,
        "public_teachers": public_teachers,
        "active_page": "mock"
    })

@router.post("/{exam_id}/start")
async def start_mock_post(
    request: Request,
    exam_id: int,
    reviewer_type: str = Form("ai"),
    teacher_id: str = Form(""),
    db: SessionMaster = Depends(get_mdb)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Check for existing in-progress attempt to resume it
    attempt = db.query(MockAttempt).filter(
        MockAttempt.student_id == user.id,
        MockAttempt.exam_id == exam.id,
        MockAttempt.status == "in_progress"
    ).order_by(MockAttempt.started_at.desc()).first()
    
    t_id = None
    if reviewer_type == "teacher" and teacher_id:
        try:
            t_id = int(teacher_id)
        except ValueError:
            pass

    if not attempt:
        attempt = MockAttempt(
            tenant_id=user.tenant_id,
            student_id=user.id,
            exam_id=exam.id,
            status="in_progress",
            started_at=datetime.utcnow(),
            reviewer_type=reviewer_type,
            teacher_id=t_id
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    else:
        attempt.reviewer_type = reviewer_type
        attempt.teacher_id = t_id
        db.commit()
        
    return RedirectResponse(f"/mock/{exam_id}/take?attempt_id={attempt.id}", status_code=303)

@router.get("/{exam_id}/take", response_class=HTMLResponse)
async def mock_take(request: Request, exam_id: int, attempt_id: int = None, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(f"/login?next=/mock/{exam_id}/take", status_code=302)
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    if not attempt_id:
        return RedirectResponse(f"/mock/{exam_id}/start", status_code=302)
        
    attempt = db.query(MockAttempt).filter(MockAttempt.id == attempt_id, MockAttempt.student_id == user.id).first()
    if not attempt:
        raise HTTPException(status_code=403, detail="Attempt not found or unauthorized")
        
    return templates.TemplateResponse("mock_take.html", {
        "request": request,
        "user": user,
        "exam": exam,
        "attempt": attempt
    })


from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

# Global dict to track background extraction status
EXTRACTION_STATUS = {}

def process_pdf_background(temp_path: str, exam_id: int, test_scope: str):
    def update_progress(percent: int, message: str):
        EXTRACTION_STATUS[exam_id] = {"progress": percent, "message": message, "status": "processing"}
        
    try:
        update_progress(5, "Initializing AI pipeline...")
        result = extract_ielts_exam_from_pdf(temp_path, test_scope=test_scope, progress_callback=update_progress)
        
        if "error" in result and result["sections"] == []:
            EXTRACTION_STATUS[exam_id] = {"progress": 100, "message": f"AI Error: {result['error']}", "status": "error"}
            return

        update_progress(95, "Building internal database structures...")
        db = SessionMaster()
        try:
            if "sections" in result:
                for s_data in result["sections"]:
                    section = ExamSection(
                        exam_id=exam_id,
                        section_type=s_data.get("section_type", "Reading Section"),
                        time_limit_minutes=20
                    )
                    db.add(section)
                    db.flush()
                    
                    for b_data in s_data.get("blocks", []):
                        block = QuestionBlock(
                            section_id=section.id,
                            instructions=b_data.get("instructions", ""),
                            passage_text=b_data.get("passage_text", "")
                        )
                        db.add(block)
                        db.flush()
                        
                        for idx, q_data in enumerate(b_data.get("questions", [])):
                            question = Question(
                                block_id=block.id,
                                q_type=q_data.get("q_type", "GAP_FILL"),
                                question_number=q_data.get("question_number", idx+1),
                                prompt=q_data.get("prompt", ""),
                                correct_answer_text=q_data.get("correct_answer_text", "")
                            )
                            db.add(question)
                            db.flush()
                            
                            for o_data in q_data.get("options", []):
                                opt = AnswerOption(
                                    question_id=question.id,
                                    text=o_data.get("text", ""),
                                    is_correct=o_data.get("is_correct", False)
                                )
                                db.add(opt)
                
                db.commit()
            EXTRACTION_STATUS[exam_id] = {"progress": 100, "message": "Extraction complete!", "status": "completed"}
        except Exception as e:
            EXTRACTION_STATUS[exam_id] = {"progress": 100, "message": f"Database error: {str(e)}", "status": "error"}
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        EXTRACTION_STATUS[exam_id] = {"progress": 100, "message": f"Pipeline crash: {str(e)}", "status": "error"}

@router.post("/{exam_id}/upload-pdf")
async def process_pdf(request: Request, exam_id: int, background_tasks: BackgroundTasks, pdf_doc: UploadFile = File(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can process tests")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    os.makedirs("uploads/tmp", exist_ok=True)
    temp_path = f"uploads/tmp/{pdf_doc.filename}"
    with open(temp_path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(pdf_doc.file, buffer)
        
    # Start tracking
    EXTRACTION_STATUS[exam.id] = {"progress": 0, "message": "Queuing document...", "status": "processing"}
    background_tasks.add_task(process_pdf_background, temp_path, exam.id, exam.test_scope)
    
    return JSONResponse({"status": "started"})

@router.get("/{exam_id}/upload-status")
async def get_upload_status(exam_id: int, request: Request):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    status = EXTRACTION_STATUS.get(exam_id, {"progress": 0, "message": "Waiting...", "status": "idle"})
    return JSONResponse(status)

@router.post("/{exam_id}/upload-audio")
async def upload_audio(request: Request, exam_id: int, audio_file: UploadFile = File(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can upload audio")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    os.makedirs("uploads/audio", exist_ok=True)
    file_path = f"uploads/audio/{exam_id}_{audio_file.filename}"
    with open(file_path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(audio_file.file, buffer)
        
    exam.audio_url = f"/{file_path}"
    db.commit()
    
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/upload-image")
async def upload_image(request: Request, exam_id: int, image_file: UploadFile = File(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can upload images")
        
    os.makedirs("uploads/images", exist_ok=True)
    import time
    file_path = f"uploads/images/{int(time.time())}_{image_file.filename}"
    with open(file_path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(image_file.file, buffer)
        
    # Auto-link image to first writing block for Writing exams
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if exam and exam.test_scope and "Writing" in exam.test_scope:
        first_section = next((s for s in exam.sections if "writing" in s.section_type.lower()), None)
        if first_section:
            block = db.query(QuestionBlock).filter(QuestionBlock.section_id == first_section.id).first()
            if not block:
                block = QuestionBlock(section_id=first_section.id, passage_text="", instructions="", media_url=f"/{file_path}")
                db.add(block)
            else:
                block.media_url = f"/{file_path}"
            db.commit()
            
    return RedirectResponse(f"/mock/{exam_id}/build?uploaded_img=/{file_path}", status_code=303)

@router.post("/{exam_id}/upload-section-graph/{section_id}")
async def upload_section_graph(
    request: Request,
    exam_id: int,
    section_id: int,
    graph_file: UploadFile = File(...),
    db: SessionMaster = Depends(get_mdb)
):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    section = db.query(ExamSection).filter(ExamSection.id == section_id, ExamSection.exam_id == exam_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    os.makedirs("uploads/images", exist_ok=True)
    import time
    filename = f"graph_{int(time.time())}_{graph_file.filename}"
    file_path = f"uploads/images/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(graph_file.file, buffer)
        
    # Get or create the first block in the section
    block = db.query(QuestionBlock).filter(QuestionBlock.section_id == section.id).first()
    if not block:
        block = QuestionBlock(section_id=section.id, passage_text="", instructions="", media_url=f"/{file_path}")
        db.add(block)
    else:
        block.media_url = f"/{file_path}"
        
    db.commit()
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/delete-block-media/{block_id}")
async def delete_block_media(
    request: Request,
    exam_id: int,
    block_id: int,
    db: SessionMaster = Depends(get_mdb)
):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    block = db.query(QuestionBlock).filter(QuestionBlock.id == block_id).first()
    if block:
        block.media_url = ""
        db.commit()
        
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/save-answers")
async def save_answers(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    form = await request.form()
    
    # Process inputs like answer_14, option_23_4
    for key, val in form.items():
        if key.startswith("answer_"):
            q_id = int(key.split("_")[1])
            question = db.query(Question).filter(Question.id == q_id).first()
            if question:
                question.correct_answer_text = val
        elif key.startswith("option_"):
            # expects option_{q_id}_{opt_id}
            _, q_id, opt_id = key.split("_")
            q_id, opt_id = int(q_id), int(opt_id)
            option = db.query(AnswerOption).filter(AnswerOption.id == opt_id).first()
            if option:
                # set all other options for this q to false first, but only if val is "on"
                if val == "on":
                    db.query(AnswerOption).filter(AnswerOption.question_id == q_id).update({"is_correct": False})
                    option.is_correct = True
                    
    db.commit()
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/bulk-answers")
async def bulk_answers(request: Request, exam_id: int, bulk_text: str = Form(...), db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Only Admins can save answers")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    import re
    lines = [l.strip() for l in bulk_text.split("\n") if l.strip()]
    
    for line in lines:
        match = re.match(r'^(\d+)(?:[\.\)\s-]*)\s*(.+)$', line)
        if not match:
            continue
            
        try:
            q_num = int(match.group(1))
            ans_text = match.group(2).strip()
            
            # Find question
            q = db.query(Question).join(QuestionBlock).join(ExamSection).filter(
                ExamSection.exam_id == exam_id,
                Question.question_number == q_num
            ).first()
            
            if q:
                q.correct_answer_text = ans_text
                
                # If it's an MCQ, try to automatically set the correct AnswerOption
                if q.q_type == "MCQ":
                    db.query(AnswerOption).filter(AnswerOption.question_id == q.id).update({"is_correct": False})
                    # E.g., if ans_text is "C" or "C. Something", look for matching option
                    ans_letter = ans_text[0].upper() if ans_text else ""
                    
                    options = db.query(AnswerOption).filter(AnswerOption.question_id == q.id).all()
                    for opt in options:
                        if opt.text.strip().upper().startswith(ans_letter):
                            opt.is_correct = True
                            break
        except Exception:
            pass
            
    db.commit()
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/delete-section/{section_id}")
async def delete_section(request: Request, exam_id: int, section_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    section = db.query(ExamSection).filter(ExamSection.id == section_id, ExamSection.exam_id == exam_id).first()
    if section:
        db.delete(section)
        db.commit()
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

@router.post("/{exam_id}/delete-question/{question_id}")
async def delete_question(request: Request, exam_id: int, question_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    question = db.query(Question).filter(Question.id == question_id).first()
    if question:
        db.delete(question)
        db.commit()
    return RedirectResponse(f"/mock/{exam_id}/build", status_code=303)

from services.scoring_engine import calculate_band, normalize_text
from datetime import datetime

@router.post("/{exam_id}/submit")
async def submit_exam(request: Request, exam_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=403, detail="Must be logged in to submit")
        
    exam = db.query(MockExam).filter(MockExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    form = await request.form()
    
    # 1. Fetch existing attempt
    attempt_id_val = form.get("attempt_id")
    if attempt_id_val:
        attempt = db.query(MockAttempt).filter(
            MockAttempt.id == int(attempt_id_val),
            MockAttempt.student_id == user.id
        ).first()
    else:
        attempt = None
        
    if not attempt:
        # Fallback if no attempt was created at start
        attempt = MockAttempt(
            tenant_id=user.tenant_id,
            student_id=user.id,
            exam_id=exam.id,
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(attempt)
        db.flush()
    else:
        attempt.status = "completed"
        attempt.completed_at = datetime.utcnow()
        
    # 2. Grade MCQ/Gap-fills & save answers
    raw_score = 0
    writing_responses = [] # list of (question_prompt, student_essay)
    speaking_responses = [] # list of (question_prompt, audio_file_path)
    
    for key, val in form.items():
        if key.startswith("q"):
            q_id = int(key[1:])
            question = db.query(Question).filter(Question.id == q_id).first()
            if not question:
                continue
                
            is_correct = False
            option_id = None
            text_resp = ""
            
            if question.q_type == "MCQ":
                try:
                    option_id = int(val)
                    opt = db.query(AnswerOption).filter(AnswerOption.id == option_id).first()
                    if opt and opt.is_correct:
                        is_correct = True
                except ValueError:
                    pass
            elif val.startswith("data:audio/"):
                import base64
                import os
                from config import UPLOADS_DIR
                try:
                    header, base64_data = val.split(";base64,", 1)
                    ext = "webm"
                    if "/" in header:
                        subparts = header.split(";")
                        if subparts:
                            mime = subparts[0]
                            if "/" in mime:
                                ext = mime.split("/")[-1]
                    audio_data = base64.b64decode(base64_data)
                    filename = f"speaking_{attempt.id}_{q_id}.{ext}"
                    filepath = os.path.join(UPLOADS_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(audio_data)
                    text_resp = f"/uploads/{filename}"
                    
                    # Store for AI/Teacher grading
                    speaking_responses.append((question.prompt, filepath))
                except Exception as e:
                    text_resp = f"Error saving speaking response: {str(e)}"
            else:
                text_resp = val
                expected = normalize_text(question.correct_answer_text)
                provided = normalize_text(text_resp)
                
                # Check if it is a writing section task
                is_writing = False
                if question.block and question.block.section:
                    is_writing = "writing" in question.block.section.section_type.lower()
                    
                if is_writing:
                    writing_responses.append((question.prompt, text_resp))
                else:
                    if expected and provided == expected:
                        is_correct = True
                        
            if is_correct:
                raw_score += question.points
                
            ans = AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q_id,
                text_response=text_resp,
                option_id=option_id,
                is_correct=is_correct
            )
            db.add(ans)
            
    attempt.total_score = raw_score
    
    # 3. Handle Grading Reviewer Types (AI vs. Teacher)
    has_graded_content = len(writing_responses) > 0 or len(speaking_responses) > 0
    
    if has_graded_content:
        if attempt.reviewer_type == "teacher" and attempt.teacher_id:
            # Create a ReviewRequest for the selected teacher
            db.query(ReviewRequest).filter_by(attempt_id=attempt.id, student_id=user.id).delete()
            new_req = ReviewRequest(
                attempt_id=attempt.id,
                student_id=user.id,
                teacher_id=attempt.teacher_id,
                status="pending"
            )
            db.add(new_req)
            attempt.band_score = None # pending review
        else:
            # AI Agent grading
            from services.ai_grader import grade_writing_submission, grade_speaking_submission
            ai_scores = []
            feedback_parts = []
            
            # Grade Writing responses
            for prompt_text, essay_text in writing_responses:
                res = grade_writing_submission(prompt_text, essay_text)
                if res.get("overall_band"):
                    ai_scores.append(res.get("overall_band"))
                feedback_parts.append(f"### Writing Task Feedback\n\n{res.get('feedback_markdown', '')}")
                
            # Grade Speaking responses
            for prompt_text, audio_path in speaking_responses:
                res = grade_speaking_submission(prompt_text, audio_path)
                if res.get("overall_band"):
                    ai_scores.append(res.get("overall_band"))
                feedback_parts.append(f"### Speaking Task Feedback\n\n{res.get('feedback_markdown', '')}")
                
            overall_band = 0.0
            if ai_scores:
                overall_band = round(sum(ai_scores) / len(ai_scores) * 2) / 2 # round to nearest 0.5
                
            combined_feedback = "\n\n---\n\n".join(feedback_parts)
            
            db.query(ReviewRequest).filter_by(attempt_id=attempt.id, student_id=user.id).delete()
            new_req = ReviewRequest(
                attempt_id=attempt.id,
                student_id=user.id,
                teacher_id=1, # Use owner ID (1) to satisfy NOT NULL constraint for AI reviews
                status="reviewed",
                score=overall_band,
                feedback=combined_feedback,
                reviewed_at=datetime.utcnow()
            )
            db.add(new_req)
            attempt.band_score = overall_band
    else:
        # Standard Listening/Reading exam auto-calculated
        attempt.band_score = calculate_band(raw_score, exam.test_scope)
        
    db.commit()
    return RedirectResponse(f"/mock/results/{attempt.id}", status_code=303)

@router.get("/results/{attempt_id}", response_class=HTMLResponse)
async def mock_results(request: Request, attempt_id: int, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    attempt = db.query(MockAttempt).filter(MockAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Result not found")
        
    is_auth = (attempt.student_id == user.id) or (user.role == "owner") or (user.role == "teacher" and attempt.teacher_id == user.id)
    if not is_auth:
        raise HTTPException(status_code=404, detail="Result not found")
        
    review = db.query(ReviewRequest).filter(ReviewRequest.attempt_id == attempt.id).first()
    
    return templates.TemplateResponse("mock_results.html", {
        "request": request,
        "user": user,
        "attempt": attempt,
        "review": review,
        "active_page": "mock"
    })

@router.get("/history", response_class=HTMLResponse)
async def mock_history(request: Request, db: SessionMaster = Depends(get_mdb)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
        
    # Get all completed attempts for this user
    attempts = db.query(MockAttempt).filter(
        MockAttempt.student_id == user.id,
        MockAttempt.status == "completed"
    ).order_by(MockAttempt.completed_at.desc()).all()
    
    return templates.TemplateResponse("mock_history.html", {
        "request": request,
        "user": user,
        "attempts": attempts,
        "active_page": "history"
    })
