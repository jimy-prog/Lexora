"""
Run this on your Mac to add the online router to main.py
python3 main_patch.py
"""
content = open('main.py').read()

if 'online' not in content:
    content = content.replace(
        "from routers import timetable_export\nfrom routers import holidays as holidays_router",
        "from routers import timetable_export\nfrom routers import holidays as holidays_router\nfrom routers import online as online_router"
    )
    content = content.replace(
        "          holidays_router.router,",
        "          holidays_router.router,\n          online_router.router,"
    )
    open('main.py','w').write(content)
    print("✓ main.py updated with online router")
else:
    print("— online router already in main.py")

# Add sidebar link
base = open('templates/base.html').read()
if 'online' not in base:
    base = base.replace(
        '    <a class="nav-link {% if active_page==\'waitlist\' %}active{% endif %}" href="/waitlist/">',
        '    <a class="nav-link {% if active_page==\'online\' %}active{% endif %}" href="/online/">\n      <span class="nav-icon">🌐</span> Online\n    </a>\n    <a class="nav-link {% if active_page==\'waitlist\' %}active{% endif %}" href="/waitlist/">'
    )
    open('templates/base.html','w').write(base)
    print("✓ Sidebar updated")
else:
    print("— sidebar already has online link")

print("\n✓ Done. Now run:")
print("  python3 migrate_online.py")
print("  launchctl stop com.lexora.app && launchctl start com.lexora.app")
