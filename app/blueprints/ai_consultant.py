"""Skalantech AI Consultant — guarded website chat endpoint.

The browser only talks to Flask. If ``N8N_AI_CONSULTANT_WEBHOOK_URL`` is set,
Flask forwards a small, validated payload to the internal n8n workflow. When
n8n is unavailable or not configured, a deterministic local consultant keeps
the widget useful without exposing infrastructure or requiring an LLM key in
the web application.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from urllib import request as urlrequest

from flask import Blueprint, jsonify, request

from app.extensions import limiter

consultant_bp = Blueprint("ai_consultant", __name__)

MAX_MESSAGE_LENGTH = 1500
MAX_PAGE_LENGTH = 160
N8N_AI_CONSULTANT_WEBHOOK_URL = os.environ.get(
    "N8N_AI_CONSULTANT_WEBHOOK_URL", ""
).strip()

_CONVERSATION_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
_ALLOWED_INTERNAL_ACTION_PREFIXES = (
    "/demos",
    "/automationen",
    "/#termin",
    "/websites-apps",
    "/it-infrastruktur",
    "/ki-integration",
    "/ki-agenten",
    "/n8n-automatisierung",
)

CONSULTANT_POLICY = (
    "Du bist der Skalantech AI Consultant. Antworte kurz, konkret und auf Deutsch. "
    "Analysiere den beschriebenen Geschäftsprozess, nenne einen sinnvollen nächsten "
    "Automationsschritt und verweise nur auf reale Skalantech-Angebote oder Demos. "
    "Erfinde keine Kunden, Mitarbeiter, Preise, Einsparungen, Referenzen oder Fähigkeiten. "
    "Behaupte nicht, ein Mensch zu sein. Bitte niemals um Passwörter, Zugangsdaten, "
    "Gesundheitsdaten oder andere vertrauliche Informationen. Bei Kaufinteresse darfst du "
    "die 30-minütige Business-Analyse empfehlen."
)


def _clean_text(value: object, limit: int) -> str:
    text = " ".join(str(value or "").strip().split())
    return text[:limit]


def _conversation_id(value: object) -> str:
    candidate = _clean_text(value, 64)
    if candidate and _CONVERSATION_RE.fullmatch(candidate):
        return candidate
    return uuid.uuid4().hex


def _safe_action(action: object) -> dict | None:
    """Accept only same-site actions from an n8n response."""
    if not isinstance(action, dict):
        return None
    label = _clean_text(action.get("label"), 80)
    url = _clean_text(action.get("url"), 180)
    if not label or not url:
        return None
    if not any(url == prefix or url.startswith(prefix + "#") for prefix in _ALLOWED_INTERNAL_ACTION_PREFIXES):
        return None
    return {"label": label, "url": url}


def _normalise_orchestrated_response(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    reply = _clean_text(payload.get("reply"), 3000)
    if not reply:
        return None
    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list):
        suggestions = []
    clean_suggestions = [
        _clean_text(item, 90) for item in suggestions[:3] if _clean_text(item, 90)
    ]
    return {
        "reply": reply,
        "suggestions": clean_suggestions,
        "action": _safe_action(payload.get("action")),
    }


def _call_n8n(message: str, conversation_id: str, page: str) -> dict | None:
    if not N8N_AI_CONSULTANT_WEBHOOK_URL:
        return None

    payload = {
        "message": message,
        "conversation_id": conversation_id,
        "page": page,
        "channel": "skalantech-web",
        "language": "de",
        "policy": CONSULTANT_POLICY,
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urlrequest.Request(
        N8N_AI_CONSULTANT_WEBHOOK_URL,
        data=raw,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=25) as response:
            body = response.read(32768).decode("utf-8", errors="replace")
            if response.status >= 400:
                return None
            return _normalise_orchestrated_response(json.loads(body))
    except Exception:
        return None


def _fallback_response(message: str) -> dict:
    """Useful, truthful response when the n8n/LLM path is not available."""
    text = message.casefold()

    if any(word in text for word in ("rechnung", "invoice", "buchhaltung", "beleg")):
        return {
            "reply": (
                "Das eignet sich häufig für einen Ablauf wie: Eingang → Daten extrahieren → "
                "prüfen → strukturiert an Buchhaltung oder ERP übergeben. Skalantech zeigt "
                "dieses Muster bereits mit InvoiceFlow."
            ),
            "suggestions": ["Wie würde die Integration aussehen?", "Welche Daten werden extrahiert?"],
            "action": {"label": "InvoiceFlow live testen", "url": "/demos#invoiceflow"},
        }

    if any(word in text for word in ("e-mail", "email", "mail", "postfach", "nachricht")):
        return {
            "reply": (
                "Ein sinnvoller Prozess ist: E-Mail → klassifizieren → relevante Daten erkennen → "
                "CRM/Aufgabe erzeugen → Antwort zur Freigabe vorbereiten. Genau dieses Muster "
                "demonstriert MailAgent."
            ),
            "suggestions": ["Kann das mit meinem CRM verbunden werden?", "Wie funktioniert die Freigabe?"],
            "action": {"label": "MailAgent live testen", "url": "/demos#mailagent"},
        }

    if any(word in text for word in ("angebot", "anfrage", "kalkulation", "angebotserstellung")):
        return {
            "reply": (
                "Dafür lässt sich ein Workflow aufbauen, der Anfragen strukturiert, fehlende Angaben "
                "erkennt und einen prüfbaren Angebotsentwurf vorbereitet. Die finale Freigabe bleibt "
                "beim Menschen."
            ),
            "suggestions": ["Welche Daten braucht der Workflow?", "Kann ich eine Demo sehen?"],
            "action": {"label": "OfferAI live testen", "url": "/demos#offerai"},
        }

    if any(word in text for word in ("crm", "lead", "follow-up", "followup", "kunde", "vertrieb")):
        return {
            "reply": (
                "Skalantech kann den Weg vom Erstkontakt bis zum Follow-up verbinden: Formular oder "
                "E-Mail → Qualifizierung → CRM → Aufgabe → Nachfassen. Entscheidend sind Ihre "
                "bestehenden Systeme und die verfügbaren Schnittstellen."
            ),
            "suggestions": ["Wir nutzen bereits ein CRM", "Welche Systeme lassen sich anbinden?"],
            "action": {"label": "Automationsbeispiele ansehen", "url": "/automationen"},
        }

    if any(word in text for word in ("n8n", "self-host", "selfhost", "docker", "api", "webhook")):
        return {
            "reply": (
                "Skalantech setzt je nach Anforderung auf n8n, APIs, Webhooks, Python, Docker und "
                "Self-Hosting. Ziel ist nicht möglichst viel KI, sondern ein nachvollziehbarer, "
                "wartbarer Prozess mit klaren Fehler- und Freigabepfaden."
            ),
            "suggestions": ["Was kann n8n automatisieren?", "Ist Self-Hosting möglich?"],
            "action": {"label": "Automationen ansehen", "url": "/automationen"},
        }

    if any(word in text for word in ("preis", "kosten", "termin", "beratung", "projekt", "starten")):
        return {
            "reply": (
                "Der Aufwand hängt vom Prozess, den Schnittstellen und den Betriebsanforderungen ab. "
                "In der kostenlosen 30-minütigen Business-Analyse lässt sich der Engpass zuerst "
                "technisch einordnen, bevor ein konkreter Umsetzungsvorschlag entsteht."
            ),
            "suggestions": ["Was soll ich für den Termin vorbereiten?", "Welche Prozesse lohnen sich zuerst?"],
            "action": {"label": "Business-Analyse anfragen", "url": "/#termin"},
        }

    return {
        "reply": (
            "Beschreiben Sie mir am besten einen konkreten Ablauf, der heute manuell Zeit kostet. "
            "Hilfreich sind: Was löst ihn aus, welche Software ist beteiligt, welche Daten werden "
            "übertragen und was soll am Ende passieren? Bitte keine vertraulichen Daten eingeben."
        ),
        "suggestions": [
            "Rechnungen automatisch verarbeiten",
            "E-Mails ins CRM übertragen",
            "Angebote vorbereiten",
        ],
        "action": {"label": "Live-Demos ansehen", "url": "/demos"},
    }


@consultant_bp.route("/api/ai-consultant/message", methods=["POST"])
@limiter.limit("30 per hour")
def message():
    if not request.is_json:
        return jsonify(success=False, message="JSON erwartet."), 415

    payload = request.get_json(silent=True) or {}
    message_text = _clean_text(payload.get("message"), MAX_MESSAGE_LENGTH + 1)
    if len(message_text) < 2:
        return jsonify(success=False, message="Bitte geben Sie eine kurze Frage ein."), 400
    if len(message_text) > MAX_MESSAGE_LENGTH:
        return jsonify(success=False, message="Bitte maximal 1.500 Zeichen eingeben."), 400

    conversation_id = _conversation_id(payload.get("conversation_id"))
    page = _clean_text(payload.get("page"), MAX_PAGE_LENGTH)
    if not page.startswith("/"):
        page = "/"

    result = _call_n8n(message_text, conversation_id, page)
    source = "n8n"
    if result is None:
        result = _fallback_response(message_text)
        source = "local"

    return jsonify(
        success=True,
        conversation_id=conversation_id,
        reply=result["reply"],
        suggestions=result.get("suggestions", []),
        action=result.get("action"),
        source=source,
    )
