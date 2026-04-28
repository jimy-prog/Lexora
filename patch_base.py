import os

base_path = "/Users/jamshidmahkamov/Desktop/teacher_admin/templates/base.html"
with open(base_path, "r") as f:
    html = f.read()

# Make sidebar translucent
html = html.replace(
    """.sidebar{
  position:fixed;left:0;top:0;bottom:0;width:var(--sidebar-w);
  background:var(--bg2);
  border-right:1px solid var(--border);
  box-shadow:var(--shadow-bar);
  display:flex;flex-direction:column;z-index:200;overflow-y:auto
}""",
    """.sidebar{
  position:fixed;left:0;top:0;bottom:0;width:var(--sidebar-w);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border-right: 1px solid rgba(0,0,0,0.05);
  box-shadow: 1px 0 10px rgba(0,0,0,0.02);
  display:flex;flex-direction:column;z-index:200;overflow-y:auto;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
body.dark .sidebar {
  background: rgba(19, 22, 29, 0.7);
  border-right: 1px solid rgba(255,255,255,0.05);
}"""
)

# Nav links to pill style
html = html.replace(
    """.nav-link{
  display:flex;align-items:center;gap:10px;padding:9px 14px;margin:2px 10px;
  color:var(--text2);text-decoration:none;border-radius:999px;font-size:.82rem;font-weight:500;
  transition:background .15s,color .15s
}
.nav-link:hover{background:var(--bg3);color:var(--text)}
.nav-link.active{background:var(--accent-glow);color:var(--accent);font-weight:600}""",
    """.nav-link{
  display:flex;align-items:center;gap:10px;padding:10px 14px;margin:3px 12px;
  color:var(--text2);text-decoration:none;border-radius:10px;font-size:.85rem;font-weight:500;
  transition:all .2s cubic-bezier(0.16, 1, 0.3, 1);
}
.nav-link:hover{background:var(--bg3);color:var(--text)}
.nav-link.active{background:var(--accent);color:#fff;font-weight:600;box-shadow: 0 4px 12px var(--accent-glow); border-radius: 10px;}"""
)

# Cards to inset rounded style
html = html.replace(
    """.card{
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;box-shadow:var(--shadow-card)
}""",
    """.card{
  background:var(--bg2);border:none;border-radius:16px;
  overflow:hidden;box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
body.dark .card { box-shadow: 0 4px 24px rgba(0,0,0,0.15) }"""
)

html = html.replace(
    """.card-header{
  display:flex;align-items:center;justify-content:space-between;padding:14px 18px;
  border-bottom:1px solid var(--border);background:var(--bg3)
}""",
    """.card-header{
  display:flex;align-items:center;justify-content:space-between;padding:16px 20px;
  border-bottom:1px solid var(--border);background:transparent
}"""
)

# Inputs to softer look
html = html.replace(
    """.form-control{
  width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm);
  padding:10px 14px;font-family:var(--font-b);font-size:.85rem;color:var(--text);outline:none;
  transition:border-color .15s, box-shadow .15s;-webkit-appearance:none
}""",
    """.form-control{
  width:100%;background:var(--bg3);border:1px solid transparent;border-radius:10px;
  padding:12px 14px;font-family:var(--font-b);font-size:.85rem;color:var(--text);outline:none;
  transition:border-color .15s, box-shadow .15s, background .15s;-webkit-appearance:none;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
}
.form-control:hover{ background: var(--bg4); }"""
)

# Buttons softer layout
html = html.replace(
    """.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  padding:9px 18px;border-radius:999px;font-family:var(--font-b);font-size:.82rem;font-weight:600;
  cursor:pointer;border:1px solid transparent;text-decoration:none;transition:all .15s;white-space:nowrap
}""",
    """.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  padding:10px 20px;border-radius:10px;font-family:var(--font-b);font-size:.85rem;font-weight:600;
  cursor:pointer;border:1px solid transparent;text-decoration:none;transition:transform .2s, opacity .2s, background .2s, box-shadow .2s;white-space:nowrap
}
.btn:hover{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.btn:active{ transform: scale(0.97); box-shadow: none; }"""
)


with open(base_path, "w") as f:
    f.write(html)
print("Base CSS patched for Apple structure.")
