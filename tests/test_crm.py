"""Tests für die CRM-Vertriebs-Pipeline (Leads, API, Admin-UI, Follow-ups)."""
import importlib
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

API_KEY = "test-crm-api-key"


def _drop_app_modules():
    """Entferne gecachte app-Module, damit DATABASE_URL/Env je Testklasse greift."""
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


class CrmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["ADMIN_PASSWORD"] = "test-admin-password"
        os.environ["SESSION_COOKIE_SECURE"] = "false"
        os.environ["DATABASE_URL"] = f"sqlite:///{cls.temp_dir.name}/site.db"
        os.environ["CRM_API_KEY"] = API_KEY

        _drop_app_modules()
        from app import create_app

        cls.app = create_app("production")
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        from app.extensions import db

        self.db = db
        self.client = self.app.test_client()

        # Test-Isolation: Leads + Notizen + Analytics-Events + Nachrichten vor
        # jedem Test leeren, damit sich Tests nicht gegenseitig beeinflussen.
        with self.app.app_context():
            from app.models import AnalyticsEvent, Booking, ContactMessage, Lead, LeadNote

            Booking.query.delete()
            LeadNote.query.delete()
            Lead.query.delete()
            AnalyticsEvent.query.delete()
            ContactMessage.query.delete()
            db.session.commit()

        # Rate-Limiter (in-memory) zurücksetzen — sonst kumulieren sich die
        # /contact-POSTs über die Tests hinweg und lösen 400 aus.
        from app.blueprints.public import _CONTACT_LIMITS

        _CONTACT_LIMITS.clear()

    def _login(self):
        return self.client.post(
            "/login",
            data={"username": "admin", "password": "test-admin-password"},
            follow_redirects=True,
        )

    def _api_headers(self):
        return {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    def _create_lead(self, email="anna@beispiel.de", **extra):
        payload = {
            "name": "Anna Beispiel",
            "email": email,
            "company": "Beispiel GmbH",
            "service": "Prozessautomatisierung",
            "source": "google",
            "medium": "organic",
            **extra,
        }
        return self.client.post("/api/crm/leads", json=payload, headers=self._api_headers())

    # ══════════════════════════════════════════════════════════════════
    # API
    # ══════════════════════════════════════════════════════════════════

    def test_api_requires_valid_key(self):
        r = self.client.post("/api/crm/leads", json={"name": "X", "email": "x@x.de"})
        self.assertEqual(r.status_code, 401)
        r = self.client.post(
            "/api/crm/leads",
            json={"name": "X", "email": "x@x.de"},
            headers={"X-API-Key": "wrong-key"},
        )
        self.assertEqual(r.status_code, 401)

    def test_api_creates_lead_with_attribution(self):
        r = self._create_lead(email="api-attribution@test.de")
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertTrue(data["created"])
        self.assertEqual(data["status"], "lead")

        with self.app.app_context():
            from app.models import Lead

            lead = Lead.query.filter_by(email="api-attribution@test.de").first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.company, "Beispiel GmbH")
            self.assertEqual(lead.source, "google")
            self.assertEqual(lead.medium, "organic")
            self.assertIsNone(lead.next_followup_at)

    def test_api_upsert_by_email_is_idempotent(self):
        first = self._create_lead(email="api-upsert@test.de").get_json()
        second = self._create_lead(email="api-upsert@test.de", company="Neue Firma GmbH").get_json()
        self.assertFalse(second["created"])
        self.assertEqual(first["id"], second["id"])
        with self.app.app_context():
            from app.models import Lead

            lead = Lead.query.filter_by(email="api-upsert@test.de").first()
            self.assertEqual(lead.company, "Neue Firma GmbH")
            self.assertEqual(Lead.query.filter_by(email="api-upsert@test.de").count(), 1)

    def test_api_patch_updates_status_and_adds_note(self):
        lead_id = self._create_lead(email="api-patch@test.de").get_json()["id"]
        r = self.client.patch(
            f"/api/crm/leads/{lead_id}",
            json={"status": "qualified", "note": "Erstgespräch vereinbart"},
            headers=self._api_headers(),
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "qualified")

        with self.app.app_context():
            from app.models import Lead

            lead = self.db.session.get(Lead, lead_id)
            bodies = [n.body for n in lead.notes]
            self.assertTrue(any("Lead → Qualified" in b for b in bodies), bodies)
            self.assertTrue(any("Erstgespräch vereinbart" in b for b in bodies), bodies)

    def test_api_patch_lost_sets_reason(self):
        lead_id = self._create_lead(email="api-lost@test.de").get_json()["id"]
        self.client.patch(
            f"/api/crm/leads/{lead_id}",
            json={"status": "lost", "lost_reason": "Preis"},
            headers=self._api_headers(),
        )
        with self.app.app_context():
            from app.models import Lead

            lead = self.db.session.get(Lead, lead_id)
            self.assertEqual(lead.status, "lost")
            self.assertEqual(lead.lost_reason, "Preis")
            self.assertIsNotNone(lead.lost_at)

    def test_api_due_followup_filter(self):
        self._create_lead(email="due@beispiel.de", next_followup_at="2020-01-01T09:00:00Z")
        self._create_lead(email="future@beispiel.de", next_followup_at="2099-01-01T09:00:00Z")
        self._create_lead(email="nowon@beispiel.de", status="won")

        r = self.client.get("/api/crm/leads?due_followup=1", headers=self._api_headers())
        data = r.get_json()
        emails = {l["email"] for l in data["leads"]}
        self.assertEqual(emails, {"due@beispiel.de"})

        r_all = self.client.get("/api/crm/leads", headers=self._api_headers())
        self.assertEqual(r_all.get_json()["count"], 3)

    def test_api_validates_required_fields(self):
        r = self.client.post(
            "/api/crm/leads",
            json={"name": "", "email": "kaputt"},
            headers=self._api_headers(),
        )
        self.assertEqual(r.status_code, 400)

    # ══════════════════════════════════════════════════════════════════
    # Kontaktformular → Lead
    # ══════════════════════════════════════════════════════════════════

    def _contact(self, **overrides):
        data = {
            "name": "Bernd Kontakt",
            "company": "Kontakt GmbH",
            "email": overrides.pop("email", "bernd@kontakt.de"),
            "service": "Prozessautomatisierung",
            "message": "Wir wollen Prozesse automatisieren.",
            "privacy": "accepted",
            "website": "",
            **overrides,
        }
        return self.client.post(
            "/contact?utm_source=linkedin&utm_medium=social&utm_campaign=launch",
            data=data,
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )

    def test_contact_creates_lead_with_utm(self):
        r = self._contact(email="bernd-utm@kontakt.de")
        self.assertEqual(r.status_code, 200)
        with self.app.app_context():
            from app.models import Lead

            lead = Lead.query.filter_by(email="bernd-utm@kontakt.de").first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.status, "lead")
            self.assertEqual(lead.source, "linkedin")
            self.assertEqual(lead.medium, "social")
            self.assertEqual(lead.campaign, "launch")
            self.assertEqual(lead.company, "Kontakt GmbH")

    def test_booking_success_qualifies_lead(self):
        with mock.patch("app.blueprints.public._forward_to_n8n") as mocked:
            mocked.return_value = {"success": True, "status": "confirmed", "message": "ok"}
            r = self._contact(email="bernd-ok@kontakt.de", book_slot="1", preferred_day="2026-09-10", preferred_time="10:00")
            self.assertEqual(r.status_code, 200)
            body = r.get_json()
            self.assertTrue(body["success"])
            self.assertEqual(body["booking"], {"day": "2026-09-10", "time": "10:00", "status": "confirmed"})

        with self.app.app_context():
            from app.models import Lead

            lead = Lead.query.filter_by(email="bernd-ok@kontakt.de").first()
            self.assertEqual(lead.status, "qualified")
            bodies = [n.body for n in lead.notes]
            self.assertTrue(any("Lead → Qualified" in b for b in bodies), bodies)
            self.assertTrue(any("Terminwunsch bestätigt" in b for b in bodies), bodies)

    def test_booking_slot_taken_keeps_lead_and_message(self):
        n8n_message = "Der gewünschte Termin ist leider bereits belegt. Bitte wählen Sie eine andere Zeit."
        with mock.patch("app.blueprints.public._forward_to_n8n") as mocked:
            mocked.return_value = {"success": False, "status": "slot_taken", "message": n8n_message}
            r = self._contact(email="bernd-belegt@kontakt.de", book_slot="1", preferred_day="2026-09-10", preferred_time="10:00")
            self.assertEqual(r.status_code, 200)  # KEIN 409 (D7: 409 nur bei Validierung)
            body = r.get_json()
            self.assertFalse(body["success"])
            self.assertEqual(body["message"], n8n_message)  # n8n-Message 1:1
            self.assertNotIn("booking", body)

        with self.app.app_context():
            from app.models import AnalyticsEvent, Lead

            lead = Lead.query.filter_by(email="bernd-belegt@kontakt.de").first()
            self.assertIsNotNone(lead)  # Lead IMMER gespeichert (kein Verlust)
            self.assertEqual(lead.status, "lead")  # kein Statuswechsel bei „belegt“
            # KEIN booking_error-Event bei „belegt“ (normaler Nutzerpfad, D6)
            self.assertEqual(AnalyticsEvent.query.filter_by(event="booking_error").count(), 0)

    def test_booking_down_keeps_lead_queued(self):
        with mock.patch("app.blueprints.public._forward_to_n8n") as mocked:
            mocked.return_value = {"success": False, "status": "unreachable", "message": "Termindienst nicht erreichbar."}
            r = self._contact(email="bernd-down@kontakt.de", book_slot="1", preferred_day="2026-09-10", preferred_time="10:00")
            self.assertEqual(r.status_code, 200)  # KEIN 409, kein HTTP-Fehler für den Nutzer (D3)
            body = r.get_json()
            self.assertTrue(body["success"])
            self.assertEqual(body["booking"], {"day": "2026-09-10", "time": "10:00", "status": "queued"})

        with self.app.app_context():
            from app.models import AnalyticsEvent, Lead

            lead = Lead.query.filter_by(email="bernd-down@kontakt.de").first()
            self.assertIsNotNone(lead)  # Lead IMMER gespeichert
            self.assertEqual(lead.status, "lead")  # Statuswechsel NUR bei success
            err = AnalyticsEvent.query.filter_by(event="booking_error").first()
            self.assertIsNotNone(err)
            self.assertEqual(json.loads(err.props), {"reason": "unreachable"})

    # ══════════════════════════════════════════════════════════════════
    # Booking-Reservierung (atomar, Google-frei)
    # ══════════════════════════════════════════════════════════════════

    def _reserve(self, start="2026-10-01T09:00:00Z", email="buchung@test.de", **extra):
        payload = {
            "start_at_utc": start,
            "end_at_utc": "2026-10-01T09:30:00Z",
            "name": "Bernd Buchung",
            "email": email,
            "company": "Buchung GmbH",
            "topic": "Erstgespräch",
            **extra,
        }
        return self.client.post(
            "/api/crm/bookings/reserve", json=payload, headers=self._api_headers()
        )

    def test_booking_reserve_creates_confirmed(self):
        r = self._reserve()
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertTrue(data["booked"])
        self.assertTrue(data["booking_id"])
        with self.app.app_context():
            from app.models import Booking
            self.assertEqual(Booking.query.count(), 1)
            b = Booking.query.first()
            self.assertEqual(b.status, "confirmed")
            self.assertEqual(b.timezone, "Europe/Berlin")

    def test_booking_duplicate_slot_rejected(self):
        first = self._reserve()
        self.assertEqual(first.status_code, 201)
        second = self._reserve(email="zweiter@test.de")
        self.assertEqual(second.status_code, 409)
        body = second.get_json()
        self.assertFalse(body["booked"])
        self.assertIn("bereits belegt", body["message"])
        with self.app.app_context():
            from app.models import Booking
            self.assertEqual(Booking.query.count(), 1)  # nur eine Buchung

    def test_booking_parallel_duplicate_only_one_wins(self):
        """Parallele Doppelbuchung: genau EINE Buchung darf gewinnen."""
        from concurrent.futures import ThreadPoolExecutor
        with self.app.app_context():
            from app.models import Booking

            def reserve(i):
                return self._reserve(email=f"para{i}@test.de").status_code

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(reserve, range(2)))
            self.assertEqual(sorted(results), [201, 409])
            self.assertEqual(Booking.query.count(), 1)

    def test_booking_requires_fields(self):
        r = self._reserve(start="", email="")
        self.assertEqual(r.status_code, 400)

    def test_booking_list_and_delete(self):
        bid = self._reserve().get_json()["booking_id"]
        r = self.client.get("/api/crm/bookings", headers=self._api_headers())
        self.assertEqual(r.get_json()["count"], 1)
        r = self.client.delete(f"/api/crm/bookings/{bid}", headers=self._api_headers())
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/crm/bookings", headers=self._api_headers())
        self.assertEqual(r.get_json()["count"], 0)

    # ══════════════════════════════════════════════════════════════════
    # Admin-UI
    # ══════════════════════════════════════════════════════════════════

    def test_admin_crm_requires_login(self):
        r = self.client.get("/admin/crm")
        self.assertEqual(r.status_code, 302)

    def test_admin_crm_board_renders_leads(self):
        self._login()
        self._create_lead(email="admin-board@test.de")
        r = self.client.get("/admin/crm")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("CRM · Vertriebs-Pipeline", html)
        self.assertIn("Anna Beispiel", html)
        self.assertIn("Beispiel GmbH", html)

    def test_admin_crm_form_renders_stage_select(self):
        """GET /admin/crm/new muss das Status-Dropdown (stages) rendern."""
        self._login()
        r = self.client.get("/admin/crm/new")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        for stage in ("Lead", "Qualified", "Discovery", "Proposal", "Won", "Lost"):
            self.assertIn(f'value="{stage.lower()}"', html)
            self.assertIn(stage, html)

    def test_admin_manual_lead_creation(self):
        self._login()
        r = self.client.post(
            "/admin/crm/new",
            data={
                "name": "Manuell Angelegt",
                "email": "manuell@firma.de",
                "company": "Firma AG",
                "service": "KI-Agenten & RAG",
                "value_estimate": "8000",
                "status": "discovery",
                "note": "Empfehlung von Kollege",
            },
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)
        with self.app.app_context():
            from app.models import Lead

            lead = Lead.query.filter_by(email="manuell@firma.de").first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.status, "discovery")
            self.assertEqual(lead.value_estimate, 8000)
            self.assertTrue(any("Empfehlung von Kollege" in n.body for n in lead.notes))

    def test_admin_status_change_and_note(self):
        self._login()
        lead_id = self._create_lead(email="admin-status@test.de").get_json()["id"]

        r = self.client.post(
            f"/admin/crm/{lead_id}/status",
            data={"status": "proposal", "lost_reason": ""},
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.post(
            f"/admin/crm/{lead_id}/note",
            data={"body": "Angebot über 12k € raus"},
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)

        with self.app.app_context():
            from app.models import Lead

            lead = self.db.session.get(Lead, lead_id)
            self.assertEqual(lead.status, "proposal")
            bodies = [n.body for n in lead.notes]
            self.assertTrue(any("Lead → Proposal" in b for b in bodies), bodies)
            self.assertTrue(any("Angebot über 12k € raus" in b for b in bodies), bodies)
            self.assertIsNotNone(lead.last_contact_at)

    def test_admin_sidebar_shows_due_followup_badge(self):
        self._login()
        self._create_lead(email="admin-badge@test.de", next_followup_at="2020-01-01T09:00:00Z")
        r = self.client.get("/admin/settings")
        html = r.get_data(as_text=True)
        self.assertIn("admin-sidebar__badge", html)

    def test_admin_detail_edit_followup_date(self):
        self._login()
        lead_id = self._create_lead(email="admin-edit@test.de").get_json()["id"]
        r = self.client.post(
            f"/admin/crm/{lead_id}/edit",
            data={
                "name": "Anna Beispiel",
                "email": "anna@beispiel.de",
                "company": "Beispiel GmbH",
                "phone": "+49 170 1234567",
                "service": "Prozessautomatisierung",
                "value_estimate": "15000",
                "status": "discovery",
                "next_followup_at": "2026-09-15T10:30",
                "last_contact_at": "",
                "message": "Text",
                "note": "",
            },
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)
        with self.app.app_context():
            from app.models import Lead

            lead = self.db.session.get(Lead, lead_id)
            self.assertEqual(lead.status, "discovery")
            self.assertEqual(lead.value_estimate, 15000)
            self.assertEqual(lead.phone, "+49 170 1234567")
            self.assertIsNotNone(lead.next_followup_at)


if __name__ == "__main__":
    unittest.main()
