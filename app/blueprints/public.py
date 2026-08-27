"""Skalantech Hub — Public routes."""
import json
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from urllib import request as urlrequest

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, redirect, url_for, jsonify, Response, abort
from app.models import Settings, Link, Project, ContactMessage, Lead
from app.extensions import db
from app.seo_pages import LANDING_PAGES, LANDING_ORDER
from app.wissen import ARTICLES, ARTICLE_ORDER, ARTICLE_PUBLISHED
from app.blueprints.analytics import _record_event

public_bp = Blueprint("public", __name__)

# ── n8n-Terminwebhook (intern, Tailscale) ─────────────────────────────
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/skalantech-termin")

# ── SEO: indexierbare Seiten für Sitemap & robots ──────────────────────
SITE_URL = "https://skalantech.store"

SITEMAP_PAGES = [
    {"loc": "/", "priority": "1.0"},
    *[{"loc": f"/{slug}", "priority": "0.8"} for slug in LANDING_ORDER],
    {"loc": "/wissen", "priority": "0.7"},
    *[{"loc": f"/wissen/{slug}", "priority": "0.7"} for slug in ARTICLE_ORDER],
    {"loc": "/faq", "priority": "0.6"},
]

ROBOTS_TXT = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /login
Disallow: /auth
Disallow: /test-footer

Sitemap: {SITE_URL}/sitemap.xml
"""


def _forward_to_n8n(name, email, company, topic, message, preferred_day, preferred_time):
    """Send a booking request to the n8n workflow. Returns dict(success, message)."""
    payload = {
        "name": name,
        "email": email,
        "company": company,
        "topic": topic or "Erstgespräch",
        "message": message,
        "preferred_day": preferred_day,
        "preferred_time": preferred_time,
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                parsed = None
            # Nur ein explizites success:true im JSON zählt als Buchung.
            # n8n liefert bei internen Workflow-Fehlern (z. B. Kalender-Credential
            # abgelaufen) HTTP 200 mit leerem/Fehler-Body — das wäre sonst eine
            # falsche meeting_booked-Conversion und eine falsche Nutzer-Bestätigung.
            if parsed is None or resp.status >= 400 or parsed.get("success") is not True:
                message = parsed.get("message", "Terminanfrage abgelehnt.") if isinstance(parsed, dict) else "Termindienst hat keine gültige Antwort geliefert."
                return {"success": False, "message": f"{message} Anfrage wurde gespeichert."}
            return {"success": True, "message": parsed.get("message", "ok")}
    except Exception as exc:
        # n8n nicht erreichbar — Anfrage bleibt in der DB, kein Block für den Nutzer
        return {"success": False, "message": f"Termindienst nicht erreichbar ({type(exc).__name__}). Anfrage wurde gespeichert."}

# ── Contact form rate-limiting (in-memory, single-instance) ──────────────
_CONTACT_LIMITS: dict[str, list[float]] = {}
_CONTACT_MAX = 3          # max messages per IP
_CONTACT_WINDOW = 3600    # sliding window in seconds (1 hour)

_SERVICE_CHOICES = {
    "Infrastruktur & Cloud",
    "Prozessautomatisierung",
    "KI-Agenten & RAG",
    "Betrieb & Reliability",
    "System-Check / Beratung",
    "Erstgespräch",
    "Etwas anderes",
}


def _client_ip() -> str:
    """Get real client IP behind reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _check_contact_limit(ip: str) -> bool:
    """Sliding-window rate limit. Returns True if allowed."""
    now = time.time()
    window_start = now - _CONTACT_WINDOW

    timestamps = _CONTACT_LIMITS.get(ip, [])
    # Prune old entries
    timestamps = [t for t in timestamps if t > window_start]

    if len(timestamps) >= _CONTACT_MAX:
        _CONTACT_LIMITS[ip] = timestamps
        return False

    timestamps.append(now)
    _CONTACT_LIMITS[ip] = timestamps
    return True


def _send_email(name: str, email: str, text: str) -> bool:
    """Send contact notification via Gmail SMTP. Returns True on success."""
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_pass:
        return False  # SMTP not configured — just save to DB

    msg = MIMEText(
        f"Neue Kontaktanfrage von {name} ({email}):\n\n{text}",
        "plain", "utf-8",
    )
    msg["Subject"] = f"Skalantech Kontakt: {name}"
    msg["From"] = gmail_user
    msg["To"] = gmail_user

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, [gmail_user], msg.as_string())
        return True
    except Exception:
        return False


@public_bp.route("/")
def index():
    settings = Settings.get()
    links = (
        Link.query
        .filter_by(visible=True)
        .order_by(Link.position.asc(), Link.id.asc())
        .all()
    )
    projects = (
        Project.query
        .filter_by(visible=True)
        .order_by(Project.position.asc(), Project.id.asc())
        .all()
    )
    today = time.strftime("%Y-%m-%d")
    max_booking_day = time.strftime("%Y-%m-%d", time.localtime(time.time() + 90 * 86400))
    return render_template("index.html", settings=settings, links=links, projects=projects, today=today, max_booking_day=max_booking_day)


