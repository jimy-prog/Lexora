import os
import re

settings_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/templates/settings_page.html"
with open(settings_path, "r") as f:
    html = f.read()

# Replace styles
old_style_block = """{% block extra_styles %}
<style>
.stab-bar{display:flex;gap:0;border-bottom:2px solid var(--border);margin-bottom:28px;overflow-x:auto}
.stab{display:inline-block;padding:12px 20px;font-size:.82rem;font-weight:500;color:var(--text3);border-bottom:2px solid transparent;margin-bottom:-2px;cursor:pointer;text-decoration:none;transition:all .15s;font-family:var(--font-b);white-space:nowrap}
.stab:hover{color:var(--text)}
.stab.on{color:var(--accent);border-bottom-color:var(--accent)}
.tp{display:none}.tp.on{display:block}"""

new_style_block = """{% block extra_styles %}
<style>
.settings-container { display:flex; flex-direction: row; gap: 32px; align-items: flex-start; }
.settings-nav { width: 240px; flex-shrink: 0; padding: 0px;}
.settings-nav-header { font-size: .65rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .08em; margin-bottom: 12px; padding: 0 10px; }
.nav-st { display:flex; align-items:center; gap: 10px; padding: 10px 14px; color: var(--text2); text-decoration: none; border-radius: 12px; font-size: .85rem; font-weight: 500; transition: all .2s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 4px; }
.nav-st:hover { background: var(--bg3); color: var(--text); }
.nav-st.active { background: var(--accent); color: #fff; font-weight: 600; box-shadow: 0 4px 12px var(--accent-glow); }
.settings-content { flex: 1; min-width: 0; }
.tp { display: none; margin-bottom: 0px; }
.tp.on { display: block; animation: fade-in 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fade-in { 0% { opacity: 0; transform: translateY(6px); } 100% { opacity: 1; transform: translateY(0); } }
@media(max-width: 768px) { .settings-container{ flex-direction: column; gap: 20px; } .settings-nav{ width: 100%; display: flex; flex-wrap: wrap; gap: 4px; padding: 0; } .nav-st{ padding: 8px 12px; margin-bottom: 0;} .settings-nav-header{ width: 100%; } }"""

html = html.replace(old_style_block, new_style_block)

# Replace stab-bar
old_tabs = """<!-- Tab bar -->
<div class="stab-bar">
  <a class="stab {% if tab=='profile' or not tab %}on{% endif %}" href="/profile/?tab=profile">👤 Profile</a>
  <a class="stab {% if tab=='appearance' %}on{% endif %}" href="/profile/?tab=appearance">🎨 Appearance</a>
  <a class="stab {% if tab=='finance' %}on{% endif %}" href="/profile/?tab=finance">💰 Finance Rates</a>
  <a class="stab {% if tab=='security' %}on{% endif %}" href="/profile/?tab=security">🔐 Security</a>
  <a class="stab {% if tab=='system' %}on{% endif %}" href="/profile/?tab=system">🔧 System</a>
</div>"""

new_tabs = """<!-- Split Layout -->
<div class="settings-container">
  <div class="settings-nav">
    <div class="settings-nav-header">Preferences</div>
    <a class="nav-st {% if tab=='profile' or not tab %}active{% endif %}" href="/profile/?tab=profile"><span class="icon">👤</span> General Profile</a>
    <a class="nav-st {% if tab=='appearance' %}active{% endif %}" href="/profile/?tab=appearance"><span class="icon">🎨</span> Appearance</a>
    <a class="nav-st {% if tab=='finance' %}active{% endif %}" href="/profile/?tab=finance"><span class="icon">💰</span> Billing & Rates</a>
    <a class="nav-st {% if tab=='security' %}active{% endif %}" href="/profile/?tab=security"><span class="icon">🔐</span> Security</a>
    <a class="nav-st {% if tab=='system' %}active{% endif %}" href="/profile/?tab=system"><span class="icon">🔧</span> System Admin</a>
  </div>
  
  <div class="settings-content">"""

html = html.replace(old_tabs, new_tabs)

# Close the new divs at the bottom before {% endblock %}
if "</div>\n</div>\n\n{% endblock %}" not in html:
    html = html.replace(
        "</div>\n\n{% endblock %}",
        "</div>\n\n  </div> <!-- end settings-content -->\n</div> <!-- end settings-container -->\n\n{% endblock %}"
    )

with open(settings_path, "w") as f:
    f.write(html)
print("Settings patched for Apple structure.")
