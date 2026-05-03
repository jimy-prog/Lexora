import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

MASTER_DB_URL = "sqlite:///./master.db"
engine_master = create_engine(MASTER_DB_URL, connect_args={"check_same_thread": False})
SessionMaster = sessionmaker(autocommit=False, autoflush=False, bind=engine_master)
MasterBase = declarative_base()

class PlatformTenant(MasterBase):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, nullable=False)
    db_filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

class User(MasterBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="owner")  # owner, admin
    is_active = Column(Boolean, default=True)
    full_name = Column(String, default="")
    title = Column(String, default="")
    bio = Column(String, default="")
    phone = Column(String, default="")
    school_name = Column(String, default="")
    bank_details = Column(String, default="")
    photo_path = Column(String, default="")
    account_type = Column(String, default="student") # teacher or student
    study_focus = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    is_public_teacher = Column(Boolean, default=False)
    
    tenant = relationship("PlatformTenant", back_populates="users")
    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")

class AuthSession(MasterBase):
    __tablename__ = "auth_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")

class EmailOTP(MasterBase):
    __tablename__ = "email_otps"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MockExam(MasterBase):
    __tablename__ = "mock_exams"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    exam_type = Column(String, default="IELTS")
    test_scope = Column(String, default="Full Test")
    test_mode = Column(String, default="Exam Mode")
    is_published = Column(Boolean, default=False)
    audio_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sections = relationship("ExamSection", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("MockAttempt", back_populates="exam", cascade="all, delete-orphan")

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
    correct_answer_text = Column(String, default="")
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
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("mock_exams.id"), nullable=False)
    status = Column(String, default="in_progress")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Integer, default=0)
    band_score = Column(Float, nullable=True)
    feedback_preference = Column(String, nullable=True) # 'ai' or 'teacher'
    selected_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    tenant = relationship("PlatformTenant")
    student = relationship("User", foreign_keys=[student_id])
    exam = relationship("MockExam", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")
    feedback = relationship("WritingFeedback", back_populates="attempt", cascade="all, delete-orphan")

class AttemptAnswer(MasterBase):
    __tablename__ = "mock_attempt_answers"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("mock_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("mock_questions.id"), nullable=False)
    text_response = Column(String, default="")
    option_id = Column(Integer, ForeignKey("mock_answer_options.id"), nullable=True)
    audio_url = Column(String, nullable=True) # For speaking section
    file_url = Column(String, nullable=True)  # For writing section image/pdf uploads
    is_correct = Column(Boolean, nullable=True)
    
    attempt = relationship("MockAttempt", back_populates="answers")
    question = relationship("Question")
    option = relationship("AnswerOption")

class ClassRoom(MasterBase):
    __tablename__ = "class_rooms"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User")
    members = relationship("ClassMember", back_populates="classroom", cascade="all, delete-orphan")

class ClassMember(MasterBase):
    __tablename__ = "class_members"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("class_rooms.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    classroom = relationship("ClassRoom", back_populates="members")
    student = relationship("User")

class WritingFeedback(MasterBase):
    __tablename__ = "writing_feedback"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("mock_attempts.id"), nullable=False)
    feedback_type = Column(String, nullable=False) # 'ai' or 'teacher'
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="pending") # 'pending', 'completed'
    score = Column(Float, nullable=True)
    feedback_text = Column(String, default="")
    ai_analysis = Column(String, default="") # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    attempt = relationship("MockAttempt")
    teacher = relationship("User")

class SupportTicket(MasterBase):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False) # 'bug', 'feedback', 'question'
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="open") # 'open', 'resolved'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class PasswordResetToken(MasterBase):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


def init_master_db():
    MasterBase.metadata.create_all(bind=engine_master)
    
    # Try to initialize the default owner if not exists
    db = SessionMaster()
    try:
        from config import OWNER_EMAIL, OWNER_USERNAME, OWNER_FULL_NAME, DEFAULT_ADMIN_PASSWORD
        import auth 
        # But wait, auth depends on master_database now, we might get circular imports.
        # We will handle default user seeding in a separate script.
    finally:
        db.close()
