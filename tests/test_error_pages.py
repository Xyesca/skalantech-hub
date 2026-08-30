"""Regression tests: öffentliche Fehlerseiten leaken keine Secrets/Interna.

DoD-Punkt „keine Secrets/Env in öffentlichen Fehlerseiten“ (t_9b14d915).
- 404-Seite: generisch, kein Traceback, keine Env-Werte, keine Pfade.
- 500-Handler: generische Seite statt Debug-Traceback.
"""
import os
import sys
import tempfile
import unittest


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class ErrorPageLeakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "leak-test-super-secret-value-42"
        os.environ["ADMIN_PASSWORD"] = "leak-test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"
        os.environ["RATELIMIT_STORAGE_URI"] = "memory://"  # hermetisch; zentraler Storage (Redis) wird in test_ratelimit_storage.py getestet

        _drop_app_modules()
        from app import create_app

        cls.app = create_app("production")
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        # Fehler-Handler testen (nicht Exceptions propagieren lassen)
        cls.app.config["PROPAGATE_EXCEPTIONS"] = False

        # Route, die eine Exception wirft → 500-Handler testen.
        # Muss VOR dem ersten Request registriert werden (Flask-Regel).
        @cls.app.route("/__test_boom")
        def boom():
            raise RuntimeError("sensitiver interner Fehler: key=leak-test-super-secret-value-42")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def _forbidden_substrings(self):
        return [
            "Traceback",
            "leak-test-super-secret-value-42",   # SECRET_KEY-Wert
            "leak-test-admin-password",          # ADMIN_PASSWORD-Wert
            os.environ["DATABASE_URL"],          # DB-Pfad
            "/skalantech-hub/",                  # Repo-Pfad
            "gunicorn",
            "werkzeug",
            "sqlalchemy",
            "File \"",
            "line 1",
        ]

    def test_404_page_is_generic(self):
        response = self.client.get("/definitiv-nicht-vorhanden-abc123")
        self.assertEqual(response.status_code, 404)
        html = response.get_data(as_text=True)
        self.assertIn("Diese Seite gibt es nicht.", html)
        for needle in self._forbidden_substrings():
            with self.subTest(needle=needle):
                self.assertNotIn(needle, html)

    def test_500_handler_returns_generic_page_without_leaks(self):
        response = self.client.get("/__test_boom")
        self.assertEqual(response.status_code, 500)
        html = response.get_data(as_text=True)
        self.assertIn("Etwas ist schiefgelaufen.", html)
        for needle in self._forbidden_substrings():
            with self.subTest(needle=needle):
                self.assertNotIn(needle, html)

    def test_security_headers_on_error_pages(self):
        # Fehlerseiten durchlaufen den after_request-Hook (Security-Header)
        for path in ("/definitiv-nicht-vorhanden-abc123",):
            response = self.client.get(path)
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
            self.assertIn("frame-ancestors 'none'", response.headers.get("Content-Security-Policy", ""))
