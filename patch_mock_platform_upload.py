import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/routers/mock_platform.py"
with open(file_path, "r") as f:
    content = f.read()

upload_endpoint = """
@router.post("/{exam_id}/upload-pdf")
async def process_pdf(request: Request, exam_id: int, pdf_doc: UploadFile = File(...), db: SessionMaster = Depends(get_mdb)):
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
        
    # Call Gemini Integration
    result = extract_ielts_exam_from_pdf(temp_path)
    
    # Save AI JSON directly to DB schema
    if "sections" in result:
        for s_data in result["sections"]:
            section = ExamSection(
                exam_id=exam.id,
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
                        prompt=q_data.get("prompt", "")
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
    
    return RedirectResponse(f"/mock/{exam.id}/build", status_code=303)
"""

if "upload-pdf" not in content:
    with open(file_path, "a") as f:
        f.write("\n" + upload_endpoint + "\n")
    print("Endpoint appended")
