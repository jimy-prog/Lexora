from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import Session, relationship
from datetime import datetime
import os, shutil
from database import get_db, Base, Group

router = APIRouter(prefix="/courses")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "./uploads/course_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Models ────────────────────────────────────────────────────────────────────
class Course(Base):
    __tablename__ = "courses"
    __table_args__ = {"extend_existing": True}
    id          = Column(Integer, primary_key=True)
    name        = Column(String, nullable=False)
    description = Column(Text, default="")
    duration    = Column(String, default="")   # "1-2 months"
    target      = Column(String, default="")   # "A2 → B1"
    color       = Column(String, default="#4c6ef5")
    order_num   = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
    weeks       = relationship("CourseWeek", back_populates="course",
                               order_by="CourseWeek.week_num", cascade="all, delete-orphan")

class CourseWeek(Base):
    __tablename__ = "course_weeks"
    __table_args__ = {"extend_existing": True}
    id          = Column(Integer, primary_key=True)
    course_id   = Column(Integer, ForeignKey("courses.id"))
    week_num    = Column(Integer, nullable=False)
    title       = Column(String, default="")
    grammar_focus = Column(Text, default="")
    created_at  = Column(DateTime, default=datetime.utcnow)
    course      = relationship("Course", back_populates="weeks")
    lessons     = relationship("CourseLessonTemplate", back_populates="week",
                               order_by="CourseLessonTemplate.day_num", cascade="all, delete-orphan")

class CourseLessonTemplate(Base):
    __tablename__ = "course_lesson_templates"
    __table_args__ = {"extend_existing": True}
    id           = Column(Integer, primary_key=True)
    week_id      = Column(Integer, ForeignKey("course_weeks.id"))
    day_num      = Column(Integer, nullable=False)   # 1, 2, 3
    title        = Column(String, default="")
    objectives   = Column(Text, default="")
    in_lesson    = Column(Text, default="")   # bullet points
    homework     = Column(Text, default="")
    grammar_note = Column(Text, default="")
    file_path    = Column(String, default="")
    file_name    = Column(String, default="")
    created_at   = Column(DateTime, default=datetime.utcnow)
    week         = relationship("CourseWeek", back_populates="lessons")

class GroupCourseProgress(Base):
    __tablename__ = "group_course_progress"
    __table_args__ = {"extend_existing": True}
    id                   = Column(Integer, primary_key=True)
    group_id             = Column(Integer, ForeignKey("groups.id"))
    course_id            = Column(Integer, ForeignKey("courses.id"))
    current_week         = Column(Integer, default=1)
    current_day          = Column(Integer, default=1)
    started_date         = Column(Date, nullable=True)
    notes                = Column(Text, default="")
    created_at           = Column(DateTime, default=datetime.utcnow)



