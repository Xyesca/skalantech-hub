"""Regression: Brute-Force-Schutz auf /login (Rate-Limit + Lockout).

SENTINEL-Härtung t_3124abb3 + Issue #4: /login POST wird mit 5/min limitiert
(methods=["POST"]). Storage ist zentral (Redis in Production, shared über
alle gunicorn-Worker — exakt 5/min/IP, kein Pro-Worker-Aufweichen). Primärer
Schutz bleibt der Account-Lockout (5 Fehlversuche → 5 min Sperre, DB-basiert).

Dieser Test ist hermetisch: RATELIMIT_STORAGE_URI=memory:// (die zentrale
Redis-Sharing-Semantik wird in tests/test_ratelimit_storage.py getestet).
TESTING=False aktiviert den echten Limiter-Pfad.
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
        os.environ["RATELIMIT_STORAGE_URI"] = "memory://"  # hermetisch; zentraler Storage (Redis) wird in test_ratelimit_storage.py getestet

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
        """Mehr als 5 Login-POSTs innerhalb einer Minute → abgewiesen.

        Ab dem 6. Versuch greift der zentrale Limiter (5/min, Redis in
        Production): der RateLimitExceeded-Handler leitet Browser-Flows mit
        Flash auf die Herkunftsseite weiter (302; API-Clients bekämen 429).
        Zusätzlich sperrt der Account-Lockout (DB-basiert) nach 5 Fehlversuchen
        für 5 Minuten. Beide Schutzschichten zählen als Abweisung.
        """
        statuses = [self._post_login().status_code for _ in range(7)]
        # Erlaubt sind maximal 5 Versuche (200 = Login-Seite mit Flash).
        # Alles danach muss abgewiesen sein: 302 (Limiter-Redirect) oder 429
        # (Lockout / Limiter-Default).
        allowed = [s for s in statuses if s == 200]
        rejected = [s for s in statuses if s in (302, 429)]
        self.assertLessEqual(
            len(allowed), 5, f"zu viele erlaubte Versuche: {statuses}"
        )
        self.assertGreaterEqual(
            len(rejected), 1, f"keine Abweisung nach 7 Versuchen: {statuses}"
        )

    def test_login_get_not_rate_limited(self):
        """GET /login (Seitenaufruf) wird NICHT gezählt — Limit nur auf POST."""
        statuses = [self.client.get("/login").status_code for _ in range(8)]
        self.assertTrue(all(s == 200 for s in statuses), f"GET wurde limitiert: {statuses}")


if __name__ == "__main__":
    unittest.main()
