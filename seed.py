"""Skalantech Hub — Seed initial data (updated for new structure)."""
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Settings, Link, Project

app = create_app(os.environ.get("FLASK_ENV", "production"))

with app.app_context():
    s = Settings.get()
    s.name = "Skalantech"
    s.tagline = "Stabile IT · Weniger Handarbeit · Mehr Wirkung"
    s.location = "Köln, Germany"
    s.about = (
        "Ich bin Xavier — IT-Infrastructure & Automation Engineer mit mehr als "
        "sieben Jahren Praxiserfahrung.\n\n"
        "Skalantech verbindet klassische Infrastruktur mit moderner "
        "Prozessautomatisierung und produktiven KI-Agenten.\n\n"
        "Open-Source-first, selbst gehostet und für einen verlässlichen Betrieb "
        "gebaut."
    )

    links = [
        # Interne Tailscale-Apps (DeepDive, n8n, Dashboard, Workspace) sind
        # bewusst NICHT öffentlich -> visible=False. Nur GitHub ist öffentlich.
        ("DeepDive", "https://deepdive.skalantech.store", "app", 0, False),
        ("n8n", "https://n8n.skalantech.store", "app", 1, False),
        ("Dashboard", "https://dashboard.skalantech.store", "app", 2, False),
        ("Workspace", "https://workspace.skalantech.store", "app", 3, False),
        ("GitHub", "https://github.com/Xyesca", "github", 10, True),
    ]
    for label, url, platform, pos, vis in links:
        existing = Link.query.filter_by(url=url).first()
        if existing:
            existing.visible = vis
        else:
            db.session.add(Link(label=label, url=url, platform=platform, position=pos, visible=vis))

    projects = [
        ("DeepDive", "YouTube zu KI-Analyse in Sekunden. Transkribieren, zusammenfassen, exportieren.", "https://github.com/Xyesca/deepdive", 0),
        ("DebtPilot AI", "Self-hosted KI-Plattform mit lokalen Modellen, RAG-Dokumentenanalyse und modularer Architektur.", "", 1),
        ("AI Job Agent", "Sucht Stellenangebote, analysiert Anforderungen und erstellt automatisch personalisierte Bewerbungen mit KI.", "", 2),
    ]
    for title, desc, url, pos in projects:
        if not Project.query.filter_by(title=title).first():
            db.session.add(Project(title=title, description=desc, url=url, position=pos, visible=True))

    db.session.commit()
    print("✓ Seed data inserted successfully")
