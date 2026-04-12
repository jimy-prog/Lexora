"""
Run this on your Mac to fix all finance calculations:
python3 fix_finance.py
"""
import os, re

base = os.path.dirname(os.path.abspath(__file__))
routers = os.path.join(base, 'routers')

def fix_file(path, replacements):
    content = open(path).read()
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✓ Fixed in {os.path.basename(path)}")
        else:
            print(f"  ✗ Pattern not found in {os.path.basename(path)}: {old[:60]}...")
    open(path, 'w').write(content)

# ── 1. finance.py ─────────────────────────────────────────────────────────────
fix_file(os.path.join(routers, 'finance.py'), [
    # Fix EPL calculation - individual always /12
    (
        "    lpm = held if held > 0 else (group.lessons_per_week * group.weeks_per_month)\n"
        "    teacher_max = group.price_monthly * group.teacher_pct\n"
        "    if group.group_type == \"individual\":\n"
        "        epl = teacher_max / lpm if lpm else 0\n"
        "    else:\n"
        "        epl = 25000  # fixed 25,000 per student per lesson\n"
        "    return {\"group\":group,\"held\":held,\"countable\":countable,\n"
        "            \"price_monthly\":group.price_monthly,\n"
        "            \"earn_per_lesson\":round(epl),\"income\":round(countable*epl)}",
        "    if group.group_type == \"individual\":\n"
        "        epl = round(group.price_monthly / 12 * group.teacher_pct)\n"
        "    else:\n"
        "        epl = 25000\n"
        "    return {\"group\":group,\"held\":held,\"countable\":countable,\n"
        "            \"price_monthly\":group.price_monthly,\n"
        "            \"earn_per_lesson\":round(epl),\"income\":round(countable*epl)}"
    ),
])

# ── 2. timetable_export.py ────────────────────────────────────────────────────
fix_file(os.path.join(routers, 'timetable_export.py'), [
    (
        "        if g.group_type == \"individual\":\n"
        "            income = round(total_countable * epl)\n"
        "        else:\n"
        "            # Group rate: fixed 25,000 per student per lesson\n"
        "            group_rate = 25000\n"
        "            income = round(total_countable * group_rate)\n"
        "            epl = group_rate  # update epl for display\n"
        "        total_income += income",
        "        if g.group_type == \"individual\":\n"
        "            epl = round(g.price_monthly / 12 * g.teacher_pct)\n"
        "            income = round(total_countable * epl)\n"
        "        else:\n"
        "            epl = 25000\n"
        "            income = round(total_countable * epl)\n"
        "        total_income += income"
    ),
])

# ── 3. monthly_report.py ──────────────────────────────────────────────────────
fix_file(os.path.join(routers, 'monthly_report.py'), [
    (
        "        if g.group_type == \"individual\":\n"
        "            epl = (g.price_monthly * g.teacher_pct / lpm) if lpm else 0\n"
        "            income = round(total_countable * epl)\n"
        "        else:\n"
        "            epl = 25000  # fixed 25,000 per student per lesson for groups\n"
        "            income = round(total_countable * epl)\n"
        "        total_income += income",
        "        if g.group_type == \"individual\":\n"
        "            epl = round(g.price_monthly / 12 * g.teacher_pct)\n"
        "        else:\n"
        "            epl = 25000\n"
        "        income = round(total_countable * epl)\n"
        "        total_income += income"
    ),
])

# ── 4. groups.py ──────────────────────────────────────────────────────────────
fix_file(os.path.join(routers, 'groups.py'), [
    (
        "    if g.group_type == \"individual\":\n"
        "        ppl = round(g.price_monthly / 12 * g.teacher_pct)  # always /12\n"
        "    else:\n"
        "        ppl = 25000  # fixed per student per lesson\n"
        "    income = round(countable * ppl)",
        "    if g.group_type == \"individual\":\n"
        "        ppl = round(g.price_monthly / 12 * g.teacher_pct)\n"
        "    else:\n"
        "        ppl = 25000\n"
        "    income = round(countable * ppl)"
    ),
    # If the old pattern is still there
    (
        "    lpm = held_this_month if held_this_month > 0 else (g.lessons_per_week * g.weeks_per_month)\n"
        "    ppl = g.price_monthly * g.teacher_pct / lpm if lpm else 0\n"
        "    income = round(countable * ppl)",
        "    if g.group_type == \"individual\":\n"
        "        ppl = round(g.price_monthly / 12 * g.teacher_pct)\n"
        "    else:\n"
        "        ppl = 25000\n"
        "    income = round(countable * ppl)"
    ),
])

# ── 5. Fix scheduler: future lessons should be Scheduled not Held ─────────────
fix_file(os.path.join(base, 'scheduler.py'), [
    (
        '                    status = "Held" if day <= today else "Scheduled"',
        '                    if day > today:\n'
        '                        status = "Scheduled"\n'
        '                    else:\n'
        '                        status = "Held"'
    ),
])

print("\n✓ All fixes applied. Restart the app:")
print("  launchctl stop com.lexora.app && launchctl start com.lexora.app")