# ── SEO Landingpages (eine View, mehrere explizite Routen) ────────────────
def _landing_map():
    """Landing-Daten + fertige URLs für Templates."""
    return {
        s: {**p, "slug": s, "url": url_for(f"public.landing_{s.replace('-', '_')}")}
        for s, p in LANDING_PAGES.items()
    }


def _render_landing(slug: str):
    """Render a SEO landing page from seo_pages.py."""
    if slug not in LANDING_PAGES:
        abort(404)
    page = LANDING_PAGES[slug]
    page = {**page, "slug": slug, "url": url_for(f"public.landing_{slug.replace('-', '_')}")}
    return render_template(
        "landing.html",
        landing_page=page,
        landing_map=_landing_map(),
    )


@public_bp.route("/it-infrastruktur")
def landing_it_infrastruktur():
    return _render_landing("it-infrastruktur")


@public_bp.route("/ki-integration")
def landing_ki_integration():
    return _render_landing("ki-integration")


@public_bp.route("/ki-automatisierung")
def landing_ki_automatisierung():
    return _render_landing("ki-automatisierung")


@public_bp.route("/ki-agenten")
def landing_ki_agenten():
    return _render_landing("ki-agenten")


@public_bp.route("/n8n-automatisierung")
def landing_n8n_automatisierung():
    return _render_landing("n8n-automatisierung")


@public_bp.route("/lokale-ki")
def landing_lokale_ki():
    return _render_landing("lokale-ki")


# ── Wissensstruktur ────────────────────────────────────────────────────
@public_bp.route("/wissen")
def wissen():
    return render_template(
        "wissen.html",
        article_map=ARTICLES,
        article_order=ARTICLE_ORDER,
        article_published=ARTICLE_PUBLISHED,
        landing_map=_landing_map(),
    )


@public_bp.route("/wissen/<slug>")
def article(slug: str):
    if slug not in ARTICLES:
        abort(404)
    article_data = {**ARTICLES[slug], "slug": slug}
    return render_template(
        "article.html",
        article_data=article_data,
        article_published=ARTICLE_PUBLISHED,
        landing_map=_landing_map(),
    )


@public_bp.route("/robots.txt")
def robots_txt():
    """Serve crawler instructions from the canonical application route."""
    return Response(ROBOTS_TXT, mimetype="text/plain")


@public_bp.route("/sitemap.xml")
def sitemap_xml():
    """Sitemap generated from the explicit indexable-pages list."""
    today = time.strftime("%Y-%m-%d")
    urls = "\n".join(
        f'  <url><loc>{SITE_URL}{p["loc"]}</loc><lastmod>{today}</lastmod><priority>{p["priority"]}</priority></url>'
        for p in SITEMAP_PAGES
    )
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""
    return Response(content, mimetype="application/xml")


# ── Legal Pages ──────────────────────────────────────────────────────
@public_bp.route("/impressum")
def impressum():
    settings = Settings.get()
    return render_template("legal/impressum.html", settings=settings)

@public_bp.route("/datenschutz")
def datenschutz():
    settings = Settings.get()
    return render_template("legal/datenschutz.html", settings=settings)

@public_bp.route("/agb")
def agb():
    settings = Settings.get()
    return render_template("legal/agb.html", settings=settings)

@public_bp.route("/faq")
def faq():
    settings = Settings.get()
    return render_template("legal/faq.html", settings=settings)

