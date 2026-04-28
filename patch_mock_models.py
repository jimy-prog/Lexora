import os

file_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/master_database.py"
with open(file_path, "r") as f:
    content = f.read()

models = """
class MockExam(MasterBase):
    __tablename__ = "mock_exams"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    exam_type = Column(String, default="IELTS")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sections = relationship("ExamSection", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("MockAttempt", back_populates="exam")

class ExamSection(MasterBase):
    __tablename__ = "mock_exam_sections"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("mock_exams.id"), nullable=False)
    section_type = Column(String, nullable=False)
    order = Column(Integer, default=1)
    time_limit_minutes = Column(Integer, default=60)
    
    exam = relationship("MockExam", back_populates="sections")
    blocks = relationship("QuestionBlock", back_populates="section", cascade="all, delete-orphan")

class QuestionBlock(MasterBase):
    __tablename__ = "mock_question_blocks"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("mock_exam_sections.id"), nullable=False)
    part_number = Column(Integer, default=1)
    instructions = Column(String, default="")
    passage_text = Column(String, default="")
    media_url = Column(String, default="")
    
    section = relationship("ExamSection", back_populates="blocks")
    questions = relationship("Question", back_populates="block", cascade="all, delete-orphan")

class Question(MasterBase):
    __tablename__ = "mock_questions"
    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey("mock_question_blocks.id"), nullable=False)
    q_type = Column(String, nullable=False)
    question_number = Column(Integer, nullable=False)
    prompt = Column(String, default="")
    points = Column(Integer, default=1)
    
    block = relationship("QuestionBlock", back_populates="questions")
    options = relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan")

class AnswerOption(MasterBase):
    __tablename__ = "mock_answer_options"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("mock_questions.id"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    
    question = relationship("Question", back_populates="options")

class MockAttempt(MasterBase):
    __tablename__ = "mock_attempts"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    student_id = Column(Integer, nullable=False)
    exam_id = Column(Integer, ForeignKey("mock_exams.id"), nullable=False)
    status = Column(String, default="in_progress")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Integer, default=0)
    
    tenant = relationship("PlatformTenant")
    exam = relationship("MockExam", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

class AttemptAnswer(MasterBase):
    __tablename__ = "mock_attempt_answers"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("mock_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("mock_questions.id"), nullable=False)
    text_response = Column(String, default="")
    option_id = Column(Integer, ForeignKey("mock_answer_options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    attempt = relationship("MockAttempt", back_populates="answers")
    question = relationship("Question")
    option = relationship("AnswerOption")

"""

if "MockExam" not in content:
    content = content.replace("def init_master_db():", models + "\ndef init_master_db():")
    with open(file_path, "w") as f:
        f.write(content)
    print("Models inserted.")
else:
    print("Models already exist.")
