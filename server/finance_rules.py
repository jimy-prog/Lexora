from database import Settings


def _get_setting_float(db, key, default):
    s = db.query(Settings).filter(Settings.key == key).first()
    if not s:
        return float(default)
    try:
        return float(s.value)
    except Exception:
        return float(default)


def get_group_epl(db, group):
    """Return effective earnings-per-lesson for a group.

    Priority:
    1) explicit per-group override
    2) per-group custom formula (price/teacher_pct)
    3) global finance defaults (standard mode)
    """
    override = float(getattr(group, "epl_override", 0) or 0)
    if override > 0:
        return round(override)

    finance_mode = (getattr(group, "finance_mode", "standard") or "standard").lower()
    group_type = getattr(group, "group_type", "group")

    default_teacher_pct = _get_setting_float(db, "teacher_pct", 40) / 100

    if finance_mode == "custom":
        price_monthly = float(getattr(group, "price_monthly", 0) or 0)
        teacher_pct = float(getattr(group, "teacher_pct", 0) or 0)
        if group_type == "individual":
            lessons = _get_setting_float(db, "rate_ind_ielts_lessons", 12)
        else:
            lessons = float((getattr(group, "lessons_per_week", 3) or 3) * (getattr(group, "weeks_per_month", 4) or 4))
        if lessons <= 0:
            lessons = 12
        return round((price_monthly / lessons) * teacher_pct) if price_monthly > 0 else 0

    # Standard mode (global defaults from settings)
    if group_type == "individual":
        monthly = _get_setting_float(db, "rate_ind_ielts_monthly", 2400000)
        lessons = _get_setting_float(db, "rate_ind_ielts_lessons", 12)
        if lessons <= 0:
            lessons = 12
        return round((monthly / lessons) * default_teacher_pct)

    group_rate = _get_setting_float(db, "rate_group_per_lesson", 25000)
    return round(group_rate)


def get_default_group_values(db, group_type):
    teacher_pct = _get_setting_float(db, "teacher_pct", 40)
    if group_type == "individual":
        price = _get_setting_float(db, "rate_ind_ielts_monthly", 2400000)
    else:
        price = _get_setting_float(db, "rate_group_monthly", 750000)

    mode_setting = db.query(Settings).filter(Settings.key == "finance_mode_default").first()
    finance_mode = (mode_setting.value if mode_setting and mode_setting.value else "standard").lower()
    if finance_mode not in {"standard", "custom"}:
        finance_mode = "standard"

    return {
        "price_monthly": float(price),
        "teacher_pct": float(teacher_pct),
        "finance_mode": finance_mode,
    }
