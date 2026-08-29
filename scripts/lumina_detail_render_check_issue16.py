"""Detail-Render-Check: Artikel-CTA (primär + sekundär) auf gerendertem HTML."""
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

problems = []

# 1. Artikel mit Potenzial-Check: primärer CTA -> /rechner, sekundär Termin + Service
html = client.get("/wissen/kosten-roi-ki-automatisierung").get_data(as_text=True)
if 'Nächster Schritt' not in html:
    problems.append("kosten-roi: kein Nächster-Schritt-Label")
if 'href="/rechner"' not in html:
    problems.append("kosten-roi: Potenzial-Check-Link fehlt")
if 'Termin vereinbaren' not in html:
    problems.append("kosten-roi: sekundärer Termin-Button fehlt")
if 'KI-Automatisierung im Überblick' not in html and 'n8n-Automatisierung im Überblick' not in html:
    problems.append("kosten-roi: Service-Link fehlt")

# 2. Artikel mit Branchenverweis: Branchenseite-Link vorhanden
html = client.get("/wissen/n8n-selbst-hosten").get_data(as_text=True)
if 'Branchenseite Handwerk' not in html:
    problems.append("n8n-selbst-hosten: Branchenseite-Link fehlt")
if 'href="/n8n-automatisierung"' not in html:
    problems.append("n8n-selbst-hosten: Nächster Schritt /n8n-automatisierung fehlt")
if 'Termin vereinbaren' not in html:
    problems.append("n8n-selbst-hosten: sekundärer Termin-Button fehlt")

# 3. Alle Artikel-Cards auf /wissen zeigen korrekte Step-Ziele
html = client.get("/wissen").get_data(as_text=True)
for needle in ["Potenzial-Check starten", "KI-Agenten im Überblick",
               "n8n-Automatisierung im Überblick", "Lokale KI im Überblick"]:
    if needle not in html:
        problems.append(f"/wissen: Step-Link '{needle}' fehlt")
for slug in ["handwerk", "kfz", "kanzleien", "immobilien"]:
    if f"/branchen/{slug}" not in html:
        problems.append(f"/wissen: Branchenkarte /branchen/{slug} fehlt")
if 'href="/automationen"' not in html:
    problems.append("/wissen: Automationen-Karte fehlt")

if problems:
    print("PROBLEME:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("DETAIL-RENDER-CHECK BESTANDEN")
