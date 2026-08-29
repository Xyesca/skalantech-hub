"""QA-Gate lokaler Launcher (nur für SENTINEL-Tests, Port 5099, loopback-only)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/sentinel_smoke.db")
os.environ.setdefault("RATELIMIT_STORAGE_URI", "memory://")
os.environ.setdefault("WTF_CSRF_ENABLED", "false")

from app import create_app
app = create_app("production")
app.config.update(WTF_CSRF_ENABLED=False)
app.run(host="127.0.0.1", port=5099, debug=False, use_reloader=False)
