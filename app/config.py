"""Skalantech Hub — Configuration Classes"""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Shared configuration defaults."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "50")) * 1024 * 1024

    # ── Security ──────────────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "skalantech_session"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # CSRF: SSL_STRICT abschalten — die Website ist über Caddy zwingend
    # HTTPS-only (HSTS + Redirect). SSL_STRICT bricht sonst jeden Formular-POST,
    # sobald request.is_secure in Proxy-/Healthcheck-Kontexten False ist.
    WTF_CSRF_SSL_STRICT = False

    # ── Uploads ───────────────────────────────────────────────────────────
    UPLOAD_FOLDER = str(BASE_DIR / "instance" / "uploads")
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_VIDEO_EXT = {"mp4", "webm", "mov"}

    # ── Rate limiting ─────────────────────────────────────────────────────
    RATELIMIT_STORAGE_URI = "memory://"


class ProductionConfig(BaseConfig):
    """Production — strict security."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "true").strip().lower()
        in {"1", "true", "yes", "on"}
    )
    PREFERRED_URL_SCHEME = "https"

    SEND_FILE_MAX_AGE_DEFAULT = 604800


class DevelopmentConfig(BaseConfig):
    """Development — relaxed for local work."""
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    SESSION_COOKIE_SECURE = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": ProductionConfig,
}
