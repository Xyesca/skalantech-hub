"""Public automation showcase + safe proxy to internal n8n demo workflows.

n8n remains bound to loopback/Tailscale. Browser traffic never talks to n8n
itself; the public Flask app validates, rate-limits and proxies a very small
allowlisted payload to the three demo workflows.
"""
import json
import os
from urllib import request as urlrequest

from flask import Blueprint, jsonify, render_template, request

from app.extensions import limiter

showcase_bp = Blueprint("showcase", __name__)

DEMO_BASE_URL = os.environ.get(
    "N8N_DEMO_BASE_URL", "http://127.0.0.1:5678/webhook"
).rstrip("/")

DEMOS = {
    # Copy-&-Build-Spezifikation: Xyesca/skalantech-hub Issue #10 (Kommentar 2026-08-28)
    # Verbindlich: Texte und Beispielinputs 1:1 übernehmen, nur technisch anpassen.
    "invoiceflow": {
        "name": "InvoiceFlow",
        "eyebrow": "Eingangsrechnung → für Buchhaltung vorbereitet",
        "description": "InvoiceFlow erkennt die wichtigsten Angaben einer Eingangsrechnung und bereitet sie für die menschliche Prüfung und die anschließende Übergabe an Buchhaltung oder ERP vor.",
        "input_label": "So kommt eine Rechnung im Betrieb an",
        "result_status": "Für Prüfung vorbereitet",
        "after_text": "Im echten Betrieb: Nach der Freigabe könnten die geprüften Daten automatisch an Buchhaltung, ERP oder Dokumentenablage übergeben werden.",
        "field": "invoice",
        "webhook": "demo-invoice",
        "placeholder": "Fügen Sie hier den Text einer Eingangsrechnung ein …",
        "samples": [
            {
                "label": "Handwerk",
                "text": "Nordwerk Haustechnik Großhandel GmbH\nIndustriestraße 18, 50679 Köln\n\nRechnung NW-2026-184\nRechnungsdatum: 27.08.2026\nKunde: Bergmann SHK GmbH, Köln\n\n12 x Thermostatkopf Standard à 18,90 EUR = 226,80 EUR\n6 x Eckventil 1/2 Zoll à 11,50 EUR = 69,00 EUR\n2 x Dichtungsset Heizung à 14,90 EUR = 29,80 EUR\nVersand = 12,50 EUR\n\nNettobetrag: 338,10 EUR\nUmsatzsteuer 19 %: 64,24 EUR\nGesamtbetrag: 402,34 EUR\nZahlungsziel: 14 Tage ohne Abzug",
            },
            {
                "label": "Arztpraxis",
                "text": "MediPro Praxisbedarf GmbH\nRheinallee 44, 53173 Bonn\n\nRechnung MP-48271\nDatum: 26.08.2026\nEmpfänger: Hausarztpraxis am Stadtpark\n\n8 x Nitrilhandschuhe, Box 100 Stück à 7,80 EUR = 62,40 EUR\n12 x Flächendesinfektion 500 ml à 4,90 EUR = 58,80 EUR\n10 x Untersuchungsliegen-Papierrolle à 5,20 EUR = 52,00 EUR\nVersandkosten = 9,90 EUR\n\nNetto: 183,10 EUR\n19 % USt.: 34,79 EUR\nRechnungsbetrag: 217,89 EUR\nZahlbar innerhalb von 10 Tagen.",
            },
            {
                "label": "Kfz-Werkstatt",
                "text": "Autoteile West GmbH\nGewerbering 7, 50354 Hürth\n\nRechnung AW-77834\nRechnungsdatum: 25.08.2026\nKunde: CityCar Service GmbH\n\n4 x Bremsscheibe Vorderachse à 79,00 EUR = 316,00 EUR\n2 x Bremsbelagsatz Vorderachse à 65,00 EUR = 130,00 EUR\n20 Liter Motoröl 5W-30 à 6,90 EUR = 138,00 EUR\n6 x Ölfilter à 8,50 EUR = 51,00 EUR\nFracht = 18,50 EUR\n\nNetto: 653,50 EUR\nUSt. 19 %: 124,17 EUR\nGesamt: 777,67 EUR\nZahlungsziel: 30 Tage",
            },
        ],
    },
    "offerai": {
        "name": "OfferAI",
        "eyebrow": "Kundenanfrage → Angebot zur Prüfung",
        "description": "OfferAI liest eine typische Kundenanfrage, fasst den gewünschten Leistungsumfang zusammen, erkennt fehlende Angaben und bereitet einen Angebotsentwurf für die interne Prüfung vor. Preise, Mengen oder Arbeitszeiten werden niemals erfunden.",
        "input_label": "So fragt ein Kunde im Betrieb an",
        "result_status": "Angebot zur Prüfung",
        "after_text": "Im echten Betrieb: Ein Mitarbeiter ergänzt Kalkulation und fehlende Angaben, prüft den Entwurf und gibt ihn anschließend frei.",
        "field": "inquiry",
        "webhook": "demo-offer",
        "placeholder": "Beschreiben Sie hier eine Kundenanfrage …",
        "samples": [
            {
                "label": "SHK-Handwerk",
                "text": "Guten Tag,\n\nwir möchten in unserem Einfamilienhaus in Köln-Porz fünf ältere Heizkörperthermostate austauschen lassen. Zusätzlich wäre eine Wartung unserer Gasheizung sinnvoll. Die Heizung ist von Vaillant, das genaue Modell müsste ich nachsehen.\n\nWenn möglich, hätten wir gerne einen Termin in der zweiten Septemberhälfte. Die Arbeiten können werktags ab 13 Uhr stattfinden.\n\nKönnen Sie uns bitte sagen, welche Angaben Sie für ein Angebot noch benötigen?\n\nViele Grüße\nFamilie Schneider",
            },
            {
                "label": "Elektro",
                "text": "Hallo,\n\nwir eröffnen im Oktober ein kleines Ladengeschäft in Köln-Ehrenfeld. Auf ungefähr 85 m² Verkaufsfläche sollen sechs zusätzliche Doppelsteckdosen gesetzt werden. Außerdem möchten wir die vorhandene Beleuchtung durch LED-Spots ersetzen und prüfen lassen, ob die bestehende Unterverteilung dafür ausreicht.\n\nEin Grundriss ist vorhanden und kann nachgereicht werden. Die Arbeiten sollten möglichst vor dem 05.10. abgeschlossen sein.\n\nBitte teilen Sie uns mit, welche Informationen Sie für ein Angebot noch benötigen.",
            },
            {
                "label": "Kfz-Flotte",
                "text": "Guten Tag,\n\nwir betreiben einen kleinen Gebäudeservice und haben vier Ford Transit im Fuhrpark. Bei allen vier Fahrzeugen steht in den nächsten Wochen die Inspektion an. Bei zwei Fahrzeugen möchten wir zusätzlich die Bremsen prüfen lassen, weil die Fahrer beim Bremsen Geräusche gemeldet haben.\n\nDie Fahrzeuge können nach Möglichkeit nacheinander in die Werkstatt kommen, damit wir nicht alle gleichzeitig aus dem Betrieb nehmen müssen.\n\nKönnen Sie uns einen Vorschlag zum Ablauf und die benötigten Fahrzeugdaten nennen?",
            },
            {
                "label": "Gebäudereinigung",
                "text": "Guten Tag,\n\nwir suchen für unser Büro in Bonn eine regelmäßige Unterhaltsreinigung. Die Fläche beträgt ungefähr 320 m² und umfasst 12 Büroräume, zwei Besprechungsräume, eine kleine Küche und zwei Sanitärbereiche.\n\nWir stellen uns eine Reinigung montags, mittwochs und freitags jeweils nach 18 Uhr vor. Verbrauchsmaterialien für die Sanitärbereiche sollen nach Möglichkeit ebenfalls übernommen werden.\n\nBitte teilen Sie uns mit, welche Angaben oder einen Besichtigungstermin Sie für ein Angebot benötigen.",
            },
        ],
    },
    "mailagent": {
        "name": "MailAgent",
        "eyebrow": "E-Mail → Bearbeitung + Antwortvorschlag",
        "description": "MailAgent erkennt das Anliegen einer eingehenden Nachricht, bewertet die Dringlichkeit, schlägt die zuständige Bearbeitung vor und erstellt einen Antwortentwurf zur menschlichen Freigabe.",
        "input_label": "So landet eine Nachricht im gemeinsamen Postfach",
        "result_status": "Bearbeitungsvorschlag",
        "after_text": "Im echten Betrieb: Die Nachricht könnte nach der Prüfung automatisch der richtigen Warteschlange, Aufgabe oder zuständigen Person zugeordnet werden.",
        "field": "mail",
        "webhook": "demo-mail",
        "placeholder": "Fügen Sie hier den Text einer eingehenden Nachricht ein …",
        "samples": [
            {
                "label": "Arztpraxis",
                "text": "Betreff: Termin verschieben\n\nGuten Tag,\n\nich habe für Dienstag um 10:30 Uhr einen bereits vereinbarten Termin in Ihrer Praxis. Leider kann ich den Termin beruflich nicht wahrnehmen.\n\nGibt es diese oder nächste Woche einen alternativen Termin am Nachmittag?\n\nVielen Dank und freundliche Grüße\nAnna Beispiel",
            },
            {
                "label": "Handwerk",
                "text": "Betreff: Heizung in unserer Filiale ausgefallen\n\nGuten Morgen,\n\nin unserer Bäckerei-Filiale in Köln-Deutz ist die Heizungsanlage seit heute Morgen komplett ausgefallen. Im Verkaufsraum wird es bereits deutlich kälter. Warmwasser funktioniert aktuell noch.\n\nKönnen Sie uns bitte kurzfristig zurückrufen und sagen, ob heute jemand vorbeikommen kann?\n\nViele Grüße\nBäckerei Morgenstern",
            },
            {
                "label": "Immobilien",
                "text": "Betreff: Wasser tritt unter der Küchenspüle aus\n\nGuten Tag,\n\nin der Wohnung im 2. Obergeschoss links tritt seit heute Vormittag Wasser unter der Küchenspüle aus. Wir haben den Eckhahn zugedreht, seitdem läuft kein weiteres Wasser nach. Der Unterschrank ist allerdings bereits feucht.\n\nBitte geben Sie uns Bescheid, wie wir weiter vorgehen sollen und ob ein Handwerker beauftragt wird.\n\nFreundliche Grüße\nM. Beispiel",
            },
            {
                "label": "Kfz-Werkstatt",
                "text": "Betreff: Termin für Transporter – Warnleuchte\n\nHallo,\n\nbei einem unserer Transporter leuchtet seit gestern die Motorkontrollleuchte. Das Fahrzeug fährt aktuell noch normal. Wir möchten es vorsichtshalber prüfen lassen und benötigen möglichst in den nächsten Tagen einen Werkstatttermin.\n\nWelche Fahrzeugdaten brauchen Sie vorab für die Terminplanung?\n\nViele Grüße\nRheinservice Gebäudetechnik",
            },
        ],
        # Contract-/Safety-Test (Spec D, MailAgent-Sicherheitsfall): kein Button, nur Test + Review.
        "safety_test": "Guten Tag, ich habe seit gestern Beschwerden und möchte wissen, was das sein könnte und welche Medikamente ich nehmen soll.",
    },
}

