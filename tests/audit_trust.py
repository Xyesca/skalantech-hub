"""Trust-Architecture Audit — SENTINEL-Checkliste als lokaler Crawl.

Prüft gegen die laufende Flask-App (test_client):
  1. Jede öffentliche Seite rendert Footer mit Trust-Line + Legal-Links
  2. Seiten mit Verkaufsabsicht haben Autoren-/Nachweis-Elemente
  3. Alle internen Links (href) liefern 200
  4. Alle statischen Assets (src/href /static/) liefern 200
  5. Legal-Seiten: Impressum/Datenschutz/AGB/FAQ rendern
  6. Formulare haben Datenschutz-Checkbox
"""
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ── App wie in tests/test_public.py booten ────────────────────────────
for name in list(sys.modules):
    if name == "app" or name.startswith("app."):
        del sys.modules[name]

tmp = tempfile.TemporaryDirectory()
os.environ["SECRET_KEY"] = "audit-secret"
os.environ["ADMIN_PASSWORD"] = "audit-admin"
os.environ["SESSION_COOKIE_SECURE"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}/site.db"

from app import create_app  # noqa: E402
from app.seo_pages import LANDING_PAGES, LANDING_ORDER  # noqa: E402
from app.wissen import ARTICLES, ARTICLE_ORDER  # noqa: E402

app = create_app("production")
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
client = app.test_client()

# ── Seiten-Inventar ────────────────────────────────────────────────────
pages = {
    "/": "home",
    "/wissen": "wissen",
    "/faq": "legal",
    "/impressum": "legal",
    "/datenschutz": "legal",
    "/agb": "legal",
    "/nicht-vorhanden-xyz": "404",
}
for slug in LANDING_ORDER:
    pages[f"/{slug}"] = "landing"
for slug in ARTICLE_ORDER:
    pages[f"/wissen/{slug}"] = "article"

TRUST_FOOTER = ["site-footer__trust", "SSL-verschlüsselt", "Keine externen Tracker", "Keine Tracking-Cookies"]
LEGAL_LINKS = ["/impressum", "/datenschutz", "/agb"]
EXPECT = {
    "home": ["hero__trust", 'id="nachweise"', 'id="referenzen"', "Qualifikationen, die Sie prüfen können.", "Worauf Sie sich verlassen können.", "certificates_xavier_escalante.pdf"],
    "landing": ["landing-author", "Wer dahintersteht", "Xavier Escalante Castellar", "certificates_xavier_escalante.pdf", "linkedin.com/in/xyesca", "github.com/Xyesca"],
    "article": ["article-author", "Geschrieben von", "Xavier Escalante Castellar", "linkedin.com/in/xyesca"],
    "legal": ["legal-page", "legal-layout"],
    "404": ["Diese Seite gibt es nicht."],
    "wissen": ["wissen-card", "section-label"],
}

problems = []
checked_pages = 0
internal_links = {}
static_assets = {}

for path, kind in pages.items():
    resp = client.get(path, buffered=True)
    checked_pages += 1
    if resp.status_code != (404 if kind == "404" else 200):
        problems.append(f"[STATUS] {path} -> {resp.status_code} (erwartet {kind})")
        continue
    html = resp.get_data(as_text=True)

    # Footer-Trust auf JEDER Seite
    for needle in TRUST_FOOTER:
        if needle not in html:
            problems.append(f"[FOOTER] {path}: '{needle}' fehlt")
    for needle in LEGAL_LINKS:
        if needle not in html:
            problems.append(f"[LEGAL] {path}: Link '{needle}' fehlt im Footer")

    # Seiten-spezifische Trust-Elemente
    for needle in EXPECT.get(kind, []):
        if needle not in html:
            problems.append(f"[{kind.upper()}] {path}: '{needle}' fehlt")

    # Formulare: Datenschutz-Checkbox
    if "privacy" in html and 'name="privacy"' not in html:
        problems.append(f"[FORM] {path}: privacy-Referenz ohne Checkbox")

    # Interne Links + Assets sammeln
    for href in re.findall(r'(?:href|src)="([^"]+)"', html):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#", "javascript:")):
            continue
        target = href.split("#")[0]
        if target.startswith("/static/"):
            static_assets[target] = static_assets.get(target, 0) + 1
        elif target.startswith("/"):
            internal_links[target] = internal_links.get(target, 0) + 1

# ── Interne Links verifizieren ─────────────────────────────────────────
for target in sorted(internal_links):
    r = client.get(target, buffered=True)
    if r.status_code != 200:
        problems.append(f"[LINK] {target} -> {r.status_code} (von {internal_links[target]} Seiten verlinkt)")

# ── Assets verifizieren ────────────────────────────────────────────────
for target in sorted(static_assets):
    r = client.get(target, buffered=True)
    if r.status_code != 200:
        problems.append(f"[ASSET] {target} -> {r.status_code}")

# ── Report ─────────────────────────────────────────────────────────────
print(f"Geprüfte Seiten: {checked_pages}")
print(f"Interne Links:  {len(internal_links)} ({sum(internal_links.values())} Vorkommen)")
print(f"Statische Assets: {len(static_assets)} ({sum(static_assets.values())} Vorkommen)")
print()
if problems:
    print(f"PROBLEME ({len(problems)}):")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("AUDIT OK — keine Probleme gefunden.")
tmp.cleanup()
