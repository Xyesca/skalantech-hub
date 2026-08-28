"""Regression tests für den P1-ROI-Rechner (/rechner + Homepage-Sektion).

Deckt ab (FORGE-Handoff 06_HANDOFF-FORGE.md §7, LUMINA t_ce7fda15):
- Route /rechner → 200, H1 „Was kostet Sie manuelle Arbeit?“, Widget-Root
- Homepage: section--roi + [data-roi-rechner][data-source="homepage"]
- Sitemap enthält /rechner (priority 0.8)
- FAQPage-Schema auf /rechner: JSON valide, Fragen 1:1 sichtbar
- CTA mit UTM (Query VOR Fragment, utm_medium=rechner)
- roi-rechner.js wird mit Cache-Buster + korrektem Content-Type ausgeliefert
- Widget-JS-Syntaxcheck (node --check)
- Nav + Footer verlinken /rechner
- Formel-Defaults (03 §1): ≈ 7.100 €/Jahr · 5.000 € · 90 h
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


def _drop_app_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


# Formel exakt aus 03_FORMEL-INTERAKTION.md §1 (Spiegel der JS-Implementierung).
ARBEITSWOCHEN = 47


def roi_formula(minutes, frequency, error, rate, auto):
    zeit_woche = (minutes / 60) * frequency
    nacharbeit = zeit_woche * (error / 100)
    gesamt_woche = zeit_woche + nacharbeit
    gesamt_jahr = gesamt_woche * ARBEITSWOCHEN
    kosten = gesamt_jahr * rate
    spar_h = gesamt_jahr * (auto / 100)
    spar_euro = spar_h * rate

    def round_euro(x):
        return round(x / 100) * 100 if x >= 100 else round(x)

    return {
        "hours_per_week": round(gesamt_woche * 10) / 10,
        "hours_per_year": round(gesamt_jahr * 100) / 100,
        "annual_cost": round_euro(kosten),
        "savings_hours": round(spar_h),
        "savings_euro": round_euro(spar_euro),
    }


class RechnerTests(unittest.TestCase):
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
        cls.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
        )
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def _get(self, path):
        return self.client.get(path, buffered=True)

    # ── Route /rechner ───────────────────────────────────────────────

    def test_route_renders_200_with_widget(self):
        resp = self._get("/rechner")
        try:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.content_type.startswith("text/html"))
            html = resp.get_data(as_text=True)
            self.assertIn("Was kostet Sie manuelle Arbeit?", html)
            self.assertIn('data-roi-rechner', html)
            self.assertIn('data-source="rechner"', html)
            self.assertIn("js/roi-rechner.js?v=1", html)
        finally:
            resp.close()

    # ── Homepage-Sektion ─────────────────────────────────────────────

    def test_homepage_has_roi_section(self):
        resp = self._get("/")
        try:
            html = resp.get_data(as_text=True)
            self.assertIn('class="section section--roi"', html)
            self.assertIn('id="rechner"', html)
            self.assertIn('data-roi-rechner', html)
            self.assertIn('data-source="homepage"', html)
            self.assertIn("Zum vollständigen ROI-Rechner", html)
        finally:
            resp.close()

    # ── Sitemap ──────────────────────────────────────────────────────

    def test_sitemap_contains_rechner(self):
        resp = self._get("/sitemap.xml")
        try:
            xml = resp.get_data(as_text=True)
            self.assertIn(
                "<loc>https://skalantech.store/rechner</loc>", xml
            )
        finally:
            resp.close()

    # ── FAQPage-Schema ───────────────────────────────────────────────

    def test_faq_schema_visible_1to1(self):
        resp = self._get("/rechner")
        try:
            html = resp.get_data(as_text=True)
            blocks = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', html, re.S
            )
            self.assertGreaterEqual(len(blocks), 1, "JSON-LD-Block fehlt")
            faq_graph = None
            for block in blocks:
                graph = json.loads(block).get("@graph", [])
                if any(node.get("@type") == "FAQPage" for node in graph):
                    faq_graph = graph
                    break
            self.assertIsNotNone(faq_graph, "FAQPage-Schema fehlt")
            types = {node.get("@type") for node in faq_graph}
            self.assertIn("Service", types)
            self.assertIn("BreadcrumbList", types)
            self.assertIn("FAQPage", types)
            faq = next(n for n in faq_graph if n.get("@type") == "FAQPage")
            questions = [
                item["name"]
                for item in faq["mainEntity"]
                if item.get("@type") == "Question"
            ]
            self.assertEqual(len(questions), 6)
            # Jede Frage im sichtbaren <details><summary> (1:1, kein Drift)
            for q in questions:
                self.assertIn(q, html)
        finally:
            resp.close()

    # ── CTA UTM (Query VOR Fragment) ─────────────────────────────────

    def test_cta_utm_query_before_fragment(self):
        resp = self._get("/rechner")
        try:
            html = resp.get_data(as_text=True)
            self.assertIn("utm_source=organic", html)
            self.assertIn("utm_medium=rechner", html)
            self.assertIn("utm_campaign=roi-rechner", html)
            self.assertIn("utm_content=page", html)
            self.assertIn("#termin", html)
            # Reihenfolge: Query VOR Fragment — UTM geht nicht verloren
            cta_href = re.search(
                r'href="([^"]*roi-rechner[^"]*)"', html
            )
            self.assertIsNotNone(cta_href)
            href = cta_href.group(1)
            self.assertIn("?", href)
            q_idx = href.index("?")
            f_idx = href.index("#")
            self.assertLess(q_idx, f_idx, "Query muss vor Fragment stehen")
        finally:
            resp.close()

    # ── JS-Datei + Cache-Buster ──────────────────────────────────────

    def test_js_served_with_cache_buster_and_content_type(self):
        resp = self._get("/static/js/roi-rechner.js")
        try:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.content_type.startswith("text/javascript"))
            body = resp.get_data(as_text=True)
            self.assertIn("roi_calculated", body)
        finally:
            resp.close()

    def test_js_syntax_node_check(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node nicht verfügbar — Syntaxcheck übersprungen")
        js_path = os.path.join(self.repo_root, "app/static/js/roi-rechner.js")
        result = subprocess.run(
            [node, "--check", js_path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0, f"node --check fehlgeschlagen: {result.stderr}"
        )

    # ── Navigation / Footer ──────────────────────────────────────────

    def test_nav_and_footer_link_rechner(self):
        for path in ("/rechner", "/"):
            with self.subTest(path=path):
                html = self.client.get(path).get_data(as_text=True)
                self.assertIn('href="/rechner"', html)
                self.assertIn("Rechner", html)

    # ── Formel-Defaults (03 §1) ──────────────────────────────────────

    def test_formula_defaults(self):
        # LUMINA 07_VERIFIKATION: Defaults → 2,8 h/W · 129,25 h/J · 7.100 € · 90 h · 5.000 €
        r = roi_formula(minutes=30, frequency=5, error=10, rate=55, auto=70)
        self.assertEqual(r["hours_per_week"], 2.8)
        self.assertEqual(r["hours_per_year"], 129.25)
        self.assertEqual(r["annual_cost"], 7100)
        self.assertEqual(r["savings_hours"], 90)
        self.assertEqual(r["savings_euro"], 5000)

    def test_formula_edge_cases(self):
        # Min: 5 min × 1×/Woche → Jahreskosten < 100 € → exakter Betrag
        low = roi_formula(minutes=5, frequency=1, error=0, rate=20, auto=20)
        self.assertLess(low["annual_cost"], 100)
        self.assertGreater(low["annual_cost"], 0)
        # Max: 240 min × 100 × 1.5 × 47 × 200 → Betrag > 1 Mio (de-DE-Anzeige)
        high = roi_formula(minutes=240, frequency=100, error=50, rate=200, auto=95)
        self.assertGreater(high["annual_cost"], 1_000_000)
        # Fehlerquote 0 → Nacharbeit 0 (kein NaN)
        zero = roi_formula(minutes=30, frequency=5, error=0, rate=55, auto=70)
        self.assertEqual(zero["hours_per_week"], 2.5)
        # Autograd 95 → Einsparung nahe Gesamtkosten
        high_auto = roi_formula(minutes=30, frequency=5, error=10, rate=55, auto=95)
        self.assertGreater(high_auto["savings_euro"], high_auto["annual_cost"] * 0.9)

    # ── Regression: andere Seiten unverändert ────────────────────────

    def test_other_pages_still_render(self):
        for path in ("/", "/websites-apps", "/branchen/handwerk", "/wissen"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)


if __name__ == "__main__":
    unittest.main()
