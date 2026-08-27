"""Regression tests for the first-party, cookie-less analytics pipeline.

Deckt den kompletten Event-Flow ab:
  Client (Beacon)  →  POST /analytics/event  →  analytics_events (SQLite)
  Formular (POST)  →  serverseitige Conversion-Events (lead_created,
                      demo_completed, meeting_booked) inkl. Session-/UTM-Attribution

Hermetisch: keine app-Importe auf Modulebene, damit die Datei unabhängig von
der Ausführungsreihenfolge (test_crm.py & Co. cachen app-Module mit eigener
DATABASE_URL) gegen die eigene Test-DB läuft.
"""
import importlib
import json
import os
import sys
import tempfile
import unittest


def _drop_app_modules():
    """Entferne gecachte app-Module, damit DATABASE_URL/Env je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class AnalyticsEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"

        _drop_app_modules()
        from app import create_app
        from app.models import AnalyticsEvent, ContactMessage, Lead

        cls.app = create_app("production")
        cls.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
        )
        cls.AnalyticsEvent = AnalyticsEvent
        cls.ContactMessage = ContactMessage
        cls.Lead = Lead
        cls.public_module = importlib.import_module("app.blueprints.public")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            self.AnalyticsEvent.query.delete()
            self.ContactMessage.query.delete()
            self.Lead.query.delete()
            from app.extensions import db

            db.session.commit()

    def _events(self):
        with self.app.app_context():
            return self.AnalyticsEvent.query.order_by(self.AnalyticsEvent.id.asc()).all()

    def _post_event(self, payload, headers=None):
        headers = dict(headers or {})
        headers.setdefault("Content-Type", "application/json")
        return self.client.post("/analytics/event", data=json.dumps(payload), headers=headers)

    # ── Endpoint ────────────────────────────────────────────────────────

    def test_valid_event_is_stored(self):
        response = self._post_event({
            "event": "page_view",
            "page": "/",
            "session_id": "sess-abc-123",
            "source": "google",
            "medium": "organic",
            "campaign": "seo",
            "props": {"foo": "bar"},
        })
        self.assertEqual(response.status_code, 204)

        events = self._events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event, "page_view")
        self.assertEqual(events[0].page, "/")
        self.assertEqual(events[0].session_id, "sess-abc-123")
        self.assertEqual(events[0].source, "google")
        self.assertEqual(events[0].medium, "organic")
        self.assertEqual(events[0].campaign, "seo")
        self.assertEqual(json.loads(events[0].props), {"foo": "bar"})
        self.assertTrue(events[0].user_agent)  # Server-seitig erfasst

    def test_all_required_events_are_accepted(self):
        for event in (
            "demo_started", "demo_completed", "contact_clicked",
            "calendar_opened", "meeting_booked", "service_viewed",
            "case_study_viewed", "roi_calculated", "lead_created",
        ):
            with self.subTest(event=event):
                response = self._post_event({"event": event, "page": "/"})
                self.assertEqual(response.status_code, 204)

        stored = {e.event for e in self._events()}
        self.assertEqual(
            stored,
            {"demo_started", "demo_completed", "contact_clicked", "calendar_opened",
             "meeting_booked", "service_viewed", "case_study_viewed",
             "roi_calculated", "lead_created"},
        )

    def test_unknown_event_is_silently_dropped(self):
        response = self._post_event({"event": "nonsense_event", "page": "/"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(self._events()), 0)

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/analytics/event",
            data="not json at all",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 400)

    def test_oversized_props_returns_413(self):
        response = self._post_event({
            "event": "page_view",
            "props": {"blob": "x" * 5000},
        })
        self.assertEqual(response.status_code, 413)
        self.assertEqual(len(self._events()), 0)

    def test_get_method_not_allowed(self):
        response = self.client.get("/analytics/event")
        self.assertEqual(response.status_code, 405)

    def test_endpoint_is_csrf_exempt(self):
        """Beacon hat kein Session-Token — der Blueprint ist per csrf.exempt() frei."""
        app = self.app
        old_check = app.config.get("WTF_CSRF_ENABLED")
        app.config["WTF_CSRF_ENABLED"] = True
        try:
            response = self._post_event({"event": "page_view", "page": "/"})
            self.assertEqual(response.status_code, 204)
            self.assertEqual(len(self._events()), 1)
        finally:
            app.config["WTF_CSRF_ENABLED"] = old_check

    # ── Serverseitige Conversion-Events aus dem Formular ────────────────

    def _submit_contact(self, extra=None, headers=None):
        data = {
            "name": "Analytics Test",
            "company": "Analytics GmbH",
            "email": "analytics@example.com",
            "service": "Prozessautomatisierung",
            "message": "Wir wollen einen Ablauf automatisieren.",
            "privacy": "accepted",
            "website": "",
            # Von analytics.js injizierte Hidden-Fields (First-Touch-Attribution)
            "session_id": "sess-form-1",
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "kampagne-a",
        }
        if extra:
            data.update(extra)
        return self.client.post(
            "/contact",
            data=data,
            headers=headers or {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )

    def test_contact_submit_records_lead_created_with_attribution(self):
        response = self._submit_contact()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

        events = self._events()
        lead_created = [e for e in events if e.event == "lead_created"]
        self.assertEqual(len(lead_created), 1)
        self.assertEqual(lead_created[0].session_id, "sess-form-1")
        self.assertEqual(lead_created[0].source, "google")
        self.assertEqual(lead_created[0].medium, "cpc")
        self.assertEqual(lead_created[0].campaign, "kampagne-a")
        self.assertEqual(json.loads(lead_created[0].props), {"service": "Prozessautomatisierung"})

        # Session-Attribution landet auch am Lead/der Nachricht (Funnel-Stitching)
        with self.app.app_context():
            message = self.ContactMessage.query.filter_by(email="analytics@example.com").first()
            lead = self.Lead.query.filter_by(email="analytics@example.com").first()
            self.assertEqual(message.session_id, "sess-form-1")
            self.assertEqual(lead.session_id, "sess-form-1")

    def test_booking_submit_records_demo_completed_but_no_meeting_without_n8n(self):
        # Hermetisch: n8n-Forwarder gemockt (auf dem VPS ist der Webhook sonst
        # live erreichbar → Test wäre vom Netzwerk-Zustand abhängig).
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": False,
            "message": "Termindienst nicht erreichbar",
        }
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        # n8n hat abgelehnt → Anfrage bleibt gespeichert, Client bekommt 409
        self.assertEqual(response.status_code, 409)

        names = {e.event for e in self._events()}
        self.assertIn("lead_created", names)
        self.assertIn("demo_completed", names)
        # n8n ohne Erfolg → keine echte Buchung
        self.assertNotIn("meeting_booked", names)

    def test_booking_with_n8n_success_records_meeting_booked(self):
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {"success": True, "message": "ok"}
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        self.assertEqual(response.status_code, 200)
        events = self._events()
        meeting = [e for e in events if e.event == "meeting_booked"]
        self.assertEqual(len(meeting), 1)
        self.assertEqual(
            json.loads(meeting[0].props),
            {"day": "2026-09-15", "time": "10:00", "service": "Erstgespräch"},
        )
        self.assertIn("demo_completed", {e.event for e in events})

    # ── Template-Integration ────────────────────────────────────────────

    def test_homepage_loads_analytics_script(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        self.assertIn("js/analytics.js?v=15", html)
        # Reihenfolge: analytics.js VOR main.js (Attribution vor Formular-Submit)
        self.assertLess(html.index("analytics.js"), html.index("main.js"))

    def test_datenschutz_discloses_event_tracking(self):
        response = self.client.get("/datenschutz")
        html = response.get_data(as_text=True)
        self.assertIn("anonyme Interaktions-Events", html)
        self.assertIn("keine Cookies", html)


if __name__ == "__main__":
    unittest.main()
