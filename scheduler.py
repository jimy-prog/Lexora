"""
Auto-generates lessons for ACTIVE groups only.
Future lessons = Scheduled (never Held).
Archived/paused groups = no new lessons ever.
"""
import calendar
from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import Group, Lesson, Attendance, Student, Notification

DAY_MAP = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}

def parse_schedule(s):
    slots = []
    if not s: return slots
    for part in s.split(","):
        t = part.strip().split()
        if len(t) >= 2 and t[0] in DAY_MAP:
            slots.append((DAY_MAP[t[0]], t[1]))
    return slots

def generate_month_lessons(db: Session, year: int, month: int):
    today = date.today()
    # ONLY active groups get new lessons
    groups = db.query(Group).filter(Group.status == "active").all()
    num_days = calendar.monthrange(year, month)[1]
    month_days = [date(year, month, d) for d in range(1, num_days+1)]
    created = 0

    for group in groups:
        slots = parse_schedule(group.schedule)
        for slot_day, slot_time in slots:
            for day in month_days:
                if day.weekday() == slot_day:
                    existing = db.query(Lesson).filter_by(
                        group_id=group.id, date=day, time=slot_time).first()
                    if existing:
                        # Fix any future lessons wrongly marked as Held
                        if existing.date > today and existing.status == "Held":
                            existing.status = "Scheduled"
                        continue
                    # Future = Scheduled, Past/Today = Held
                    status = "Held" if day <= today else "Scheduled"
                    lesson = Lesson(
                        group_id=group.id, date=day,
                        time=slot_time, status=status,
                        auto_generated=True
                    )
                    db.add(lesson)
                    db.flush()
                    # Auto-attendance only for past held lessons
                    if status == "Held":
                        students = db.query(Student).filter(
                            Student.group_id==group.id,
                            Student.active==True,
                            Student.archived==False
                        ).all()
                        for s in students:
                            db.add(Attendance(
                                lesson_id=lesson.id,
                                student_id=s.id,
                                status="Present"
                            ))
                    created += 1
    if created:
        db.commit()
    return created

def fix_archived_future_lessons(db: Session):
    """Remove future lessons for archived/paused groups."""
    today = date.today()
    archived = db.query(Group).filter(
        Group.status.in_(["archived","paused"])
    ).all()
    removed = 0
    for g in archived:
        future = db.query(Lesson).filter(
            Lesson.group_id == g.id,
            Lesson.date > today,
            Lesson.auto_generated == True
        ).all()
        for l in future:
            # Delete attendance first
            for a in l.attendance:
                db.delete(a)
            db.delete(l)
            removed += 1
    if removed:
        db.commit()
    return removed

def check_unmarked_lessons(db: Session):
    today = date.today()
    for lesson in db.query(Lesson).filter_by(date=today, status="Held").all():
        if lesson.group and lesson.group.status != "active": continue
        if not lesson.attendance:
            ex = db.query(Notification).filter(
                Notification.message.contains(f"[id:{lesson.id}]"),
                Notification.read==False
            ).first()
            if not ex:
                db.add(Notification(
                    message=f"Lesson not marked: {lesson.group.name} at {lesson.time or 'today'} [id:{lesson.id}]",
                    type="warning"
                ))
    db.commit()
