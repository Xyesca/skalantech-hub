"""Regression tests for the first-party, cookie-less analytics pipeline.

Deckt den kompletten Event-Flow ab:
  Client (Beacon)  →  POST /analytics/event  →  analytics_events (SQLite)
  Formular (POST)  →  serverseitige Conversion-Events (lead_created,
                      demo_completed, meeting_booked) inkl. Session-/UTM-Attribution

Hermetisch: keine app-Importe auf Modulebene, damit die Datei unabhängig von
der Ausführungsreihenfolge (test_crm.py & Co. cachen app-Module mit eigener
DATABASE_URL) gegen die eigene Test-DB läuft.
"""
import importlib
import json
import os
import sys
import tempfile
import unittest


def _drop_app_modules():
    """Entferne gecachte app-Module, damit DATABASE_URL/Env je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class AnalyticsEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"

        _drop_app_modules()
        from app import create_app
        from app.models import AnalyticsEvent, ContactMessage, Lead

        cls.app = create_app("production")
        cls.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
        )
        cls.AnalyticsEvent = AnalyticsEvent
        cls.ContactMessage = ContactMessage
        cls.Lead = Lead
        cls.public_module = importlib.import_module("app.blueprints.public")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            self.AnalyticsEvent.query.delete()
            self.ContactMessage.query.delete()
            self.Lead.query.delete()
            from app.extensions import db

            db.session.commit()

    def _events(self):
        with self.app.app_context():
            return self.AnalyticsEvent.query.order_by(self.AnalyticsEvent.id.asc()).all()

    def _post_event(self, payload, headers=None):
        headers = dict(headers or {})
        headers.setdefault("Content-Type", "application/json")
        return self.client.post("/analytics/event", data=json.dumps(payload), headers=headers)

    # ── Endpoint ────────────────────────────────────────────────────────

    def test_valid_event_is_stored(self):
        response = self._post_event({
            "event": "page_view",
            "page": "/",
            "session_id": "sess-abc-123",
            "source": "google",
            "medium": "organic",
            "campaign": "seo",
            "props": {"foo": "bar"},
        })
        self.assertEqual(response.status_code, 204)

        events = self._events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event, "page_view")
        self.assertEqual(events[0].page, "/")
        self.assertEqual(events[0].session_id, "sess-abc-123")
        self.assertEqual(events[0].source, "google")
        self.assertEqual(events[0].medium, "organic")
        self.assertEqual(events[0].campaign, "seo")
        self.assertEqual(json.loads(events[0].props), {"foo": "bar"})
        self.assertTrue(events[0].user_agent)  # Server-seitig erfasst

    def test_all_required_events_are_accepted(self):
        for event in (
            "demo_started", "demo_completed", "contact_clicked",
            "calendar_opened", "meeting_booked", "service_viewed",
            "case_study_viewed", "roi_calculated", "lead_created",
        ):
            with self.subTest(event=event):
                response = self._post_event({"event": event, "page": "/"})
                self.assertEqual(response.status_code, 204)

        stored = {e.event for e in self._events()}
        self.assertEqual(
            stored,
            {"demo_started", "demo_completed", "contact_clicked", "calendar_opened",
             "meeting_booked", "service_viewed", "case_study_viewed",
             "roi_calculated", "lead_created"},
        )

    def test_unknown_event_is_silently_dropped(self):
        response = self._post_event({"event": "nonsense_event", "page": "/"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(self._events()), 0)

    def test_rebrand_events_accepted(self):
        """Issue #3 (Studio-Rebrand): Nachweise-/Demo-Tracking-Events
        (case_study_click, demo_clicked) sind serverseitig erlaubt."""
        for event in ("case_study_click", "demo_clicked"):
            with self.subTest(event=event):
                response = self._post_event({
                    "event": event, "page": "/", "props": {"label": "hero"},
                })
                self.assertEqual(response.status_code, 204)
        stored = {e.event for e in self._events()}
        self.assertIn("case_study_click", stored)
        self.assertIn("demo_clicked", stored)

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/analytics/event",
            data="not json at all",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 400)

    def test_oversized_props_returns_413(self):
        response = self._post_event({
            "event": "page_view",
            "props": {"blob": "x" * 5000},
        })
        self.assertEqual(response.status_code, 413)
        self.assertEqual(len(self._events()), 0)

    def test_get_method_not_allowed(self):
        response = self.client.get("/analytics/event")
        self.assertEqual(response.status_code, 405)

    def test_endpoint_is_csrf_exempt(self):
        """Beacon hat kein Session-Token — der Blueprint ist per csrf.exempt() frei."""
        app = self.app
        old_check = app.config.get("WTF_CSRF_ENABLED")
        app.config["WTF_CSRF_ENABLED"] = True
        try:
            response = self._post_event({"event": "page_view", "page": "/"})
            self.assertEqual(response.status_code, 204)
            self.assertEqual(len(self._events()), 1)
        finally:
            app.config["WTF_CSRF_ENABLED"] = old_check

    # ── Serverseitige Conversion-Events aus dem Formular ────────────────

    def _submit_contact(self, extra=None, headers=None):
        data = {
            "name": "Analytics Test",
            "company": "Analytics GmbH",
            "email": "analytics@example.com",
            "service": "Prozessautomatisierung",
            "message": "Wir wollen einen Ablauf automatisieren.",
            "privacy": "accepted",
            "website": "",
            # Von analytics.js injizierte Hidden-Fields (First-Touch-Attribution)
            "session_id": "sess-form-1",
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "kampagne-a",
        }
        if extra:
            data.update(extra)
        return self.client.post(
            "/contact",
            data=data,
            headers=headers or {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )

    def test_contact_submit_records_lead_created_with_attribution(self):
        response = self._submit_contact()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

        events = self._events()
        lead_created = [e for e in events if e.event == "lead_created"]
        self.assertEqual(len(lead_created), 1)
        self.assertEqual(lead_created[0].session_id, "sess-form-1")
        self.assertEqual(lead_created[0].source, "google")
        self.assertEqual(lead_created[0].medium, "cpc")
        self.assertEqual(lead_created[0].campaign, "kampagne-a")
        self.assertEqual(json.loads(lead_created[0].props), {"service": "Prozessautomatisierung"})

        # Session-Attribution landet auch am Lead/der Nachricht (Funnel-Stitching)
        with self.app.app_context():
            message = self.ContactMessage.query.filter_by(email="analytics@example.com").first()
            lead = self.Lead.query.filter_by(email="analytics@example.com").first()
            self.assertEqual(message.session_id, "sess-form-1")
            self.assertEqual(lead.session_id, "sess-form-1")

    def test_booking_submit_records_demo_completed_but_no_meeting_without_n8n(self):
        # Hermetisch: n8n-Forwarder gemockt (auf dem VPS ist der Webhook sonst
        # live erreichbar → Test wäre vom Netzwerk-Zustand abhängig).
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": False,
            "status": "unreachable",
            "message": "Termindienst nicht erreichbar.",
        }
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        # n8n down → Anfrage bleibt gespeichert, KEIN 409, queued-Erfolgsansicht (D3)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["booking"]["status"], "queued")

        names = {e.event for e in self._events()}
        self.assertIn("lead_created", names)
        self.assertIn("demo_completed", names)
        self.assertIn("booking_error", names)
        # n8n ohne Erfolg → keine echte Buchung
        self.assertNotIn("meeting_booked", names)

    def test_booking_with_n8n_success_records_meeting_booked(self):
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {"success": True, "status": "confirmed", "message": "ok"}
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        self.assertEqual(response.status_code, 200)
        events = self._events()
        meeting = [e for e in events if e.event == "meeting_booked"]
        self.assertEqual(len(meeting), 1)
        self.assertEqual(
            json.loads(meeting[0].props),
            {"day": "2026-09-15", "time": "10:00", "service": "Potenzial-Check"},
        )
        self.assertIn("demo_completed", {e.event for e in events})

    # ── Lead-Funnel-Kette (LUMINA-Spez §6 / D6) ─────────────────────────

    def test_booking_events_accepted_by_allowlist(self):
        """booking_error + booking_confirmed sind in der Event-Taxonomie
        (D6) und werden vom /analytics/event-Endpoint akzeptiert."""
        for event in ("booking_error", "booking_confirmed"):
            with self.subTest(event=event):
                response = self._post_event({"event": event, "page": "/"})
                self.assertEqual(response.status_code, 204)

        stored = {e.event for e in self._events()}
        self.assertEqual(stored, {"booking_error", "booking_confirmed"})

    def test_funnel_chain_page_view_to_meeting_booked(self):
        """Komplette Funnel-Kette in EINER Session (LUMINA-Spez §6):
        page_view → demo_started → calendar_opened → form_submit
        → (Server) demo_completed → meeting_booked — in dieser Reihenfolge
        mit derselben session_id (Funnel-Stitching)."""
        session = "sess-funnel-1"
        for event in ("page_view", "demo_started", "calendar_opened", "form_submit"):
            response = self._post_event({"event": event, "page": "/", "session_id": session})
            self.assertEqual(response.status_code, 204)

        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": True,
            "status": "confirmed",
            "message": "ok",
        }
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
                "session_id": session,
            })
        finally:
            self.public_module._forward_to_n8n = original

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["booking"]["status"], "confirmed")

        chain = [e.event for e in self._events() if e.session_id == session]
        # lead_created wird serverseitig bei jedem /contact-POST geschrieben
        # (vor dem n8n-Call) — die Kette in DB-Reihenfolge:
        self.assertEqual(
            chain,
            ["page_view", "demo_started", "calendar_opened", "form_submit",
             "lead_created", "demo_completed", "meeting_booked"],
        )
        # Die Conversion-relevante Funnel-Kette (LUMINA-Spez §6) ist darin enthalten:
        funnel = [name for name in chain if name in
                  ("page_view", "demo_started", "calendar_opened", "form_submit",
                   "demo_completed", "meeting_booked")]
        self.assertEqual(
            funnel,
            ["page_view", "demo_started", "calendar_opened", "form_submit",
             "demo_completed", "meeting_booked"],
        )
        meeting_events = [e for e in self._events()
                          if e.session_id == session and e.event == "meeting_booked"]
        self.assertEqual(len(meeting_events), 1)
        self.assertEqual(
            json.loads(meeting_events[0].props),
            {"day": "2026-09-15", "time": "10:00", "service": "Potenzial-Check"},
        )

    def test_booking_error_invalid_response_reason(self):
        """n8n liefert kein valides JSON → booking_error mit
        props.reason='invalid_response' (D6), Lead bleibt gespeichert."""
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": False,
            "status": "invalid_response",
            "message": "Termindienst hat keine gültige Antwort geliefert.",
        }
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["booking"]["status"], "queued")

        errors = [e for e in self._events() if e.event == "booking_error"]
        self.assertEqual(len(errors), 1)
        self.assertEqual(json.loads(errors[0].props), {"reason": "invalid_response"})
        self.assertNotIn("meeting_booked", {e.event for e in self._events()})

    def test_slot_taken_is_no_booking_error(self):
        """„Slot belegt“ (n8n success:false) ist ein normaler Nutzerpfad (D2):
        KEIN booking_error, KEIN meeting_booked — Lead bleibt 'lead'."""
        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": False,
            "status": "slot_taken",
            "message": "Der gewünschte Termin ist leider bereits belegt.",
        }
        try:
            response = self._submit_contact(extra={
                "book_slot": "1",
                "preferred_day": "2026-09-15",
                "preferred_time": "10:00",
            })
        finally:
            self.public_module._forward_to_n8n = original

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertFalse(body["success"])
        self.assertEqual(
            body["message"], "Der gewünschte Termin ist leider bereits belegt.",
        )
        names = {e.event for e in self._events()}
        self.assertIn("lead_created", names)
        self.assertIn("demo_completed", names)
        self.assertNotIn("booking_error", names)
        self.assertNotIn("meeting_booked", names)

        with self.app.app_context():
            lead = self.Lead.query.filter_by(email="analytics@example.com").first()
            self.assertEqual(lead.status, "lead")  # nicht qualifiziert

    # ── ROI-Rechner (roi_calculated, P1 /rechner) ───────────────────────

    def test_roi_calculated_full_props_recalc_and_cta_stored(self):
        """P1 ROI-Rechner (04_EVENT-SPEC §2): POST /analytics/event mit
        roi_calculated + voller Props-Liste (action=recalc UND action=cta)
        → 204 + DB-Read-back: props-JSON exakt gespeichert, Zahlentypen
        (int/float) bleiben erhalten — Basis des „gerechnet → gehandelt“-Funnels."""
        props_recalc = {
            "process": "angebote",
            "source": "rechner",
            "minutes": 60,
            "frequency": 5,
            "error_share": 10,
            "rate": 55,
            "automation_share": 70,
            "hours_per_week": 5.5,
            "hours_per_year": 258.5,
            "annual_cost": 14200,
            "savings_hours": 181,
            "savings_euro": 10000,
            "action": "recalc",
        }
        props_cta = dict(props_recalc, action="cta")

        for props in (props_recalc, props_cta):
            with self.subTest(action=props["action"]):
                response = self._post_event({
                    "event": "roi_calculated",
                    "page": "/rechner",
                    "session_id": "sess-roi-p1",
                    "props": props,
                })
                self.assertEqual(response.status_code, 204)

        events = self._events()
        roi_events = [e for e in events if e.event == "roi_calculated"]
        self.assertEqual(len(roi_events), 2)
        self.assertEqual([e.page for e in roi_events], ["/rechner", "/rechner"])
        self.assertEqual(json.loads(roi_events[0].props), props_recalc)
        self.assertEqual(json.loads(roi_events[1].props), props_cta)

        # Zahlentypen überstehen den JSON-Roundtrip (Props nur Zahlen/Slugs, keine PII)
        stored = json.loads(roi_events[0].props)
        self.assertIsInstance(stored["hours_per_week"], float)
        self.assertIsInstance(stored["hours_per_year"], float)
        self.assertIsInstance(stored["annual_cost"], int)
        self.assertIsInstance(stored["savings_hours"], int)
        self.assertIsInstance(stored["savings_euro"], int)

    # ── Client-Kontrakt (analytics.js / main.js) ────────────────────────

    def test_client_event_allowlist_matches_spec(self):
        """D6-Client-Kontrakt: analytics.js enthält booking_confirmed,
        aber NICHT booking_error (Server-only-Event). main.js feuert
        booking_confirmed genau 1× pro Submit (Guard-Flag)."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        analytics_js = (repo_root / "app" / "static" / "js" / "analytics.js").read_text(encoding="utf-8")
        self.assertIn('"booking_confirmed"', analytics_js)
        self.assertNotIn('"booking_error"', analytics_js)

        main_js = (repo_root / "app" / "static" / "js" / "main.js").read_text(encoding="utf-8")
        self.assertIn("bookingConfirmedTracked", main_js)
        self.assertIn('"booking_confirmed"', main_js)

    def test_roi_rechner_js_emits_full_props_contract(self):
        """P1 ROI-Rechner (04 §2): roi-rechner.js sendet die volle Props-Liste
        inkl. action (recalc|cta); analytics.js-Allowlist enthält
        roi_calculated. Regression-Guard: Props-Drift bricht den Test,
        nicht erst die Doku."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        roi_js = (repo_root / "app" / "static" / "js" / "roi-rechner.js").read_text(encoding="utf-8")
        analytics_js = (repo_root / "app" / "static" / "js" / "analytics.js").read_text(encoding="utf-8")

        for key in ("process", "source", "minutes", "frequency", "error_share",
                    "rate", "automation_share", "hours_per_week", "hours_per_year",
                    "annual_cost", "savings_hours", "savings_euro", "action"):
            with self.subTest(key=key):
                self.assertIn(key + ":", roi_js)
        self.assertIn('"recalc"', roi_js)
        self.assertIn('"cta"', roi_js)
        self.assertIn('"roi_calculated"', analytics_js)

    # ── Template-Integration ────────────────────────────────────────────

    def test_homepage_loads_analytics_script(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        self.assertIn("js/analytics.js?v=19", html)
        # Reihenfolge: analytics.js VOR main.js (Attribution vor Formular-Submit)
        self.assertLess(html.index("analytics.js"), html.index("main.js"))

    def test_datenschutz_discloses_event_tracking(self):
        response = self.client.get("/datenschutz")
        html = response.get_data(as_text=True)
        self.assertIn("anonyme Interaktions-Events", html)
        self.assertIn("keine Cookies", html)

    def test_rebrand_project_demo_hooks_present(self):
        """Issue #3 (Studio-Rebrand) + Customer-First: Demo-Klicks sind
        trackbar — data-track-Hooks in index.html + Client-Selektoren.
        Regression-Guard: ein künftiger Rebrand darf diese Hooks nicht
        stillschweigend entfernen."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        index_html = (repo_root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
        base_html = (repo_root / "app" / "templates" / "base.html").read_text(encoding="utf-8")
        analytics_js = (repo_root / "app" / "static" / "js" / "analytics.js").read_text(encoding="utf-8")

        # Demo-Klicks trackbar (Hero + Demo-Karten)
        self.assertIn('data-track="demo_clicked" data-track-label="hero"', index_html)
        self.assertIn('data-track="demo_clicked" data-track-label="invoiceflow"', index_html)
        self.assertIn('data-track="demo_clicked" data-track-label="offerai"', index_html)
        self.assertIn('data-track="demo_clicked" data-track-label="mailagent"', index_html)
        # Customer-First: Projekt-Nachweise verlinken auf die Live-Demos
        self.assertIn('data-track="demo_clicked" data-track-label="invoiceflow"', index_html)
        self.assertIn('data-track="demo_clicked" data-track-label="offerai"', index_html)
        self.assertIn('data-track="demo_clicked" data-track-label="mailagent"', index_html)
        # case_study_click bleibt in der Event-Allowlist (Landingpages/Projekte),
        # auch wenn die Homepage selbst keine DeepDive-Case-Study mehr trackt.
        self.assertIn('"case_study_click"', analytics_js)
        # Neue Projekt-Karten zählen als Case Studies (Viewport)
        self.assertIn('".work-card, .project-card"', analytics_js)
        # Leistungs-Karten (usecase/pain) zählen als service_viewed
        self.assertIn('".service-card, .usecase-card, .pain-card"', analytics_js)
        # Client-Allowlist enthält die neuen Events
        self.assertIn('"case_study_click"', analytics_js)
        self.assertIn('"demo_clicked"', analytics_js)

    def test_customer_first_service_label_canonical(self):
        """Customer-First (C15, PULSE): Das service-Label des Buchungs-Funnels ist
        kanonisch „Potenzial-Check“. (1) Header-CTA trägt weiterhin die Klasse
        `header-cta` (demo_started-Label „header“), (2) alle „Potenzial-Check“-
        CTA-Links zeigen weiterhin auf `#termin` (demo_started-Labels hero/section),
        (3) das versteckte service-Feld im Buchungsformular ist vom dokumentierten
        Label-Mapping abgedeckt (Legacy „Business-Analyse“ wird serverseitig auf
        „Potenzial-Check“ kanonisiert), (4) der neue Footer-Potenzial-Check ist als
        demo_started/footer getrackt. Regression-Guard gegen stillschweigende
        Entkopplung von Copy und Tracking (Mapping: docs/ANALYTICS_EVENTS.md §0)."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent
        index_html = (repo_root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
        base_html = (repo_root / "app" / "templates" / "base.html").read_text(encoding="utf-8")

        # 1) Header-CTA: Klasse bleibt → analytics.js wireClick('.header-cta, …')
        self.assertIn('class="header-cta"', base_html)
        self.assertIn("Potenzial-Check buchen", base_html)
        # 2) CTA-Links → #termin (hero + section)
        self.assertIn('href="#termin"', index_html)
        # 3) Hidden service-Feld: Wert ist vom Label-Mapping abgedeckt
        #    („Business-Analyse“ → kanonisch „Potenzial-Check“; C15)
        self.assertIn('name="service" value="', index_html)
        hidden_service = index_html.split('name="service" value="', 1)[1].split('"', 1)[0]
        self.assertIn(hidden_service, ("Business-Analyse", "Potenzial-Check"))
        # 4) Footer-Potenzial-Check getrackt (demo_started, Label footer)
        self.assertIn('data-track="demo_started" data-track-label="footer"', base_html)

    def test_booking_service_label_canonicalized_to_potenzial_check(self):
        """C15 (PULSE): Alt-Labels „Business-Analyse“ (Formular-Hidden-Field) und
        „Erstgespräch“ (CRM-Historie) werden beim Formular-POST auf das kanonische
        Label „Potenzial-Check“ gemappt — lead_created, demo_completed und
        meeting_booked tragen damit in derselben Buchung ein einheitliches
        service-Label. Event-Namen bleiben unverändert (keine Breaking-Change)."""
        from app.extensions import db as _db

        original = self.public_module._forward_to_n8n
        self.public_module._forward_to_n8n = lambda *a, **kw: {
            "success": True,
            "status": "confirmed",
            "message": "ok",
        }
        try:
            for legacy in ("Business-Analyse", "Erstgespräch"):
                with self.subTest(legacy=legacy):
                    with self.app.app_context():
                        self.AnalyticsEvent.query.delete()
                        _db.session.commit()
                    response = self._submit_contact(extra={
                        "book_slot": "1",
                        "preferred_day": "2026-09-15",
                        "preferred_time": "10:00",
                        "service": legacy,
                    })
                    self.assertEqual(response.status_code, 200)
                    events = {e.event: json.loads(e.props) for e in self._events()}
                    self.assertEqual(events["lead_created"]["service"], "Potenzial-Check")
                    self.assertEqual(events["demo_completed"]["service"], "Potenzial-Check")
                    self.assertEqual(events["meeting_booked"]["service"], "Potenzial-Check")
        finally:
            self.public_module._forward_to_n8n = original


if __name__ == "__main__":
    unittest.main()
