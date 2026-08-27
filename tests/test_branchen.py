"""Regression tests für die 4 Branchen-Landingpages (Stage 5 der Pipeline).

Deckt ab (DoD FORGE-Build):
- Routen /branchen/{handwerk,kfz,kanzleien,immobilien} → 200
- Sitemap enthält die 4 neuen URLs (priority 0.8)
- Eindeutige H1s/Descriptions (Anti-Kannibalisierung)
- JSON-LD: Service + BreadcrumbList + FAQPage, einzeln valides JSON
- Canonical/OG/Twitter pro Seite, kein hartcodierter Canonical
- CTA mit UTM (Query VOR Fragment) + First-Party-UTM-Speicherung
- Kein noindex auf den neuen Seiten
- Integration nur bei Kfz/Immobilien, related_articles bei Kanzleien
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


BRANCHES = {
    "handwerk": "branche_handwerk",
    "kfz": "branche_kfz",
    "kanzleien": "branche_kanzleien",
    "immobilien": "branche_immobilien",
}


class BranchenLandingTests(unittest.TestCase):
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

    # ── Routen ─────────────────────────────────────────────────────────

    def test_branch_routes_render_200(self):
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                resp = self._get(f"/branchen/{slug}")
                try:
                    self.assertEqual(resp.status_code, 200)
                    self.assertTrue(resp.content_type.startswith("text/html"))
                finally:
                    resp.close()

    def test_branch_unknown_slug_404(self):
        self.assertEqual(self._get("/branchen/gibt-es-nicht").status_code, 404)

    # ── Sitemap ────────────────────────────────────────────────────────

    def test_sitemap_contains_branch_urls(self):
        resp = self._get("/sitemap.xml")
        body = resp.get_data(as_text=True)
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                self.assertIn(f"https://skalantech.store/branchen/{slug}</loc>", body)
        # Priorität 0.8 für die Branchenseiten
        self.assertIn("<priority>0.8</priority>", body)

    # ── Anti-Kannibalisierung ──────────────────────────────────────────

    def test_branch_unique_h1_and_description(self):
        h1s = []
        descs = []
        for slug in BRANCHES:
            resp = self._get(f"/branchen/{slug}")
            html = resp.get_data(as_text=True)
            h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
            desc = re.search(r'<meta name="description" content="([^"]*)"', html)
            self.assertIsNotNone(h1, f"H1 fehlt auf /branchen/{slug}")
            self.assertIsNotNone(desc, f"Description fehlt auf /branchen/{slug}")
            h1s.append(h1.group(1).strip())
            descs.append(desc.group(1))
        self.assertEqual(len(set(h1s)), 4, "H1s der Branchenseiten müssen eindeutig sein")
        self.assertEqual(len(set(descs)), 4, "Descriptions der Branchenseiten müssen eindeutig sein")

    # ── JSON-LD ────────────────────────────────────────────────────────

    def test_branch_jsonld_valid_and_complete(self):
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                resp = self._get(f"/branchen/{slug}")
                html = resp.get_data(as_text=True)
                blocks = re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>', html, re.S
                )
                self.assertGreaterEqual(len(blocks), 1, "JSON-LD-Block fehlt")
                # Jeder Block einzeln valides JSON
                for block in blocks:
                    json.loads(block)  # wirft bei ungültigem JSON

                # Der Landing-Block enthält Service + BreadcrumbList + FAQPage
                landing_graph = None
                for block in blocks:
                    data = json.loads(block)
                    graph = data.get("@graph", [])
                    if any(node.get("@type") == "Service" for node in graph):
                        landing_graph = graph
                        break
                self.assertIsNotNone(landing_graph, "Service-Schema fehlt")
                types = {node.get("@type") for node in landing_graph}
                self.assertIn("Service", types)
                self.assertIn("BreadcrumbList", types)
                self.assertIn("FAQPage", types)

    # ── Canonical / OG / Twitter ───────────────────────────────────────

    def test_branch_canonical_and_social_meta(self):
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                resp = self._get(f"/branchen/{slug}")
                html = resp.get_data(as_text=True)
                canonical = f'<link rel="canonical" href="https://skalantech.store/branchen/{slug}">'
                self.assertIn(canonical, html)
                self.assertIn(f'property="og:url" content="https://skalantech.store/branchen/{slug}"', html)
                self.assertIn('name="twitter:title"', html)
                self.assertIn('name="twitter:description"', html)

    # ── CTA + UTM (First-Party-Tracking) ───────────────────────────────

    def test_branch_cta_has_utm_query_before_fragment(self):
        for slug, campaign in BRANCHES.items():
            with self.subTest(slug=slug):
                resp = self._get(f"/branchen/{slug}")
                html = resp.get_data(as_text=True)
                # & wird von Jinja im HTML-Attribut zu &amp; escaped — der Browser
                # dekodiert es zurück, location.search sieht die echten &-Trenner.
                expected = (
                    f"/?utm_source=organic&amp;utm_medium=landing&amp;utm_campaign={campaign}#termin"
                )
                self.assertIn(expected, html, "CTA muss UTM-Query VOR dem #termin-Fragment tragen")
                # Kein kaputtes Muster: Fragment darf nicht vor den Query-Parametern stehen
                self.assertNotIn(f"#termin?utm_source", html)

    def test_branch_utm_campaign_is_stored(self):
        from app.models import ContactMessage

        resp = self.client.post(
            "/contact?utm_source=organic&utm_medium=landing&utm_campaign=branche_handwerk",
            data={
                "name": "Branche Test",
                "email": "branche@example.com",
                "service": "Erstgespräch",
                "message": "Automatisierung im Handwerksbetrieb prüfen.",
                "privacy": "accepted",
                "website": "",
            },
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["success"])

        with self.app.app_context():
            saved = ContactMessage.query.filter_by(email="branche@example.com").first()
            self.assertIsNotNone(saved)
            self.assertEqual(saved.source, "organic")
            self.assertEqual(saved.medium, "landing")
            self.assertEqual(saved.campaign, "branche_handwerk")

    # ── Indexierung ────────────────────────────────────────────────────

    def test_branch_pages_are_indexable(self):
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                resp = self._get(f"/branchen/{slug}")
                html = resp.get_data(as_text=True)
                self.assertIn('name="robots" content="index, follow', html)
                self.assertNotIn('name="robots" content="noindex', html)

    # ── NOVA-Pflichten: Integration (Kfz/Immobilien), related_articles (Kanzleien) ──

    def test_integration_section_only_on_kfz_and_immobilien(self):
        for slug in ("kfz", "immobilien"):
            with self.subTest(slug=slug):
                html = self._get(f"/branchen/{slug}").get_data(as_text=True)
                self.assertIn("landing-integration", html, "Integration-Sektion fehlt (NOVA-Pflicht)")
        for slug in ("handwerk", "kanzleien"):
            with self.subTest(slug=slug):
                html = self._get(f"/branchen/{slug}").get_data(as_text=True)
                self.assertNotIn("landing-integration", html)

    def test_kanzleien_has_related_articles(self):
        html = self._get("/branchen/kanzleien").get_data(as_text=True)
        self.assertIn("/wissen/rag-wissensassistenten", html)
        self.assertIn("/wissen/lokale-ki-vs-cloud-ki", html)

    def test_branch_pages_link_to_services(self):
        html = self._get("/branchen/handwerk").get_data(as_text=True)
        for service in ("/ki-agenten", "/n8n-automatisierung", "/lokale-ki"):
            self.assertIn(service, html)

    # ── Trust / ROI / Autor (DoD Trust Architecture) ───────────────────

    def test_branch_roi_and_trust_and_author(self):
        for slug in BRANCHES:
            with self.subTest(slug=slug):
                html = self._get(f"/branchen/{slug}").get_data(as_text=True)
                self.assertIn("landing-roi", html)
                self.assertIn("landing-trust", html)
                self.assertIn("landing-author", html)
                self.assertIn("Wer dahintersteht", html)
                self.assertIn("Xavier Escalante Castellar", html)
                self.assertIn("certificates_xavier_escalante.pdf", html)

    def test_branch_footer_links_present(self):
        html = self._get("/branchen/handwerk").get_data(as_text=True)
        for slug in BRANCHES:
            self.assertIn(f"/branchen/{slug}", html)


if __name__ == "__main__":
    unittest.main()
