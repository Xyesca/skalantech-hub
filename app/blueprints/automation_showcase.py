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
    "invoiceflow": {
        "name": "InvoiceFlow",
        "eyebrow": "Rechnung → strukturierte Daten",
        "description": "Liest Rechnungstext aus und strukturiert Lieferant, Rechnungsnummer, Datum, Beträge und Positionen für die Weiterverarbeitung.",
        "field": "invoice",
        "webhook": "demo-invoice",
        "placeholder": "Rechnung Nr. 2026-184 · Muster GmbH · Netto 1.250,00 € · USt. 237,50 € · Gesamt 1.487,50 € ...",
        "samples": [
            "Rechnung Nr. RE-2026-184 vom 27.08.2026. Lieferant: Rheinbau GmbH, Köln. Leistung: Wartung Serverraum 10 Std. à 125,00 EUR. Netto 1.250,00 EUR, MwSt. 19% 237,50 EUR, Gesamt 1.487,50 EUR. Zahlungsziel 14 Tage.",
            "TechParts KG · Rechnung TP-8841 · 25.08.2026 · 4x SSD 2TB à 149,00 EUR, Versand 12,90 EUR. Netto 608,90 EUR, 19% USt 115,69 EUR, Brutto 724,59 EUR.",
        ],
    },
    "offerai": {
        "name": "OfferAI",
        "eyebrow": "Kundenanfrage → Angebotsentwurf",
        "description": "Verwandelt eine kurze Kundenanfrage in einen strukturierten Angebotsentwurf, den ein Mensch prüft und finalisiert.",
        "field": "inquiry",
        "webhook": "demo-offer",
        "placeholder": "Wir sind ein Handwerksbetrieb mit 14 Mitarbeitern und möchten Kundenanfragen automatisch erfassen ...",
        "samples": [
            "Wir sind ein SHK-Handwerksbetrieb mit 14 Mitarbeitenden. Kundenanfragen kommen per E-Mail und Telefon. Wir möchten Anfragen automatisch erfassen, nach Dringlichkeit sortieren und einen Angebotsentwurf vorbereiten lassen.",
            "Unsere Kanzlei möchte eingehende Mandantenanfragen automatisch klassifizieren und die relevanten Daten in eine strukturierte Übersicht für die Sachbearbeitung übertragen.",
            "Wir benötigen eine neue B2B-Website mit Terminbuchung, Lead-Erfassung, n8n-Anbindung und einem kleinen Kundenportal. Bitte skizziere ein mögliches Angebot.",
        ],
    },
    "mailagent": {
        "name": "MailAgent",
        "eyebrow": "E-Mail → Klassifikation + Antwortvorschlag",
        "description": "Ordnet eine eingehende Nachricht ein, erkennt Handlungsbedarf und formuliert einen Antwortvorschlag zur menschlichen Freigabe.",
        "field": "mail",
        "webhook": "demo-mail",
        "placeholder": "Guten Tag, unsere Anlage ist seit heute Morgen ausgefallen ...",
        "samples": [
            "Guten Tag, seit heute Morgen ist unsere Produktionsanlage ausgefallen. Bitte melden Sie sich dringend, da aktuell keine Aufträge bearbeitet werden können. Ansprechpartner ist Herr Becker unter 0221 555123.",
            "Hallo, wir interessieren uns für Ihre Prozessautomatisierung. Wir haben ca. 80 Rechnungen pro Woche und übertragen die Daten heute manuell in unser System. Können wir dazu einen Termin vereinbaren?",
            "Bitte senden Sie uns die Rechnung vom letzten Monat erneut zu. Unsere Buchhaltung findet die Datei nicht mehr. Vielen Dank.",
        ],
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
