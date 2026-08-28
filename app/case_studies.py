# -*- coding: utf-8 -*-
"""Skalantech Hub — Case Studies / Anwendungsbeispiele.

Quelle: VELA-Copy (Task t_e263a52c, case_study_dict.py), DoD-verifiziert per
case_study_check.py (Exit 0). Verbatim uebernommen — Dict-Schluessel unveraendert.

Verbindliche Rahmen (Sperren, CLOSER/SENTINEL P0):
- KEIN erfundener Kunde: Label „Anwendungsbeispiel Handwerk" (Badge/Kicker + H1).
- KEIN „Live-Terminbuchung"-Claim: n8n-Credentials (Kalender/Gmail) sind abgelaufen;
  Text sagt „erprobt"/„selbst betrieben". Erst nach n8n-Credential-Reconnect (separater
  NEXUS-Task) darf der Wortlaut ggf. verschaerft werden.
- KEINE Steigerungsraten/Prozent-Claims.
- Disclaimer roi_note zwingend unter der Zahlenbox.
- Zahlen NUR aus dem Dict (520 h/65 Tg/33.800 € + Sensitivitaet 187 h/23 Tg/12.200 €),
  Quelle = produktiver ROI-Rechner (app/static/js/roi-calculator.js).
"""

CASE_STUDIES = {
    # Dict-Schluessel = case-slug. Route: /case-studies/{slug}
    "anwendungsbeispiel-handwerk": {
        "label": "Anwendungsbeispiel Handwerk",          # Boss-Marker: KEIN erfundener Kunde
        "type": "case_study",
        "title": "Anwendungsbeispiel Handwerk: 520 Stunden Bürozeit pro Jahr",  # SEO-Meta <=60
        "title_redaktion": "Anwendungsbeispiel Handwerk: 520 Stunden Bürozeit pro Jahr zurückgewinnen",  # Langform für Seite, nicht Meta
        "description": "Rund 520 Stunden Bürozeit pro Jahr: So holt Prozessautomatisierung die Zeit zurück – Angebote in Minuten, Rechnungen automatisch, E-Rechnung inklusive.",
        "h1": "Anwendungsbeispiel Handwerk: 520 Stunden Bürozeit pro Jahr",
        "intro": (
            "Ein typischer Handwerksbetrieb hat kein Software-Problem. Er hat ein Zeitproblem. "
            "Die Aufträge sind da, das Handwerk läuft – und trotzdem bleibt die Büroarbeit abends liegen. "
            "Dieses Anwendungsbeispiel zeigt, wo die Zeit verloren geht und wie Prozessautomatisierung sie zurückgibt."
        ),
        "problem_title": "Ausgangslage: Wo die Büroarbeit Zeit frisst",
        "problem": [
            "Angebote entstehen abends im Büro statt auf der Baustelle – jede Anfrage kostet Stunden, die niemand hat.",
            "Der Papierkram stapelt sich: Rechnungen, Lieferscheine, Abnahmen – manuell, fehleranfällig, und das Wichtigste wird vergessen.",
            "Termine werden telefonisch hin- und hergeschoben – Rückrufe, Zettel, Kalender, die niemand pflegt.",
            "Anfragen werden nicht nachverfolgt – Interessenten hören nichts, Aufträge versickern im Papierkorb.",
        ],
        "solution_title": "Lösung: Drei Prozesse, die sofort Zeit zurückgeben",
        "solution": [
            ("Angebot aus der Anfrage – in Minuten statt Stunden",
             "Aus einer Kundenanfrage entsteht automatisch ein vollständiger Angebotsentwurf: mit Ihren Preisen, Ihren Positionen, Ihrem Briefkopf. Der Inhaber gibt frei statt zu tippen."),
            ("Rechnungen gehen automatisch raus – E-Rechnung inklusive",
             "Nach Auftragsabschluss erstellt das System die Rechnung, prüft die Pflichtangaben und versendet sie. Keine vergessenen Rechnungen – und der Betrieb ist E-Rechnung-fähig, bevor die Pflicht ihn trifft."),
            ("Kein Kunde geht verloren, keine Anfrage bleibt liegen",
             "Anfragen landen zentral, Kunden buchen Termine selbst online – rund um die Uhr, ohne Rückruf-Pingpong. Follow-ups laufen automatisch: Bestätigung, Erinnerung, No-Show-Nachfass. Skalantech betreibt diese Automatisierung selbst im eigenen Geschäftsbetrieb – der Aufbau ist erprobt."),
        ],
        "setup_note": "Die Lösung setzt auf den bestehenden Systemen des Betriebs auf – kein Neuaufbau, kein Vendor-Lock-in, Self-Hosting möglich. Der erste Quick-Win steht in Tagen, nicht in Monaten. Fixpreis vorab.",
        "ergebnis_title": "Ergebnis: Was das an Zeit und Geld bedeutet",
        "zahlen": {
            "quelle": "ROI-Rechner der Handwerk-Landingpage (app/static/js/roi-calculator.js), Defaults = konservatives Beispiel",
            "defaults": {
                "annahmen": "15 Angebote/Monat à 90 min · 20 Rechnungen/Monat à 30 min · 10 Anfragen/Woche à 15 min",
                "formel": "(Angebots-Std × 12) + (Rechnungs-Std × 12) + (Anfragen-Std × 52)",
                "stunden_pro_jahr": 520,
                "arbeitstage_pro_jahr": 65,
                "eur_pro_jahr_bei_65eur_h": 33800,
                "durchsatz": 65,
            },
            "sensitivitaet": {
                "annahmen": "8 Angebote/Monat à 60 min · 12 Rechnungen/Monat à 20 min · 5 Anfragen/Woche à 10 min",
                "stunden_pro_jahr": 187,
                "arbeitstage_pro_jahr": 23,
                "eur_pro_jahr_bei_65eur_h": 12200,
            },
            "roi_note": "Konservative Schätzung aus Ihren Eingaben – anpassbar, keine Garantie. Der Nutzen wird vor dem Start gemeinsam mit Ihren echten Zahlen konkret beziffert.",
        },
        "erechnung_title": "Dringlichkeits-Baustein: Die E-Rechnungspflicht kommt",
        "erechnung_facts": [
            "Seit dem 01.01.2025 sind alle inländischen B2B-Unternehmen verpflichtet, E-Rechnungen zu empfangen – auch Handwerksbetriebe und Kleinunternehmer. Keine Übergangsfrist.",
            "Versandpflicht gestaffelt: ab 01.01.2027 für Betriebe mit Vorjahresumsatz über 800.000 €, ab 01.01.2028 für alle B2B-Rechnungen (Ausnahme: Kleinbetragsrechnungen bis 250 €).",
            "Formate: XRechnung (öffentliche Hand) und ZUGFeRD ab Version 2.0 – ZUGFeRD enthält zusätzlich ein lesbares PDF.",
            "ZDH-Umfrage 2026 (1.926 Betriebe): Empfang und Versand laufen in der Praxis noch nicht reibungslos – der Bedarf ist real.",
        ],
        "erechnung_note": "Wer jetzt vorbereitet ist, muss nichts umstellen, wenn die Pflicht zuschlägt – die Rechnung geht automatisch im richtigen Format raus.",
        "process_title": "So starten Sie – in drei Schritten",
        "process": [
            ("Ausgangslage aufnehmen", "Wir sehen uns Ihre Abläufe an – Angebote, Termine, Rechnungen – und wo sie hängen."),
            ("Nutzen konkret beziffern", "Gemeinsam legen wir fest, was automatisiert wird und wie der Nutzen in Ihren Zahlen aussieht. Fixpreis vorab."),
            ("Quick-Win in Tagen", "Wir bauen genau einen Prozess zuerst – den, der am meisten Zeit kostet. Sie sehen das Ergebnis mit Ihren Daten, dann entscheiden Sie, ob es weitergeht."),
        ],
        "fazit_title": "Fazit",
        "fazit_paragraphs": [
            "Automatisierung im Handwerksbetrieb heißt nicht „KI für alles“-Großprojekt. Es heißt: Angebote in Minuten, Rechnungen ohne Aufwand, kein Kunde verloren – und Abende, die wieder Ihnen gehören. Einstieg in Tagen, nicht in Monaten.",
            "Starten Sie mit einer Demo mit Branchendaten – 20 Minuten, unverbindlich.",
        ],
        # CTA (UTM-Bau nach LUMINA §4.1: Query ... VOR Fragment)
        "cta_primary": "Demo mit Branchendaten",
        "cta_primary_url": "/?utm_source=organic&utm_medium=landing&utm_campaign=case_handwerk#termin",
        "cta_secondary": "Projekt besprechen",
        "cta_secondary_url": "/?utm_source=organic&utm_medium=landing&utm_campaign=case_handwerk#contact",
        "related_landing": "branchen-handwerk",        # bestehende Handwerk-Branch-Landing
        "related_articles": ["welche-prozesse-ki-automatisierung", "kosten-roi-ki-automatisierung"],
        # Meta für VELA/QA (wird NICHT gerendert)
        "keywords_primary": ["ki automatisierung handwerk", "terminbuchung handwerksbetrieb", "anwendungsbeispiel handwerk ki"],
        "keywords_secondary": ["zeit sparen handwerk", "angebotserstellung automatisieren", "rechnungen automatisch handwerk", "e-rechnungspflicht handwerk"],
        "intent": "Case-Study/Anwendungsbeispiel: Prozess-Automatisierung im Handwerksbetrieb konkrekt gemacht",
    },
}

CASE_STUDY_ORDER = [
    "anwendungsbeispiel-handwerk",
]
