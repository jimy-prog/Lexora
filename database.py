from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL, DATABASE_FILE

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    schedule = Column(String, default="")
    price_monthly = Column(Float, default=750000)
    teacher_pct = Column(Float, default=0.40)
    lessons_per_week = Column(Integer, default=3)
    weeks_per_month = Column(Integer, default=4)
    color = Column(String, default="#4c6ef5")
    notes = Column(Text, default="")
    group_type = Column(String, default="group")
    status = Column(String, default="active")  # active / paused / archived
    archived_date = Column(Date, nullable=True)
    mode = Column(String, default="in-person")
    finance_mode = Column(String, default="standard")  # standard/custom
    epl_override = Column(Float, default=0)
    company_name = Column(String, default="")
    rate_type = Column(String, default="per_lesson")
    rate_amount = Column(Float, default=0)
    lesson_duration = Column(Integer, default=60)
    zoom_link = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    students = relationship("Student", back_populates="group")
    lessons = relationship("Lesson", back_populates="group")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    phone = Column(String, default="")
    parent_phone = Column(String, default="")
    email = Column(String, default="")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    stop_reason = Column(String, default="")
    notes = Column(Text, default="")
    active = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    banned_reason = Column(Text, default="")
    banned_date = Column(Date, nullable=True)
    level = Column(String, default="")
    progress_notes = Column(Text, default="")
    strengths = Column(Text, default="")
    weaknesses = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    group = relationship("Group", back_populates="students")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
    tests = relationship("TestResult", back_populates="student", cascade="all, delete-orphan")
    performance = relationship("WeeklyPerformance", back_populates="student", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    date = Column(Date, nullable=False)
    time = Column(String, default="")
    status = Column(String, default="Held")  # Held/Cancelled/Rescheduled/Holiday
    topic = Column(String, default="")
    homework = Column(String, default="")
    notes = Column(Text, default="")
    auto_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    group = relationship("Group", back_populates="lessons")
    attendance = relationship("Attendance", back_populates="lesson", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(String, default="Present")  # Present/Absent/Excused/Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    lesson = relationship("Lesson", back_populates="attendance")
    student = relationship("Student", back_populates="attendance")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    amount = Column(Float, nullable=False)
    month = Column(String, nullable=False)
    paid_date = Column(Date, nullable=True)
    method = Column(String, default="Cash")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="payments")

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    test_date = Column(Date, nullable=False)
    month = Column(String, nullable=False)
    grammar = Column(Float, nullable=True)
    vocabulary = Column(Float, nullable=True)
    activity = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    comments = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="tests")

class WeeklyPerformance(Base):
    __tablename__ = "weekly_performance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    month = Column(String, nullable=False)
    week_num = Column(Integer, nullable=False)
    grammar = Column(Integer, nullable=True)
    activity = Column(Integer, nullable=True)
    vocabulary = Column(Integer, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="performance")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    type = Column(String, default="info")
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentEvent(Base):
    __tablename__ = "student_events"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    student_name = Column(String, default="")
    phone = Column(String, default="")
    event_type = Column(String, default="note")
    source = Column(String, default="")
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, default="")
    label = Column(String, default="")
    category = Column(String, default="general")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def migrate_db():
    import sqlite3
    if DATABASE_FILE is None:
        return
    conn = sqlite3.connect(str(DATABASE_FILE))
    cur = conn.cursor()
    for table, col, coldef in [
        ("students","archived","INTEGER DEFAULT 0"),
        ("students","level","TEXT DEFAULT ''"),
        ("students","progress_notes","TEXT DEFAULT ''"),
        ("students","strengths","TEXT DEFAULT ''"),
        ("students","weaknesses","TEXT DEFAULT ''"),
        ("students","end_date","TEXT"),
        ("students","stop_reason","TEXT DEFAULT ''"),
        ("students","banned","INTEGER DEFAULT 0"),
        ("students","banned_reason","TEXT DEFAULT ''"),
        ("students","banned_date","TEXT"),
        ("lessons","time","TEXT DEFAULT ''"),
        ("lessons","homework","TEXT DEFAULT ''"),
        ("lessons","auto_generated","INTEGER DEFAULT 0"),
        ("groups","group_type","TEXT DEFAULT 'group'"),
        ("groups","status","TEXT DEFAULT 'active'"),
        ("groups","archived_date","TEXT"),
        ("groups","mode","TEXT DEFAULT 'in-person'"),
        ("groups","finance_mode","TEXT DEFAULT 'standard'"),
        ("groups","epl_override","REAL DEFAULT 0"),
        ("groups","company_name","TEXT DEFAULT ''"),
        ("groups","rate_type","TEXT DEFAULT 'per_lesson'"),
        ("groups","rate_amount","REAL DEFAULT 0"),
        ("groups","lesson_duration","INTEGER DEFAULT 60"),
        ("groups","zoom_link","TEXT DEFAULT ''"),
    ]:
        try: cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coldef}")
        except: pass
    try:
        cur.execute("UPDATE students SET group_id = NULL, active = 0 WHERE banned = 1")
    except:
        pass
    conn.commit(); conn.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_db()
    _seed_settings()
    _seed_data()

