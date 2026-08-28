"""Skalantech Hub — CRM API (maschinenlesbar für n8n & Hermes-Automation).

Auth: X-API-Key Header, Wert aus Umgebungsvariable CRM_API_KEY.
CSRF ist hier nicht anwendbar (kein Browser-Session) — der Blueprint wird
in der App-Factory per csrf.exempt() freigeschaltet.
"""
import hmac
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Lead, Booking, PIPELINE_STAGES, PIPELINE_TERMINAL

crm_api_bp = Blueprint("crm_api", __name__, url_prefix="/api/crm")

CRM_API_KEY = os.environ.get("CRM_API_KEY", "")

_MAX_LEADS = 200


def _utcnow():
    return datetime.now(timezone.utc)


def _parse_dt(value):
    """ISO-8601 (ggf. mit 'Z') oder 'YYYY-MM-DD' → datetime (UTC)."""
    if not value:
        return None
    v = str(value).strip()
    try:
        if len(v) == 10 and v.count("-") == 2:  # reines Datum → Tagesbeginn UTC
            return datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None


@crm_api_bp.before_request
def _require_api_key():
    provided = request.headers.get("X-API-Key", "")
    if not CRM_API_KEY or not hmac.compare_digest(provided, CRM_API_KEY):
        return jsonify({"success": False, "error": "Unauthorized"}), 401


def _apply_fields(lead: Lead, data: dict) -> None:
    """Übertrage erlaubte Felder auf den Lead (kein Overwrite leerer Strings)."""
    for field, limit in (
        ("name", 120), ("company", 160), ("phone", 60),
        ("service", 120), ("source", 120), ("medium", 60),
        ("campaign", 160), ("referrer", 512),
    ):
        value = (data.get(field) or "").strip()
        if value:
            setattr(lead, field, value[:limit])

    if data.get("message"):
        lead.message = str(data["message"]).strip()[:5000]

    if data.get("value_estimate") is not None:
        try:
            lead.value_estimate = max(0, int(data["value_estimate"]))
        except (TypeError, ValueError):
            pass

    for field in ("next_followup_at", "last_contact_at"):
        if data.get(field):
            parsed = _parse_dt(data[field])
            if parsed is not None:
                setattr(lead, field, parsed)

    new_status = (data.get("status") or "").strip().lower()
    if new_status and new_status in PIPELINE_STAGES and new_status != lead.status:
        reason = (data.get("lost_reason") or data.get("note") or "")[:200]
        lead.set_status(new_status, reason=reason, author="API")

    note = (data.get("note") or "").strip()
    if note:
        # Statuswechsel erzeugt bereits eine Notiz — nur zusätzliche Notiz anhängen
        lead.add_note(note, author="API")


@crm_api_bp.route("/bookings/reserve", methods=["POST"])
def reserve_booking():
    """Atomare Slot-Reservierung (concurrency-sicher, Google-frei).

    Nutzt den UNIQUE-Constraint auf ``bookings.start_at_utc``: der INSERT
    schlägt fehl (IntegrityError), wenn der Slot bereits vergeben ist.
    Kein SELECT-then-INSERT — die DB ist die atomare Sperre.

    Body (JSON): start_at_utc (ISO 8601, UTC), end_at_utc, name, email,
    company?, topic?, booking_id? (optional, sonst UUID), lead_id? (optional)
    """
    data = request.get_json(silent=True) or {}

    start_raw = (data.get("start_at_utc") or "").strip()
    end_raw = (data.get("end_at_utc") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    errors = []
    start_dt = _parse_dt(start_raw)
    end_dt = _parse_dt(end_raw)
    if start_dt is None:
        errors.append("start_at_utc ist erforderlich (ISO-8601)")
    if end_dt is None:
        errors.append("end_at_utc ist erforderlich (ISO-8601)")
    if not name or len(name) > 120:
        errors.append("name ist erforderlich (max. 120 Zeichen)")
    if not email or "@" not in email or len(email) > 254:
        errors.append("email ist erforderlich (gültige Adresse)")
    if errors:
        return jsonify({"success": False, "booked": False, "errors": errors}), 400

    company = (data.get("company") or "").strip()[:160]
    topic = (data.get("topic") or "Erstgespräch").strip()[:120]
    booking_id = (data.get("booking_id") or str(uuid.uuid4())).strip()[:64]
    lead_id = data.get("lead_id")

    booking = Booking(
        booking_id=booking_id,
        start_at_utc=start_dt,
        end_at_utc=end_dt,
        timezone="Europe/Berlin",
        name=name,
        email=email,
        company=company,
        topic=topic,
        status="confirmed",
        lead_id=lead_id if isinstance(lead_id, int) else None,
    )
    db.session.add(booking)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "booked": False,
            "message": "Der gewünschte Termin ist leider bereits belegt. Bitte wählen Sie eine andere Zeit.",
        }), 409

    return jsonify({
        "success": True,
        "booked": True,
        "booking_id": booking.booking_id,
        "start_at_utc": booking.start_at_utc.isoformat(),
        "end_at_utc": booking.end_at_utc.isoformat(),
    }), 201


