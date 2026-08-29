"""Verifikation Issue #16 — /wissen 5-Säulen + Nächster Schritt je Artikel.

Läuft mit demselben Setup wie die Regression-Suite (production config,
Test-DB, memory-Ratelimit) und prüft die verbindlichen Kriterien:
  1. 5 Säulen in fester Reihenfolge, Technik erklkärt an letzter Stelle
  2. Jede Artikelkarte auf /wissen zeigt einen Nächsten Schritt
  3. Branchen-Säule rendert 4 Branchenkarten
  4. Potenzial-Check-Karte in Kosten & Entscheidung
  5. Jeder Artikel hat den Nächster-Schritt-Block; Ziel-URL antwortet 200
"""
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
from app.wissen import ARTICLES, PILLARS  # noqa: E402

app = create_app("production")
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
client = app.test_client()

problems = []

# ── 1. /wissen: Säulen-Reihenfolge ─────────────────────────────────────
resp = client.get("/wissen")
html = resp.get_data(as_text=True)
assert resp.status_code == 200, f"/wissen -> {resp.status_code}"

expected_titles = ["Praxis &amp; Prozesse", "Branchen", "Datenschutz &amp; Kontrolle",
                   "Kosten &amp; Entscheidung", "Technik erklärt"]
pillar_ids = ["praxis-prozesse", "branchen", "datenschutz-kontrolle",
              "kosten-entscheidung", "technik-erklaert"]
positions = [html.find(f'id="{pid}-title"') for pid in pillar_ids]
for t, p in zip(expected_titles, positions):
    if p < 0:
        problems.append(f"FALsch: Säulentitel '{t}' fehlt auf /wissen")
    else:
        # Text der Säulen-Überschrift direkt hinter dem id-Anker prüfen
        after = html[p:p + 200]
        if t not in after:
            problems.append(f"FALSCH: Säule '{t}' nicht direkt hinter id-Anker")
        print(f"OK   Säule '{t}' an Position {p}")
if -1 not in positions and positions != sorted(positions):
    problems.append("FALSCH: Säulen-Reihenfolge nicht wie vorgegeben (Technik muss letzte sein)")

# Technik darf nicht vor Kosten stehen
tech_pos = html.find('id="technik-erklaert-title"')
kosten_pos = html.find('id="kosten-entscheidung-title"')
if tech_pos < kosten_pos:
    problems.append("FALSCH: 'Technik erklärt' steht vor 'Kosten & Entscheidung' (soll letzte Säule sein)")

# ── 2. Nächster Schritt je Artikelkarte ────────────────────────────────
step_count = html.count("wissen-card__step")
print(f"OK   Nächster-Schritt-Zeilen auf /wissen: {step_count} (erwartet {len(ARTICLES)})")
if step_count < len(ARTICLES):
    problems.append(f"FALSCH: nur {step_count} Nächste-Schritte, erwartet {len(ARTICLES)}")

# ── 3. Branchen-Karten ────────────────────────────────────────────────
branch_count = html.count("Branchenseite")
print(f"OK   Branchen-Karten auf /wissen: {branch_count}")
if branch_count < 4:
    problems.append(f"FALSCH: nur {branch_count} Branchen-Karten, erwartet 4")

# ── 4. Potenzial-Check-Karte ───────────────────────────────────────────
if html.count("Potenzial-Check") < 1:
    problems.append("FALSCH: Potenzial-Check-Karte fehlt in 'Kosten & Entscheidung'")

# ── 5. Artikel: Nächster Schritt + Ziel-URL antwortet 200 ──────────────
for slug, article in ARTICLES.items():
    r = client.get(f"/wissen/{slug}")
    ah = r.get_data(as_text=True)
    if r.status_code != 200:
        problems.append(f"FALSCH: /wissen/{slug} -> {r.status_code}")
        continue
    if "Nächster Schritt" not in ah:
        problems.append(f"FALSCH: /wissen/{slug} ohne 'Nächster Schritt'-Block")
        continue
    ns = article.get("next_step")
    if ns is None:
        problems.append(f"FALSCH: {slug} hat kein next_step")
        continue
    # Ziel-URL aus dem gerenderten Block extrahieren (erster .button--accent href)
    import re
    m = re.search(r'class="button button--accent" href="([^"]+)"', ah)
    if not m:
        problems.append(f"FALSCH: {slug}: kein .button--accent Nächster-Schritt-Link")
        continue
    target = m.group(1)
    tr = client.get(target)
    status = tr.status_code
    print(f"OK   {slug}: Nächster Schritt [{ns['kind']}] -> {target} ({status})")
    if status != 200:
        problems.append(f"FALSCH: {slug} Nächster-Schritt-Ziel {target} -> {status}")

# ── Fazit ──────────────────────────────────────────────────────────────
print()
if problems:
    print("PROBLEME:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("ALLE PRÜFUNGEN BESTANDEN — /wissen 5-Säulen + Nächster Schritt OK")
