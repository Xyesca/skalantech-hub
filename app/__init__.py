"""Skalantech Hub — Application Factory."""
import os
import secrets

from flask import Flask, flash, redirect, request, url_for
from markupsafe import Markup
from flask_wtf.csrf import CSRFError

from app.config import config_map
from app.extensions import db, csrf, limiter
from app.utils.security import add_security_headers

# ── Icon SVGs (inline for zero-dependency rendering) ──────────────────────
ICONS = {
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56 0-.27-.01-1.17-.02-2.13-3.2.7-3.88-1.36-3.88-1.36-.52-1.34-1.28-1.69-1.28-1.69-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.03 1.78 2.71 1.26 3.37.97.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.18 1.18a10.9 10.9 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.77.11 3.06.74.81 1.19 1.83 1.19 3.09 0 4.42-2.7 5.39-5.27 5.68.41.36.78 1.06.78 2.15 0 1.55-.01 2.8-.01 3.18 0 .31.21.67.8.56C20.21 21.38 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 5.82c-.92-.8-1.5-1.96-1.6-3.27h-3.1v13.6c0 1.67-1.36 3.02-3.03 3.02a3.03 3.03 0 0 1-3.03-3.02 3.03 3.03 0 0 1 3.03-3.03c.3 0 .58.04.85.12V10.1a6.3 6.3 0 0 0-.85-.06A6.18 6.18 0 0 0 3.65 16.2 6.18 6.18 0 0 0 9.87 22.4a6.18 6.18 0 0 0 6.18-6.18V9.1a8.3 8.3 0 0 0 4.85 1.55V7.55a4.9 4.9 0 0 1-4.3-1.73z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="2.5" width="19" height="19" rx="5"/><circle cx="12" cy="12" r="4.3"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "app": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.5"/></svg>',
    "website": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M9.5 14.5l5-5M8.2 16.8l-1.4 1.4a3.5 3.5 0 0 1-5-5l2.8-2.8a3.5 3.5 0 0 1 5-.1M15.8 7.2l1.4-1.4a3.5 3.5 0 0 1 5 5l-2.8 2.8a3.5 3.5 0 0 1-5 .1"/></svg>',
}


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # Ensure required directories
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    instance_dir = os.path.join(os.path.dirname(app.root_path), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # ── Security headers on every response ────────────────────────────────
    app.after_request(add_security_headers)

    # ── CSRF error handler ────────────────────────────────────────────────
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        flash("Sitzung abgelaufen. Bitte Seite neu laden.", "error")
        return redirect(request.referrer or url_for("public.index")), 400

    # ── Template globals ──────────────────────────────────────────────────
    @app.template_global()
    def icon_svg(platform: str) -> Markup:
        return Markup(ICONS.get(platform, ICONS["link"]))

    # ── Register blueprints ───────────────────────────────────────────────
    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # ── Database bootstrap ────────────────────────────────────────────────
    with app.app_context():
        _migrate_db()
        db.create_all()
        _ensure_admin()

    return app


def _migrate_db() -> None:
    """Add missing columns to existing SQLite tables (lightweight migration)."""
    import sqlite3

    db_path = db.engine.url.database
    if not db_path or not os.path.isfile(db_path):
        return  # fresh database — create_all() will handle it

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    migrations = [
        ("admin", "last_login",      "DATETIME"),
        ("admin", "failed_attempts", "INTEGER DEFAULT 0"),
        ("admin", "locked_until",    "DATETIME"),
        ("admin", "created_at",      "DATETIME"),
        ("admin", "updated_at",      "DATETIME"),
        ("settings", "updated_at",   "DATETIME"),
        ("links", "created_at",      "DATETIME"),
        ("projects", "created_at",   "DATETIME"),
    ]

    for table, column, col_type in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except sqlite3.OperationalError:
            pass  # column already exists

    conn.commit()
    conn.close()


def _ensure_admin() -> None:
    """Create the default admin user when the database is fresh."""
    from app.models import Admin
    from werkzeug.security import generate_password_hash

    if Admin.query.count() == 0:
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD")
        if not password:
            password = secrets.token_urlsafe(12)
            print("=" * 60)
            print(f"  Kein ADMIN_PASSWORD in .env gefunden.")
            print(f"  Temporäres Passwort für '{username}': {password}")
            print("  Bitte in .env setzen und Container neu starten!")
            print("=" * 60)
        db.session.add(Admin(
            username=username,
            password_hash=generate_password_hash(password),
        ))
        db.session.commit()
