"""Skalantech Hub — Database Models."""
from datetime import datetime, timezone
from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_login = db.Column(db.DateTime)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)


class Settings(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default="Skalantech")
    tagline = db.Column(db.String(240), default="")
    location = db.Column(db.String(120), default="")
    about = db.Column(db.Text, default="")
    hero_path = db.Column(db.String(255), default="")
    hero_type = db.Column(db.String(16), default="none")  # image | video | none
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    @classmethod
    def get(cls):
        """Return the singleton settings row (auto-creates if missing)."""
        s = cls.query.first()
        if not s:
            s = cls()
            db.session.add(s)
            db.session.commit()
        return s


class Link(db.Model):
    __tablename__ = "links"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    platform = db.Column(db.String(32), default="link")
    position = db.Column(db.Integer, default=0, index=True)
    visible = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    url = db.Column(db.String(512), default="")
    image_path = db.Column(db.String(255), default="")
    position = db.Column(db.Integer, default=0, index=True)
    visible = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # First-Party Conversion-Attribution (kein Tracker, keine Cookies):
    # UTM-Parameter + Referrer der Anfrage — für SEO-/Kanal-Auswertung.
    source = db.Column(db.String(120), default="")
    medium = db.Column(db.String(60), default="")
    campaign = db.Column(db.String(160), default="")
    referrer = db.Column(db.String(512), default="")
    # Analytics-Session (First-Party, cookie-less) — erlaubt Funnel-Stitching
    # zwischen anonymen Seiten-Events (analytics_events) und dem Lead.
    session_id = db.Column(db.String(64), default="", index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow)


# ══════════════════════════════════════════════════════════════════════════
# CRM — Vertriebs-Pipeline (Lead → Qualified → Discovery → Proposal → Won/Lost)
# ══════════════════════════════════════════════════════════════════════════

PIPELINE_STAGES = {
    "lead": "Lead",
    "qualified": "Qualified",
    "discovery": "Discovery",
    "proposal": "Proposal",
    "won": "Won",
    "lost": "Lost",
}

# Endstufen — Leads dort landen nicht mehr in Follow-up-/Pipeline-Abfragen
PIPELINE_TERMINAL = frozenset({"won", "lost"})

PIPELINE_FLOW = ["lead", "qualified", "discovery", "proposal", "won", "lost"]

LOST_REASONS = (
    "Preis",
    "Kein Budget",
    "Zeitpunkt",
    "Anderer Anbieter",
    "Interne Entscheidung",
    "Kein Bedarf",
    "Keine Rückmeldung",
    "Sonstiges",
)


