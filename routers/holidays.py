from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, DateTime
from sqlalchemy.orm import Session
from datetime import datetime, date
from database import get_db, Base

router = APIRouter(prefix="/holidays")
templates = Jinja2Templates(directory="templates")

class Holiday(Base):
    __tablename__ = "holidays"
    __table_args__ = {"extend_existing": True}
    id          = Column(Integer, primary_key=True)
    date        = Column(Date, nullable=False)
    name        = Column(String, nullable=False)
    name_ru     = Column(String, default="")
    editable    = Column(Boolean, default=True)
    lesson_held = Column(Boolean, default=False)  # teacher can override
    notes       = Column(Text, default="")
    created_at  = Column(DateTime, default=datetime.utcnow)



UZ_HOLIDAYS_2025_2026 = [
    # 2025
    (date(2025,1,1),   "New Year's Day",          "Янги йил"),
    (date(2025,3,8),   "International Women's Day","Халқаро хотин-қизлар куни"),
    (date(2025,3,21),  "Navruz",                  "Навруз байрами"),
    (date(2025,3,30),  "Ramazon Hayit",           "Рамазон ҳайити"),
    (date(2025,3,31),  "Ramazon Hayit (2nd day)", "Рамазон ҳайити (2-кун)"),
    (date(2025,5,9),   "Day of Remembrance",      "Хотира ва қадрлаш куни"),
    (date(2025,6,6),   "Qurbon Hayit",            "Қурбон ҳайити"),
    (date(2025,6,7),   "Qurbon Hayit (2nd day)",  "Қурбон ҳайити (2-кун)"),
    (date(2025,9,1),   "Independence Day",        "Мустақиллик куни"),
    (date(2025,10,1),  "Teacher's Day",           "Ўқитувчи ва мураббийлар куни"),
    (date(2025,12,8),  "Constitution Day",        "Конституция куни"),
    (date(2025,12,31), "New Year's Eve",          "Янги йил арафаси"),
    # 2026
    (date(2026,1,1),   "New Year's Day",          "Янги йил"),
    (date(2026,1,2),   "New Year Holiday",        "Янги йил (қўшимча)"),
    (date(2026,3,8),   "International Women's Day","Халқаро хотин-қизлар куни"),
    (date(2026,3,9),   "Women's Day (transfer)",  "8 март (кўчирилган)"),
    (date(2026,3,19),  "Ramazon Hayit",           "Рамазон ҳайити"),
    (date(2026,3,20),  "Ramazon Hayit (2nd day)", "Рамазон ҳайити (2-кун)"),
    (date(2026,3,21),  "Navruz",                  "Навруз байрами"),
    (date(2026,3,23),  "Navruz (transfer)",       "Навруз (кўчирилган)"),
    (date(2026,5,9),   "Day of Remembrance",      "Хотира ва қадрлаш куни"),
    (date(2026,5,11),  "Remembrance Day (transfer)","Хотира куни (кўчирилган)"),
    (date(2026,5,27),  "Qurbon Hayit",            "Қурбон ҳайити"),
    (date(2026,5,28),  "Qurbon Hayit (2nd day)",  "Қурбон ҳайити (2-кун)"),
    (date(2026,5,29),  "Qurbon Hayit (3rd day)",  "Қурбон ҳайити (3-кун)"),
    (date(2026,5,30),  "Qurbon Hayit (4th day)",  "Қурбон ҳайити (4-кун)"),
    (date(2026,8,29),  "Independence Day",        "Мустақиллик куни"),
    (date(2026,8,31),  "Independence Day (extra)","Мустақиллик (қўшимча)"),
    (date(2026,9,1),   "Independence Day",        "Мустақиллик куни"),
    (date(2026,10,1),  "Teacher's Day",           "Ўқитувчи ва мураббийлар куни"),
    (date(2026,12,8),  "Constitution Day",        "Конституция куни"),
    (date(2026,12,31), "New Year's Eve",          "Янги йил арафаси"),
]

def seed_holidays(db):
    if db.query(Holiday).count() > 0:
        return
    for d, name, name_ru in UZ_HOLIDAYS_2025_2026:
        db.add(Holiday(date=d, name=name, name_ru=name_ru,
                       editable=True, lesson_held=False))
    db.commit()

def get_holidays_dict(db):
    """Returns {date: Holiday} for quick lookup"""
    seed_holidays(db)
    return {h.date: h for h in db.query(Holiday).all()}

@router.get("/")
def holidays_page(request: Request, db: Session = Depends(get_db)):
    seed_holidays(db)
    holidays = db.query(Holiday).order_by(Holiday.date).all()
    return templates.TemplateResponse("holidays.html", {
        "request": request, "holidays": holidays,
        "active_page": "settings"
    })

@router.post("/{hid}/toggle-lesson")
def toggle_lesson(hid: int, db: Session = Depends(get_db)):
    h = db.query(Holiday).get(hid)
    if h: h.lesson_held = not h.lesson_held; db.commit()
    return RedirectResponse("/holidays/", status_code=303)

@router.post("/add")
def add_holiday(
    date_str: str = Form(...), name: str = Form(...),
    db: Session = Depends(get_db)
):
    db.add(Holiday(date=date.fromisoformat(date_str), name=name, editable=True))
    db.commit()
    return RedirectResponse("/holidays/", status_code=303)

@router.post("/{hid}/delete")
def delete_holiday(hid: int, db: Session = Depends(get_db)):
    h = db.query(Holiday).get(hid)
    if h: db.delete(h); db.commit()
    return RedirectResponse("/holidays/", status_code=303)
