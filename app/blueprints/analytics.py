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

ANALYTICS_EVENTS = frozenset({
    "page_view",
    "demo_started",
    "demo_completed",
    "contact_clicked",
    "calendar_opened",
    "meeting_booked",
    "booking_error",
    "booking_confirmed",
    "service_viewed",
    "case_study_viewed",
    "case_study_click",
    "demo_clicked",
    "roi_calculated",
    "lead_created",
    "hero_cta_click",
    "quickwin_cta_click",
    "erechnung_cta_click",
    "faq_open",
    "check_cta_click",
    "form_start",
    "form_submit",
    "roi_slider_start",
    "roi_cta_click",
    "form_field_error",
    "form_success_view",
    # AI Consultant: nur Funnel-Metadaten, niemals Nachrichteninhalt speichern.
    "chat_opened",
    "chat_message_sent",
    "chat_reply_received",
    "chat_action_clicked",
    "chat_error",
})

MAX_EVENT_BODY = 8192
MAX_PROPS_CHARS = 2000

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
    """Serverseitig ein Analytics-Event schreiben."""
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
    """Anonymes Event entgegennehmen und speichern."""
    if request.content_length and request.content_length > MAX_EVENT_BODY:
        return jsonify({"success": False, "error": "payload_too_large"}), 413

    data = _parse_payload()
    if not data:
        return jsonify({"success": False, "error": "invalid_json"}), 400

    event_name = _clean(data.get("event"), 64)
    if event_name not in ANALYTICS_EVENTS:
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
