"""Live-Audit gegen den deployed Container (http://127.0.0.1:5000).

Nutzung: python tests/audit_live.py  (läuft gegen den laufenden Container)
"""
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"

# Alle Seiten, die es geben muss (aus dem Repo-Inventar)
pages = [
    "/", "/wissen", "/faq", "/impressum", "/datenschutz", "/agb",
    "/it-infrastruktur", "/ki-integration", "/ki-automatisierung", "/ki-agenten",
    "/n8n-automatisierung", "/lokale-ki",
    "/wissen/was-ist-ein-ki-agent", "/wissen/n8n-selbst-hosten",
    "/wissen/lokale-ki-vs-cloud-ki", "/wissen/n8n-vs-power-automate",
    "/wissen/welche-prozesse-ki-automatisierung", "/wissen/rag-wissensassistenten",
    "/wissen/kosten-roi-ki-automatisierung",
    "/gibt-es-nicht",
]

TRUST_FOOTER = ["site-footer__trust", "SSL-verschlüsselt", "Keine externen Tracker"]
LEGAL_LINKS = ["/impressum", "/datenschutz", "/agb"]

problems = []
checked = 0
for path in pages:
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as resp:
            code = resp.status
            html = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        code = e.code
        html = ""
    except Exception as e:
        code = f"ERR:{type(e).__name__}"
        html = ""
    checked += 1
    expected = 404 if path == "/gibt-es-nicht" else 200
    if code != expected:
        problems.append(f"[STATUS] {path} -> {code}")
        continue
    if html:
        for needle in TRUST_FOOTER:
            if needle not in html:
                problems.append(f"[FOOTER] {path}: '{needle}' fehlt")
        for needle in LEGAL_LINKS:
            if needle not in html:
                problems.append(f"[LEGAL] {path}: Link '{needle}' fehlt")
    if path == "/":
        for needle in ['id="nachweise"', 'id="referenzen"', "hero__trust", "Qualifikationen, die Sie prüfen können."]:
            if needle not in html:
                problems.append(f"[HOME] '{needle}' fehlt auf /")
    if path.startswith("/wissen/") and path != "/wissen":
        for needle in ["article-author", "Geschrieben von", "linkedin.com/in/xyesca"]:
            if needle not in html:
                problems.append(f"[ARTICLE] {path}: '{needle}' fehlt")
    if path in ("/it-infrastruktur", "/ki-integration", "/ki-automatisierung", "/ki-agenten", "/n8n-automatisierung", "/lokale-ki"):
        for needle in ["landing-author", "Wer dahintersteht", "linkedin.com/in/xyesca"]:
            if needle not in html:
                problems.append(f"[LANDING] {path}: '{needle}' fehlt")

print(f"Live geprüfte Seiten: {checked}")
if problems:
    print(f"LIVE-PROBLEME ({len(problems)}):")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("LIVE-AUDIT OK — Trust-Elemente auf allen deployed Seiten.")
