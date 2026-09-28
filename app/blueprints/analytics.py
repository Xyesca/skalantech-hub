"""Skalantech Hub — First-party, cookie-less Event-Analytics.

Anonymes Conversion-/Interaktions-Tracking der eigenen Website. Kein externer
Dienst, keine Tracking-Cookies, keine IP-Speicherung, keine personenbezogenen
Inhalte. Die Session-ID stammt aus sessionStorage (Tab-Session) und erlaubt
Funnel-Stitching über mehrere Events einer Sitzung.

CSRF ist hier nicht anwendbar (Beacon/fetch ohne Browser-Session-Token) —
der Blueprint wird in der App-Factory per csrf.exempt() freigeschaltet.
Stattdessen: strikte Event-Allowlist, Feld-Limits, Payload-Limit und
Rate-Limit pro IP.
"""
import json

from flask import Blueprint, jsonify, request

from app.extensions import db, limiter
from app.models import AnalyticsEvent

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

# ── Event-Taxonomie (PULSE, P0 Conversion Tracking) ────────────────────────
# Jedes Event hat genau eine Bedeutung; Conversions (lead_created,
# demo_completed, meeting_booked) werden serverseitig beim Formular-POST
# geschrieben und sind damit die verlässliche Quelle der Wahrheit.
ANALYTICS_EVENTS = frozenset({
    "page_view",          # Seite wurde geladen (Funnel-Nenner für Conversion Rates)
    "demo_started",       # CTA „Potenzial-Check“ geklickt (Header/Hero/Sektion)
    "demo_completed",     # Termin-Anfrage erfolgreich abgeschickt (Formular ok)
    "contact_clicked",    # Kontakt-CTA / mailto geklickt
    "calendar_opened",    # Datumsauswahl (Kalender) im Buchungsformular geöffnet
    "meeting_booked",     # n8n-Terminwebhook hat die Buchung bestätigt
    "booking_error",      # n8n down/timeout/invalid_response (Server; props reason unreachable|invalid_response)
    "booking_confirmed",  # Bestätigungsansicht im Booking-Box sichtbar (Client)
    "service_viewed",     # Leistungs-Karte im Viewport (einmal pro Session)
    "case_study_viewed",  # Projekt-/Case-Study-Karte im Viewport (einmal pro Session)
    "case_study_click",   # Klick auf Projekt-Link (Nachweise/Gebaute Systeme; label = Projektname)
    "demo_clicked",       # Live-Demo geöffnet (hero | invoiceflow | offerai | mailagent)
    "roi_calculated",     # ROI-Rechner ausgelöst (UI folgt; API/Event ist bereit)
    "lead_created",       # Kontaktanfrage erfolgreich gespeichert (Lead in CRM)
    # Landingpage-Events (LUMINA-Spez, Branchen-Seiten) — data-track-Attribute
    "hero_cta_click",     # Hero-Primär-CTA auf Landingpages
    "quickwin_cta_click", # Quick-Win-Karten-CTA (Angebot/Termine)
    "erechnung_cta_click",# E-Rechnung-CTA (Stufe 3, Dringlichkeit)
    "faq_open",           # FAQ-Accordion geöffnet
    "check_cta_click",    # Stufe-0-CTA (5-Minuten-Check) im FAQ-Fuß
    "form_start",         # Erstes Input im Kontakt-/Buchungsformular
    "form_submit",        # Formular abgeschickt (Client-Event, serverseitige Conversions bleiben Quelle der Wahrheit)
    # ROI-Rechner (LUMINA UX-Spez) — reine Dashboard-Signale, nie Lead-Wahrheit
    "roi_slider_start",   # Erste Slider-Interaktion im ROI-Rechner (1×/Session)
    "roi_calculated",     # Rechner-Ergebnis als BUCKET (h_lt_150 | h_150_400 | h_gt_400)
    "roi_cta_click",      # Personalisierter Ergebnis-CTA (Bucket im Label)
    # Formular-Feedback (DSGVO-konformer Demo-/Booking-Pfad, Client-Events)
    "form_field_error",   # Feldvalidierung fehlgeschlagen (Client)
    "form_success_view",  # Erfolgsansicht nach Formular-Abschluss sichtbar (Client)
    # Issue #16 (Customer-First-Konsolidierung): Navigation, Zielgruppen-Profile,
    # Wissensbereich — neue Interaktionen der kundenorientierten IA messbar.
    # Mappings: docs/ANALYTICS_EVENTS.md §8 (Kanonische Labels für Profile A–E,
    # Wissen-Säulen, Artikel-Nächster-Schritt). Keine Breaking-Change an bestehenden
    # Events — diese fünf ergänzen die Taxonomie, damit die neuen Strukturen
    # (Nav „Für wen“/„Wissen“, Zielgruppen-Profile, /wissen-Säulen + Artikel-CTAs)
    # ab dem ersten Release messbar sind.
    "nav_click",              # Hauptnavigation geklickt (header .site-nav a; label = Ziel, z. B. fuer-wen|wissen)
    "target_group_viewed",    # Zielgruppen-Profil-Karte im Viewport (1×/Session; label = Profil-Slug A–E)
    "target_group_click",     # Klick auf Zielgruppen-Profil/-CTA (label = Profil-Slug A–E)
    "article_cta_clicked",    # Wissen-Artikel: „nächster Schritt“ geklickt (label = potenzial-check|prozess|branche|demo)
    "wissen_pillar_click",    # /wissen: Säulen-Interaktion (label = praxis-prozesse|branchen|datenschutz-kontrolle|kosten-entscheidung|technik-erklaert)
})

