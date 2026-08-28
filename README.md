# Skalantech Hub

Conversion-orientierte Website, CRM- und Automationsplattform für Skalantech: Prozessautomatisierung, Business Apps, Websites, IT-Infrastruktur und produktive KI-Systeme für KMU.

## Highlights

- Outcome-orientierte Startseite mit konkreten Automationsfällen statt Tool-Buzzwords
- Öffentliche Angebotsseite `/automationen` mit 12 geschäftsnahen Use Cases
- Geschützte Live-Demos unter `/demos` für **InvoiceFlow**, **OfferAI** und **MailAgent**
- Demo-Architektur: Browser → Flask-Validierung/Rate-Limit → internes n8n → Browser; n8n bleibt nicht öffentlich exponiert
- Responsive, barrierearme Oberfläche ohne externe Frontend-Abhängigkeiten
- Dynamische Projektverwaltung über ein geschütztes Admin-Dashboard
- Qualifiziertes Kontaktformular mit CSRF-Schutz, Validierung, Honeypot und Rate-Limit
- **CRM-Vertriebs-Pipeline** (Lead → Qualified → Discovery → Proposal → Won/Lost) mit Admin-Board, Follow-up-Tracking und API für n8n/Hermes
- **Follow-up-Automation**: Hermes kann fällige Follow-ups über die CRM-API erkennen und melden
- Technisches SEO mit strukturierten Daten, Sitemap, Canonical- und Social-Metadaten
- Self-hosted Flask-/SQLite-Stack mit Docker-Deployment
- Sicherheitsheader, datensparsame Auslieferung und optimiertes Asset-Caching
- Geschäftliche Kontaktadresse und SMTP über **`xyesca@skalantech.store` / IONOS** statt Gmail

## Öffentliche Kernrouten

| Route | Zweck |
| --- | --- |
| `/` | Conversion-Startseite |
| `/automationen` | Automations-Use-Cases und Angebotspositionierung |
| `/demos` | Interaktive Live-Demos über gesicherten Flask→n8n-Proxy |
| `/websites-apps` | Websites & Business Apps |
| `/it-infrastruktur` | IT-Infrastruktur |
| `/ki-integration` | KI-Integration |
| `/n8n-automatisierung` | n8n-Automatisierung |
| `/branchen/*` | Branchen-Landingpages |
| `/wissen/*` | Wissensbereich / SEO-Content |

## Stack

| Bereich | Technologie |
| --- | --- |
| Backend | Python 3.12, Flask, SQLAlchemy |
| Frontend | Jinja2, semantisches HTML, Vanilla CSS und JavaScript |
| Datenbank | SQLite, PostgreSQL-Migration geplant |
| Automation | n8n über interne Loopback-/Tailscale-Verbindung |
| Mail | IONOS SMTP/IMAP |
| Auth & Formulare | Werkzeug, Flask-WTF, Flask-Limiter |
| Betrieb | Gunicorn, Docker Compose, Caddy |

Es werden keine externen Webfonts, Tracking-Skripte oder UI-CDNs geladen.

## Schnellstart mit Docker

```bash
git clone https://github.com/Xyesca/skalantech-hub.git
cd skalantech-hub
cp .env.example .env
docker compose up --build -d
```

Die Website läuft im produktiven Compose-Setup ausschließlich auf `127.0.0.1:5000`; Caddy übernimmt den öffentlichen HTTPS-Zugriff.

## Konfiguration

| Variable | Zweck |
| --- | --- |
| `ADMIN_USERNAME` | Benutzername für das Admin-Dashboard |
| `ADMIN_PASSWORD` | Starkes Admin-Passwort |
| `SECRET_KEY` | Persistenter, zufälliger Flask-Session-Key |
| `SESSION_COOKIE_SECURE` | In Produktion `true` |
| `DATABASE_URL` | SQLAlchemy-Datenbank-URL |
| `CRM_API_KEY` | API-Key für n8n/Hermes |
| `N8N_WEBHOOK_URL` | Interner Webhook für Terminbuchung |
| `N8N_LEAD_WEBHOOK_URL` | Interner Webhook für Lead-Erfassung |
| `N8N_DEMO_BASE_URL` | Interne Basis-URL für Demo-Webhooks, Standard `http://127.0.0.1:5678/webhook` |
| `BUSINESS_EMAIL` | Öffentliche Geschäftsadresse, `xyesca@skalantech.store` |
| `IONOS_SMTP_HOST` | SMTP-Host, `smtp.ionos.de` |
| `IONOS_SMTP_PORT` | SMTP-Port, `465` |
| `IONOS_MAIL_USER` | IONOS-Postfachbenutzer |
| `IONOS_MAIL_PASSWORD` | Nur im VPS-/n8n-Secret-Store setzen, niemals committen |
| `IONOS_IMAP_HOST` | Optional für eingehende Mail-Automationen |
| `IONOS_IMAP_PORT` | IMAP-Port, `993` |
| `RATELIMIT_STORAGE_URI` | Rate-Limit-Storage; Production-Default `redis://127.0.0.1:6379/0` (Container `skalantech-redis`, nur loopback). Für Tests/Dev `memory://` |

