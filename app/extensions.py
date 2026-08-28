"""Skalantech Hub — Flask Extensions (centralised init)."""
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
csrf = CSRFProtect()

# Zentrales Rate-Limiting (Issue #4): KEIN storage_uri im Konstruktor setzen —
# sonst gewinnt der Konstruktor-Wert in init_app() und die App-Config
# (RATELIMIT_STORAGE_URI) wird ignoriert. Ohne storage_uri liest init_app()
# die Config: Production → Redis (shared über alle gunicorn-Worker),
# Development/Tests → memory:// (hermetisch). Siehe app/config.py.
limiter = Limiter(key_func=get_remote_address)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record):
    """SQLite: WAL + busy_timeout für concurrency-sichere Schreibzugriffe.

    Ohne WAL/busy_timeout kann eine parallele Doppelbuchung mit
    ``database is locked`` scheitern, statt sauber am UNIQUE-Constraint
    abgewiesen zu werden.
    """
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
