"""Skalantech Hub — Public routes."""
import os
import smtplib
import time
from email.mime.text import MIMEText

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, redirect, url_for, jsonify
from app.models import Settings, Link, Project, ContactMessage
from app.extensions import db

public_bp = Blueprint("public", __name__)

# ── Contact form rate-limiting (in-memory, single-instance) ──────────────
_CONTACT_LIMITS: dict[str, list[float]] = {}
_CONTACT_MAX = 3          # max messages per IP
_CONTACT_WINDOW = 3600    # sliding window in seconds (1 hour)


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
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message_text = request.form.get("message", "").strip()

    # ── Validierung ──────────────────────────────────────────────────
    errors = []
    if not name:
        errors.append("Bitte gib deinen Namen ein.")
    if not email or "@" not in email or len(email) > 254:
        errors.append("Bitte gib eine gültige E-Mail-Adresse ein.")
    if not message_text:
        errors.append("Bitte gib eine Nachricht ein.")
    if len(message_text) > 5000:
        errors.append("Nachricht ist zu lang (max. 5000 Zeichen).")

    # ── Rate-Limiting ────────────────────────────────────────────────
    if not errors:
        ip = _client_ip()
        if not _check_contact_limit(ip):
            errors.append("Zu viele Anfragen. Bitte versuche es später erneut.")

    if errors:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message='; '.join(errors)), 400
        for err in errors:
            flash(err, "error")
        return redirect(url_for("public.index", _anchor="contact"))

    # ── Speichern + optional E-Mail ──────────────────────────────────
    msg = ContactMessage(name=name, email=email, message=message_text)
    db.session.add(msg)
    db.session.commit()

    _send_email(name, email, message_text)  # silent — don't block on failure

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True, message='Nachricht erfolgreich gesendet!')
    flash("Nachricht erfolgreich gesendet. Ich melde mich bald!", "success")
    return redirect(url_for("public.index", _anchor="contact"))


@public_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve user-uploaded media from the instance/uploads directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
