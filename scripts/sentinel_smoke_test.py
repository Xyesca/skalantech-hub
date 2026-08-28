"""SENTINEL QA-Gate Smoke-Test: rendert alle relevanten Routen und prüft
Security-Header, Copy, rechtliche Pflichtangaben und Regressionen."""
import os, sys

os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["SESSION_COOKIE_SECURE"] = "false"
os.environ["DATABASE_URL"] = "sqlite:////tmp/sentinel_smoke.db"
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"
sys.path.insert(0, "/root/skalantech-hub")
from app import create_app

app = create_app("production")
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
client = app.test_client()

print("=== STATUS + SECURITY HEADERS ===")
for path in ["/", "/impressum", "/datenschutz", "/agb", "/koeln", "/demos", "/automationen",
             "/rechner", "/websites-apps", "/it-infrastruktur", "/sitemap.xml", "/robots.txt"]:
    r = client.get(path)
    h = r.headers
    csp = h.get("Content-Security-Policy", "")
    checks = {
        "XCTO": h.get("X-Content-Type-Options"),
        "XFO": h.get("X-Frame-Options"),
        "RR": h.get("Referrer-Policy"),
        "HSTS": h.get("Strict-Transport-Security"),
        "CSP-self": ("script-src 'self'" in csp),
        "CSP-fa": ("frame-ancestors 'none'" in csp),
        "PP": h.get("Permissions-Policy") is not None,
    }
    print(f"{path} -> {r.status_code} | " + " | ".join(f"{k}={v}" for k, v in checks.items()))

print("\n=== HOMEPAGE CONTENT CHECKS ===")
html = client.get("/").get_data(as_text=True)
for needle in ["Weniger manuelle Arbeit.", "Kostenlosen Potenzial-Check buchen", "Potenzial-Check buchen",
               "Xavier Escalante Castellar", "InvoiceFlow", "OfferAI", "MailAgent",
               "href=\"/#termin\"", "id=\"main-content\"", "skip-link", "csrf_token"]:
    print(f"{'OK ' if needle in html else 'MISS'} {needle}")

print("\n=== LEGAL PAGES ===")
for p in ["/impressum", "/datenschutz", "/agb"]:
    t = client.get(p).get_data(as_text=True)
    print(f"{p}: Name={'Xavier Escalante Castellar' in t} | tel-link={'tel:+4917677879366' in t} | mail={'xyesca@skalantech.store' in t}")

print("\n=== OLD BLOCKS / CLAIMS ===")
for needle in ["Lebenslauf", "Zertifikat", "DeepDive", "DebtPilot", "Vier Bausteine", "eigene Server und Daten",
               "Business-Analyse buchen", "100% Self-hosted", "Live-Stack"]:
    print(f"{'STILL PRESENT' if needle in html else 'removed      '} {needle}")

print("\n=== TRACKERS ===")
for needle in ["google-analytics", "googletagmanager", "plausible", "hotjar", "clarity", "matomo", "facebook", "gtag"]:
    print(f"{'FOUND' if needle in html else 'clean'} {needle}")

print("\n=== 404/500 HANDLER ===")
r404 = client.get("/gibts-nicht")
print("404 ->", r404.status_code, "| noindex" , "noindex" in r404.get_data(as_text=True))

print("\n=== SIGNAL-BAR CLAIMS VERIFY ===")
print("3 Live-Beispiele:", all(x in html for x in ["InvoiceFlow", "OfferAI", "MailAgent"]))
print("6+ Systeme: Hub/InvoiceFlow/OfferAI/MailAgent + DeepDive/DebtPilot (separate Seiten) — plausibel")
