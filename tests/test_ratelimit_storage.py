"""Issue #4: Zentrales Rate-Limiting — Redis-Storage statt memory://.

Verifiziert die Multi-Worker-Sicherheit (gunicorn -w 4):

1. ProductionConfig nutzt Redis als Rate-Limit-Storage (Default), NICHT
   memory:// — damit teilen sich alle Worker denselben Counter.
2. Der Counter lebt in Redis: eine zweite App-Instanz (= zweiter Worker bzw.
   Worker-Restart) sieht den bereits verbrauchten Stand → 9. Request einer
   IP auf /api/demos (Limit 8/h) wird 429, obwohl die ersten 8 Requests auf
   zwei verschiedene App-Instanzen verteilt waren.

Hermetik: Die restliche Test-Suite nutzt memory:// (per Testklasse gesetzt).
Dieser Test nutzt Redis-DB 15 (nicht DB 0 der Produktion) und eine zufällige
Test-IP pro Lauf → keine Interferenz mit echten Rate-Limit-Countern.
Ist kein Redis erreichbar (lokale Entwicklung ohne Container), werden die
Storage-Tests übersprungen — die Config-Assertions laufen immer.
"""
import os
import random
import sys
import tempfile
import unittest
from unittest import mock

REDIS_URI = os.environ.get("TEST_RATELIMIT_REDIS_URI", "redis://127.0.0.1:6379/15")


def _drop_app_modules():
    """Entferne gecachte app-Module, damit Env/Config je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


def _redis_reachable() -> bool:
    try:
        import redis as redis_lib

        client = redis_lib.Redis.from_url(REDIS_URI, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


REDIS_REACHABLE = _redis_reachable()


def _make_app():
    """Frische App-Instanz (simuliert einen gunicorn-Worker)."""
    _drop_app_modules()
    from app import create_app

    app = create_app("production")
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app


class RateLimitStorageConfigTests(unittest.TestCase):
    """Production nutzt Redis als zentralen Storage (kein memory://)."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"
        # Default (kein explizites Override) prüfen:
        os.environ.pop("RATELIMIT_STORAGE_URI", None)

        cls.app = _make_app()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_production_storage_defaults_to_redis(self):
        """ProductionConfig: RATELIMIT_STORAGE_URI zeigt auf Redis (zentral)."""
        uri = self.app.config["RATELIMIT_STORAGE_URI"]
        self.assertTrue(
            uri.startswith("redis://"),
            f"Production muss Redis als Rate-Limit-Storage nutzen, war: {uri!r}",
        )

    def test_limiter_storage_is_redis_backed(self):
        """Der aktive Limiter-Storage ist RedisStorage (nicht MemoryStorage)."""
        from app.extensions import limiter
        from limits.storage.redis import RedisStorage

        self.assertIsInstance(limiter._storage, RedisStorage)

    def test_strategy_is_moving_window(self):
        """Gleitendes Fenster — keine Window-Boundary-Effekte bei 3/h."""
        self.assertEqual(self.app.config["RATELIMIT_STRATEGY"], "moving-window")


@unittest.skipUnless(REDIS_REACHABLE, f"Redis nicht erreichbar ({REDIS_URI})")
class RateLimitCrossWorkerTests(unittest.TestCase):
    """Limits greifen über App-Instanzen hinweg (= über gunicorn-Worker)."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"
        os.environ["RATELIMIT_STORAGE_URI"] = REDIS_URI

        # Test-DB 15 leeren (Produktions-DB 0 bleibt unberührt).
        import redis as redis_lib

        redis_lib.Redis.from_url(REDIS_URI).flushdb()

        cls.app_a = _make_app()
        cls.app_b = _make_app()

        # Zufällige Test-IP → eigener Redis-Key, keine Kollision mit echten
        # Countern oder anderen Testläufen.
        cls.test_ip = f"198.51.100.{random.randint(2, 254)}"

        # n8n-Demo-Proxy hermetisch mocken (kein echter n8n-Aufruf).
        from app.blueprints import automation_showcase as showcase

        cls._orig_call = showcase._call_internal_demo
        showcase._call_internal_demo = lambda slug, value: {
            "success": True, "result": {"ok": True},
        }

    @classmethod
    def tearDownClass(cls):
        from app.blueprints import automation_showcase as showcase

        showcase._call_internal_demo = cls._orig_call
        cls.temp_dir.cleanup()

    def _post_demo(self, client):
        return client.post(
            "/api/demos/invoiceflow",
            data={"input": "Rechnung RE-2026-001 vom 27.08.2026 über 100,00 Euro netto."},
            headers={"X-Forwarded-For": self.test_ip},
        )

    def test_limit_shared_across_app_instances(self):
        """8 Requests verteilt auf 2 App-Instanzen erlaubt; 9. → 429.

        App A = Worker 1, App B = Worker 2: Der Redis-Counter ist geteilt,
        daher greift das 8/h-Limit exakt ab dem 9. Request — unabhängig
        davon, welcher Worker den Request verarbeitet.
        """
        client_a = self.app_a.test_client()
        client_b = self.app_b.test_client()

        # 4 Requests über Worker A, 4 über Worker B → 8 insgesamt, erlaubt.
        for _ in range(4):
            self.assertEqual(self._post_demo(client_a).status_code, 200)
            self.assertEqual(self._post_demo(client_b).status_code, 200)

        # 9. Request (Worker A) überschreitet das 8/h-Limit → 429.
        limited = self._post_demo(client_a)
        self.assertEqual(limited.status_code, 429)
        self.assertFalse(limited.get_json()["success"])

        # Auch Worker B blockt jetzt — der Counter ist zentral, nicht pro
        # Prozess.
        limited_b = self._post_demo(client_b)
        self.assertEqual(limited_b.status_code, 429)

    def test_counter_survives_app_recreation(self):
        """Counter überlebt Worker-Restart: frischer Worker siehts Limit."""
        # Vorab: neues Limit-Fenster über eigene IP aufbauen.
        fresh_ip = f"203.0.113.{random.randint(2, 254)}"
        client = self.app_a.test_client()
        for _ in range(8):
            r = client.post(
                "/api/demos/offerai",
                data={"input": "Bitte skizzieren Sie ein Angebot für unsere Kanzlei mit 12 Mitarbeitern."},
                headers={"X-Forwarded-For": fresh_ip},
            )
            self.assertEqual(r.status_code, 200)

        # App neu bauen (= Worker-Restart), gleicher Redis-Storage.
        app_new = _make_app()
        client_new = app_new.test_client()
        r = client_new.post(
            "/api/demos/offerai",
            data={"input": "Bitte skizzieren Sie ein Angebot für unsere Kanzlei mit 12 Mitarbeitern."},
            headers={"X-Forwarded-For": fresh_ip},
        )
        self.assertEqual(r.status_code, 429, "Counter muss den Worker-Restart überleben")


if __name__ == "__main__":
    unittest.main()