@crm_api_bp.route("/bookings", methods=["GET"])
def list_bookings():
    """Buchungen auflisten (für E2E-Tests & Admin). Filter: status=…"""
    query = Booking.query
    status = (request.args.get("status") or "").strip().lower()
    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.start_at_utc.asc()).limit(200).all()
    return jsonify({
        "success": True,
        "count": len(bookings),
        "bookings": [b.to_dict() for b in bookings],
    })


@crm_api_bp.route("/bookings/<booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    """Buchung löschen (nur für Tests/Aufräumen)."""
    booking = Booking.query.filter_by(booking_id=booking_id).first()
    if booking is None:
        return jsonify({"success": False, "error": "Not found"}), 404
    db.session.delete(booking)
    db.session.commit()
    return jsonify({"success": True, "deleted": booking_id})


@crm_api_bp.route("/leads", methods=["POST"])
def create_lead():
    """Lead anlegen oder per E-Mail aktualisieren (idempotent für Automation)."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    errors = []
    if not name or len(name) > 120:
        errors.append("name ist erforderlich (max. 120 Zeichen)")
    if not email or "@" not in email or len(email) > 254:
        errors.append("email ist erforderlich (gültige Adresse)")
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    lead = Lead.query.filter_by(email=email, is_archived=False).first()
    created = lead is None
    if created:
        lead = Lead(name=name, email=email)
        db.session.add(lead)
        db.session.flush()  # id benötigt für Status-Notizen (lead_id FK)

    _apply_fields(lead, data)
    if created and not lead.status:
        lead.status = "lead"

    db.session.commit()
    return jsonify({
        "success": True,
        "created": created,
        "id": lead.id,
        "status": lead.status,
    }), (201 if created else 200)


@crm_api_bp.route("/leads/<int:lead_id>", methods=["PATCH"])
def update_lead(lead_id):
    """Bestehenden Lead aktualisieren (Status, Follow-up, Felder, Notiz)."""
    lead = db.get_or_404(Lead, lead_id)
    data = request.get_json(silent=True) or {}
    _apply_fields(lead, data)
    db.session.commit()
    return jsonify({"success": True, "id": lead.id, "status": lead.status, "lead": lead.to_dict()})


@crm_api_bp.route("/leads")
def list_leads():
    """Leads auflisten. Filter: status=…, due_followup=1 (fällig + nicht terminiert)."""
    query = Lead.query

    status = (request.args.get("status") or "").strip().lower()
    if status:
        query = query.filter_by(status=status)

    if request.args.get("due_followup") in {"1", "true", "yes"}:
        query = query.filter(
            Lead.is_archived.is_(False),
            Lead.status.notin_(PIPELINE_TERMINAL),
            Lead.next_followup_at.isnot(None),
            Lead.next_followup_at <= _utcnow(),
        )

    if request.args.get("archived") != "1":
        query = query.filter(Lead.is_archived.is_(False))

    leads = query.order_by(Lead.created_at.desc()).limit(_MAX_LEADS).all()
    return jsonify({
        "success": True,
        "count": len(leads),
        "leads": [lead.to_dict() for lead in leads],
    })


@crm_api_bp.route("/leads/<int:lead_id>")
def get_lead(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    data = lead.to_dict()
    data["notes"] = [
        {"body": n.body, "author": n.author,
         "created_at": n.created_at.isoformat() if n.created_at else None}
        for n in lead.notes
    ]
    return jsonify({"success": True, "lead": data})


@crm_api_bp.route("/health")
def health():
    return jsonify({"success": True, "service": "skalantech-crm"})


@crm_api_bp.errorhandler(404)
def _handle_404(_e):
    return jsonify({"success": False, "error": "Not found"}), 404
