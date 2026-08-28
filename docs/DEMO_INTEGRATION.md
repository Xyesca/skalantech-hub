# Demo-Integration — InvoiceFlow · OfferAI · MailAgent

Stand: 2026-08-28. Dieses Dokument beschreibt sowohl die internen n8n-Demos als auch die neue öffentliche, abgesicherte Demo-Oberfläche auf `skalantech.store`.

## 1. Interne n8n-Demos

| Produkt | Workflow-ID | interner Webhook | Feld | Funktion |
| --- | ---: | --- | --- | --- |
| InvoiceFlow | `400` | `/webhook/demo-invoice` | `invoice` | Rechnungstext → strukturierte Rechnungsdaten |
| OfferAI | `401` | `/webhook/demo-offer` | `inquiry` | Kundenanfrage → Angebotsentwurf |
| MailAgent | `402` | `/webhook/demo-mail` | `mail` | E-Mail → Klassifikation + Antwortvorschlag |
| Lead-Erfassung | `8Xol9ORELU3HN29V` | `/webhook/lead-erfassung` | Formularfelder | Lead validieren und weiterverarbeiten |

Die n8n-Instanz bleibt **intern** auf Loopback/Tailscale. Es gibt keinen öffentlichen Link auf die n8n-UI und keinen direkten Browserzugriff auf n8n-Webhooks.

## 2. Neue öffentliche Demo-Seite

Route:

`GET https://skalantech.store/demos`

Die Seite zeigt alle drei Workflows mit Beispieltexten. Besucher können eine Eingabe absenden, ohne die interne n8n-Adresse zu kennen.

Datenfluss:

```text
Browser
  → POST /api/demos/<slug>
  → Flask: CSRF + Slug-Allowlist + Längenlimit + Rate-Limit
  → interner n8n Webhook auf 127.0.0.1:5678
  → Ergebnis zurück an Flask
  → JSON-Ergebnis im Browser
```

Implementierung:

- `app/blueprints/automation_showcase.py`
- `app/templates/demos.html`
- `app/static/js/showcase.js`
- `app/static/css/showcase.css`
- `tests/test_showcase.py`

## 3. Schutzgrenzen

Öffentlich erlaubt sind ausschließlich:

- `invoiceflow`
- `offerai`
- `mailagent`

Der Browser darf keinen beliebigen Webhook-Namen oder eine interne URL mitgeben. Das Mapping wird serverseitig fest vorgegeben.

Zusätzliche Grenzen:

- maximal 2.000 Zeichen pro Eingabe
- mindestens 20 Zeichen für sinnvolle Demo-Eingaben
- maximal 8 Demo-Aufrufe pro IP und Stunde über Flask-Limiter
- CSRF bleibt aktiv
- keine n8n-Credentials oder Tokens im Frontend
- n8n bleibt auf Loopback/Tailscale
- Upstream-Fehler werden als generische Fehlermeldung zurückgegeben
- Nutzerhinweis: keine vertraulichen oder produktiven personenbezogenen Daten in die Demo eingeben

Der aktuelle Flask-Limiter nutzt noch `memory://`. Gemessen 2026-08-28 (4 Gunicorn-Worker): 429 erscheint konsistent nach ~9–13 Requests pro IP, weil jeder Worker einen eigenen Zähler führt (Streuung durch Worker-Verteilung). Effektiv sind es damit bis zu ~8 Requests pro Stunde je Worker statt strikt 8/IP gesamt. GitHub Issue #4 migriert dies auf einen zentralen Store, bevor mehrere App-Instanzen horizontal skaliert werden.

## 4. Automations-Angebotsseite

Route:

`GET /automationen`

Sie übersetzt technische Fähigkeiten in geschäftsnahe Use Cases, u. a.:

- Anfrage → Angebot
- Rechnung → Daten
- E-Mail → CRM
- Lead → Follow-up
- Dokument → Wissen
- Formular → Prozess
- Termin → Bestätigung
- KPI → Tagesbriefing
- Mitarbeiter → Onboarding
- System → Alarm

Die Referenz `automaticprocess.de` dient nur als Benchmark für Klarheit, Ergebnisorientierung und einfache Conversion-Pfade. Texte, Design und Claims werden nicht kopiert.

## 5. Branchen-Landingpages und Lead-Demo

Die bestehenden Branchen-Seiten behalten zusätzlich das Demo-Anfrageformular `#demo`:

```text
Branchen-Landingpage
  → POST /demo
  → Lead zuerst in Flask-DB speichern
  → First-Party-Analytics
  → n8n Lead-Erfassung best-effort
  → interne Benachrichtigung über IONOS SMTP best-effort
```

Diese Route ist ein **Lead-/Demo-Terminpfad**. Die neue Route `/demos` ist dagegen ein **direkt ausführbarer Demonstrator**.

