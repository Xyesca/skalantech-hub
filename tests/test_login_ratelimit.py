"""Regression: Brute-Force-Schutz auf /login (Rate-Limit + Lockout).

SENTINEL-Härtung t_3124abb3: /login POST wird mit 5/min limitiert
(methods=["POST"], memory://-Storage = pro gunicorn-Worker; primärer Schutz
ist der Account-Lockout: 5 Fehlversuche → 5 min Sperre, DB-basiert/shared).
In Tests (TESTING=True) ist das Limit via exempt_when deaktiviert — dieser
Test setzt TESTING=False, um den echten Limiter-Pfad zu prüfen.
"""
import os
import sys
import tempfile
import unittest


def _drop_app_modules():
    """Entferne gecachte app-Module, damit DATABASE_URL/Env je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class LoginRateLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"

        _drop_app_modules()
        from app import create_app

        # TESTING=False → Limiter aktiv (exempt_when greift nur bei TESTING=True)
        cls.app = create_app("production")
        cls.app.config.update(TESTING=False, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def _post_login(self):
        return self.client.post(
            "/login",
            data={"username": "admin", "password": "wrong-password"},
        )

    def test_login_post_gets_rate_limited(self):
        """Mehr als 5 Login-POSTs innerhalb einer Minute → 429 (Rate-Limit oder Lockout)."""
        statuses = [self._post_login().status_code for _ in range(7)]
        # Die ersten Antworten sind 200 (Login-Seite mit Flash), danach muss
        # der Schutz greifen: 429 vom Limiter oder vom Account-Lockout.
        limited = [s for s in statuses if s == 429]
        self.assertGreaterEqual(len(limited), 1, f"kein 429 nach 7 Versuchen: {statuses}")

    def test_login_get_not_rate_limited(self):
        """GET /login (Seitenaufruf) wird NICHT gezählt — Limit nur auf POST."""
        statuses = [self.client.get("/login").status_code for _ in range(8)]
        self.assertTrue(all(s == 200 for s in statuses), f"GET wurde limitiert: {statuses}")


if __name__ == "__main__":
    unittest.main()
