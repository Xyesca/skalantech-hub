"""Verify PR #12 copy at a specific git ref (default HEAD) — durable-state check."""
import re
import subprocess
import sys

repo = "/root/skalantech-hub"
ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
idx = subprocess.run(["git", "-C", repo, "show", f"{ref}:app/templates/index.html"], capture_output=True, text=True, check=True).stdout
base = subprocess.run(["git", "-C", repo, "show", f"{ref}:app/templates/base.html"], capture_output=True, text=True, check=True).stdout
combined = idx + "\n" + base
norm = re.sub(r"\s+", " ", combined)

def has(needle):
    return re.sub(r"\s+", " ", needle) in norm

checks = {
    "Hero-Eyebrow": "Digitale Prozesse für kleine und mittelständische Unternehmen",
    "Hero-H1-1": "Weniger manuelle Arbeit.",
    "Hero-H1-2": "Mehr Zeit für Kunden, Team und Wachstum.",
    "Hero-Lead": "Skalantech verbindet bestehende Systeme, automatisiert wiederkehrende Abläufe und entwickelt digitale Lösungen, die Ihr Tagesgeschäft spürbar entlasten – schrittweise, nachvollziehbar und passend zu Ihrem Unternehmen.",
    "Hero-Primaer-CTA": "Kostenlosen Potenzial-Check buchen",
    "Hero-Sekundaer-CTA": "Live-Beispiele ansehen",
    "Hero-Trust-1": "Bestehende Systeme zuerst sinnvoll weiterverwenden",
    "Hero-Trust-2": "Mit einem klar abgegrenzten Prozess starten",
    "Hero-Trust-3": "Nachvollziehbar umgesetzt und dokumentiert",
    "Nav-Loesungen": "Lösungen", "Nav-Branchen": "Branchen", "Nav-Live-Demos": "Live-Demos",
    "Nav-Projekte": "Projekte", "Nav-Ueber-uns": "Über uns",
    "Nav-CTA": "Potenzial-Check buchen",
    "Ueber-H2": "Technologie, die Arbeit abnimmt – statt neue Arbeit zu schaffen.",
    "GF-Name": "Xavier Escalante Castellar",
    "Hub": "Skalantech Hub", "InvoiceFlow": "InvoiceFlow", "OfferAI": "OfferAI", "MailAgent": "MailAgent",
    "KEIN-certificates": "certificates_xavier",
    "KEIN-Live-Stack": "Live-Stack",
    "KEIN-n8n-APIs-Hero": "n8n · APIs",
    "KEIN-DeepDive": "DeepDive",
    "KEIN-DebtPilot": "DebtPilot",
    "KEIN-alte-Hero": "Arbeit, die heute Zeit frisst",
    "KEIN-Kostenlose-Business-Analyse": "Kostenlose Business-Analyse",
}

fails = []
for name, needle in checks.items():
    if name.startswith("KEIN"):
        ok = not has(needle)
    else:
        ok = has(needle)
    if not ok:
        fails.append(name)
    print(f"{name:<28} {'OK' if ok else 'FAIL'}")

print()
print(f"Ref {ref}: " + ("Copy OK — Freigabe 'Copy ✓' bestätigt." if not fails else "DEVIATIONS: " + ", ".join(fails)))
sys.exit(0 if not fails else 1)
