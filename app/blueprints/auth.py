"""Skalantech Hub — Authentication routes."""
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
)
from werkzeug.security import check_password_hash

from app.extensions import db, limiter, csrf
from app.models import Admin

auth_bp = Blueprint("auth", __name__)

_LOCKOUT_MINUTES = 5
_MAX_ATTEMPTS = 5


def _safe_next_url(default_endpoint: str = "admin.settings") -> str:
    """Verhindert Open-Redirect via next-Parameter."""
    next_url = request.args.get("next", "")
    if not next_url:
        return url_for(default_endpoint)
    parsed = urlparse(next_url)
    if parsed.netloc:
        return url_for(default_endpoint)
    if next_url.startswith("//"):
        return url_for(default_endpoint)
    return next_url


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
@csrf.exempt
def login():
    if session.get("logged_in"):
        return redirect(url_for("admin.settings"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()

        if admin:
            # ── Locked? ──────────────────────────────────────────────
            if admin.locked_until and admin.locked_until > datetime.now(timezone.utc):
                flash("Konto temporär gesperrt. Bitte später erneut versuchen.", "error")
                return render_template("login.html"), 429

            if check_password_hash(admin.password_hash, password):
                # Success — reset counters
                admin.failed_attempts = 0
                admin.locked_until = None
                admin.last_login = datetime.now(timezone.utc)
                db.session.commit()

                session.clear()
                session["logged_in"] = True
                session["username"] = admin.username
                session.permanent = True

                next_url = _safe_next_url()
                return redirect(next_url)

            # Failed — increment counter
            admin.failed_attempts = (admin.failed_attempts or 0) + 1
            if admin.failed_attempts >= _MAX_ATTEMPTS:
                admin.locked_until = datetime.now(timezone.utc) + timedelta(minutes=_LOCKOUT_MINUTES)
            db.session.commit()

        flash("Benutzername oder Passwort falsch.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.index"))
