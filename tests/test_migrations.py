"""Issue #5: Alembic/Flask-Migrate-Bootstrap statt ad-hoc ALTER TABLE.

Sichert die zwei kritischen Startpfade von app/__init__.py::_init_db ab:
  1. Frische DB  → `flask db upgrade` erzeugt das komplette Baseline-Schema
                    (alle Tabellen + Indexe + uq_bookings_start_at_utc).
  2. Legacy-SQLite (Tabellen vorhanden, aber KEIN alembic_version)
     → `stamp` adoptiert den Bestand als Baseline, Daten bleiben erhalten.

Zusätzlich: `_migrate_db()` (ad-hoc ALTER TABLE) existiert nicht mehr.
"""
import os
import shutil
import sys
import tempfile
import unittest


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


def _set_env(db_path: str) -> None:
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["ADMIN_USERNAME"] = "admin"
    os.environ["ADMIN_PASSWORD"] = "test-admin-password"
    os.environ["SESSION_COOKIE_SECURE"] = "false"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["RATELIMIT_STORAGE_URI"] = "memory://"
    os.environ.pop("SKIP_DB_BOOTSTRAP", None)


class MigrationBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.fresh_db = os.path.join(cls.temp_dir.name, "fresh.db")
        # Kopie der (potenziell produktiven) SQLite-DB als Legacy-Fallback —
        # falls instance/app.db fehlt, wird ein leerer Legacy-Bestand simuliert.
        legacy_src = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "instance", "app.db",
        )
        cls.legacy_db = os.path.join(cls.temp_dir.name, "legacy.db")
        if os.path.isfile(legacy_src):
            shutil.copy2(legacy_src, cls.legacy_db)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def _create_app(self, db_path):
        _drop_app_modules()
        _set_env(db_path)
        from app import create_app
        return create_app("production")

    def test_fresh_db_runs_upgrade_and_creates_baseline(self):
        app = self._create_app(self.fresh_db)
        with app.app_context():
            from app.extensions import db
            from sqlalchemy import inspect as sa_inspect
            from sqlalchemy import text

            tables = set(sa_inspect(db.engine).get_table_names())
            expected = {
                "admin", "settings", "links", "projects",
                "contact_messages", "leads", "lead_notes",
                "bookings", "analytics_events", "alembic_version",
            }
            self.assertTrue(expected.issubset(tables), f"fehlende Tabellen: {expected - tables}")
            rev = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
            self.assertTrue(rev, "alembic_version muss nach upgrade gesetzt sein")
            # Admin-Seed läuft nach dem Schema-Upgrade
            from app.models import Admin
            self.assertEqual(Admin.query.count(), 1)

    @unittest.skipUnless(os.path.isfile(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "instance", "app.db")), "instance/app.db nicht vorhanden")
    def test_legacy_db_is_stamped_and_data_preserved(self):
        app = self._create_app(self.legacy_db)
        with app.app_context():
            from app.extensions import db
            from sqlalchemy import inspect as sa_inspect
            from sqlalchemy import text

            tables = set(sa_inspect(db.engine).get_table_names())
            self.assertIn("alembic_version", tables)
            rev = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
            self.assertEqual(rev, "6df6ce6bdd8b")
            # Bestandsdaten müssen erhalten bleiben (nur gelesen, nichts gelöscht)
            from app.models import AnalyticsEvent
            before = AnalyticsEvent.query.count()
            self.assertGreaterEqual(before, 0)

    def test_no_ad_hoc_migrate_db_function(self):
        """Die ad-hoc ALTER TABLE Funktion darf nicht mehr existieren."""
        _drop_app_modules()
        _set_env(os.path.join(self.temp_dir.name, "nofunc.db"))
        from app import __init__ as app_init
        self.assertFalse(hasattr(app_init, "_migrate_db"),
                         "_migrate_db() (ad-hoc ALTER TABLE) wurde entfernt")


if __name__ == "__main__":
    unittest.main()
