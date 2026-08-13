"""Regression tests for the public Skalantech experience."""
import os
import tempfile
import unittest


class PublicSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"

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
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        for phrase in (
            "IT, die läuft.",
            "Was ich für Sie löse.",
            "Projektanfrage senden",
            "skalantech-og.jpg",
            "brand/skalantech-mark.svg",
            "founder-600.webp",
            "application/ld+json",
            'id="services"',
            'id="contact"',
        ):
            self.assertIn(phrase, html)

        self.assertNotIn("fonts.googleapis.com", html)
        self.assertNotIn("cdnjs.cloudflare.com", html)

    def test_brand_assets_are_served_with_expected_types(self):
        expected_types = {
            "/static/favicon.svg": "image/svg+xml",
            "/static/brand/skalantech-mark.svg": "image/svg+xml",
            "/static/brand/skalantech-logo.svg": "image/svg+xml",
            "/static/img/skalantech-systems.webp": "image/webp",
            "/static/img/skalantech-systems-480.webp": "image/webp",
            "/static/img/skalantech-og.jpg": "image/jpeg",
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
            "/contact",
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
            self.assertIn("Anliegen: Prozessautomatisierung", saved.message)

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


if __name__ == "__main__":
    unittest.main()
