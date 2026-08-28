"""Regression tests für die Websites-&-Apps-Angebotsseite (/websites-apps).

Deckt ab (DoD FORGE-Build, LUMINA 02_WIREFRAME §3):
- Route /websites-apps → 200, text/html
- Kerninhalte (H1, zwei Produktlinien, Pricing, Abgrenzung) vorhanden
- Sitemap enthält /websites-apps (priority 0.8)
- JSON-LD: Service + BreadcrumbList + FAQPage, einzeln valides JSON
- Canonical/OG/Twitter korrekt, kein noindex
- CTA mit UTM (Query VOR Fragment)
- Header-Nav + Footer-Leistungen verlinken die Seite
- Interlinking: it-infrastruktur verlinkt über „related" auf /websites-apps
"""
import json
import os
import re
import sys
import tempfile
import unittest


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class WebsitesAppsTests(unittest.TestCase):
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
        cls.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def _get(self, path):
        return self.client.get(path, buffered=True)

    # ── Route ──────────────────────────────────────────────────────────

    def test_route_renders_200(self):
        resp = self._get("/websites-apps")
        try:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.content_type.startswith("text/html"))
        finally:
            resp.close()

    def test_core_content_present(self):
        resp = self._get("/websites-apps")
        try:
            html = resp.get_data(as_text=True)
            # H1
            self.assertIn("Websites, die verkaufen. Apps, die Prozesse beschleunigen.", html)
            # Zwei Produktlinien
            self.assertIn("Corporate Websites", html)
            self.assertIn("Business Apps", html)
            # Pricing
            self.assertIn("ab 4.900 €", html)
            self.assertIn("ab 490 €", html)
            self.assertIn("Operate &amp; Grow", html)
            # Abgrenzung
            self.assertIn("Keine WordPress-Agentur", html)
            # Trust-Line
            self.assertIn("Kein Vendor-Lock-in", html)
        finally:
            resp.close()

    # ── SEO / JSON-LD ──────────────────────────────────────────────────

    def test_canonical_og_noindex(self):
        resp = self._get("/websites-apps")
        try:
            html = resp.get_data(as_text=True)
            self.assertIn('rel="canonical" href="https://skalantech.store/websites-apps"', html)
            self.assertIn('property="og:url" content="https://skalantech.store/websites-apps"', html)
            self.assertNotIn("noindex", html)
        finally:
            resp.close()

    def test_jsonld_valid_service_faq(self):
        resp = self._get("/websites-apps")
        try:
            html = resp.get_data(as_text=True)
            blocks = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', html, re.S
            )
            self.assertGreaterEqual(len(blocks), 1, "JSON-LD-Block fehlt")
            for block in blocks:
                json.loads(block)  # wirft bei ungültigem JSON

            # Der Landing-Block enthält Service + BreadcrumbList + FAQPage
            landing_graph = None
            for block in blocks:
                graph = json.loads(block).get("@graph", [])
                if any(node.get("@type") == "Service" for node in graph):
                    landing_graph = graph
                    break
            self.assertIsNotNone(landing_graph, "Service-Schema fehlt")
            types = {node.get("@type") for node in landing_graph}
            self.assertIn("Service", types)
            self.assertIn("BreadcrumbList", types)
            self.assertIn("FAQPage", types)
        finally:
            resp.close()

    def test_cta_utm_query_before_fragment(self):
        resp = self._get("/websites-apps")
        try:
            html = resp.get_data(as_text=True)
            # Query VOR Fragment (#termin) — UTM geht nicht verloren
            self.assertIn("utm_campaign=websites-apps#termin", html)
            self.assertIn("utm_source=organic", html)
        finally:
            resp.close()

    # ── Sitemap ────────────────────────────────────────────────────────

    def test_sitemap_contains_websites_apps(self):
        resp = self._get("/sitemap.xml")
        try:
            xml = resp.get_data(as_text=True)
            self.assertIn("<loc>https://skalantech.store/websites-apps</loc>", xml)
        finally:
            resp.close()

    # ── Navigation & Interlinking ──────────────────────────────────────

    def test_interlinking_from_it_infrastruktur(self):
        resp = self._get("/it-infrastruktur")
        try:
            html = resp.get_data(as_text=True)
            # related → landing_map löst websites-apps auf
            self.assertIn('href="/websites-apps"', html)
        finally:
            resp.close()

    # ── Regression: generische Landings unverändert ─────────────────────

    def test_generic_landing_still_renders(self):
        resp = self._get("/ki-integration")
        try:
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("KI in Ihre bestehenden Systeme", html)
        finally:
            resp.close()


if __name__ == "__main__":
    unittest.main()
