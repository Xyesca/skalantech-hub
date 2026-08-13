"""Skalantech Hub — Public routes."""
import os
import smtplib
import time
from email.mime.text import MIMEText

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, redirect, url_for, jsonify, Response
from app.models import Settings, Link, Project, ContactMessage
from app.extensions import db

public_bp = Blueprint("public", __name__)

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
    return render_template("index.html", settings=settings, links=links, projects=projects)


@public_bp.route("/robots.txt")
def robots_txt():
    """Serve crawler instructions from the canonical application route."""
    content = "User-agent: *\nAllow: /\n\nSitemap: https://skalantech.store/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@public_bp.route("/sitemap.xml")
def sitemap_xml():
    """Small, explicit sitemap for indexable public pages."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://skalantech.store/</loc><priority>1.0</priority></url>
  <url><loc>https://skalantech.store/faq</loc><priority>0.6</priority></url>
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

@public_bp.route("/test-footer")
def test_footer():
    """Minimale Testseite nur für Footer-Diagnose."""
    return render_template("test-footer.html")

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

    msg = ContactMessage(name=name, email=email, message=stored_message)
    db.session.add(msg)
    db.session.commit()

    _send_email(name, email, stored_message)  # silent — don't block on failure

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True, message='Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.')
    flash("Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.", "success")
    return redirect(url_for("public.index", _anchor="contact"))


@public_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve user-uploaded media from the instance/uploads directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