# ── Seed helper ───────────────────────────────────────────────────────────────
def seed_courses(db: Session):
    if db.query(Course).count() > 0:
        return

    # ── PRE-IELTS ─────────────────────────────────────────────────────────────
    pre = Course(name="Pre-IELTS", description="Prepares students linguistically and strategically for IELTS. Covers core GE grammar, IELTS-style tasks, academic vocabulary, writing & speaking foundations.",
                 duration="1–2 months", target="A2 → B1 / weak B1", color="#40c057", order_num=1)
    db.add(pre); db.flush()

    pre_weeks = [
        (1, "Sentence Basics & Word Order",
         "Subject–verb–object order · Basic sentence types · Common word order errors",
         [("Day 1 — Listening + Grammar",
           "Article & Vocab (20min) · Listening BC intro to question types · Speaking support & discussion (20min) · Grammar focus (20min)",
           "Article + Vocab · Listening BC · Grammar worksheet"),
          ("Day 2 — Reading + Vocabulary",
           "Article & Vocab · Reading BC intro to question types · Vocabulary work & worksheet · Grammar in IELTS unit",
           "Article + Vocab · Reading BC · Vocab usage worksheet"),
          ("Day 3 — Writing + Speaking + Test",
           "Article & Vocab (20min) · Writing skills · Speaking skills · Week Test",
           "Article + Vocab · Short writing task · Speaking recording")]),
        (2, "Core Tenses — Control not theory",
         "Present simple · Present continuous · Past simple",
         [("Day 1 — Listening + Grammar",
           "Article & Vocab (20min) · Listening BC · Speaking support · Grammar: Core Tenses",
           "Article + Vocab · Listening BC · Grammar worksheet"),
          ("Day 2 — Reading + Vocabulary",
           "Article & Vocab · Reading BC · Vocabulary worksheet · Grammar unit",
           "Article + Vocab · Reading BC · Vocab worksheet"),
          ("Day 3 — Writing + Speaking + Test",
           "Article & Vocab · Writing skills · Speaking skills · Week Test",
           "Article + Vocab · Short writing task · Speaking recording")]),
        (3, "Future Forms & Intentions",
         "will vs going to · Present continuous for future · Time expressions",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Future Forms", "Article + Vocab · Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Article + Vocab · Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing · Speaking · Week Test", "Article + Vocab · Writing task · Speaking recording")]),
        (4, "Expanding Sentences",
         "Coordinating conjunctions (and/but/so/because) · Basic complex sentences · Sentence linking",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Expanding Sentences", "Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing · Speaking · Week Test", "Writing task · Speaking recording")]),
        (5, "Comparison & Description",
         "Comparatives & superlatives · as…as / more/less · Descriptive adjectives",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Comparison", "Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing (describing charts intro) · Speaking · Week Test", "Writing task · Speaking recording")]),
        (6, "Modals & Functions",
         "Ability: can/could · Advice: should · Obligation: must/have to",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Modals", "Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing · Speaking · Week Test", "Writing task · Speaking recording")]),
        (7, "Conditionals — Basic Control",
         "Zero conditional · First conditional · Basic form, no theory overload",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Conditionals", "Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing · Speaking · Week Test", "Writing task · Speaking recording")]),
        (8, "Passive Voice & Focus",
         "Passive in present & past · When passive is used · Active vs passive choice",
         [("Day 1", "Article & Vocab · Listening BC · Speaking · Grammar: Passive Voice", "Listening · Grammar worksheet"),
          ("Day 2", "Article & Vocab · Reading BC · Vocabulary · Grammar unit", "Reading · Vocab worksheet"),
          ("Day 3", "Article & Vocab · Writing (process description) · Speaking · Week Test", "Writing task · Speaking recording")]),
        (9, "Articles & Determiners (Extension)",
         "a/an/the · some/any/most/many",
         [("Day 1", "Article & Vocab · Listening · Speaking · Grammar: Articles", "Listening · Grammar"),
          ("Day 2", "Article & Vocab · Reading · Vocabulary · Grammar unit", "Reading · Vocab"),
          ("Day 3", "Article & Vocab · Writing · Speaking · Week Test", "Writing · Speaking recording")]),
        (10, "Error Awareness & Review (Extension)",
         "Common learner mistakes · Self-correction habits · Mixed grammar revision",
         [("Day 1", "Article & Vocab · Listening · Speaking · Error review", "Listening · Grammar review"),
          ("Day 2", "Article & Vocab · Reading · Vocabulary · Error correction", "Reading · Vocab"),
          ("Day 3", "Article & Vocab · Final writing task · Speaking · Final Test", "Writing · Speaking recording")]),
    ]
    for wnum, wtitle, grammar, days in pre_weeks:
        w = CourseWeek(course_id=pre.id, week_num=wnum, title=wtitle, grammar_focus=grammar)
        db.add(w); db.flush()
        for dnum, (dtitle, objectives, hw) in enumerate(days, 1):
            db.add(CourseLessonTemplate(week_id=w.id, day_num=dnum, title=dtitle,
                                        objectives=objectives, homework=hw))

    # ── IELTS ─────────────────────────────────────────────────────────────────
    ielts = Course(name="IELTS", description="Core IELTS training covering all sections, question types, and skills needed for target band score. Two internal stages: Orientation & Training → Practice & Strategy.",
                   duration="2 months", target="B1+ → B2 / Band 5.5–6.5", color="#4c6ef5", order_num=2)
    db.add(ielts); db.flush()

    ielts_weeks = [
        (1, "IELTS Orientation + Stage 1 begins",
         "Sentence Control & Accuracy · Simple vs compound vs complex sentences · Fragments and run-ons",
         "Listening: Matching (W1) · Reading: Summary Completion (W1) · Speaking: Part 1 (W1) · Writing Task 1: Bar chart (W1) · Writing Task 2: Intro + essay structure (W1)"),
        (2, "Skills foundation",
         "Tense Control for Academic Writing · Present simple / Past simple / Present perfect",
         "Listening: Multiple Choice (W2) · Reading: True/False/Not Given (W2) · Writing Task 1: Line Graph (W2) · Writing Task 2: Opinion personal viewpoint (W2)"),
        (3, "All skills — new question types",
         "Comparison & Degree · Comparatives/superlatives · slightly/significantly + comparative · by contrast/whereas/while",
         "Listening: Note Completion + Form + Diagram + Short Answer + Table (W3) · Reading: Matching Sentence Endings + Note/Table/Form (W3) · Speaking: Part 2 (W3) · Writing Task 1: Table chart (W3) · Writing Task 2: Opinion Discussion (W3) · Preview Test W3–W4"),
        (4, "Stage 2 begins — real practice",
         "Complex Sentences & Linking · Subordinating conjunctions · Relative clauses · Reason/contrast clauses",
         "Listening: Listening Preview Test continues (W4) · Reading: Multiple Choice 1&2 (W4) · Speaking: Part 3 (W4) · Writing Task 1: Map (W4) · Writing Task 2: Opinion agree/disagree (W4)"),
        (5, "Strategy + timing",
         "Conditionals for Arguments · Zero/First/Second conditional",
         "Listening: Map/Plan labelling (W5) · Reading: Matching Information + Sentence Completion (W5) · Writing Task 1: Multiple graphs + Pie chart (W5) · Writing Task 2: Problem/Solution (W5)"),
        (6, "Advanced question types",
         "Passive Voice IELTS Style · Passive forms across tenses · When passive is appropriate",
         "Listening: Multiple Choice 2nd type (W6) · Reading: Yes/No/Not Given (W6) · Writing Task 1: Preview test (W6) · Writing Task 2: Cause/Effect (W6)"),
        (7, "Polishing + self-correction",
         "Modality & Hedging · may/might/could/tend to · Softening claims · Avoiding absolute language",
         "Listening: Sentence Completion (W7) · Reading: Short Answer + Name Matching (W7) · Writing Task 1: Process diagram (W7) · Writing Task 2: Evaluate (W7)"),
        (8, "Review + Mock tests",
         "Error Correction & Band Polishing · Common IELTS grammar mistakes · Self-editing techniques",
         "Listening: Review Test (W8) · Reading: Matching Headings (W8) · Writing Task 1: Review Test (W8) · Writing Task 2: Review Test (W8) · Full Mock Test"),
    ]
    ielts_lesson_templates = {
        "Day 1": ("Day 1 — Listening + Writing Task 2 + Grammar",
                  "Article retell + vocab (20min) · Listening ONE question type explanation · Listening practice same type · Writing Task 2: ONE question type explanation",
                  "Listening practice same type · Write Task 2 same question type · Article + vocab"),
        "Day 2": ("Day 2 — Reading + Speaking + Vocabulary",
                  "Article retell + vocab (20min) · Reading: ONE type explanation · Reading practice same type · Speaking: ONE part only explanation + short practice",
                  "Reading practice · Speaking recording · Article + vocab"),
        "Day 3": ("Day 3 — Writing Task 1 + Grammar + Check",
                  "Article retell + vocab (20min) · Writing Task 1: ONE type explanation · Grammar for writing targeted · Short weekly check",
                  "Task 1 writing · Article + vocab"),
    }
    for wnum, wtitle, grammar, week_content in ielts_weeks:
        w = CourseWeek(course_id=ielts.id, week_num=wnum, title=wtitle, grammar_focus=grammar)
        db.add(w); db.flush()
        for dnum, day_key in enumerate(["Day 1", "Day 2", "Day 3"], 1):
            dtitle, obj_base, hw = ielts_lesson_templates[day_key]
            full_obj = obj_base + f"\n\nWeek {wnum} focus:\n{week_content}"
            db.add(CourseLessonTemplate(week_id=w.id, day_num=dnum, title=dtitle,
                                        objectives=full_obj, homework=hw, grammar_note=grammar))

    # ── INTENSIVE ─────────────────────────────────────────────────────────────
    intensive = Course(name="Intensive", description="Final stage. Pressure + refinement. Mock tests, deep analysis, individual weak-point focus. No explanations — only repetition, correction, speed, accuracy.",
                       duration="1 month+", target="B2 → C1 / Band 6–7.5", color="#f03e3e", order_num=3)
    db.add(intensive); db.flush()

    int_weeks = [
        (1, "Mock Test Week 1 + Error Log Setup",
         "Article retell upgrade · 20 Cambridge words (2nd 350) · Paraphrasing + collocations",
         [("Day 1 — Mock + Analysis",
           "Article retell C1–C2 level · 20 new Cambridge words active usage · Full Listening test under exam conditions · Error log review",
           "Full Reading test · Error log completion · Article + vocab"),
          ("Day 2 — Writing + Speaking drill",
           "Article retell · 20 words · Writing Task 1 timed rewrite · Speaking Part 2 fluency drill",
           "Task 2 writing timed · Speaking recording Part 3 · Article + vocab"),
          ("Day 3 — Deep analysis + Speaking mock",
           "Article retell · 20 words · Error analysis from week tests · Speaking mock interview · Individual weak-point focus",
           "Rewrite corrected task · Vocab revision · Article + vocab")]),
        (2, "Mock Test Week 2 + Speed Training",
         "Advanced paraphrasing under pressure · Vocabulary upgrading topic-based · Complex sentences/conditionals/passive",
         [("Day 1 — Full Mock",
           "Article retell · 20 words · Full Listening + Reading test under conditions · Strict timing",
           "Error log update · Reading review · Article + vocab"),
          ("Day 2 — Writing band analysis",
           "Article retell · 20 words · Band analysis of student writing · Self-correction techniques · Writing Task 1 rewrite",
           "Task 2 rewrite Band 7 target · Article + vocab"),
          ("Day 3 — Speaking + Weak point",
           "Article retell · 20 words · Speaking: abstract questions Part 3 · Individual correction session",
           "Speaking recording · Vocab collocations · Article + vocab")]),
        (3, "Mock Test Week 3 + Refinement",
         "Coherence & cohesion · Task response perfection · Examiner-style feedback",
         [("Day 1 — Full Mock",
           "Article retell · 20 words · Full test simulation · Error log",
           "Error log · Review weak sections · Article + vocab"),
          ("Day 2 — Writing perfection",
           "Article retell · 20 words · Examiner-style feedback on writing · Band 7–8 vocabulary upgrade",
           "Timed writing task · Self-correction · Article + vocab"),
          ("Day 3 — Final mock interview",
           "Article retell · 20 words · Speaking mock interview examiner-style correction · Natural language focus",
           "Speaking recording · Fluency drill · Article + vocab")]),
        (4, "Final Week — Exam Readiness",
         "Final error elimination · Stability under pressure · Exam-day strategy",
         [("Day 1 — Full Mock Final",
           "Article retell · 20 words · Final full mock test · Strict conditions",
           "Error log final review · Article + vocab"),
          ("Day 2 — Final analysis",
           "Article retell · 20 words · Final writing analysis · Last corrections",
           "Final writing rewrite · Article + vocab"),
          ("Day 3 — Pre-exam session",
           "Article retell · 20 words · Confidence session · Exam strategy review · Speaking final drill",
           "Light reading · Speaking recording · Rest")]),
    ]
    for wnum, wtitle, grammar, days in int_weeks:
        w = CourseWeek(course_id=intensive.id, week_num=wnum, title=wtitle, grammar_focus=grammar)
        db.add(w); db.flush()
        for dnum, (dtitle, objectives, hw) in enumerate(days, 1):
            db.add(CourseLessonTemplate(week_id=w.id, day_num=dnum, title=dtitle,
                                        objectives=objectives, homework=hw, grammar_note=grammar))

    db.commit()

# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/")
def courses_list(request: Request, db: Session = Depends(get_db)):
    seed_courses(db)
    courses = db.query(Course).order_by(Course.order_num).all()
    groups  = db.query(Group).filter(Group.status == "active").all()
    progress = db.query(GroupCourseProgress).all()
    prog_map = {(p.group_id, p.course_id): p for p in progress}
    return templates.TemplateResponse("courses.html", {
        "request": request, "courses": courses,
        "groups": groups, "prog_map": prog_map,
        "active_page": "courses"
    })

@router.get("/{cid}")
def course_detail(cid: int, request: Request, db: Session = Depends(get_db)):
    course  = db.query(Course).get(cid)
    groups  = db.query(Group).filter(Group.status == "active").all()
    progress= db.query(GroupCourseProgress).filter_by(course_id=cid).all()
    prog_map= {p.group_id: p for p in progress}
    return templates.TemplateResponse("course_detail.html", {
        "request": request, "course": course,
        "groups": groups, "prog_map": prog_map,
        "active_page": "courses"
    })

@router.post("/{cid}/assign-group")
def assign_group(cid: int, group_id: int = Form(...), db: Session = Depends(get_db)):
    from datetime import date
    existing = db.query(GroupCourseProgress).filter_by(
        course_id=cid, group_id=group_id).first()
    if not existing:
        db.add(GroupCourseProgress(course_id=cid, group_id=group_id,
                                   current_week=1, current_day=1,
                                   started_date=date.today()))
        db.commit()
    return RedirectResponse(f"/courses/{cid}", status_code=303)

@router.post("/{cid}/progress/{gid}")
def update_progress(cid: int, gid: int,
                    week: int = Form(...), day: int = Form(...),
                    db: Session = Depends(get_db)):
    p = db.query(GroupCourseProgress).filter_by(
        course_id=cid, group_id=gid).first()
    if p:
        p.current_week = week
        p.current_day  = day
        db.commit()
    return RedirectResponse(f"/courses/{cid}", status_code=303)

@router.post("/lesson/{lid}/upload")
async def upload_file(lid: int, file: UploadFile = File(...),
                      db: Session = Depends(get_db)):
    lesson = db.query(CourseLessonTemplate).get(lid)
    if lesson and file.filename:
        safe_name = f"{lid}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, safe_name)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        lesson.file_path = path
        lesson.file_name = file.filename
        db.commit()
    return RedirectResponse(f"/courses/{lesson.week.course_id}", status_code=303)
