"""Skalantech Hub — Seed initial data"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from app import app, db
from models import Settings, Link, Project

with app.app_context():
    # Settings
    s = Settings.get()
    s.name = "Skalantech"
    s.tagline = "Digitale Infrastruktur · Cloud Engineering · KI-Automation"
    s.location = "Köln, Germany"
    s.about = (
        "Ich bin Xavier — IT-Engineer mit Leidenschaft für Infrastruktur, "
        "Cloud und KI-Automation.\n\n"
        "Skalantech ist meine digitale Plattform: Hier findet ihr meine Projekte, "
        "Tools und Dienste — von DeepDive (YouTube zu KI-Analyse) bis zu "
        "massgeschneiderten Automationsloesungen.\n\n"
        "Alles selbst gehostet, Open-Source-first, designed fuer Performanz."
    )

    # Links (Subdomains + Social)
    links = [
        ("DeepDive", "https://deepdive.skalantech.store", "app", 0),
        ("n8n", "https://n8n.skalantech.store", "app", 1),
        ("Dashboard", "https://dashboard.skalantech.store", "app", 2),
        ("Workspace", "https://workspace.skalantech.store", "app", 3),
        ("GitHub", "https://github.com/Xyesca", "github", 10),
    ]
    for label, url, platform, pos in links:
        if not Link.query.filter_by(url=url).first():
            db.session.add(Link(label=label, url=url, platform=platform, position=pos, visible=True))

    # Projects
    projects = [
        ("DeepDive", "YouTube zu KI-Analyse in Sekunden. Transkribieren, zusammenfassen, exportieren.", "https://deepdive.skalantech.store", 0),
        ("Skalantech Hub", "Diese Seite — persoenliche Visitenkarte mit Admin-Dashboard, selbst gehostet.", "https://skalantech.store", 1),
        ("Hermes Agent", "KI-Agenten-Framework — konfigurierbar, erweiterbar, multi-provider.", "https://github.com/NousResearch/hermes-agent", 2),
    ]
    for title, desc, url, pos in projects:
        if not Project.query.filter_by(title=title).first():
            db.session.add(Project(title=title, description=desc, url=url, position=pos, visible=True))

    db.session.commit()
    print("Seed data inserted successfully")
