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
            "IT, Automatisierung und KI,",
            "die im Alltag wirklich funktionieren.",
            "Kostenloses Erstgespräch",
            "Kommt dir das bekannt vor?",
            "KI-Kompetenz trifft IT-Praxis.",
            "Technologien, mit denen ich arbeite.",
            "KI-Manager:in Advanced",
            "Projektanfrage senden",
            "skalantech-og.jpg",
            "brand/skalantech-mark.svg",
            "founder-600.webp",
            "application/ld+json",
            'id="services"',
            'id="ki"',
            'id="about"',
            'id="contact"',
            # Conversion: Zielgruppe + Trust im Hero (5-Sekunden-Test)
            "Für kleine und mittelständische Unternehmen",
            "Direkt vom Gründer",
            "7+ Jahre IT-Praxiserfahrung",
            "Self-Hosting &amp; Datensouveränität statt Vendor-Lock-in",
            "hero__trust",
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
            self.assertIn("Anliegen: Prozessautomatisierung", saved.message)
            # First-Party-Attribution (UTM) wird mitgespeichert
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

    # ── SEO: Landingpages, Wissen, Sitemap, robots, 404 ──────────────────

    def test_seo_landing_pages_render(self):
        for path in (
            "/it-infrastruktur",
            "/ki-integration",
            "/ki-automatisierung",
            "/ki-agenten",
            "/n8n-automatisierung",
            "/lokale-ki",
            "/wissen",
            "/wissen/was-ist-ein-ki-agent",
            "/wissen/n8n-selbst-hosten",
            "/wissen/lokale-ki-vs-cloud-ki",
            "/wissen/n8n-vs-power-automate",
            "/wissen/welche-prozesse-ki-automatisierung",
            "/wissen/rag-wissensassistenten",
            "/wissen/kosten-roi-ki-automatisierung",
        ):
            with self.subTest(path=path):
                response = self.client.get(path, buffered=True)
                try:
                    self.assertEqual(response.status_code, 200)
                finally:
                    response.close()

    def test_landing_page_seo_structure(self):
        response = self.client.get("/ki-agenten")
        html = response.get_data(as_text=True)

        self.assertIn('<h1>KI-Agenten, die Aufgaben wirklich erledigen.</h1>', html)
        self.assertIn('<link rel="canonical" href="https://skalantech.store/ki-agenten">', html)
        self.assertIn('og:url', html)
        # Strukturierte Daten: Service, BreadcrumbList, FAQPage
        self.assertIn('"@type": "Service"', html)
        self.assertIn('"@type": "BreadcrumbList"', html)
        self.assertIn('"@type": "FAQPage"', html)
        # CTA zur Terminbuchung
        self.assertIn('#termin', html)

    def test_landing_pages_are_not_duplicate_content(self):
        """Jede Landingpage hat eigene H1 + unique Description."""
        titles = []
        descriptions = []
        for slug in ("it-infrastruktur", "ki-integration", "ki-automatisierung", "ki-agenten", "n8n-automatisierung", "lokale-ki"):
            response = self.client.get(f"/{slug}")
            html = response.get_data(as_text=True)
            import re
            h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
            desc = re.search(r'<meta name="description" content="([^"]*)"', html)
            self.assertIsNotNone(h1, f"H1 fehlt auf /{slug}")
            self.assertIsNotNone(desc, f"Description fehlt auf /{slug}")
            titles.append(h1.group(1).strip())
            descriptions.append(desc.group(1))
        self.assertEqual(len(set(titles)), 6, "H1s der Landingpages müssen eindeutig sein")
        self.assertEqual(len(set(descriptions)), 6, "Descriptions der Landingpages müssen eindeutig sein")

    def test_sitemap_lists_all_indexable_pages(self):
        response = self.client.get("/sitemap.xml")
        body = response.get_data(as_text=True)

        for path in (
            "/",
            "/it-infrastruktur",
            "/ki-integration",
            "/ki-automatisierung",
            "/ki-agenten",
            "/n8n-automatisierung",
            "/lokale-ki",
            "/wissen",
            "/wissen/was-ist-ein-ki-agent",
            "/wissen/n8n-selbst-hosten",
            "/wissen/lokale-ki-vs-cloud-ki",
            "/wissen/n8n-vs-power-automate",
            "/wissen/welche-prozesse-ki-automatisierung",
            "/wissen/rag-wissensassistenten",
            "/wissen/kosten-roi-ki-automatisierung",
            "/faq",
        ):
            self.assertIn(f"https://skalantech.store{path}</loc>", body)

        # Keine nicht-indexierbaren Routen in der Sitemap
        for blocked in ("/admin", "/login", "/impressum", "/datenschutz", "/agb", "/test-footer"):
            self.assertNotIn(f"<loc>https://skalantech.store{blocked}</loc>", body)

    def test_robots_txt_disallows_private_routes(self):
        response = self.client.get("/robots.txt")
        body = response.get_data(as_text=True)

        self.assertIn("Disallow: /admin", body)
        self.assertIn("Disallow: /login", body)
        self.assertIn("Disallow: /auth", body)
        self.assertIn("Disallow: /test-footer", body)
        self.assertIn("Sitemap: https://skalantech.store/sitemap.xml", body)

    def test_custom_404_page(self):
        response = self.client.get("/gibt-es-nicht")
        self.assertEqual(response.status_code, 404)
        html = response.get_data(as_text=True)
        self.assertIn("Diese Seite gibt es nicht.", html)
        self.assertIn('noindex', html)

    def test_unknown_article_and_landing_slug_404(self):
        self.assertEqual(self.client.get("/wissen/gibt-es-nicht").status_code, 404)
        self.assertEqual(self.client.get("/wissen/../gibt-es-nicht").status_code, 404)

    def test_removed_test_footer_route_404(self):
        self.assertEqual(self.client.get("/test-footer").status_code, 404)

    def test_faq_page_has_faq_schema(self):
        response = self.client.get("/faq")
        html = response.get_data(as_text=True)
        self.assertIn('"@type": "FAQPage"', html)

    def test_homepage_has_faq_schema_and_landing_links(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        self.assertIn('"@type": "FAQPage"', html)
        self.assertIn("/ki-automatisierung", html)
        self.assertIn("/it-infrastruktur", html)
        self.assertIn("/ki-integration", html)

    def test_article_has_article_schema_and_related_cta(self):
        response = self.client.get("/wissen/n8n-selbst-hosten")
        html = response.get_data(as_text=True)
        self.assertIn('"@type": "Article"', html)
        self.assertIn('"@type": "BreadcrumbList"', html)
        self.assertIn("n8n-Automatisierung im Überblick", html)

    def test_csrf_protected_contact_flow(self):
        """Regressions-Test: Formular-POST mit echtem CSRF-Flow (nicht deaktiviert).

        Früher wurde CSRF in Tests deaktiviert -> WTF_CSRF_SSL_STRICT-Bug
        (400 auf jeden POST) blieb unentdeckt.
        """
        # CSRF für diesen Test aktivieren (Rest der Suite nutzt deaktiviertes CSRF)
        app = self.app
        old_check = app.config.get("WTF_CSRF_ENABLED")
        app.config["WTF_CSRF_ENABLED"] = True
        client = app.test_client()
        import re
        try:
            r = client.get("/")
            html = r.get_data(as_text=True)
            m = re.search(r'name="csrf_token" value="([^"]+)"', html)
            self.assertIsNotNone(m, "CSRF-Token fehlt im Formular")
            token = m.group(1)

            resp = client.post(
                "/contact",
                data={
                    "csrf_token": token,
                    "name": "CSRF Flow Test",
                    "email": "csrf-flow@example.com",
                    "message": "Test des echten CSRF-Flows",
                    "privacy": "accepted",
                    "website": "",
                },
                headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )
            self.assertEqual(resp.status_code, 200, "CSRF-geschützter POST muss 200 liefern")
            self.assertTrue(resp.get_json()["success"])
        finally:
            app.config["WTF_CSRF_ENABLED"] = old_check


if __name__ == "__main__":
    unittest.main()
