import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import DATA_DIR
MASTER_DB_URL = f"sqlite:///{DATA_DIR / 'master.db'}"
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
    phone = Column(String, nullable=True, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")  # owner, teacher, student
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    full_name = Column(String, default="")
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    tenant = relationship("PlatformTenant", back_populates="users")
    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class TeacherProfile(MasterBase):
    __tablename__ = "teacher_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String, default="")
    description = Column(String, default="")
    is_public_for_reviews = Column(Boolean, default=False)
    rating_avg = Column(Float, default=0.0)
    google_form_link = Column(String, default="")
    
    user = relationship("User", back_populates="teacher_profile")

class StudentProfile(MasterBase):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String, default="")
    parent_phone = Column(String, default="")
    
    user = relationship("User", back_populates="student_profile")

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

class PhoneOTP(MasterBase):
    __tablename__ = "phone_otps"
    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
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
    original_pdf_url = Column(String, nullable=True)
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
    layout_style = Column(String, default="default")
    
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
    low_confidence = Column(Boolean, default=False)
    
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
    band_score = Column(Float, nullable=True)
    
    # Reviewer tracking
    reviewer_type = Column(String, default="ai")  # ai, teacher
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    tenant = relationship("PlatformTenant")
    exam = relationship("MockExam", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")
    teacher = relationship("User", foreign_keys=[teacher_id])
    reviews = relationship("ReviewRequest", back_populates="attempt", cascade="all, delete-orphan")

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


class PublicClass(MasterBase):
    __tablename__ = "public_classes"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    invite_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User")
    members = relationship("ClassMember", back_populates="public_class", cascade="all, delete-orphan")

class ClassMember(MasterBase):
    __tablename__ = "class_members"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("public_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    public_class = relationship("PublicClass", back_populates="members")
    student = relationship("User")

class ReviewRequest(MasterBase):
    __tablename__ = "review_requests"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("mock_attempts.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, reviewed
    score = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    attempt = relationship("MockAttempt", back_populates="reviews")
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
class PlatformErrorLog(MasterBase):
    __tablename__ = "platform_error_logs"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, nullable=True)
    error_type = Column(String, default="ai_grading")
    message = Column(String, nullable=False)
    details = Column(String, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClassTask(MasterBase):
    __tablename__ = "class_tasks"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("public_classes.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    mock_exam_id = Column(Integer, ForeignKey("mock_exams.id"), nullable=True)
    deadline_str = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    public_class = relationship("PublicClass")
    mock_exam = relationship("MockExam")


class ClassMessage(MasterBase):
    __tablename__ = "class_messages"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("public_classes.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User")


class ClassTimelineEvent(MasterBase):
    __tablename__ = "class_timeline_events"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("public_classes.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_date_str = Column(String, nullable=False)  # Date string for easy display
    created_at = Column(DateTime, default=datetime.utcnow)


def init_master_db():
    MasterBase.metadata.create_all(bind=engine_master)
    
    from sqlalchemy import text
    with engine_master.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url STRING"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE mock_attempts ADD COLUMN reviewer_type VARCHAR DEFAULT 'ai'"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE mock_attempts ADD COLUMN teacher_id INTEGER"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE mock_exams ADD COLUMN original_pdf_url VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE mock_question_blocks ADD COLUMN layout_style VARCHAR DEFAULT 'default'"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE mock_questions ADD COLUMN low_confidence BOOLEAN DEFAULT 0"))
            conn.commit()
        except Exception:
            pass
            
    db = SessionMaster()
    try:
        from config import OWNER_EMAIL, OWNER_USERNAME, OWNER_FULL_NAME, DEFAULT_ADMIN_PASSWORD
        import auth 
    finally:
        db.close()
