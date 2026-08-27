# Skalantech Hub

Conversion-orientierte Website und Content-Backend für Skalantech: IT-Infrastruktur, Cloud Engineering, Prozessautomatisierung und produktive KI-Agenten.

## Highlights

- Klar positionierte Leistungs- und Angebotsarchitektur
- Responsive, barrierearme Oberfläche ohne externe Frontend-Abhängigkeiten
- Dynamische Projektverwaltung über ein geschütztes Admin-Dashboard
- Qualifiziertes Kontaktformular mit CSRF-Schutz, Validierung, Honeypot und Rate-Limit
- **CRM-Vertriebs-Pipeline** (Lead → Qualified → Discovery → Proposal → Won/Lost) mit
  Admin-Board, Follow-up-Tracking und maschinenlesbarer API (n8n/Hermes)
- **Follow-up-Automation**: täglicher Poller (Hermes-Cron) alarmiert per Telegram bei
  fälligen Follow-ups — Details in [docs/CRM_PIPELINE.md](docs/CRM_PIPELINE.md)
- Technisches SEO mit strukturierten Daten, Sitemap, Canonical- und Social-Metadaten
- Self-hosted Flask-/SQLite-Stack mit Docker-Deployment
- Sicherheitsheader, datensparsame Auslieferung und optimiertes Asset-Caching

## Stack

| Bereich | Technologie |
| --- | --- |
| Backend | Python 3.11+, Flask, SQLAlchemy |
| Frontend | Jinja2, semantisches HTML, Vanilla CSS und JavaScript |
| Datenbank | SQLite |
| Auth & Formulare | Werkzeug, Flask-WTF, Flask-Limiter |
| Betrieb | Gunicorn, Docker Compose |

Es werden keine externen Webfonts, Tracking-Skripte oder UI-CDNs geladen.

## Schnellstart mit Docker

```bash
git clone https://github.com/Xyesca/skalantech-hub.git
cd skalantech-hub
cp .env.example .env
docker compose up --build -d
```

Die Website läuft anschließend standardmäßig auf Port `5000`.

## Konfiguration

| Variable | Zweck |
| --- | --- |
| `ADMIN_USERNAME` | Benutzername für das Admin-Dashboard |
| `ADMIN_PASSWORD` | Starkes Admin-Passwort |
| `SECRET_KEY` | Persistenter, zufälliger Flask-Session-Key |
| `SESSION_COOKIE_SECURE` | In Produktion mit HTTPS auf `true` setzen |
| `DATABASE_URL` | Optional: abweichende SQLAlchemy-Datenbank-URL |
| `GMAIL_USER` | Optional: SMTP-Absender für Kontaktbenachrichtigungen |
| `GMAIL_APP_PASSWORD` | Optional: App-Passwort für SMTP |

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
FLASK_ENV=development python run.py
```

## Tests

```bash
python -m unittest discover -v
```

Die Tests decken öffentliche Routen, Conversion-Inhalte, Kontaktvalidierung, Bot-Honeypot, Datenspeicherung und Security-Header ab.

## Architektur

```text
app/
├── blueprints/      # Public-, Auth- und Admin-Routen
├── static/          # Eigenes CSS, JavaScript und Medien
├── templates/       # Öffentliche, rechtliche und Admin-Templates
├── utils/           # Security- und Upload-Helfer
├── config.py
├── models.py
└── __init__.py
```

## Lizenz

MIT – siehe [LICENSE](LICENSE).