class Lead(db.Model):
    """Ein Vertriebs-Lead in der Skalantech-Pipeline."""

    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(254), nullable=False, index=True)
    company = db.Column(db.String(160), default="")
    phone = db.Column(db.String(60), default="")
    service = db.Column(db.String(120), default="")
    message = db.Column(db.Text, default="")

    # Pipeline
    status = db.Column(db.String(24), default="lead", nullable=False, index=True)
    value_estimate = db.Column(db.Integer, default=0)  # € geschätzter Projektwert
    lost_reason = db.Column(db.String(120), default="")
    won_at = db.Column(db.DateTime)
    lost_at = db.Column(db.DateTime)

    # Follow-up
    next_followup_at = db.Column(db.DateTime, index=True)
    last_contact_at = db.Column(db.DateTime)

    # First-Party-Attribution (wie ContactMessage)
    source = db.Column(db.String(120), default="")
    medium = db.Column(db.String(60), default="")
    campaign = db.Column(db.String(160), default="")
    referrer = db.Column(db.String(512), default="")
    # Analytics-Session (First-Party, cookie-less) — siehe ContactMessage.
    session_id = db.Column(db.String(64), default="", index=True)

    is_archived = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    notes = db.relationship(
        "LeadNote",
        backref="lead",
        lazy="selectin",
        order_by="LeadNote.created_at.asc(), LeadNote.id.asc()",
        cascade="all, delete-orphan",
    )

    @property
    def status_label(self) -> str:
        return PIPELINE_STAGES.get(self.status, self.status)

    @property
    def is_terminal(self) -> bool:
        return self.status in PIPELINE_TERMINAL

    @property
    def followup_overdue(self) -> bool:
        return (
            self.next_followup_at is not None
            and self.next_followup_at < _utcnow()
            and not self.is_terminal
            and not self.is_archived
        )

    def add_note(self, body: str, author: str = "System") -> "LeadNote | None":
        """Hänge eine Notiz an den Lead an (audit trail)."""
        if not body or not body.strip():
            return None
        note = LeadNote(lead_id=self.id, body=body.strip()[:5000], author=author[:80])
        db.session.add(note)
        return note

    def set_status(self, new_status: str, reason: str = "", author: str = "System") -> None:
        """Wechsle die Pipeline-Stufe inkl. Status-Notiz."""
        if new_status not in PIPELINE_STAGES:
            raise ValueError(f"Unbekannte Pipeline-Stufe: {new_status}")
        old = self.status
        if old == new_status:
            return
        self.status = new_status
        now = _utcnow()
        if new_status == "won":
            self.won_at = now
            self.lost_at = None
            self.lost_reason = ""
        elif new_status == "lost":
            self.lost_at = now
            self.won_at = None
            self.lost_reason = reason.strip()[:120]
        else:
            self.lost_reason = ""
        note_body = f"Status: {PIPELINE_STAGES.get(old, old)} → {PIPELINE_STAGES.get(new_status, new_status)}"
        if reason.strip():
            note_body += f" — {reason.strip()}"
        self.add_note(note_body, author=author)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "phone": self.phone,
            "service": self.service,
            "message": self.message,
            "status": self.status,
            "status_label": self.status_label,
            "value_estimate": self.value_estimate,
            "lost_reason": self.lost_reason,
            "next_followup_at": self.next_followup_at.isoformat() if self.next_followup_at else None,
            "last_contact_at": self.last_contact_at.isoformat() if self.last_contact_at else None,
            "source": self.source,
            "medium": self.medium,
            "campaign": self.campaign,
            "referrer": self.referrer,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LeadNote(db.Model):
    """Aktivitäts-/Notiz-Eintrag an einem Lead."""

    __tablename__ = "lead_notes"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), default="System")
    created_at = db.Column(db.DateTime, default=_utcnow, index=True)


# ══════════════════════════════════════════════════════════════════════════
# Analytics — First-Party Conversion-Tracking (cookie-less, kein externer Dienst)
# ══════════════════════════════════════════════════════════════════════════


class AnalyticsEvent(db.Model):
    """Ein anonymes Conversion-/Interaktions-Event der Website.

    First-Party: wird ausschließlich in der eigenen SQLite-DB gespeichert.
    Cookie-less: keine Tracking-Cookies; Session-ID liegt nur in sessionStorage
    (Tab-Session) und wird nicht über Dritte übertragen. Es werden keine
    personenbezogenen Inhalte gespeichert (kein Name, keine E-Mail, keine IP).

    Events (Allowlist siehe app/blueprints/analytics.py):
      page_view, demo_started, demo_completed, contact_clicked,
      calendar_opened, meeting_booked, service_viewed, case_study_viewed,
      roi_calculated, lead_created
    """

    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(64), nullable=False, index=True)
    page = db.Column(db.String(255), default="", index=True)
    session_id = db.Column(db.String(64), default="", index=True)
    # Attribution (First-Party, optional, nur bei vorhandenen UTM-Parametern)
    source = db.Column(db.String(120), default="")
    medium = db.Column(db.String(60), default="")
    campaign = db.Column(db.String(160), default="")
    referrer = db.Column(db.String(512), default="")
    # Zusatzdaten als JSON-String (z. B. {"label": "hero", "service": "..."}),
    # auf 2000 Zeichen begrenzt.
    props = db.Column(db.Text, default="")
    # Technische Metadaten (vom Server erfasst, nicht vom Client gesendet) —
    # dient später der Bot-Filterung in Dashboards.
    user_agent = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=_utcnow, index=True)
