"""Regression tests for the public Skalantech experience."""
import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class PublicSiteTests(unittest.TestCase):
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

    def test_public_routes_render(self):
        expected_types = {
            "/": "text/html",
            "/automationen": "text/html",
            "/demos": "text/html",
            "/koeln": "text/html",
            "/faq": "text/html",
            "/impressum": "text/html",
            "/datenschutz": "text/html",
            "/agb": "text/html",
            "/robots.txt": "text/plain",
            "/sitemap.xml": "application/xml",
        }
        for path, content_type in expected_types.items():
            with self.subTest(path=path):
                response = self.client.get(path, buffered=True)
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.content_type.startswith(content_type))
                finally:
                    response.close()

    def test_homepage_contains_conversion_and_seo_content(self):
        html = self.client.get("/").get_data(as_text=True)
        for phrase in (
            "Arbeit, die heute Zeit frisst,",
            "wird morgen zum digitalen Prozess.",
            "Kostenlose Business-Analyse",
            "Anfrage → Angebot",
            "Rechnung → strukturierte Daten",
            "E-Mail → CRM",
            "Vier Bausteine. Ein digitaler Prozess.",
            "Gebaut. Nicht nur beschrieben.",
            "InvoiceFlow",
            "OfferAI",
            "MailAgent",
            "KI-Manager:in Advanced",
            "Projektanfrage senden",
            "xyesca@skalantech.store",
            "skalantech-og.jpg",
            "brand/skalantech-mark.svg",
            "founder-600.webp",
            'id="services"',
            'id="demos"',
            'id="about"',
            'id="contact"',
            "Direkt vom Gründer",
            "7+ Jahre IT-Praxiserfahrung",
            "Self-Hosting &amp; Datensouveränität statt Vendor-Lock-in",
        ):
            self.assertIn(phrase, html)
        self.assertNotIn("xyesca1989@googlemail.com", html)
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertNotIn("cdnjs.cloudflare.com", html)

    def test_navigation_surfaces_automation_and_demos(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('href="/automationen"', html)
        self.assertIn('href="/demos"', html)
        self.assertIn("Business-Analyse buchen", html)

    def test_brand_assets_are_served(self):
        expected_types = {
            "/static/favicon.svg": "image/svg+xml",
            "/static/brand/skalantech-mark.svg": "image/svg+xml",
            "/static/brand/skalantech-logo.svg": "image/svg+xml",
            "/static/img/skalantech-og.jpg": "image/jpeg",
            "/static/css/showcase.css": "text/css",
            "/static/js/showcase.js": "text/javascript",
        }
        for path, content_type in expected_types.items():
            with self.subTest(path=path):
                response = self.client.get(path, buffered=True)
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.content_type.startswith(content_type))
                finally:
                    response.close()

    def test_valid_contact_request_is_stored(self):
        from app.models import ContactMessage
        response = self.client.post(
            "/contact?utm_source=google&utm_medium=organic&utm_campaign=seo",
            data={
                "name": "Test Person",
                "company": "Test GmbH",
                "email": "test@example.com",
                "service": "Prozessautomatisierung",
                "message": "Wir möchten einen manuellen Ablauf zuverlässig automatisieren.",
                "privacy": "accepted",
                "website": "",
            },
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        with self.app.app_context():
            saved = ContactMessage.query.filter_by(email="test@example.com").first()
            self.assertIsNotNone(saved)
            self.assertIn("Unternehmen: Test GmbH", saved.message)
            self.assertEqual(saved.source, "google")
            self.assertEqual(saved.medium, "organic")
            self.assertEqual(saved.campaign, "seo")

    def test_contact_validation_and_honeypot(self):
        invalid = self.client.post(
            "/contact",
            data={"name": "", "email": "invalid", "message": "", "privacy": ""},
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(invalid.get_json()["success"])
        bot = self.client.post(
            "/contact",
            data={"website": "spam.example"},
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        self.assertEqual(bot.status_code, 200)
        self.assertTrue(bot.get_json()["success"])

    def test_ionos_mail_configuration_is_used(self):
        from app.blueprints import public as pub
        env = {
            "BUSINESS_EMAIL": "xyesca@skalantech.store",
            "IONOS_MAIL_USER": "xyesca@skalantech.store",
            "IONOS_MAIL_PASSWORD": "test-password",
            "IONOS_SMTP_HOST": "smtp.ionos.de",
            "IONOS_SMTP_PORT": "465",
        }
        smtp = mock.MagicMock()
        smtp.__enter__.return_value = smtp
        with mock.patch.dict(os.environ, env, clear=False), mock.patch.object(pub.smtplib, "SMTP_SSL", return_value=smtp) as smtp_cls:
            self.assertTrue(pub._send_email("Tester", "kunde@example.com", "Hallo"))
        smtp_cls.assert_called_once_with("smtp.ionos.de", 465, timeout=10)
        smtp.login.assert_called_once_with("xyesca@skalantech.store", "test-password")
        args = smtp.sendmail.call_args.args
        self.assertEqual(args[0], "xyesca@skalantech.store")
        self.assertEqual(args[1], ["xyesca@skalantech.store"])
        self.assertIn("Reply-To: kunde@example.com", args[2])

    def test_forward_to_n8n_classifies_responses(self):
        from app.blueprints import public as pub

        def _mock_urlopen(status, body):
            resp = mock.MagicMock()
            resp.status = status
            resp.read.return_value = body
            cm = mock.MagicMock()
            cm.__enter__.return_value = resp
            return cm

        with mock.patch.object(pub.urlrequest, "urlopen", return_value=_mock_urlopen(200, b'{"success": true, "message": "ok"}')):
            r = pub._forward_to_n8n("N", "e@x.de", "", "Erstgespräch", "m", "2026-09-10", "10:00")
        self.assertEqual(r["status"], "confirmed")

        with mock.patch.object(pub.urlrequest, "urlopen", return_value=_mock_urlopen(200, json.dumps({"success": False, "message": "Slot belegt"}).encode())):
            r = pub._forward_to_n8n("N", "e@x.de", "", "Erstgespräch", "m", "2026-09-10", "10:00")
        self.assertEqual(r["status"], "slot_taken")

        with mock.patch.object(pub.urlrequest, "urlopen", return_value=_mock_urlopen(200, b"")):
            r = pub._forward_to_n8n("N", "e@x.de", "", "Erstgespräch", "m", "2026-09-10", "10:00")
        self.assertEqual(r["status"], "invalid_response")

        with mock.patch.object(pub.urlrequest, "urlopen", side_effect=Exception("down")):
            r = pub._forward_to_n8n("N", "e@x.de", "", "Erstgespräch", "m", "2026-09-10", "10:00")
        self.assertEqual(r["status"], "unreachable")

    def test_security_headers_are_present(self):
        response = self.client.get("/")
        for header in (
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Permissions-Policy",
            "Referrer-Policy",
        ):
            self.assertIn(header, response.headers)
        self.assertIn("script-src 'self'", response.headers["Content-Security-Policy"])

    def test_seo_landing_pages_render(self):
        for path in (
            "/websites-apps", "/it-infrastruktur", "/ki-integration", "/ki-automatisierung",
            "/ki-agenten", "/n8n-automatisierung", "/lokale-ki", "/wissen",
            "/wissen/was-ist-ein-ki-agent", "/wissen/n8n-selbst-hosten",
            "/wissen/lokale-ki-vs-cloud-ki", "/wissen/n8n-vs-power-automate",
            "/wissen/welche-prozesse-ki-automatisierung", "/wissen/rag-wissensassistenten",
            "/wissen/kosten-roi-ki-automatisierung",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_landing_page_seo_structure(self):
        html = self.client.get("/ki-agenten").get_data(as_text=True)
        self.assertIn('<h1>KI-Agenten, die Aufgaben wirklich erledigen.</h1>', html)
        self.assertIn('<link rel="canonical" href="https://skalantech.store/ki-agenten">', html)
        self.assertIn('"@type": "Service"', html)
        self.assertIn('"@type": "BreadcrumbList"', html)
        self.assertIn('"@type": "FAQPage"', html)
        self.assertIn('#termin', html)

    def test_landing_pages_are_not_duplicate_content(self):
        titles, descriptions = [], []
        for slug in ("it-infrastruktur", "ki-integration", "ki-automatisierung", "ki-agenten", "n8n-automatisierung", "lokale-ki"):
            html = self.client.get(f"/{slug}").get_data(as_text=True)
            h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
            desc = re.search(r'<meta name="description" content="([^"]*)"', html)
            self.assertIsNotNone(h1)
            self.assertIsNotNone(desc)
            titles.append(h1.group(1).strip())
            descriptions.append(desc.group(1))
        self.assertEqual(len(set(titles)), 6)
        self.assertEqual(len(set(descriptions)), 6)

    def test_sitemap_lists_public_conversion_pages(self):
        body = self.client.get("/sitemap.xml").get_data(as_text=True)
        for path in (
            "/", "/automationen", "/demos", "/koeln", "/websites-apps",
            "/it-infrastruktur", "/ki-integration", "/ki-automatisierung",
            "/ki-agenten", "/n8n-automatisierung", "/lokale-ki", "/wissen", "/faq",
        ):
            self.assertIn(f"https://skalantech.store{path}</loc>", body)
        for blocked in ("/admin", "/login", "/impressum", "/datenschutz", "/agb", "/test-footer"):
            self.assertNotIn(f"<loc>https://skalantech.store{blocked}</loc>", body)

    def test_robots_txt_disallows_private_routes(self):
        body = self.client.get("/robots.txt").get_data(as_text=True)
        for item in ("Disallow: /admin", "Disallow: /login", "Disallow: /auth", "Sitemap: https://skalantech.store/sitemap.xml"):
            self.assertIn(item, body)

    def test_custom_404_page(self):
        response = self.client.get("/gibt-es-nicht")
        self.assertEqual(response.status_code, 404)
        html = response.get_data(as_text=True)
        self.assertIn("Diese Seite gibt es nicht.", html)
        self.assertIn("noindex", html)

    def test_faq_schema_and_article_schema(self):
        self.assertIn('"@type": "FAQPage"', self.client.get("/").get_data(as_text=True))
        self.assertIn('"@type": "FAQPage"', self.client.get("/faq").get_data(as_text=True))
        article = self.client.get("/wissen/n8n-selbst-hosten").get_data(as_text=True)
        self.assertIn('"@type": "Article"', article)
        self.assertIn('"@type": "BreadcrumbList"', article)

    def test_csrf_protected_contact_flow(self):
        old = self.app.config.get("WTF_CSRF_ENABLED")
        self.app.config["WTF_CSRF_ENABLED"] = True
        client = self.app.test_client()
        try:
            html = client.get("/").get_data(as_text=True)
            token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
            response = client.post(
                "/contact",
                data={
                    "csrf_token": token,
                    "name": "CSRF Test",
                    "email": "csrf@example.com",
                    "message": "Echter CSRF-Test",
                    "privacy": "accepted",
                    "website": "",
                },
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )
            self.assertEqual(response.status_code, 200)
        finally:
            self.app.config["WTF_CSRF_ENABLED"] = old

    def test_footer_and_legal_trust(self):
        for path in ("/", "/automationen", "/demos", "/it-infrastruktur", "/wissen", "/impressum", "/datenschutz", "/agb", "/faq"):
            with self.subTest(path=path):
                html = self.client.get(path).get_data(as_text=True)
                self.assertIn("SSL-verschlüsselt", html)
                self.assertIn("Keine externen Tracker", html)
                self.assertIn("xyesca@skalantech.store", html)
                self.assertNotIn("xyesca1989@googlemail.com", html)

    def test_trust_assets_and_local_page(self):
        for path in (
            "/static/img/founder-400.webp",
            "/static/img/founder-600.webp",
            "/static/img/portrait-480.webp",
            "/static/documents/certificates_xavier_escalante.pdf",
        ):
            self.assertEqual(self.client.get(path).status_code, 200)
        html = self.client.get("/koeln").get_data(as_text=True)
        self.assertIn("IT-Dienstleister &amp; KI-Beratung für Köln", html)
        self.assertIn('href="tel:+4917677879366"', html)
        self.assertIn('"@type": "ProfessionalService"', html)


if __name__ == "__main__":
    unittest.main()
