from database import StudentEvent


def log_student_event(db, student=None, event_type="note", source="", details="", name="", phone=""):
    student_name = name or (student.name if student else "")
    phone_val = phone or (student.phone if student else "")
    db.add(StudentEvent(
        student_id=student.id if student else None,
        student_name=student_name,
        phone=phone_val,
        event_type=event_type,
        source=source,
        details=details or "",
    ))