MAX_EVENT_BODY = 8192      # Payload-Limit (Bytes) — verhindert Missbrauch
MAX_PROPS_CHARS = 2000     # props-JSON-Limit in der DB

_FIELD_LIMITS = {
    "page": 255,
    "session_id": 64,
    "source": 120,
    "medium": 60,
    "campaign": 160,
    "referrer": 512,
}


def _clean(value, limit):
    """String bereinigen + kappen (leere Werte → '')."""
    if value is None:
        return ""
    return str(value).strip()[:limit]


def _record_event(event, props=None, page=None, session_id=None,
                  source=None, medium=None, campaign=None, referrer=None):
    """Serverseitig ein Analytics-Event schreiben (z. B. Conversion).

    Wird von app/blueprints/public.py für lead_created / demo_completed /
    meeting_booked aufgerufen — die Conversions sind an den DB-Write des
    Formulars gekoppelt und gehen nie verloren (auch ohne JS-Client).
    """
    if event not in ANALYTICS_EVENTS:
        return None

    row = AnalyticsEvent(
        event=event,
        page=_clean(page, _FIELD_LIMITS["page"]),
        session_id=_clean(session_id, _FIELD_LIMITS["session_id"]),
        source=_clean(source, _FIELD_LIMITS["source"]),
        medium=_clean(medium, _FIELD_LIMITS["medium"]),
        campaign=_clean(campaign, _FIELD_LIMITS["campaign"]),
        referrer=_clean(referrer, _FIELD_LIMITS["referrer"]),
        props=json.dumps(props, ensure_ascii=False)[:MAX_PROPS_CHARS] if props else "",
        user_agent=_clean(request.user_agent.string if request else "", 255),
    )
    db.session.add(row)
    db.session.commit()
    return row


def _parse_payload():
    """Payload aus JSON-Body oder Formularfeldern lesen (dict oder None)."""
    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None
        return data
    # sendBeacon-Fallback / Form-encoded: Felder direkt aus dem Formular lesen
    props_raw = request.form.get("props", "")
    props = {}
    if props_raw:
        try:
            props = json.loads(props_raw)
        except (TypeError, ValueError):
            props = {}
    return {
        "event": request.form.get("event", ""),
        "page": request.form.get("page", ""),
        "session_id": request.form.get("session_id", ""),
        "source": request.form.get("source", ""),
        "medium": request.form.get("medium", ""),
        "campaign": request.form.get("campaign", ""),
        "referrer": request.form.get("referrer", ""),
        "props": props,
    }


@analytics_bp.route("/event", methods=["POST"])
@limiter.limit("120 per minute")
def event():
    """Anonymes Event entgegennehmen und speichern.

    Erfolg: 204 No Content (sendBeacon-kompatibel). Bei ungültigen Events
    ebenfalls 204, damit der Client keine Fehlerbehandlung braucht und
    kein Retry-Loop entsteht — ungültige Daten werden still verworfen.
    """
    if request.content_length and request.content_length > MAX_EVENT_BODY:
        return jsonify({"success": False, "error": "payload_too_large"}), 413

    data = _parse_payload()
    if not data:
        return jsonify({"success": False, "error": "invalid_json"}), 400

    event_name = _clean(data.get("event"), 64)
    if event_name not in ANALYTICS_EVENTS:
        # Unbekannte Events: still verwerfen (kein 4xx — kein Client-Retry)
        return "", 204

    props = data.get("props") or {}
    if not isinstance(props, dict):
        return jsonify({"success": False, "error": "invalid_props"}), 400

    try:
        props_json = json.dumps(props, ensure_ascii=False)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "invalid_props"}), 400
    if len(props_json) > MAX_PROPS_CHARS:
        return jsonify({"success": False, "error": "props_too_large"}), 413

    _record_event(
        event=event_name,
        props=props,
        page=data.get("page"),
        session_id=data.get("session_id"),
        source=data.get("source"),
        medium=data.get("medium"),
        campaign=data.get("campaign"),
        referrer=data.get("referrer"),
    )
    return "", 204
