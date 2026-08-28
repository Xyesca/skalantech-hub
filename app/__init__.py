"""Skalantech Hub — Application Factory."""
import mimetypes
import os
import secrets
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from markupsafe import Markup
from flask_wtf.csrf import CSRFError
from flask_limiter.errors import RateLimitExceeded

from app.config import config_map
from app.extensions import db, csrf, limiter, migrate
from app.utils.security import add_security_headers

BASE_DIR = Path(__file__).resolve().parent.parent

# ── MIME types ─────────────────────────────────────────────────────────────
# Flask/Python's mimetypes may not map .webp on minimal systems — register explicitly.
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")

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

    # Trust the Caddy reverse proxy (X-Forwarded-Proto/For) so Flask treats
    # requests behind TLS as secure — required for SESSION_COOKIE_SECURE + CSRF.
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Ensure required directories
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    instance_dir = os.path.join(os.path.dirname(app.root_path), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    # Alembic-Migrationen (Issue #5): versionierte Schema-Migrationen statt
    # ad-hoc ALTER TABLE beim Start. Das Migrationsverzeichnis (migrations/)
    # liegt im Repo und wird mit dem Code deployed. Absoluter Pfad, damit
    # upgrade()/stamp() unabhängig vom Working-Directory funktionieren
    # (gunicorn startet in /app, CLI-Tools ggf. woanders).
    migrate.init_app(app, db, directory=str(BASE_DIR / "migrations"))

    # ── Security headers on every response ────────────────────────────────
    app.after_request(add_security_headers)

    # ── CSRF error handler ────────────────────────────────────────────────
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        flash("Sitzung abgelaufen. Bitte Seite neu laden.", "error")
        return redirect(request.referrer or url_for("public.index")), 400

    # ── Rate-Limit error handler (zentrales Rate-Limiting, Issue #4) ─────
    # API-/AJAX-Clients bekommen ein sauberes 429-JSON; Browser-Formulare
    # werden mit Flash-Meldung zurück auf die Seite geleitet (bestehende UX).
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e: RateLimitExceeded):
        message = "Zu viele Anfragen. Bitte versuchen Sie es später erneut."
        wants_json = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.path.startswith("/api/")
            or request.path.startswith("/analytics/")
        )
        if wants_json:
            return jsonify(success=False, message=message), 429
        flash(message, "error")
        return redirect(request.referrer or url_for("public.index"))

    # ── 404 error handler (SEO: echte 404s mit Auswegen statt toten Seiten) ─
    @app.errorhandler(404)
    def handle_404(e):
        return render_template("404.html"), 404

    # ── 500 error handler: generische Seite, keine Interna/Stack/Env leaken.
    # Der Exception-Stacktrace wird von Flask trotzdem geloggt (docker logs)
    # und ist vom öffentlichen Response entkoppelt. DEBUG ist in Production
    # aus (config.py) — doppelte Absicherung gegen Debug-Tracebacks.
    @app.errorhandler(500)
    def handle_500(e):
        return render_template("500.html"), 500

    # ── Template globals ──────────────────────────────────────────────────
    @app.template_global()
    def icon_svg(platform: str) -> Markup:
        return Markup(ICONS.get(platform, ICONS["link"]))

    # ── Register blueprints ───────────────────────────────────────────────
    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.crm_api import crm_api_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.automation_showcase import showcase_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(crm_api_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(showcase_bp)
    # CRM-API ist maschinell (n8n/Hermes) — Auth via X-API-Key statt CSRF.
    csrf.exempt(crm_api_bp)
    # Analytics-Beacon (sendBeacon/fetch ohne Session-Token) — stattdessen
    # Event-Allowlist, Payload-Limit und Rate-Limit im Blueprint.
    csrf.exempt(analytics_bp)
    # Öffentliche Live-Demos (POST /api/demos/<slug>) — Browser-Besucher
    # haben kein Session-Token; Schutz stattdessen über Allowlist (nur
    # bekannte Slugs), Input-Länge, Rate-Limit (8/h/IP) und n8n-Loopback.
    csrf.exempt(showcase_bp)

    # ── Template global: fällige Follow-ups für die Admin-Sidebar ─────────
    @app.context_processor
    def inject_crm_stats():
        from datetime import datetime, timezone
        from app.models import Lead, PIPELINE_TERMINAL

        due = 0
        if request.endpoint and request.endpoint.startswith("admin"):
            try:
                due = Lead.query.filter(
                    Lead.is_archived.is_(False),
                    Lead.status.notin_(PIPELINE_TERMINAL),
                    Lead.next_followup_at.isnot(None),
                    Lead.next_followup_at <= datetime.now(timezone.utc),
                ).count()
            except Exception:
                due = 0
        return {"crm_due_count": due}

    # ── Database bootstrap ────────────────────────────────────────────────
    # Issue #5: Schema kommt aus versionierten Alembic-Migrationen
    # (migrations/), NICHT aus ad-hoc ALTER TABLE beim Start. Bestehende
    # SQLite-Bestände (ohne alembic_version) werden als Baseline übernommen
    # (stamp head) — ihre Tabellen entsprechen bereits den Modellen
    # (create_all + die alten ALTER-Statements haben sie synchron gehalten).
    # SKIP_DB_BOOTSTRAP=1 lässt CLI-Werkzeuge (flask db init/migrate) die App
    # importieren, ohne die Datenbank anzufassen.
    if os.environ.get("SKIP_DB_BOOTSTRAP") != "1":
        with app.app_context():
            _init_db()
            _ensure_admin()

    return app


def _init_db() -> None:
    """Flask-Migrate-Bootstrap: frisch → upgrade, verwaltet → upgrade,
    Alt-Bestand ohne alembic_version → stamp (adopt as baseline)."""
    from flask_migrate import upgrade, stamp
    from sqlalchemy import inspect as sa_inspect

    inspector = sa_inspect(db.engine)
    tables = set(inspector.get_table_names())

    if not tables:
        # Frische Datenbank: Baseline-Migration anwenden (erzeugt alles).
        upgrade()
        return
    if "alembic_version" not in tables:
        # Legacy-SQLite-Bestand: Schema entspricht bereits den Modellen →
        # als Baseline stempeln, damit künftige Migrationen sauber andocken.
        stamp()
        return
    upgrade()


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