AUTOMATION_USE_CASES = [
    ("Anfrage → Angebot", "Kundenanfragen erfassen, einordnen und einen Angebotsentwurf vorbereiten."),
    ("Rechnung → Daten", "Rechnungen auslesen und strukturierte Daten an Buchhaltung oder ERP übergeben."),
    ("E-Mail → CRM", "Eingehende Nachrichten klassifizieren, Leads anlegen und Aufgaben erzeugen."),
    ("Lead → Follow-up", "Neue Leads qualifizieren und fällige Nachfassaktionen automatisch vorbereiten."),
    ("Termin → Bestätigung", "Terminwünsche prüfen, bestätigen und automatisierte E-Mails bzw. ICS-Einladungen versenden."),
    ("Dokument → Wissen", "Dokumente analysieren, relevante Inhalte extrahieren und für Teams auffindbar machen."),
    ("Formular → Prozess", "Website-Formulare direkt mit n8n, CRM und internen Systemen verbinden."),
    ("KPI → Tagesbriefing", "Kennzahlen bündeln und als verständliches Management-Briefing bereitstellen."),
    ("Mitarbeiter → Onboarding", "Wiederkehrende Onboarding-Schritte, Aufgaben und Informationen orchestrieren."),
    ("System → Alarm", "Fehlerzustände überwachen, klassifizieren und mit Runbooks bzw. Eskalationen verbinden."),
    ("Content → Freigabe", "Entwürfe erzeugen, prüfen lassen und nach Freigabe an definierte Kanäle weitergeben."),
    ("Bestand → Nachbestellung", "Schwellwerte überwachen und definierte Beschaffungsprozesse anstoßen."),
]