def _seed_settings():
    db = SessionLocal()
    defaults = [
        Settings(key="teacher_pct",           value="40",    label="Teacher % (default)",          category="finance"),
        Settings(key="finance_mode_default",  value="standard", label="Finance Mode (default: standard/custom)", category="finance"),
        Settings(key="lessons_per_week",       value="3",     label="Default Lessons Per Week",     category="schedule"),
        Settings(key="weeks_per_month",        value="4",     label="Default Weeks Per Month",      category="schedule"),
        Settings(key="rate_group_per_lesson",  value="25000", label="Group: Teacher Rate Per Lesson (UZS)",    category="finance"),
        Settings(key="rate_ind_ielts_monthly", value="2400000",label="Individual IELTS: Monthly Price (UZS)", category="finance"),
        Settings(key="rate_ind_ielts_lessons", value="12",    label="Individual IELTS: Lessons Per Month",    category="finance"),
        Settings(key="rate_group_monthly",     value="750000",label="Group: Monthly Price Per Student (UZS)", category="finance"),
    ]
    existing_keys = {s.key for s in db.query(Settings).all()}
    for s in defaults:
        if s.key not in existing_keys:
            db.add(s)
    db.commit()
    db.close()

def _seed_data():
    from datetime import date as dt
    db = SessionLocal()
    if db.query(Group).count() > 0:
        db.close(); return

    P, A, E, C = "Present", "Absent", "Excused", "Cancelled"

    # ── GROUPS ────────────────────────────────────────────────────────────────
    # IND Джурат: 2,400,000/month × 40% = 960,000/month teacher income
    g_jurat = Group(
        name="IND Джурат", schedule="Mon 16:00, Wed 16:00, Fri 16:00",
        price_monthly=2400000, teacher_pct=0.40, color="#4c6ef5",
        group_type="individual", status="active",
        notes="Individual. 2,400,000/month × 40% = 960,000 UZS/month to teacher")

    # CEFR Group: 750,000/month × 40% = 300,000/month teacher income
    # Active — only Фирдавс & Мубина remain after Jan
    g_cefr = Group(
        name="CEFR Group", schedule="Mon 17:30, Wed 17:30, Fri 17:30",
        price_monthly=750000, teacher_pct=0.40, color="#40c057",
        group_type="group", status="active",
        notes="750,000/month × 40% = 300,000/month teacher income")

    # IELTS New: archived March 9, 2025 (holiday = last day, group ended)
    g_inew = Group(
        name="IELTS New", schedule="Mon 14:30, Wed 14:30, Fri 14:30",
        price_monthly=750000, teacher_pct=0.40, color="#f03e3e",
        group_type="group", status="archived", archived_date=dt(2025, 3, 9),
        notes="Archived March 9, 2025. Last lessons: Mar 6. Mar 9 = holiday = group ended.")

    # IELTS Old: archived end of January 2025
    g_iold = Group(
        name="IELTS Old", schedule="Tue 15:30, Thu 15:30, Sat 15:30",
        price_monthly=750000, teacher_pct=0.40, color="#e67700",
        group_type="group", status="archived", archived_date=dt(2025, 1, 31),
        notes="Archived Jan 2025. Students left or joined IELTS New.")

    # IND Samina & Orzu: archived Jan 2025 (transferred to IELTS New)
    g_ind_so = Group(
        name="IND Samina & Orzu", schedule="Mon 16:00, Wed 16:00, Fri 16:00",
        price_monthly=750000, teacher_pct=0.40, color="#ae3ec9",
        group_type="individual", status="archived", archived_date=dt(2025, 1, 22),
        notes="Самина & Орзу transferred to IELTS New January 2025")

    # IND Ablimit: archived — came only Feb 6, then stopped
    g_ablimit = Group(
        name="IND Ablimit", schedule="Mon 19:00, Wed 19:00, Fri 19:00",
        price_monthly=2400000, teacher_pct=0.40, color="#7048e8",
        group_type="individual", status="archived", archived_date=dt(2025, 2, 7),
        notes="Came only once (Feb 6), then stopped.")

    for g in [g_jurat, g_cefr, g_inew, g_iold, g_ind_so, g_ablimit]:
        db.add(g)
    db.commit()
    for g in [g_jurat, g_cefr, g_inew, g_iold, g_ind_so, g_ablimit]:
        db.refresh(g)

    # ── STUDENTS ──────────────────────────────────────────────────────────────
    def mk(name, grp, level="B1", archived=False, start=None, end=None, reason=""):
        s = Student(
            name=name, group_id=grp.id, level=level,
            active=not archived, archived=archived,
            start_date=start or dt(2024, 11, 1),
            end_date=end, stop_reason=reason)
        db.add(s); db.flush(); return s

    # IND Джурат — active
    s_jurat = mk("Тохиров Джурат", g_jurat, "B1", start=dt(2024, 11, 4))

    # CEFR Group
    s_fird = mk("Фирдавс",  g_cefr, "B1", start=dt(2024, 12, 3))
    s_mub  = mk("Мубина",   g_cefr, "B1", start=dt(2024, 12, 22))
    s_viol = mk("Виолетта", g_cefr, "B2", archived=True,
                start=dt(2024, 12, 3), end=dt(2025, 1, 30),
                reason="Stopped attending after January 2025")
    s_djav = mk("Джавохир", g_cefr, "B2", archived=True,
                start=dt(2024, 12, 5), end=dt(2025, 1, 30),
                reason="Stopped attending after January 2025")

    # IELTS New — Настя, Вика, Мадина active until group archived Mar 9
    s_nastya   = mk("Настя",   g_inew, "B2", archived=True,
                    start=dt(2025, 1, 19), end=dt(2025, 3, 9),
                    reason="Group archived March 9, 2025")
    s_vika     = mk("Вика",    g_inew, "B2", archived=True,
                    start=dt(2025, 1, 19), end=dt(2025, 3, 9),
                    reason="Group archived March 9, 2025")
    s_madina_n = mk("Мадина",  g_inew, "B1", archived=True,
                    start=dt(2025, 1, 23), end=dt(2025, 3, 9),
                    reason="Group archived March 9, 2025")

    # IELTS New — Самина & Орзу: stopped after March 4 (- = stopped)
    s_sam  = mk("Самина", g_inew, "B1", archived=True,
                start=dt(2025, 1, 23), end=dt(2025, 3, 4),
                reason="Stopped March 2025 (transferred from IND group)")
    s_orzu = mk("Орзу",   g_inew, "B1", archived=True,
                start=dt(2025, 1, 23), end=dt(2025, 3, 4),
                reason="Stopped March 2025 (transferred from IND group)")

    # IELTS New — Назар: joined from IELTS Old Jan, no March data → stopped Feb
    s_nazar = mk("Назар", g_inew, "B1", archived=True,
                 start=dt(2025, 1, 23), end=dt(2025, 2, 27),
                 reason="No data after February 2025")

    # IELTS Old alumni
    s_munisa   = mk("Муниса",             g_iold, "B1", archived=True,
                    end=dt(2024, 12, 9),  reason="Stopped December 2024")
    s_nargiza  = mk("Наргиза",            g_iold, "B1", archived=True,
                    end=dt(2025, 1, 17),  reason="Stopped January 2025")
    s_yasmina  = mk("Ясмина",             g_iold, "B1", archived=True,
                    end=dt(2025, 1, 20),  reason="Stopped January 2025")
    s_behruz   = mk("Бехруз",             g_iold, "B1", archived=True,
                    end=dt(2025, 1, 15),  reason="Stopped January 2025")
    s_mad_old  = mk("Мадина (IELTS Old)", g_iold, "B1", archived=True,
                    end=dt(2025, 1, 24),  reason="Stopped January 2025")
    s_abdulaz  = mk("Абдулазиз",          g_iold, "B1", archived=True,
                    end=dt(2025, 1, 15),  reason="Stopped January 2025")
    s_kamila   = mk("Камила",             g_iold, "B1", archived=True,
                    end=dt(2024, 12, 27), reason="Stopped December 2024")
    s_nazar_old = mk("Назар (IELTS Old)", g_iold, "B1", archived=True,
                     end=dt(2025, 1, 24), reason="Transferred to IELTS New")

    # IND Samina & Orzu group (before transfer)
    s_sam_so  = mk("Самина (IND)",     g_ind_so, "B1", archived=True,
                   end=dt(2025, 1, 21), reason="Transferred to IELTS New")
    s_orzu_so = mk("Орзу (IND)",       g_ind_so, "B1", archived=True,
                   end=dt(2025, 1, 21), reason="Transferred to IELTS New")
    s_abd_so  = mk("Абдулазиз (IND)",  g_ind_so, "B1", archived=True,
                   end=dt(2025, 1, 21), reason="Stopped January 2025")

    # IND Ablimit — came once
    s_ablimit = mk("Ablimit", g_ablimit, "B1", archived=True,
                   start=dt(2025, 2, 6), end=dt(2025, 2, 6),
                   reason="Came only once (Feb 6), stopped")

    db.commit()

    # ── LESSON + ATTENDANCE HELPERS ───────────────────────────────────────────
    lcache = {}

    def get_or_create_lesson(grp, dstr, tstr, status="Held"):
        d = __import__('datetime').date.fromisoformat(dstr)
        key = (grp.id, d, tstr)
        if key not in lcache:
            l = Lesson(group_id=grp.id, date=d, time=tstr,
                       status=status, auto_generated=False)
            db.add(l); db.flush()
            lcache[key] = l
        return lcache[key]

    def att(grp, dstr, student, status, tstr=""):
        l = get_or_create_lesson(grp, dstr, tstr)
        if not db.query(Attendance).filter_by(
                lesson_id=l.id, student_id=student.id).first():
            db.add(Attendance(lesson_id=l.id,
                              student_id=student.id, status=status))

    def mark_holiday(grp, dstr, tstr=""):
        get_or_create_lesson(grp, dstr, tstr, status="Holiday")

    def mark_cancelled(grp, dstr, tstr=""):
        get_or_create_lesson(grp, dstr, tstr, status="Cancelled")

    # ═════════════════════════════════════════════════════════════════════════
    # IND ДЖУРАТ  (16:00)
    # Teacher income = 2,400,000 × 40% = 960,000 UZS/month (fixed)
    # ═════════════════════════════════════════════════════════════════════════
    jurat = [
        # November 2024 — 11P 1A
        ("2024-11-04",P),("2024-11-06",P),("2024-11-08",P),("2024-11-11",P),
        ("2024-11-13",P),("2024-11-15",A),("2024-11-18",P),("2024-11-20",P),
        ("2024-11-22",P),("2024-11-25",P),("2024-11-27",P),("2024-12-02",P),
        # December 2024 — 9P 3A (note: 02.12 counted in Nov above)
        ("2024-12-04",A),("2024-12-06",P),("2024-12-09",A),("2024-12-11",P),
        ("2024-12-13",P),("2024-12-16",P),("2024-12-18",P),("2024-12-20",A),
        ("2024-12-23",P),("2024-12-25",A),("2024-12-27",P),("2024-12-30",P),
        # January 2025 — 11P 1A
        ("2025-01-06",P),("2025-01-08",P),("2025-01-10",P),("2025-01-13",P),
        ("2025-01-15",P),("2025-01-17",P),("2025-01-20",P),("2025-01-22",P),
        ("2025-01-24",P),("2025-01-26",P),("2025-01-28",P),("2025-01-30",A),
        # February 2025 — 12P
        ("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),("2025-02-09",P),
        ("2025-02-11",P),("2025-02-13",P),("2025-02-16",P),("2025-02-18",P),
        ("2025-02-20",P),("2025-02-23",P),("2025-02-25",P),("2025-02-27",P),
        # March 2025 — partial (blank = future, not stopped)
        ("2025-03-02",P),("2025-03-04",P),("2025-03-06",P),
        ("2025-03-11",P),("2025-03-13",P),
    ]
    for d, s in jurat:
        att(g_jurat, d, s_jurat, s, "16:00")
    mark_holiday(g_jurat, "2025-03-09", "16:00")

    # ═════════════════════════════════════════════════════════════════════════
    # CEFR GROUP  (17:30)
    # 750,000/month × 40% = 300,000/month teacher income
    # Виолетта & Джавохир: Dec + Jan only
    # Фирдавс & Мубина: Dec through Mar
    # ═════════════════════════════════════════════════════════════════════════

    # December 2024
    # Note: (*) = first lesson joining mid-month; "-" = not yet in group
    cefr_dec_dates = [
        "2024-12-03","2024-12-05","2024-12-10","2024-12-12",
        "2024-12-15","2024-12-17","2024-12-19","2024-12-22",
        "2024-12-24","2024-12-26","2024-12-29"
    ]
    # Ensure all lessons exist
    for d in cefr_dec_dates:
        get_or_create_lesson(g_cefr, d, "17:30")

    cefr_dec = {
        # Виолетта: all 11 lessons, absent on 29.12
        s_viol: [P,P,P,P,P,P,P,P,P,P,A],
        # Фирдавс: all 11, absent on 26.12
        s_fird: [P,P,P,P,P,P,P,P,P,A,P],
        # Джавохир: joined 05.12 (*), absent 22.12 & 29.12
        s_djav: [None,P,P,P,P,P,P,A,P,P,A],
        # Мубина: joined 22.12 (*), absent 26.12
        s_mub:  [None,None,None,None,None,None,None,P,P,A,P],
    }
    for student, statuses in cefr_dec.items():
        for d, s in zip(cefr_dec_dates, statuses):
            if s is not None:
                att(g_cefr, d, student, s, "17:30")

    # January 2025 — all 4 students
    cefr_jan_dates = [
        "2025-01-05","2025-01-07","2025-01-09","2025-01-12",
        "2025-01-14","2025-01-16","2025-01-19","2025-01-21",
        "2025-01-23","2025-01-26","2025-01-28","2025-01-30"
    ]
    cefr_jan = {
        s_viol: [A,P,A,P,P,P,A,P,P,A,A,A],
        s_fird: [A,P,P,P,P,P,P,P,A,P,P,P],
        s_djav: [P,P,P,P,P,P,P,P,P,P,P,P],
        s_mub:  [P,P,P,P,P,P,P,P,P,P,A,P],
    }
    for student, statuses in cefr_jan.items():
        for d, s in zip(cefr_jan_dates, statuses):
            att(g_cefr, d, student, s, "17:30")

    # February 2025 — Фирдавс & Мубина only (Виолетта & Джавохир stopped)
    cefr_feb = {
        s_mub:  [("2025-02-02",A),("2025-02-04",P),("2025-02-06",A),
                 ("2025-02-09",P),("2025-02-11",A),("2025-02-13",P),
                 ("2025-02-16",P),("2025-02-18",P),("2025-02-20",P),
                 ("2025-02-23",P),("2025-02-27",P)],
        s_fird: [("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),
                 ("2025-02-09",P),("2025-02-11",A),("2025-02-13",P),
                 ("2025-02-16",P),("2025-02-18",P),("2025-02-20",P),
                 ("2025-02-23",A),("2025-02-25",P),("2025-02-27",P)],
    }
    for student, records in cefr_feb.items():
        for d, s in records:
            att(g_cefr, d, student, s, "17:30")

    # March 2025 — Фирдавс & Мубина, 09.03 = holiday
    cefr_mar = {
        s_mub:  [("2025-03-02",A),("2025-03-04",P),("2025-03-06",P),
                 ("2025-03-11",P),("2025-03-16",P)],
        s_fird: [("2025-03-02",P),("2025-03-04",P),("2025-03-06",P),
                 ("2025-03-11",P),("2025-03-16",P)],
    }
    for student, records in cefr_mar.items():
        for d, s in records:
            att(g_cefr, d, student, s, "17:30")
    mark_holiday(g_cefr, "2025-03-09", "17:30")

    # ═════════════════════════════════════════════════════════════════════════
    # IELTS NEW  (14:30)
    # Настя & Вика from Jan 19; Самина & Орзу joined Jan 23 (from IND group)
    # Мадина joined Jan 23; Назар joined Jan 23 (from IELTS Old)
    # Group archived March 9 (holiday = last day)
    # ═════════════════════════════════════════════════════════════════════════
    inew_jan = {
        # Настя & Вика: started Jan 19, 🟡 = Excused
        s_nastya: [("2025-01-19",P),("2025-01-21",E),("2025-01-23",P),
                   ("2025-01-26",E),("2025-01-28",P),("2025-01-30",P)],
        s_vika:   [("2025-01-19",P),("2025-01-21",E),("2025-01-23",P),
                   ("2025-01-26",E),("2025-01-28",P),("2025-01-30",P)],
        # Самина & Орзу: started Jan 23
        s_sam:    [("2025-01-23",P),("2025-01-26",E),
                   ("2025-01-28",A),("2025-01-30",A)],
        s_orzu:   [("2025-01-23",P),("2025-01-26",E),
                   ("2025-01-28",A),("2025-01-30",A)],
        # Мадина: started Jan 23 (absent first lesson)
        s_madina_n:[("2025-01-23",A),("2025-01-26",E),
                    ("2025-01-28",P),("2025-01-30",P)],
        # Назар: started Jan 23
        s_nazar:  [("2025-01-23",P),("2025-01-26",E),
                   ("2025-01-28",P),("2025-01-30",P)],
    }
    inew_feb = {
        s_sam:    [("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),
                   ("2025-02-09",A),("2025-02-11",P),("2025-02-13",P),
                   ("2025-02-16",A),("2025-02-18",P),("2025-02-20",P),
                   ("2025-02-23",P),("2025-02-25",A),("2025-02-27",P)],
        s_orzu:   [("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),
                   ("2025-02-09",A),("2025-02-11",P),("2025-02-13",P),
                   ("2025-02-16",A),("2025-02-18",P),("2025-02-20",P),
                   ("2025-02-23",P),("2025-02-25",A),("2025-02-27",P)],
        s_nastya: [("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),
                   ("2025-02-09",A),("2025-02-11",A),("2025-02-13",A),
                   ("2025-02-16",P),("2025-02-18",A),("2025-02-20",P),
                   ("2025-02-23",A),("2025-02-25",P),("2025-02-27",P)],
        s_vika:   [("2025-02-02",P),("2025-02-04",P),("2025-02-06",P),
                   ("2025-02-09",A),("2025-02-11",A),("2025-02-13",A),
                   ("2025-02-16",P),("2025-02-18",A),("2025-02-20",P),
                   ("2025-02-23",P),("2025-02-25",P),("2025-02-27",P)],
        s_madina_n:[("2025-02-02",A),("2025-02-04",P),("2025-02-06",P),
                    ("2025-02-09",P),("2025-02-11",A),("2025-02-13",A),
                    ("2025-02-16",P),("2025-02-18",P),("2025-02-20",P),
                    ("2025-02-23",P),("2025-02-25",A),("2025-02-27",P)],
        s_nazar:  [("2025-02-02",A),("2025-02-04",P),("2025-02-06",P),
                   ("2025-02-09",P),("2025-02-11",P),("2025-02-13",P),
                   ("2025-02-16",P),("2025-02-18",P),("2025-02-20",P),
                   ("2025-02-23",A),("2025-02-25",P),("2025-02-27",A)],
    }
    # March: Самина & Орзу stopped after 04.03 (- means stopped)
    # Настя, Вика, Мадина attended until group ended Mar 6 (last lesson before holiday)
    inew_mar = {
        s_sam:     [("2025-03-02",P),("2025-03-04",A)],
        s_orzu:    [("2025-03-02",P),("2025-03-04",A)],
        s_nastya:  [("2025-03-02",A),("2025-03-04",P),("2025-03-06",P)],
        s_vika:    [("2025-03-02",P),("2025-03-04",P),("2025-03-06",P)],
        s_madina_n:[("2025-03-02",P),("2025-03-04",P),("2025-03-06",P)],
    }
    for month_data in [inew_jan, inew_feb, inew_mar]:
        for student, records in month_data.items():
            for d, s in records:
                att(g_inew, d, student, s, "14:30")
    mark_holiday(g_inew, "2025-03-09", "14:30")

    # ═════════════════════════════════════════════════════════════════════════
    # IELTS OLD  (15:30) — fully archived, historical only
    # ═════════════════════════════════════════════════════════════════════════
    iold_nov = {
        s_munisa:  [("2024-11-22",P),("2024-11-25",P),("2024-11-29",A),("2024-12-02",A)],
        s_nargiza: [("2024-11-22",P),("2024-11-29",P)],
        s_yasmina: [("2024-11-22",P),("2024-11-25",P),("2024-11-29",A),("2024-12-02",A)],
        s_behruz:  [("2024-11-22",P),("2024-11-25",A),("2024-11-29",P),("2024-12-02",P)],
        s_mad_old: [("2024-11-22",P),("2024-11-25",P),("2024-11-29",A),("2024-12-02",P)],
    }
    iold_dec = {
        s_munisa:  [("2024-12-06",A),("2024-12-09",A)],
        s_nargiza: [("2024-12-06",P),("2024-12-13",P),("2024-12-20",P),
                    ("2024-12-27",P),("2024-12-30",P)],
        s_yasmina: [("2024-12-06",A),("2024-12-09",A),("2024-12-13",P),
                    ("2024-12-16",P),("2024-12-20",P),("2024-12-23",P),
                    ("2024-12-27",A),("2024-12-30",A)],
        s_behruz:  [("2024-12-06",P),("2024-12-09",P),("2024-12-13",P),
                    ("2024-12-16",P),("2024-12-20",P),("2024-12-23",P),
                    ("2024-12-27",P),("2024-12-30",A)],
        s_mad_old: [("2024-12-06",P),("2024-12-09",P),("2024-12-13",P),
                    ("2024-12-16",P),("2024-12-20",P),("2024-12-23",P),
                    ("2024-12-27",P),("2024-12-30",A)],
        s_abdulaz: [("2024-12-16",P),("2024-12-20",P),("2024-12-23",P),
                    ("2024-12-27",P),("2024-12-30",A)],
        s_kamila:  [("2024-12-27",P),("2024-12-30",A)],
    }
    iold_jan = {
        s_nargiza:  [("2025-01-06",P),("2025-01-08",P),("2025-01-10",P),
                     ("2025-01-13",P),("2025-01-15",P),("2025-01-17",P)],
        s_yasmina:  [("2025-01-06",P),("2025-01-08",A),("2025-01-10",P),
                     ("2025-01-13",P),("2025-01-17",A),("2025-01-20",P)],
        s_behruz:   [("2025-01-06",A),("2025-01-08",P),("2025-01-10",P),
                     ("2025-01-13",P),("2025-01-15",P)],
        s_mad_old:  [("2025-01-06",P),("2025-01-08",P),("2025-01-10",P),
                     ("2025-01-13",P),("2025-01-15",P),("2025-01-17",P),
                     ("2025-01-20",P),("2025-01-22",A),("2025-01-24",E)],
        s_abdulaz:  [("2025-01-06",A),("2025-01-08",A),("2025-01-10",A),
                     ("2025-01-13",A),("2025-01-15",P)],
        s_nazar_old:[("2025-01-06",P),("2025-01-08",P),("2025-01-10",P),
                     ("2025-01-13",P),("2025-01-15",P),("2025-01-17",P),
                     ("2025-01-20",A),("2025-01-22",P),("2025-01-24",E)],
    }
    for month_data in [iold_nov, iold_dec, iold_jan]:
        for student, records in month_data.items():
            for d, s in records:
                att(g_iold, d, student, s, "15:30")

    # ═════════════════════════════════════════════════════════════════════════
    # IND SAMINA & ORZU  (16:00) — archived Jan 2025
    # ═════════════════════════════════════════════════════════════════════════
    ind_so_dec = {
        s_sam_so:  [("2024-12-03",P),("2024-12-05",P),("2024-12-10",P),
                    ("2024-12-12",A),("2024-12-15",P),("2024-12-17",A),
                    ("2024-12-19",P),("2024-12-22",P),("2024-12-24",A),
                    ("2024-12-26",P),("2024-12-29",A)],
        s_orzu_so: [("2024-12-03",P),("2024-12-05",P),("2024-12-10",P),
                    ("2024-12-12",A),("2024-12-15",P),("2024-12-17",A),
                    ("2024-12-19",P),("2024-12-22",P),("2024-12-24",A),
                    ("2024-12-26",P),("2024-12-29",A)],
        s_abd_so:  [("2024-12-17",P),("2024-12-19",P),("2024-12-22",A),
                    ("2024-12-24",P),("2024-12-26",P),("2024-12-29",A)],
    }
    ind_so_jan = {
        s_sam_so:  [("2025-01-05",A),("2025-01-07",P),("2025-01-09",P),
                    ("2025-01-12",P),("2025-01-14",P),("2025-01-16",E),
                    ("2025-01-19",P),("2025-01-21",P)],
        s_orzu_so: [("2025-01-05",A),("2025-01-07",P),("2025-01-09",P),
                    ("2025-01-12",P),("2025-01-14",P),("2025-01-16",E),
                    ("2025-01-19",P),("2025-01-21",P)],
        s_abd_so:  [("2025-01-05",A),("2025-01-07",A),("2025-01-09",A),
                    ("2025-01-12",P),("2025-01-14",P),("2025-01-16",E),
                    ("2025-01-19",A),("2025-01-21",A)],
    }
    for month_data in [ind_so_dec, ind_so_jan]:
        for student, records in month_data.items():
            for d, s in records:
                att(g_ind_so, d, student, s, "16:00")

    # ═════════════════════════════════════════════════════════════════════════
    # IND ABLIMIT  (19:00) — came only once
    # ═════════════════════════════════════════════════════════════════════════
    att(g_ablimit, "2025-02-06", s_ablimit, P, "19:00")

    db.commit()

    # ── WEEKLY PERFORMANCE — February 2025 ───────────────────────────────────
    R, Y, G = 1, 2, 3
    perf_data = [
        # IELTS New students
        (s_sam,     1,R,R,R), (s_sam,     2,R,Y,R),
        (s_orzu,    1,R,Y,R), (s_orzu,    2,Y,Y,R), (s_orzu,    3,None,G,None),
        (s_nastya,  1,R,R,R), (s_nastya,  2,Y,R,Y), (s_nastya,  3,R,Y,Y),
        (s_vika,    1,Y,G,R), (s_vika,    2,G,G,G), (s_vika,    3,G,G,G),
        (s_madina_n,1,G,G,G), (s_madina_n,2,G,G,G), (s_madina_n,3,G,G,G),
        (s_nazar,   1,Y,G,R),
        # CEFR + IND students
        (s_jurat,   1,Y,G,G), (s_jurat,   2,Y,G,G), (s_jurat,   3,Y,G,Y),
        (s_mub,     1,Y,G,R), (s_mub,     2,G,G,Y), (s_mub,     3,Y,G,Y),
        (s_fird,    1,R,G,R), (s_fird,    2,Y,G,Y), (s_fird,    3,Y,G,Y),
    ]
    for student, week, gram, act, voc in perf_data:
        db.add(WeeklyPerformance(
            student_id=student.id, month="2025-02", week_num=week,
            grammar=gram, activity=act, vocabulary=voc))
    db.commit()
    db.close()
