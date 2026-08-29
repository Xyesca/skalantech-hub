"""A11y-Stichprobe für /wissen (Issue #16): aria-labelledby, Heading-Reihenfolge, Link-Texte."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["SESSION_COOKIE_SECURE"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/site.db"
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"

for name in list(sys.modules):
    if name == "app" or name.startswith("app."):
        del sys.modules[name]

from app import create_app  # noqa: E402

app = create_app("production")
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
client = app.test_client()
html = client.get("/wissen").get_data(as_text=True)

problems = []
# 1. Jede Säulen-Section hat aria-labelledby auf existierendes h2-id
import re
for pid in ["praxis-prozesse", "branchen", "datenschutz-kontrolle",
            "kosten-entscheidung", "technik-erklaert"]:
    if f'id="{pid}-title"' not in html:
        problems.append(f"h2-id {pid}-title fehlt")
    if f'aria-labelledby="{pid}-title"' not in html:
        problems.append(f"aria-labelledby {pid}-title fehlt")

# 2. Genau eine h1
h1s = re.findall(r"<h1[^>]*>", html)
if len(h1s) != 1:
    problems.append(f"h1-Anzahl: {len(h1s)} (erwartet 1)")

# 3. Keine leeren Link-Texte in den Karten
empty_links = re.findall(r'<a[^>]*>\s*<span[^>]*>[^<]*</span>\s*</a>', html)
if empty_links:
    problems.append(f"Links mit nur Icon-Span: {len(empty_links)}")

# 4. Technik-Säule ist die letzte .wissen-pillar-Section
pillar_sections = re.findall(r'<section class="wissen-pillar" id="([^"]+)"', html)
if pillar_sections and pillar_sections[-1] != "technik-erklaert":
    problems.append(f"Letzte Säule ist {pillar_sections[-1]}, erwartet technik-erklaert")
print("Säulen-Reihenfolge im DOM:", pillar_sections)

if problems:
    print("A11Y-PROBLEME:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("A11Y-STICHPROBE BESTANDEN")
