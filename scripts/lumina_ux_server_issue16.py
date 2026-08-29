"""LUMINA-UX-Server für Issue #16 (loopback 5099, Worktree-Version)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/issue16_ux.db")
os.environ.setdefault("RATELIMIT_STORAGE_URI", "memory://")
os.environ.setdefault("WTF_CSRF_ENABLED", "false")

from app import create_app  # noqa: E402

app = create_app("production")
app.config.update(WTF_CSRF_ENABLED=False)
app.run(host="127.0.0.1", port=5098, debug=False, use_reloader=False)