## Zentrales Rate-Limiting (Issue #4)

Alle öffentlichen Limits (Login, Kontakt-/Demo-Formulare, `/api/demos`,
`/analytics/event`) laufen über flask-limiter mit **zentralem Redis-Storage**
(`redis://127.0.0.1:6379/0`, Container `skalantech-redis`). gunicorn startet
mit `-w 4` — ohne zentralen Storage wäre jedes Limit pro Worker separat
(`memory://` = effektiv Limit × 4). Mit Redis gilt jedes Limit exakt über
alle Worker hinweg; der Zähler überlebt Worker-Restarts. Der Redis-Container
lauscht ausschließlich auf `127.0.0.1` (Host-Netzwerk, kein öffentlicher
Port, keine Tailscale-Exposition) und nutzt AOF-Persistenz.

| Route | Limit | Storage |
| --- | --- | --- |
| `POST /login` | 5/min | Redis (zentral) + DB-Lockout |
| `POST /contact` (inkl. Terminbuchung) | 3/h | Redis (zentral) |
| `POST /demo` | 3/h | Redis (zentral) |
| `POST /api/demos/<slug>` | 8/h | Redis (zentral) |
| `POST /analytics/event` | 120/min | Redis (zentral) |

Strategie: `moving-window` (gleitendes Fenster, keine Window-Boundary-Effekte).
Bei Limit-Überschreitung liefern API-/AJAX-Routen ein 429-JSON, Browser-Formulare
bekommen einen Flash + Redirect auf die Herkunftsseite.

## Demo-Sicherheitsmodell

Die öffentliche Website darf **nie** direkt auf die n8n-UI oder interne Webhooks verlinken. `/api/demos/<slug>` erlaubt ausschließlich die drei bekannten Demo-Slugs, begrenzt Eingaben auf 2.000 Zeichen und ist serverseitig rate-limited. Secrets, Credential-IDs und interne n8n-Antwortdetails gehören nicht in den Browser.

Die Live-Demos sind Demonstratoren. Besucher sollen dort keine vertraulichen oder produktiven personenbezogenen Daten eingeben.

## Google-freie Mail-/Terminmigration

Zielzustand für die Website-Kommunikation:

`Website → n8n → persistente Buchung → ICS → IONOS SMTP → CRM/Telegram`

Gmail und Google Calendar werden aus dem aktiven Terminworkflow entfernt, sobald Hermes die IONOS-Credentials auf dem VPS gesetzt, die neue persistente Slot-Logik umgesetzt und E2E getestet hat. Technische Vorgabe und Abnahme stehen in:

- `docs/HERMES_IONOS_N8N_MIGRATION.md`
- GitHub Issue `#2`

Alte Google-Workflow-Exports bleiben bis zur erfolgreichen Produktionsabnahme nur als Rollback-/Legacy-Artefakte erhalten und dürfen nicht als Sollzustand interpretiert werden.

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
FLASK_ENV=development python run.py
```

## Tests & CI

```bash
python -m compileall app tests
python -m unittest discover -v
```

GitHub Actions führt Compile- und Regressionstests auf Pull Requests gegen `master` aus (mit Redis-Service-Container, damit die Multi-Worker-Sharing-Tests laufen). Die Tests decken u. a. öffentliche Routen, Homepage-CRO, Live-Demo-Proxy, IONOS-Mail-Konfiguration, Kontaktvalidierung, CSRF, Datenspeicherung, SEO, Security-Header und zentrales Rate-Limiting ab. Die restliche Suite ist hermetisch (`RATELIMIT_STORAGE_URI=memory://` pro Testklasse); nur `tests/test_ratelimit_storage.py` braucht Redis (Test-DB 15) und wird ohne erreichbares Redis übersprungen.

## Architektur

```text
app/
├── blueprints/
│   ├── public.py                # Website, Landingpages, Lead/Booking-Bridge
│   ├── automation_showcase.py  # Automationen + gesicherter Live-Demo-Proxy
│   ├── crm_api.py               # API für n8n/Hermes
│   └── analytics.py             # First-Party-Analytics
├── static/
├── templates/
├── utils/
├── config.py
├── models.py
└── __init__.py
```

## Betriebs- und Hermes-Dokumentation

- `docs/HERMES_EXECUTION_BOARD.md` – priorisierte Bot-Team-Aufgaben und Status
- `docs/HERMES_IONOS_N8N_MIGRATION.md` – Google-freie Mail-/Booking-Migration
- `docs/AUTOMATICPROCESS_BENCHMARK_AND_ROADMAP.md` – Referenzanalyse und Positionierungs-Roadmap
- `docs/DEMO_INTEGRATION.md` – Demo-Architektur und Lead-Flows
- `docs/CRM_PIPELINE.md` – CRM-Status und Follow-up-Logik

## Lizenz

MIT – siehe [LICENSE](LICENSE).
