"""Regression tests für die Case-Study-Seite „Anwendungsbeispiel Handwerk".

Deckt ab (DoD FORGE-Build, Vorgaben aus t_b8829870 + Sperren CLOSER/SENTINEL):
- Route /case-studies/anwendungsbeispiel-handwerk → 200, unknown slug → 404
- Sitemap enthält die Case-Study-URL
- SEO-Meta: title (<=60), description, canonical, OG/Twitter, indexierbar
- Label „Anwendungsbeispiel Handwerk" sichtbar (Badge/Kicker) + H1 enthält „Anwendungsbeispiel"
- Alle Pflicht-Sektionen gerendert (intro/problem/solution/setup/ergebnis/erechnung/process/fazit)
- Zahlenbox: 520/65/33.800 + Sensitivität 187/23/12.200, Quelle + roi_note-Disclaimer
- Sperren: kein „Live-Terminbuchung"-Claim, „erprobt"-Marker vorhanden, keine Prozent-Claims
- CTA-UTM: Query VOR Fragment (case_handwerk)
- JSON-LD valide (Article + BreadcrumbList)
- Interne Verlinkung: related_landing (/branchen/handwerk) + related_articles (/wissen/...)
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


SLUG = "anwendungsbeispiel-handwerk"
PATH = f"/case-studies/{SLUG}"


class CaseStudyTests(unittest.TestCase):
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

    # ── Route ─────────────────────────────────────────────────────────

    def test_route_renders_200(self):
        resp = self._get(PATH)
        try:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.content_type.startswith("text/html"))
        finally:
            resp.close()

    def test_unknown_slug_404(self):
        self.assertEqual(self._get("/case-studies/gibt-es-nicht").status_code, 404)

    # ── Sitemap ────────────────────────────────────────────────────────

    def test_sitemap_contains_case_study_url(self):
        resp = self._get("/sitemap.xml")
        body = resp.get_data(as_text=True)
        self.assertIn(f"https://skalantech.store/case-studies/{SLUG}</loc>", body)
        self.assertIn("<priority>0.8</priority>", body)

    # ── SEO-Meta ───────────────────────────────────────────────────────

    def test_meta_title_length_and_description(self):
        resp = self._get(PATH)
        html = resp.get_data(as_text=True)
        from app.case_studies import CASE_STUDIES

        cs = CASE_STUDIES[SLUG]
        self.assertIn(f"<title>{cs['title']}</title>", html)
        self.assertLessEqual(len(cs["title"]), 60, "SEO-Title darf 60 Zeichen nicht überschreiten")
        self.assertIn(
            f'<meta name="description" content="{cs["description"]}"', html
        )

    def test_canonical_and_social_meta(self):
        html = self._get(PATH).get_data(as_text=True)
        canonical = f'<link rel="canonical" href="https://skalantech.store/case-studies/{SLUG}">'
        self.assertIn(canonical, html)
        self.assertIn(
            f'property="og:url" content="https://skalantech.store/case-studies/{SLUG}"',
            html,
        )
        self.assertIn('name="twitter:title"', html)
        self.assertIn('name="twitter:description"', html)

    def test_page_is_indexable(self):
        html = self._get(PATH).get_data(as_text=True)
        self.assertIn('name="robots" content="index, follow', html)
        self.assertNotIn('name="robots" content="noindex', html)

    # ── Label (Sperre 1: kein erfundener Kunde) ────────────────────────

    def test_label_visible_as_badge_and_in_h1(self):
        html = self._get(PATH).get_data(as_text=True)
        # Badge/Kicker auf der Seite sichtbar
        self.assertIn("Anwendungsbeispiel Handwerk", html)
        # H1 = title_redaktion, muss das Label tragen
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        self.assertIsNotNone(h1, "H1 fehlt")
        self.assertIn("Anwendungsbeispiel", h1.group(1))
        # Kein erfundener Firmenname als Kunde
        for fake in ("Muster GmbH", "Beispiel GmbH & Co", "Herr Mustermann"):
            self.assertNotIn(fake, html)

    # ── Pflicht-Sektionen ──────────────────────────────────────────────

    def test_all_required_sections_visible(self):
        from app.case_studies import CASE_STUDIES

        cs = CASE_STUDIES[SLUG]
        html = self._get(PATH).get_data(as_text=True)
        for text in [
            cs["intro"],
            cs["problem_title"],
            cs["solution_title"],
            cs["setup_note"],
            cs["ergebnis_title"],
            cs["erechnung_title"],
            cs["erechnung_note"],
            cs["process_title"],
            cs["fazit_title"],
            cs["fazit_paragraphs"][0],
            cs["cta_primary"],
            cs["cta_secondary"],
        ]:
            with self.subTest(text=text[:40]):
                self.assertIn(text, html)

    def test_problem_solution_process_counts(self):
        from app.case_studies import CASE_STUDIES

        cs = CASE_STUDIES[SLUG]
        html = self._get(PATH).get_data(as_text=True)
        # Alle 4 Problem-Punkte, 3 Lösungs-Bausteine (Überschrift), 3 Prozess-Schritte
        for item in cs["problem"]:
            self.assertIn(item, html)
        for heading, _text in cs["solution"]:
            self.assertIn(heading, html)
        for heading, _text in cs["process"]:
            self.assertIn(heading, html)
        for fact in cs["erechnung_facts"]:
            self.assertIn(fact, html)

    # ── Zahlenbox (Sperre 4 + 5) ───────────────────────────────────────

    def test_numbers_box_exact_values(self):
        html = self._get(PATH).get_data(as_text=True)
        # Defaults: 520 h / 65 Arbeitstage / 33.800 € bei 65 €/h
        self.assertIn(">520</strong> Stunden pro Jahr", html)
        self.assertIn("65 Arbeitstage", html)
        self.assertIn("33.800 €/Jahr", html)
        self.assertIn("65 €/h", html)
        # Sensitivität: 187 h / 23 Arbeitstage / 12.200 €
        self.assertIn(">187</strong> Stunden pro Jahr", html)
        self.assertIn("23 Arbeitstage", html)
        self.assertIn("12.200 €/Jahr", html)
        # Quelle des ROI-Rechners
        self.assertIn("ROI-Rechner", html)

    def test_roi_note_disclaimer_under_numbers_box(self):
        from app.case_studies import CASE_STUDIES

        cs = CASE_STUDIES[SLUG]
        html = self._get(PATH).get_data(as_text=True)
        self.assertIn("keine Garantie", html)
        # Disclaimer steht NACH den Zahlen (Position im DOM)
        idx_zahl = html.find("33.800 €/Jahr")
        idx_disclaimer = html.find(cs["zahlen"]["roi_note"])
        self.assertGreater(idx_disclaimer, idx_zahl, "roi_note muss unter der Zahlenbox stehen")

    # ── Sperren (CLOSER P0) ────────────────────────────────────────────

    def test_no_live_terminbuchung_claim(self):
        html = self._get(PATH).get_data(as_text=True)
        self.assertNotIn("Live-Terminbuchung", html)
        self.assertNotIn("live auf dieser Seite", html)
        # Erfolgs-Marker: „erprobt" statt „live"
        self.assertIn("erprobt", html)

    def test_no_percent_claims(self):
        html = self._get(PATH).get_data(as_text=True)
        self.assertNotRegex(html, r"\d+\s*%", "Keine Steigerungsraten/Prozent-Claims erlaubt")

    # ── CTA + UTM ──────────────────────────────────────────────────────

    def test_cta_utm_query_before_fragment(self):
        html = self._get(PATH).get_data(as_text=True)
        expected = (
            "/?utm_source=organic&amp;utm_medium=landing&amp;utm_campaign=case_handwerk#termin"
        )
        self.assertIn(expected, html, "CTA muss UTM-Query VOR dem #termin-Fragment tragen")
        self.assertNotIn("#termin?utm_source", html)
        self.assertIn("case_handwerk", html)

    # ── Analytics (DoD: Events vorhanden + serverseitig erlaubt) ────────

    def test_cta_tracking_events_present_and_allowed(self):
        html = self._get(PATH).get_data(as_text=True)
        # Generisches data-track-API (analytics.js) auf allen CTAs
        self.assertIn('data-track="case_study_click"', html)
        for label in ("case-study-cta-primary", "case-study-cta-secondary",
                      "related-landing", "related-article"):
            with self.subTest(label=label):
                self.assertIn(f'data-track-label="{label}"', html)
        # Serverseitige Allowlist akzeptiert das Event (PULSE-Review)
        resp = self.client.post(
            "/analytics/event",
            json={"event": "case_study_click", "page": PATH,
                  "session_id": "cs-sess", "props": {"label": "case-study-cta-primary"}},
        )
        self.assertEqual(resp.status_code, 204, "case_study_click muss erlaubt sein")

    # ── JSON-LD ────────────────────────────────────────────────────────

    def test_jsonld_valid_and_complete(self):
        html = self._get(PATH).get_data(as_text=True)
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        self.assertGreaterEqual(len(blocks), 1, "JSON-LD-Block fehlt")
        graph = None
        for block in blocks:
            data = json.loads(block)  # wirft bei ungültigem JSON
            g = data.get("@graph", [])
            if any(node.get("@type") == "Article" for node in g):
                graph = g
                break
        self.assertIsNotNone(graph, "Article-Schema fehlt")
        types = {node.get("@type") for node in graph}
        self.assertIn("Article", types)
        self.assertIn("BreadcrumbList", types)

    # ── Interne Verlinkung ─────────────────────────────────────────────

    def test_related_landing_and_articles(self):
        html = self._get(PATH).get_data(as_text=True)
        # related_landing = branchen-handwerk
        self.assertIn("/branchen/handwerk", html)
        # related_articles
        self.assertIn("/wissen/welche-prozesse-ki-automatisierung", html)
        self.assertIn("/wissen/kosten-roi-ki-automatisierung", html)

    # ── Dict-Struktur (Wächter für spätere Änderungen) ─────────────────

    def test_dict_structure_matches_doD(self):
        from app.case_studies import CASE_STUDIES, CASE_STUDY_ORDER

        cs = CASE_STUDIES[SLUG]
        self.assertEqual(cs["type"], "case_study")
        self.assertEqual(len(cs["problem"]), 4)
        self.assertEqual(len(cs["solution"]), 3)
        self.assertEqual(len(cs["erechnung_facts"]), 4)
        self.assertEqual(len(cs["process"]), 3)
        self.assertEqual(CASE_STUDY_ORDER, [SLUG])


if __name__ == "__main__":
    unittest.main()
