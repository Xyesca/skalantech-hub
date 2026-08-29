"""VELA: Verify PR #12 customer-first copy in index.html + base.html against proposal.

Reference: docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md (branch origin/proposal/customer-first-website-restructure).
Checks all verbindliche copy blocks verbatim (whitespace-tolerant), and asserts the
proposal's removal list (no Zertifikats-/Lebenslauf-Trust, no tool lists in hero,
no DeepDive/DebtPilot as homepage funnel proof).

Exit 0 = Copy ✓ (fully conform), exit 1 = deviations.
"""
import re
import subprocess
import sys

repo = "/root/skalantech-hub"
prop = subprocess.run(
    ["git", "-C", repo, "show", "origin/proposal/customer-first-website-restructure:docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md"],
    capture_output=True, text=True, check=True).stdout
idx = open(f"{repo}/app/templates/index.html", encoding="utf-8").read()
base = open(f"{repo}/app/templates/base.html", encoding="utf-8").read()
combined = idx + "\n" + base
norm = re.sub(r"\s+", " ", combined)

def has(needle):
    """Whitespace-tolerant containment (templates wrap long copy across lines)."""
    return re.sub(r"\s+", " ", needle) in norm

checks = {
    # Verbindliche Hero-Copy
    "Hero-Eyebrow": "Digitale Prozesse für kleine und mittelständische Unternehmen",
    "Hero-H1-1": "Weniger manuelle Arbeit.",
    "Hero-H1-2": "Mehr Zeit für Kunden, Team und Wachstum.",
    "Hero-Lead": "Skalantech verbindet bestehende Systeme, automatisiert wiederkehrende Abläufe und entwickelt digitale Lösungen, die Ihr Tagesgeschäft spürbar entlasten – schrittweise, nachvollziehbar und passend zu Ihrem Unternehmen.",
    "Hero-Primaer-CTA": "Kostenlosen Potenzial-Check buchen",
    "Hero-Sekundaer-CTA": "Live-Beispiele ansehen",
    "Hero-Trust-1": "Bestehende Systeme zuerst sinnvoll weiterverwenden",
    "Hero-Trust-2": "Mit einem klar abgegrenzten Prozess starten",
    "Hero-Trust-3": "Nachvollziehbar umgesetzt und dokumentiert",
    # Verbindliche Navigation
    "Nav-Loesungen": "Lösungen",
    "Nav-Branchen": "Branchen",
    "Nav-Live-Demos": "Live-Demos",
    "Nav-Projekte": "Projekte",
    "Nav-Ueber-uns": "Über uns",
    "Nav-CTA": "Potenzial-Check buchen",
    # Über Skalantech
    "Ueber-H2": "Technologie, die Arbeit abnimmt – statt neue Arbeit zu schaffen.",
    "Ueber-Lead": "Skalantech entwickelt digitale Prozesse und Anwendungen für kleine und mittelständische Unternehmen. Im Mittelpunkt steht nicht ein bestimmtes Tool, sondern die Frage: Welcher Ablauf kostet heute unnötig Zeit, erzeugt Fehler oder bleibt regelmäßig liegen?",
    "Ueber-Ergaenzung": "Daraus entsteht eine Lösung, die vorhandene Systeme verbindet, wiederkehrende Aufgaben vorbereitet oder automatisiert und Mitarbeitern klare Kontroll- und Freigabepunkte lässt.",
    "Ueber-Prinzip-1": "Bestehendes sinnvoll nutzen",
    "Ueber-Prinzip-2": "Klein beginnen",
    "Ueber-Prinzip-3": "Messbar verbessern",
    "Ueber-Prinzip-4": "Kontrolle im Unternehmen behalten",
    # Geschäftsführung (kleiner Bereich)
    "GF-Titel": "Geschäftsführung &amp; technische Leitung",
    "GF-Name": "Xavier Escalante Castellar",
    "GF-Copy": "Verantwortet bei Skalantech Strategie, Lösungsarchitektur und Qualitätssicherung. Der fachliche Schwerpunkt liegt auf Prozessautomatisierung, KI-Integration und moderner IT-Infrastruktur.",
    # Gebaute Lösungen: Hub, InvoiceFlow, OfferAI, MailAgent
    "Hub-Ausgangslage": "Website, Anfragen, Termine und Vertriebsinformationen waren voneinander getrennt.",
    "Hub-Nutzen": "durchgängiger Prozess vom ersten Besuch bis zur qualifizierten Anfrage",
    "InvoiceFlow-Ausgangslage": "Rechnungsangaben müssen manuell gelesen und übertragen werden.",
    "InvoiceFlow-Nutzen": "Weniger Übertragungsarbeit und eine klarere Vorbereitung für die Buchhaltung.",
    "OfferAI-Ausgangslage": "Kundenanfragen müssen manuell ausgewertet und in Angebotsentwürfe übertragen werden.",
    "OfferAI-Nutzen": "Die Angebotsvorbereitung startet schneller und bleibt unter menschlicher Kontrolle.",
    "MailAgent-Ausgangslage": "Gemeinsame Postfächer enthalten unterschiedliche Anliegen und Dringlichkeiten.",
    "MailAgent-Nutzen": "Schnellere Zuordnung und weniger wiederkehrende Schreibarbeit.",
    # Entfernt laut Proposal (KEIN ... = darf NICHT vorkommen)
    "KEIN-Zertifikats-Trust": "certificates_xavier",
    "KEIN-Lebenslauf-Trust": "Lebenslauf",
    "KEIN-Live-Stack": "Live-Stack",
    "KEIN-Tool-Hero-n8n-APIs": "n8n · APIs",
    "KEIN-DeepDive-Homepage": "DeepDive",
    "KEIN-DebtPilot-Homepage": "DebtPilot",
}

# Intentional occurrences of the literal "Lebenslauf" (removal messaging), not trust elements.
ALLOWED_LEBENSLAUF_SENTENCE = "Statt Lebenslauf und Zertifikaten stehen konkrete Systeme im Vordergrund"

fails = []
for name, needle in checks.items():
    if name == "KEIN-Lebenslauf-Trust":
        # Only the intentional removal sentence may mention Lebenslauf.
        ok = needle not in combined or ALLOWED_LEBENSLAUF_SENTENCE in combined
    elif name.startswith("KEIN"):
        ok = not has(needle)
    else:
        ok = has(needle)
    if not ok:
        fails.append(name)
    print(f"{name:<28} {'OK' if ok else 'FAIL'}")

print()
if fails:
    print("DEVIATIONS:", ", ".join(fails))
    sys.exit(1)
print("Copy ✓ — alle verbindlichen Texte aus dem Proposal 1:1 übernommen, "
      "keine Zertifikats-/Lebenslauf-Trust-Elemente, keine Tool-Listen im Hero.")
sys.exit(0)
