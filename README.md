# Skalantech Hub

> Persönliche Visitenkarte + Admin-Dashboard für digitale Projekte, Tools und Dienste.

![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Öffentliche Visitenkarte** — Projekte, Links, Kontakt
- **Admin-Dashboard** — Inhalte verwalten (CRUD für Projekte, Links)
- **Docker-ready** — Ein Befehl zum Starten
- **SQLite** — Keine externe Datenbank nötig

## 🚀 Quick Start

```bash
# Klonen
git clone https://github.com/Xyesca/skalantech-hub.git
cd skalantech-hub

# Konfiguration
cp .env.example .env
# → ADMIN_USERNAME, ADMIN_PASSWORD eintragen

# Mit Docker starten
docker compose up -d
```

## 🏗️ Architektur

```
┌──────────────┐
│   Caddy      │  TLS-Terminierung + Reverse Proxy
│  (extern)    │
└──────┬───────┘
       │
┌──────▼───────┐
│   Flask App  │  :5000  — Visitenkarte + Admin
│   skalantech │
└──────┬───────┘
       │
┌──────▼───────┐
│   SQLite     │  instance/skalantech.db
└──────────────┘
```

## 🛠️ Tech Stack

| Komponente | Technologie |
|------------|-------------|
| **Backend** | Python 3, Flask, SQLAlchemy |
| **Frontend** | Jinja2 Templates, Vanilla CSS |
| **Auth** | Werkzeug (Passwort-Hash + Session) |
| **DB** | SQLite |
| **Container** | Docker Compose |

## ⚙️ Konfiguration

| Variable | Beschreibung |
|----------|-------------|
| `ADMIN_USERNAME` | Admin-Login (erforderlich) |
| `ADMIN_PASSWORD` | Admin-Passwort (erforderlich) |
| `SECRET_KEY` | Flask-Session-Key (optional, auto-generiert) |
| `PORT` | Port (Default: 5000) |

## 📄 License

MIT — siehe [LICENSE](LICENSE).

---

<div align="center">
  Entwickelt von <a href="https://github.com/Xyesca">Xavier Escalante Castellar</a> •
  <a href="https://linkedin.com/in/xyesca/">LinkedIn</a>
</div>