@public_bp.route("/contact", methods=["POST"])
def contact():
    name = " ".join(request.form.get("name", "").split())
    email = request.form.get("email", "").strip()
    company = " ".join(request.form.get("company", "").split())
    service = request.form.get("service", "").strip()
    message_text = request.form.get("message", "").strip()
    privacy = request.form.get("privacy", "")
    honeypot = request.form.get("website", "").strip()

    # Quietly accept obvious bot submissions without storing or sending them.
    if honeypot:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=True, message="Vielen Dank. Ihre Anfrage wurde übermittelt.")
        return redirect(url_for("public.index", _anchor="contact"))

    # ── Validierung ──────────────────────────────────────────────────
    errors = []
    if not name or len(name) > 120:
        errors.append("Bitte geben Sie einen gültigen Namen ein.")
    if not email or "@" not in email or len(email) > 254:
        errors.append("Bitte geben Sie eine gültige E-Mail-Adresse ein.")
    if len(company) > 160:
        errors.append("Der Unternehmensname ist zu lang.")
    if service and service not in _SERVICE_CHOICES:
        errors.append("Bitte wählen Sie ein gültiges Anliegen aus.")
    if not message_text:
        errors.append("Bitte beschreiben Sie kurz Ihre Ausgangslage.")
    if len(message_text) > 5000:
        errors.append("Nachricht ist zu lang (max. 5000 Zeichen).")
    if privacy != "accepted":
        errors.append("Bitte bestätigen Sie die Datenschutzerklärung.")

    # ── Rate-Limiting ────────────────────────────────────────────────
    if not errors:
        ip = _client_ip()
        if not _check_contact_limit(ip):
            errors.append("Zu viele Anfragen. Bitte versuchen Sie es später erneut.")

    if errors:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message='; '.join(errors)), 400
        for err in errors:
            flash(err, "error")
        return redirect(url_for("public.index", _anchor="contact"))

    # ── Speichern + optional E-Mail ──────────────────────────────────
    context = []
    if company:
        context.append(f"Unternehmen: {company}")
    if service:
        context.append(f"Anliegen: {service}")
    stored_message = "\n".join(context + ([""] if context else []) + [message_text])

    # First-Party-Attribution: UTM-Parameter + Referrer (keine Cookies,
    # kein Tracker — nur technische Metadaten dieser einen Anfrage).
    # analytics.js legt die beim Seitenaufruf erfassten UTM-/Session-Werte
    # als Hidden-Fields ins Formular (Fallback: Query-String des POST).
    session_id = (request.form.get("session_id") or request.args.get("session_id") or "").strip()[:64]
    source = (request.form.get("utm_source") or request.args.get("utm_source") or "").strip()[:120]
    medium = (request.form.get("utm_medium") or request.args.get("utm_medium") or "").strip()[:60]
    campaign = (request.form.get("utm_campaign") or request.args.get("utm_campaign") or "").strip()[:160]
    referrer = (request.referrer or "").strip()[:512]

    msg = ContactMessage(
        name=name, email=email, message=stored_message,
        source=source, medium=medium, campaign=campaign, referrer=referrer,
        session_id=session_id,
    )
    db.session.add(msg)

    # ── CRM: Lead aus der Kontaktanfrage erzeugen/aktualisieren ──────
    # Dedupe per E-Mail — wiederholte Anfragen aktualisieren denselben Lead.
    lead = Lead.query.filter_by(email=email, is_archived=False).first()
    if lead is None:
        lead = Lead(name=name, email=email, status="lead", session_id=session_id)
        db.session.add(lead)
    elif not lead.session_id:
        # First-Touch: Session nur setzen, wenn noch keine bekannt ist
        lead.session_id = session_id
    lead.company = company
    lead.service = service
    lead.message = message_text
    if source:
        lead.source = source
    if medium:
        lead.medium = medium
    if campaign:
        lead.campaign = campaign
    if referrer:
        lead.referrer = referrer
    lead.last_contact_at = datetime.now(timezone.utc)
    db.session.commit()

    # ── Analytics: Conversion-Events (serverseitig — verlustsicher, auch
    # ohne JavaScript-Client; Spezifikation: docs/ANALYTICS_EVENTS.md) ──
    _attribution = dict(
        page="/", session_id=session_id,
        source=source, medium=medium, campaign=campaign, referrer=referrer,
    )
    _record_event("lead_created", props={"service": service or "allgemein"}, **_attribution)

    _send_email(name, email, stored_message)  # silent — don't block on failure

    # ── Terminanfrage: Webhook an n8n (nur bei Terminwunsch) ─────────
    n8n_result = None
    if request.form.get("book_slot") == "1":
        # Anfrage angenommen (unabhängig vom n8n-Status) = Demo-Flow abgeschlossen
        _record_event("demo_completed", props={"service": "Erstgespräch"}, **_attribution)
        n8n_result = _forward_to_n8n(
            name=name, email=email, company=company,
            topic=service or "Erstgespräch", message=message_text,
            preferred_day=request.form.get("preferred_day", "").strip(),
            preferred_time=request.form.get("preferred_time", "").strip(),
        )
        # Erfolgreiche Buchung = qualifizierter Lead (Discovery folgt im Termin)
        if n8n_result and n8n_result.get("success"):
            if lead.status != "qualified":
                lead.set_status("qualified", reason="Termin über skalantech.store gebucht", author="Website")
            day = request.form.get("preferred_day", "").strip()
            slot = request.form.get("preferred_time", "").strip()
            lead.add_note(f"Terminwunsch bestätigt: {day} {slot}".strip(), author="Website")
            lead.last_contact_at = datetime.now(timezone.utc)
            db.session.commit()
            # n8n hat bestätigt = echte Buchung
            _record_event(
                "meeting_booked",
                props={"day": day, "time": slot, "service": "Erstgespräch"},
                **_attribution,
            )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if n8n_result is not None and not n8n_result.get("success"):
            return jsonify(success=False, message=n8n_result.get("message", "Der Terminwunsch konnte nicht verarbeitet werden. Ihre Anfrage wurde trotzdem gespeichert.")), 409
        return jsonify(success=True, message='Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.')
    flash("Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.", "success")
    return redirect(url_for("public.index", _anchor="contact"))


@public_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve user-uploaded media from the instance/uploads directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
