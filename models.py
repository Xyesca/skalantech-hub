"""Skalantech — Datenbank-Modelle"""
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


class Settings(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default="Skalantech")
    tagline = db.Column(db.String(240), default="")
    location = db.Column(db.String(120), default="")
    about = db.Column(db.Text, default="")
    hero_path = db.Column(db.String(255), default="")
    hero_type = db.Column(db.String(16), default="none")  # image | video | none

    @classmethod
    def get(cls):
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
    platform = db.Column(db.String(32), default="link")  # github, tiktok, instagram, website, app, link
    position = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    url = db.Column(db.String(512), default="")
    image_path = db.Column(db.String(255), default="")
    position = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