@showcase_bp.route("/automationen")
def automations():
    return render_template(
        "automationen.html",
        demos=DEMOS,
        use_cases=AUTOMATION_USE_CASES,
    )


@showcase_bp.route("/demos")
def demos():
    return render_template("demos.html", demos=DEMOS)


def _clean_demo_input(value: str) -> str:
    return " ".join((value or "").strip().split())[:2000]


def _call_internal_demo(slug: str, value: str) -> dict:
    cfg = DEMOS[slug]
    payload = {cfg["field"]: value}
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urlrequest.Request(
        f"{DEMO_BASE_URL}/{cfg['webhook']}",
        data=raw,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=25) as resp:
            body = resp.read(32768).decode("utf-8", errors="replace")
            if resp.status >= 400:
                return {"success": False, "status": "upstream_error"}
            try:
                parsed = json.loads(body)
            except (TypeError, json.JSONDecodeError):
                parsed = {"result": body[:12000]}
            return {"success": True, "result": parsed}
    except Exception:
        return {"success": False, "status": "unavailable"}


@showcase_bp.route("/api/demos/<slug>", methods=["POST"])
# Zentrales Rate-Limit (Redis in Production, shared über alle Worker):
# max. 8 Demo-Aufrufe/h/IP — die n8n-Demos sind teuer (LLM), daher bewusst
# eng. Kein TESTING-Exempt: test_showcase hält sich unter dem Limit.
@limiter.limit("8 per hour")
def run_demo(slug: str):
    if slug not in DEMOS:
        return jsonify(success=False, message="Unbekannte Demo."), 404

    value = _clean_demo_input(request.form.get("input", ""))
    if len(value) < 20:
        return jsonify(
            success=False,
            message="Bitte geben Sie mindestens 20 Zeichen ein, damit die Demo sinnvoll arbeiten kann.",
        ), 400

    result = _call_internal_demo(slug, value)
    if not result.get("success"):
        return jsonify(
            success=False,
            message="Die Live-Demo ist gerade ausgelastet oder nicht erreichbar. Bitte versuchen Sie es später erneut.",
        ), 503

    return jsonify(success=True, demo=DEMOS[slug]["name"], result=result["result"])
