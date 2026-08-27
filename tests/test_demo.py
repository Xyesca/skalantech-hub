"""Tests für die P0-Live-Demo-Sektion + /demo-Lead-Route (Branchen-Landingpages)."""
import os
import sys
import tempfile
import unittest
from unittest import mock


def _drop_app_modules():
    """Entferne gecachte app-Module, damit DATABASE_URL/Env je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class DemoRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"

        _drop_app_modules()
        from app import create_app

        cls.app = create_app("production")
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    # ── Demo-Sektion (Rendering) ──────────────────────────────────────
    def test_demo_section_renders_on_branchen_pages(self):
        for path in ("/branchen/handwerk", "/branchen/kfz", "/branchen/kanzleien", "/branchen/immobilien"):
            with self.subTest(path=path):
                resp = self.client.get(path, buffered=True)
                try:
                    self.assertEqual(resp.status_code, 200)
                    html = resp.get_data(as_text=True)
                    self.assertIn('id="demo"', html)
                    self.assertIn('id="demo-form"', html)
                    self.assertIn('name="demo_type"', html)
                    self.assertIn('action="/demo"', html)
                    # DSGVO: Hinweistext statt Pflicht-Checkbox (Art. 6(1)(b))
                    self.assertIn("Art. 6 Abs. 1 lit. b DSGVO", html)
                    self.assertNotIn('id="demo-privacy"', html)
                    for product in ("InvoiceFlow", "OfferAI", "MailAgent"):
                        self.assertIn(product, html)
                finally:
                    resp.close()

    def test_demo_section_absent_on_service_pages(self):
        resp = self.client.get("/ki-agenten", buffered=True)
        try:
            html = resp.get_data(as_text=True)
            self.assertNotIn('id="demo-form"', html)
            self.assertNotIn('action="/demo"', html)
        finally:
            resp.close()

    # ── /demo Route ───────────────────────────────────────────────────
    def test_valid_demo_request_stored_and_forwarded(self):
        from app.models import Lead

        with mock.patch(
            "app.blueprints.public._forward_lead_to_n8n",
            return_value={"success": True, "status": "created", "message": "abc"},
        ) as fwd:
            resp = self.client.post(
                "/demo",
                data={
                    "name": "Demo Person",
                    "email": "demo@example.com",
                    "company": "Demo GmbH",
                    "demo_type": "offerai",
                    "message": "Angebote automatisieren",
                    "website": "",
                },
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["success"])
        fwd.assert_called_once()

        with self.app.app_context():
            lead = Lead.query.filter_by(email="demo@example.com").first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.service, "Demo: OfferAI — Anfrage → Angebot")
            self.assertTrue(any("Demo-Anfrage" in n.body for n in lead.notes))

    def test_demo_validation_rejects_invalid(self):
        resp = self.client.post(
            "/demo",
            data={"name": "", "email": "invalid", "privacy": ""},
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.get_json()["success"])

    def test_demo_honeypot_silently_accepted(self):
        with mock.patch("app.blueprints.public._forward_lead_to_n8n") as fwd:
            resp = self.client.post(
                "/demo",
                data={"website": "spam.example"},
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["success"])
        fwd.assert_not_called()

    def test_demo_unreachable_n8n_still_saves_lead(self):
        """Lead ist Flask-DB-Source-of-Truth: n8n-Ausfall blockiert die Anfrage nicht."""
        from app.models import Lead

        with mock.patch(
            "app.blueprints.public._forward_lead_to_n8n",
            return_value={"success": False, "status": "unreachable", "message": "down"},
        ):
            resp = self.client.post(
                "/demo",
                data={
                    "name": "Offline Person",
                    "email": "offline@example.com",
                    "demo_type": "alle",
                    "privacy": "accepted",
                    "website": "",
                },
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["success"])
        with self.app.app_context():
            self.assertIsNotNone(Lead.query.filter_by(email="offline@example.com").first())


if __name__ == "__main__":
    unittest.main()
