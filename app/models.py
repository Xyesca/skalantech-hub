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
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow)
