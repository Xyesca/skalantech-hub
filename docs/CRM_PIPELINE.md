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
bereit; das *Versenden* übernimmt die Automation (n8n oder Hermes-Cron):

1. Täglich `GET /api/crm/leads?due_followup=1` mit `X-API-Key`.
2. Für jeden fälligen Lead: Erinnerung/Anschreiben generieren (VELA-Texte),
   versenden.
3. Danach `PATCH /api/crm/leads/<id>` mit neuem `next_followup_at`
   (z. B. +3 Werktage) oder `status: "lost"` + `lost_reason`
   (`"Keine Rückmeldung"`).

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
