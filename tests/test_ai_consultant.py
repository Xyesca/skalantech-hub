"""Regression tests for the Skalantech AI Consultant."""
import os
import sys
import tempfile
import unittest
from unittest import mock


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class AIConsultantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"
        os.environ.pop("N8N_AI_CONSULTANT_WEBHOOK_URL", None)
        _drop_app_modules()
        from app import create_app
        cls.app = create_app("production")
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def test_endpoint_requires_json_and_message(self):
        response = self.client.post("/api/ai-consultant/message", data="hello")
        self.assertEqual(response.status_code, 415)

        response = self.client.post("/api/ai-consultant/message", json={"message": ""})
        self.assertEqual(response.status_code, 400)

    def test_local_invoice_fallback_is_truthful_and_actionable(self):
        response = self.client.post(
            "/api/ai-consultant/message",
            json={
                "message": "Wir übertragen jede Rechnung manuell in die Buchhaltung.",
                "conversation_id": "chat-test-1234",
                "page": "/",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["source"], "local")
        self.assertIn("InvoiceFlow", payload["reply"])
        self.assertEqual(payload["action"]["url"], "/demos#invoiceflow")
        self.assertEqual(payload["conversation_id"], "chat-test-1234")

    def test_invalid_conversation_id_is_replaced(self):
        response = self.client.post(
            "/api/ai-consultant/message",
            json={"message": "Was kann Skalantech automatisieren?", "conversation_id": "<script>"},
        )
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(payload["conversation_id"], "<script>")
        self.assertGreaterEqual(len(payload["conversation_id"]), 8)

    def test_orchestrated_response_is_used_when_available(self):
        from app.blueprints import ai_consultant
        orchestrated = {
            "reply": "Ein passender erster Schritt ist die Prozessaufnahme.",
            "suggestions": ["Welche Systeme nutzen Sie?"],
            "action": {"label": "Business-Analyse", "url": "/#termin"},
        }
        with mock.patch.object(ai_consultant, "_call_n8n", return_value=orchestrated):
            response = self.client.post(
                "/api/ai-consultant/message",
                json={"message": "Wir möchten einen Prozess automatisieren."},
            )
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["source"], "n8n")
        self.assertEqual(payload["action"]["url"], "/#termin")

    def test_action_filter_rejects_external_urls(self):
        from app.blueprints.ai_consultant import _normalise_orchestrated_response
        result = _normalise_orchestrated_response({
            "reply": "Test",
            "action": {"label": "Extern", "url": "https://evil.example"},
        })
        self.assertIsNone(result["action"])

    def test_public_bundle_contains_consultant_mount(self):
        response = self.client.get("/static/js/showcase.js")
        self.assertEqual(response.status_code, 200)
        js = response.get_data(as_text=True)
        self.assertIn("Skalantech AI Consultant", js)
        self.assertIn("/static/js/ai-consultant.js", js)
        self.assertIn("/static/css/ai-consultant.css", js)


if __name__ == "__main__":
    unittest.main()
