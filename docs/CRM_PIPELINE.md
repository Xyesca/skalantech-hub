# CRM · Vertriebs-Pipeline (P1)

Status: **live** — Lead → Qualified → Discovery → Proposal → Won/Lost

## Zweck

Jeder Lead hat einen sauberen Pipeline-Status, einen nachvollziehbaren
Verlauf (Notizen/Audit-Trail) und ein geplantes Follow-up. Kein Lead
verschwindet still; Won/Lost wird mit Grund dokumentiert.

## Pipeline-Stufen

| Stufe      | Bedeutung                                     | Terminal |
|------------|-----------------------------------------------|----------|
| `lead`     | Neue Anfrage / importierter Lead              | –        |
| `qualified`| Bedarf bestätigt, Budget/Entscheider plausibel | –        |
| `discovery`| Erstgespräch geführt, Anforderungen erfasst   | –        |
| `proposal` | Angebot raus (value-basiert)                  | –        |
| `won`      | Kunde gewonnen (won_at gesetzt)               | ✅       |
| `lost`     | Verloren — lost_reason + lost_at gesetzt      | ✅       |

Terminale Stufen (won/lost) erscheinen nicht mehr in Follow-up- und
Pipeline-Abfragen.

## Wie Leads in die Pipeline kommen

1. **Kontaktformular** (`POST /contact`) → Lead wird mit UTM-/Session-
   Attribution angelegt (First-Party, cookie-less).
2. **Terminbuchung** über das Formular → bei erfolgreichem n8n-Webhook
   wird der Lead automatisch auf `qualified` gesetzt (Notiz: Terminwunsch
   bestätigt).
3. **CRM-API** (`POST /api/crm/leads`) → für n8n-/Hermes-Automation,
   idempotent per E-Mail (Upsert).
4. **Manuell** im Admin (`/admin/crm/new`).

## Admin-UI

- `/admin/crm` — Pipeline-Board: Funnel-Zähler je Stufe, fällige Follow-ups
  (sortiert), offener Pipeline-Wert (qualified/discovery/proposal),
  Won/Lost-Zähler, Filter-Tabs.
- `/admin/crm/<id>` — Detail: Notizen, Statuswechsel, Follow-up planen.
- `/admin/crm/<id>/status` — Statuswechsel inkl. Audit-Notiz
  (`Status: Lead → Qualified — Grund`).
- `/admin/crm/<id>/followup` — nächsten Follow-up-Termin setzen
  (`next_followup_at`).
- Sidebar-Badge zeigt Anzahl fälliger Follow-ups in allen Admin-Seiten.

## API (n8n/Hermes)

Auth: `X-API-Key: <CRM_API_KEY>` (Header, hmac-Vergleich). CSRF-frei
(maschineller Zugriff). Base: `/api/crm`.

| Methode | Pfad                       | Zweck                                    |
|---------|----------------------------|------------------------------------------|
| GET     | `/health`                  | Status                                   |
| POST    | `/leads`                   | Lead anlegen / per E-Mail aktualisieren  |
| GET     | `/leads`                   | Liste (`?status=…`, `?due_followup=1`)   |
| GET     | `/leads/<id>`              | Detail inkl. Notizen                      |
| PATCH   | `/leads/<id>`              | Felder/Status/Follow-up/Notiz aktualisieren |

PATCH-Beispiel — Lead auf `qualified` heben:

```json
{ "status": "qualified", "note": "Erstgespräch vereinbart" }
```

`GET /api/crm/leads?due_followup=1` liefert nur Leads mit fälligem
`next_followup_at`, nicht terminal, nicht archiviert — die Automation
pollen diesen Endpunkt täglich.

## Follow-up-Automation

Der Hub stellt Terminverwaltung (`next_followup_at`) + Fälligkeits-Filter
bereit. Der tägliche Poller ist **live** als Hermes-Cron:

**Job:** `CRM Follow-up täglich` (Hermes-Cron `e43e2738d866`, täglich 08:00 UTC
= 10:00 Berlin, no_agent, Script `scripts/crm_followup.py` im Repo, Symlink
nach `~/.hermes/scripts/crm_followup.py`).

**Ablauf:**
1. `GET /api/crm/leads?due_followup=1` mit `X-API-Key` (aus `<app-dir>/.env`).
2. Bei fälligen Leads: **Telegram-Alarm** an den internen Vertriebskanal
   (`TELEGRAM_HOME_CHANNEL` aus `~/.hermes/.env`, Fallback AiGents-Kanal
   `-1003956152501`) mit Name, Firma, Service, Stufe, Wert und Überfälligkeit.
   Kein Kunden-Versand — nur interne Erinnerung (Follow-up-Versand an Kunden
   bleibt Freigabe-Sache).
3. Report-JSON je Lauf unter `instance/followup/YYYYMMDD.json`; `stdout`
   meldet `OK: N fällige Follow-up(s), Telegram-Sends: X, Auto-Lost: Y`.

**Auto-Lost (optional, standardmäßig AUS):** Umgebung `CRM_AUTO_LOST_AFTER_DAYS`
auf z. B. `5` setzen → Leads, deren Follow-up seit ≥ 5 Tagen überfällig ist,
werden automatisch auf `lost` / `Keine Rückmeldung` gesetzt (mit Audit-Notiz).
Bewusst nicht aktiviert, bis Xavier das freigibt.

**Manueller Lauf / Dry-Run:**
```bash
cd <app-dir>
python3 scripts/crm_followup.py --dry-run   # nichts senden/ändern
python3 scripts/crm_followup.py             # echter Lauf
```

**Alternativ n8n:** Der generische Versand-Baustein `Baustein: Follow-up`
(Webhook, Gmail-OAuth, Dry-Run-Modus) liegt in der n8n-Automationsbibliothek
(NEXUS) und kann denselben `due_followup`-Endpunkt füttern, sobald der
E-Mail-Versand freigegeben ist.

## Won/Lost

- `won` → `won_at` gesetzt, Wert bleibt für Auswertung.
- `lost` → `lost_reason` Pflichtfeld (Preis, Kein Budget, Zeitpunkt,
  Anderer Anbieter, Interne Entscheidung, Kein Bedarf, Keine Rückmeldung,
  Sonstiges), `lost_at` gesetzt.
- Beides schreibt eine Audit-Notiz; terminale Leads fallen aus
  Follow-up- und offenen Pipeline-Abfragen.

## Betrieb

- Konfig: `CRM_API_KEY` in `.env` (docker-compose reicht durch).
- Migration: `_migrate_db()` in `app/__init__.py` ergänzt fehlende
  Spalten automatisch beim Boot (SQLite).
- Tests: `tests/test_crm.py` (API, Kontaktformular, Booking→Qualified,
  Admin-UI, Follow-ups), `tests/test_analytics.py` (Conversion-Events).
  Hermetisch: eigene Temp-DB, keine Live-n8n-Abhängigkeit.
