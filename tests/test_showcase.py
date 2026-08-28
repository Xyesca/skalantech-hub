"""Regression tests for automation showcase and public demo proxy."""
import os
import sys
import tempfile
import unittest
from unittest import mock


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class ShowcaseTests(unittest.TestCase):
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
        cls.app = create_app("production")
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def test_automation_page_exposes_outcome_use_cases(self):
        response = self.client.get("/automationen")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for phrase in (
            "Weniger klicken.",
            "Anfrage → Angebot",
            "Rechnung → Daten",
            "E-Mail → CRM",
            "Lead → Follow-up",
            "Formular → Prozess",
            "Live-Demos testen",
        ):
            self.assertIn(phrase, html)

    def test_demo_page_contains_three_interactive_workflows(self):
        response = self.client.get("/demos")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for slug, name in (("invoiceflow", "InvoiceFlow"), ("offerai", "OfferAI"), ("mailagent", "MailAgent")):
            self.assertIn(name, html)
            self.assertIn(f'/api/demos/{slug}', html)
        self.assertEqual(html.count('class="demo-card__header"'), 3)
        self.assertEqual(html.count('data-demo-result-output'), 3)
        self.assertNotIn('<pre class="demo-result', html)
        self.assertIn("maximal 2.000 Zeichen", html)
        # Copy-&-Build-Spezifikation Issue #10: verbindliche Texte in der Haupt-UX.
        self.assertIn("Live-Demos · echte KMU-Abläufe", html)
        self.assertIn("Sehen Sie, was im Arbeitsalltag automatisch vorbereitet werden kann.", html)
        self.assertIn("Alle Beispiele sind vollständig fiktiv.", html)
        self.assertIn("Typische Arbeit aus Handwerk, Praxis, Werkstatt und Büro.", html)
        self.assertIn("Sicherer Datenweg", html)
        # Ergebnisstatus pro Demo (Spec E4)
        self.assertIn("Für Prüfung vorbereitet", html)
        self.assertIn("Angebot zur Prüfung", html)
        self.assertIn("Bearbeitungsvorschlag", html)
        # 'Was passiert danach?' unter jedem Ergebnis (Spec E5)
        self.assertEqual(html.count("Was passiert danach?"), 3)
        # Fiktiv-Hinweis bei allen Demo-Beispielen (Spec E8)
        self.assertEqual(html.count("Fiktive Beispieldaten – bitte keine echten personenbezogenen oder vertraulichen Daten verwenden."), 3)
        # Keine generischen 'Beispiel N'-Buttons (Spec E1/E2)
        self.assertNotIn("Beispiel 1", html)
        self.assertNotIn("Beispiel 2", html)
        self.assertNotIn("Beispiel 3", html)
        # 'Strukturiert' nicht mehr als generisches Ergebnislabel (Spec E3)
        self.assertNotIn(">Strukturiert<", html)

    def test_demo_proxy_rejects_unknown_or_too_short_input(self):
        unknown = self.client.post("/api/demos/nope", data={"input": "x" * 50})
        self.assertEqual(unknown.status_code, 404)

        short = self.client.post("/api/demos/invoiceflow", data={"input": "zu kurz"})
        self.assertEqual(short.status_code, 400)
        self.assertFalse(short.get_json()["success"])

    def test_demo_proxy_calls_only_allowlisted_internal_workflow(self):
        from app.blueprints import automation_showcase as showcase
        with mock.patch.object(
            showcase,
            "_call_internal_demo",
            return_value={"success": True, "result": {"invoice_number": "RE-1"}},
        ) as call:
            response = self.client.post(
                "/api/demos/invoiceflow",
                data={"input": "Rechnung RE-1 vom 27.08.2026 über 100 Euro netto."},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        call.assert_called_once()
        self.assertEqual(call.call_args.args[0], "invoiceflow")

    def test_demo_proxy_truncates_input_to_2000_chars(self):
        from app.blueprints import automation_showcase as showcase
        long_input = "Rechnung Muster GmbH über 100,00 EUR netto. " * 150  # ~4000 Zeichen
        with mock.patch.object(
            showcase,
            "_call_internal_demo",
            return_value={"success": True, "result": {"rechnungsnummer": "RE-2000"}},
        ) as call:
            response = self.client.post(
                "/api/demos/invoiceflow",
                data={"input": long_input},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        sent_value = call.call_args.args[1]
        self.assertEqual(len(sent_value), 2000)

    def test_demo_proxy_upstream_failure_is_generic_no_internal_leak(self):
        """n8n-Ausfall -> 503 mit generischer Meldung, keine URLs/Fehlerdetails nach außen."""
        from app.blueprints import automation_showcase as showcase
        with mock.patch.object(
            showcase,
            "urlrequest",
        ) as urlrequest:
            urlrequest.urlopen.side_effect = OSError("Connection refused to 127.0.0.1:5678 (internal)")
            response = self.client.post(
                "/api/demos/invoiceflow",
                data={"input": "Rechnung RE-1 vom 27.08.2026 über 100 Euro netto."},
            )
        self.assertEqual(response.status_code, 503)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        body = response.get_data(as_text=True)
        for leak in ("127.0.0.1", "5678", "Connection refused", "OSError", "webhook"):
            self.assertNotIn(leak, body)


    def test_sitemap_contains_showcase_routes(self):
        xml = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("https://skalantech.store/automationen</loc>", xml)
        self.assertIn("https://skalantech.store/demos</loc>", xml)


if __name__ == "__main__":
    unittest.main()