## 6. Mail

Die Website verwendet keine Gmail-SMTP-Logik mehr. Interne Website-Benachrichtigungen werden über das IONOS-Postfach gesendet:

- Absender: `xyesca@skalantech.store`
- SMTP: `smtp.ionos.de:465` SSL/TLS
- Reply-To: E-Mail des anfragenden Kunden

Secrets liegen ausschließlich in der lokalen `.env` bzw. später in n8n Credentials.

Die Google-freie n8n-Terminmigration ist separat in `docs/HERMES_IONOS_N8N_MIGRATION.md` beschrieben.

## 7. Konfiguration

```env
N8N_DEMO_BASE_URL=http://127.0.0.1:5678/webhook
N8N_LEAD_WEBHOOK_URL=http://127.0.0.1:5678/webhook/lead-erfassung
BUSINESS_EMAIL=xyesca@skalantech.store
IONOS_SMTP_HOST=smtp.ionos.de
IONOS_SMTP_PORT=465
IONOS_MAIL_USER=xyesca@skalantech.store
IONOS_MAIL_PASSWORD=<secret>
```

`IONOS_MAIL_PASSWORD` niemals committen.

## 8. Abnahme

Automatisiert:

```bash
python -m compileall app tests
python -m unittest discover -v
```

Produktions-E2E nach Deployment durch Hermes:

1. `/demos` extern erreichbar.
2. InvoiceFlow-Beispiel liefert ein Ergebnis.
3. OfferAI-Beispiel liefert ein Ergebnis.
4. MailAgent-Beispiel liefert ein Ergebnis.
5. Ungültiger Slug liefert 404.
6. Zu kurze Eingabe liefert 400.
7. n8n-Ausfall leakt keine internen Details.
8. n8n ist weiterhin nicht direkt öffentlich erreichbar.
9. Kontakt-/Demo-Benachrichtigung kommt über `xyesca@skalantech.store`.
10. Testdaten anschließend löschen.

### E2E-Verifikation Produktion (2026-08-28, NEXUS — Issue #7)

Alle Punkte live gegen `https://skalantech.store` bzw. direkt gegen den Container verifiziert:

| # | Check | Ergebnis |
| --- | --- | --- |
| 1 | `GET /demos` öffentlich | 200, 3 Demo-Karten gerendert, CSRF-Token in allen Formularen |
| 2 | `POST /api/demos/invoiceflow` (Beispieltext) | 200, strukturierte Rechnungsdaten (`lieferant`, `rechnungsnummer`, `brutto`, …) in ~1.7 s |
| 3 | `POST /api/demos/offerai` (Beispieltext) | 200, Angebotsentwurf (`angebotsnummer`, `leistungen`, …) in ~3.0 s |
| 4 | `POST /api/demos/mailagent` (Beispieltext) | 200, Klassifikation + `antwort_vorschlag` in ~2.2 s |
| 5 | `POST /api/demos/nope` | 404 `{"message":"Unbekannte Demo.","success":false}` |
| 6 | `POST /api/demos/invoiceflow` mit „zu kurz“ | 400 (Minimum 20 Zeichen) |
| 7 | Eingabe > 2000 Zeichen | Server kürzt auf 2000, 200 (Unit-Test `test_demo_proxy_truncates_input_to_2000_chars`) |
| 8 | n8n-Ausfall (simuliert) | 503 generisch, kein `127.0.0.1`/`5678`/`webhook`/Stacktrace im Response (Unit-Test `test_demo_proxy_upstream_failure_is_generic_no_internal_leak`) |
| 9 | n8n öffentlich erreichbar? | Nein: `217.160.53.90:5678` und `skalantech.store:5678` refused/timeout; n8n lauscht nur `127.0.0.1:5678`; n8n-UI nur über Tailscale-Caddy `:9443` |
| 10 | Response-Leaks | Weder `/demos`-HTML noch Demo-JSON enthalten interne URLs, Webhook-Pfade oder Credential-IDs |
| 11 | Rate-Limit | 429 bestätigt (siehe §3, memory://-Multi-Worker-Messung) |
| 12 | Testdaten | `leads`, `contact_messages`, `bookings`, `lead_notes` nach E2E: 0 Zeilen (keine Testdatensätze) |
| 13 | Unit-Suite | 128/128 Tests grün (`python -m unittest discover`) |

Umgebung: Container `skalantech` (gunicorn 4 Worker, `N8N_DEMO_BASE_URL=http://127.0.0.1:5678/webhook` bestätigt in Container-Env), Caddy public → `127.0.0.1:5000`.

## 9. Rollback

Die öffentlichen Demos sind ein zusätzlicher Flask-Blueprint. Bei Problemen kann Hermes den Blueprint deaktivieren oder den vorherigen Containerstand deployen, ohne die bestehenden internen n8n-Workflows zu verändern.
