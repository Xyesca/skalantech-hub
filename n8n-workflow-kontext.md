# n8n-Workflow-Kontext — Skalantech Terminbuchung (deterministisch, ohne LLM)

> Stand: 29.08.2026 — Issue #15 umgesetzt: **KEIN LLM im Terminpfad** (DeepSeek/Ollama entfernt).

## 1. ÜBERSICHT

- **Workflow:** `Skalantech Terminanfrage (KI) v2` — ID `50fo5b3SqQjmEVrX`
- **Webhook:** `POST http://127.0.0.1:5678/webhook/skalantech-termin` (nur Loopback; Website/Flask ruft intern auf)
- **Published-Graph:** `e72a7a12-f6d3-4c41-a7bb-0fb1cc255c71` (19 Nodes, seit 29.08.2026)
- **Booking-Source-of-Truth:** Website-DB `/root/skalantech-hub/instance/app.db`, Tabelle `bookings` (UNIQUE `start_at_utc`), Endpoint `POST /api/crm/bookings/reserve` (201/409)
- **Mail:** IONOS SMTP (Credential `1sxzxuHJkBmhTkzw`), Absender/Reply-To `xyesca@skalantech.store`
- **Kanonicher Export:** `docs/n8n/workflow-terminbuchung-v2-issue15-privacy.json` (bereinigt, ohne Secrets)

## 2. AKTUELLER FLOW (19 Nodes, Version e72a7a12 — Issue #15)

```
Webhook (POST /skalantech-termin)
  → Validieren & Slot (Code: parst Input, DST-Validierung Europe/Berlin, 30-Min-Slots)
    → Gültig? (IF: $json.valid === true)
      ├─ TRUE → Slot gewünscht? (IF: $json.hasSlot === true)
      │          ├─ TRUE → Slot reservieren (HTTP POST http://127.0.0.1:5000/api/crm/bookings/reserve)
      │          │          → Kontext wiederherstellen (Code: mergt Request + booked/booking_id)
      │          │            → Slot frei? (IF: $json.booked === true)
      │          │              ├─ TRUE → Event-Kontext zusammenführen (Code: + booking_id)
      │          │              │        → [PARALLEL, nicht-blockierend]:
      │          │              │           ├─ Antwort: Erfolg (respondToWebhook success:true)
      │          │              │           ├─ Bestätigungstext bauen (Code, DETERMINISTISCH — kein LLM)
      │          │              │           │    → ICS erzeugen → Bestätigung an Kunde (IONOS SMTP, best-effort)
      │          │              │           ├─ Benachrichtigung Xavier (IONOS SMTP, best-effort)
      │          │              │           └─ Telegram: Buchung bestätigt (best-effort)
      │          │              └─ FALSE → Antwort: Belegt + Info Xavier (belegt, IONOS SMTP)
      │          └─ FALSE → Antwort: Ohne Termin + Info Xavier (ohne Termin, IONOS SMTP)
      └─ FALSE → Antwort: Ungültig (HTTP 400)
```

**WICHTIG — D4 (Erfolg von Mail/Telegram entkoppelt, verifiziert 2026-08-28/29):** `Antwort: Erfolg` (respondToWebhook `success:true`) ist ein **direkter Parallel-Zweig** von `Event-Kontext zusammenführen` — sobald die Slot-Reservierung committed ist, kommt `success:true`, unabhängig davon ob SMTP/Telegram fehlschlagen. Alle nicht-kritischen Nodes (Mail, Telegram) haben `onError: continueRegularOutput` + bounded retry (`retryOnFail: true, maxTries: 2`). Ein toter SMTP-/Telegram-Dienst degradiert zur Fehler-Item-Ausgabe, blockiert aber nie die Buchung.

**Response-Vertrag (unverändert):** `{success, message, booked, date, time}` — `success:false` NUR bei „belegt“/„ungültig“ (bzw. fehlender Name/E-Mail). Bei Mail-Fehler weiterhin `success:true`.

**Slot-Reservierung (Google-frei, concurrency-sicher, unverändert):** `Slot reservieren` ruft intern `POST http://127.0.0.1:5000/api/crm/bookings/reserve` auf (Flask, network_mode host). Der Endpoint nutzt den UNIQUE-Constraint auf `bookings.start_at_utc`: atomarer INSERT, kein SELECT-then-INSERT. Belegt → IntegrityError → HTTP 409 `{success:false, booked:false, message: "Der gewünschte Termin ist leider bereits belegt. …"}` → Workflow antwortet `success:false` mit exakt dieser Message (D2, 1:1 im Formular).

## 3. INFRASTRUKTUR (kritisch für Änderungen)

| Komponente | Details |
|---|---|
| **n8n** | Docker-Container `apps-n8n-1`, `network_mode: host`, Port `127.0.0.1:5678` |
| **n8n-UI** | `https://ubuntu.piranha-gray.ts.net:9443` (Caddy-TLS, Tailscale) |
| **n8n-Login** | `xyesca1989@googlemail.com` |
| **Booking-Source-of-Truth** | Website-DB `/root/skalantech-hub/instance/app.db`, Tabelle `bookings` (UNIQUE `start_at_utc`), Endpoint `/api/crm/bookings/reserve` |
| **Mail (IONOS SMTP)** | Credential `1sxzxuHJkBmhTkzw` „IONOS Skalantech Mail“ (smtp.ionos.de:465 SSL, User `xyesca@skalantech.store`) ✅ — 4 Sende-Nodes: Bestätigung Kunde, Benachrichtigung Xavier, Info ohne Termin, Info belegt |
| **CRM-API (Reserve)** | Credential `f5bCobxCf8Tnremf` „Skalantech CRM API“ (httpHeaderAuth) ✅ |
| **LLM im Terminpfad** | **ENTFERNT (Issue #15, 29.08.2026)** — kein DeepSeek, kein Ollama, kein anderes LLM. Bestätigungsmail deterministisch aus Template. |
| **DeepSeek-Credential (ALT, ungenutzt im Booking)** | `7IagYDgNYUewRxw1` „DeepSeek API Header“ — wird vom Booking-Workflow NICHT mehr referenziert (andere Workflows/Demos können es weiter nutzen). |
| **Telegram** | Credential `u9Q39TmSaAZEhFTX` (Bot HermesGambito), Chat `-1003956152501` |
| **Google-Credentials (ALT, UNGENUTZT)** | `GDSnPRh9olMLb8hC` „Skalantech Kalender (Terminbuchung)“ + `a06hhqHnYwuiVbBU` „Gmail account“ — vom aktiven Workflow NICHT mehr verwendet (Google komplett entfernt). Können nach CEO-Freigabe gelöscht werden. |

## 4. BEKANNTE PROBLEME / OFFENE PUNKTE (nach Priorität)

### ✅ P0 ERLEDIGT: DeepSeek aus Booking-PII-Pfad entfernt (Issue #15, 2026-08-29)
- Alle LLM-Nodes entfernt: `KI-Prompt bauen`, `DeepSeek Antwort` (api.deepseek.com), `KI-Fallback prüfen`, `DeepSeek OK?`, `Ollama Backup`, `Ollama Ergebnis übernehmen`, `KI-Mail extrahieren`.
- Ersatz: `Bestätigungstext bauen` (Code, deterministisch — persönlicher Absatz aus Template-Bausteinen Name/Firma/Thema/Nachricht). Kein Netzwerk, kein Modell, kein Prompt-Injection-Risiko, keine PII-Sendung an Dritte.
- SENTINEL-Nachprüfung (PRIVACY_DATAFLOW_REMEDIATION.md, 29.08. 10:47 UTC): bestätigt, Live-Graph `e72a7a12` ohne LLM-Nodes.

### ✅ P0 ERLEDIGT: Google-Abhängigkeit komplett entfernt (2026-08-28)
Früherer Blocker „Kalender-Credential needs to be reconnected“ ist **obsolet**: Der Workflow nutzt kein Google Calendar mehr (Website-DB statt Kalender, ICS statt Google-Meet). Gmail ist durch IONOS SMTP ersetzt. Ein Reconnect der alten Google-Credentials ist für die Terminbuchung **nicht mehr nötig** — nur noch falls andere Workflows sie nutzen (der Workflow „Google Kalender Assistent“ hat ein eigenes Credential `HtlDWDVotsN04Zg8`).

### ⚠️ redactionPolicy nicht nutzbar (n8n 2.32.7 Community)
Per Public-API gesetzt (`redactionPolicy: non-manual`), aber von dieser n8n-Version NICHT persistiert (nicht in `workflow_entity.settings`). Execution-Retention läuft über Defaults: Pruning EIN, `EXECUTIONS_DATA_MAX_AGE=336h` (14 Tage). Keine Env-Overrides in Compose/Container.

### ℹ️ Code-Node hat KEIN `fetch`/`$helpers`
In dieser n8n-Version ist `$helpers.httpRequest()` im Code-Node NICHT definiert. Falls doch wieder HTTP-Calls nötig sind: über HTTP-Request-Node (Best Practice). Keine Code-Node-HTTP-Aufrufe einbauen.

### ℹ️ Reserve-Endpoint statt Google-Calendar-availability
Slot-Prüfung + Sperre passiert atomar im Website-Endpoint `/api/crm/bookings/reserve` (UNIQUE-Constraint, IntegrityError → 409). Kein 0-Items-Problem, keine Race Conditions (parallel getestet: nur 1 Buchung gewinnt).

## 5. VALIDIERUNGSDETAILS („Validieren & Slot“)

- Akzeptiert: `name`, `email`, `company`, `topic`, `message`, `preferred_day` (YYYY-MM-DD), `preferred_time` (HH:MM)
- Fehlerfall: kein Name/ungültige E-Mail → `{valid:false, error:...}` → Antwort: Ungültig (400)
- Kein preferred_day/time → `{valid:true, hasSlot:false}` → „Ohne Termin“-Pfad
- Slot vorhanden → `{valid:true, hasSlot:true, startIso, endIso, displayDate, displayTime}`
- **Terminlänge 30 Min**, Zeitzone Europe/Berlin (DST-Round-trip-Validierung), nur Mo–Fr, max 90 Tage voraus, erlaubte Zeiten 09:00–16:30 (30-min-Raster)

## 6. BESTÄTIGUNGSMAIL (deterministisch, „Bestätigungstext bauen“)

- Kein LLM, kein Prompt. Code-Node baut `aiEmail` + `aiPersonal` aus Template-Bausteinen.
- Persönlicher Absatz (deterministisch):
  - Nachricht + Thema → „Vielen Dank für Ihre Nachricht zum Thema {Thema}. Ich schaue mir Ihre Ausgangslage vor unserem Gespräch an.“
  - Nachricht + Firma → „…Ihre Nachricht zu {Firma}. …“
  - Nur Nachricht → „Vielen Dank für Ihre Nachricht. Ich schaue mir Ihre Ausgangslage vor unserem Gespräch an.“
  - Nur Thema → „Ich freue mich auf unser Gespräch zum Thema {Thema}.“
  - Nur Firma → „Ich freue mich auf unser Gespräch zu {Firma}.“
  - Sonst → „Ich freue mich auf unser Gespräch.“
- HTML-Escaping aller Kundendaten (Name/Firma/Thema/Nachricht) gegen HTML-Injection.
- Kein `console.*` im Node → keine PII in Logs.

## 7. DEPLOY-HINWEISE (wie man Änderungen aktiviert)

**Kritisch:** Nach einer Änderung muss der Workflow deaktiviert+aktiviert werden, damit der laufende Webhook-Prozess die neue Node-Definition lädt. Zwei Wege:

### Weg A — Public API (n8n ≥1.119, funktioniert mit API-Key, 2026-08-27/29 verifiziert)
```bash
# PUT veröffentlicht direkt (activeVersionId == versionId danach)
curl -X PUT "$BASE/api/v1/workflows/50fo5b3SqQjmEVrX" \
  -H "X-N8N-API-KEY: ***" -H "Content-Type: application/json" \
  -d '{"name":"...","nodes":[...],"connections":{...},"settings":{...}}'
```
**Pitfall:** `settings` ist im PUT-Schema PFLICHT, akzeptiert aber nur `executionOrder`/`timezone`/`callerPolicy`/`redactionPolicy` u.ä. — NICHT `binaryMode`/`timeSavedMode`/`availableInMCP` (sonst 400 „additional properties“). `nodes`+`connections` MÜSSEN vollständig sein. GET liefert den vollen aktuellen Zustand.

### Weg B — interner REST (Session-Cookie)
Wie bisher: `PATCH /rest/workflows/<id>` mit vollem Objekt → `POST /rest/workflows/<id>/deactivate` → `POST /rest/workflows/<id>/activate {"versionId":"..."}`.

- Workflow-ID: `50fo5b3SqQjmEVrX`
- **Container-Restart `docker restart apps-n8n-1` ist durch Guard blockiert** — nie versuchen.

## 8. WEBSITE-SEITIG (Flask)

- `app/blueprints/public.py` → `/contact`-Endpoint: POSTet JSON an `http://127.0.0.1:5678/webhook/skalantech-termin`
- `app/blueprints/crm_api.py` → `/api/crm/bookings/reserve` (atomare Slot-Reservierung, 201/409) + `/api/crm/bookings` (Liste) + `DELETE /api/crm/bookings/<booking_id>` (Cleanup)
- Lead wird VOR dem n8n-Call committet (Lead-Verlust bei n8n/SMTP-Ausfall ausgeschlossen, D3)
- skalantech-Container läuft mit `network_mode: host` (erreicht n8n über 127.0.0.1:5678 und sich selbst über 127.0.0.1:5000)

## 9. ZUGEHÖRIGE DATEIEN

| Datei | Inhalt |
|---|---|
| `docs/n8n/workflow-terminbuchung-v2-issue15-privacy.json` | **Kanonicher Export** (aktuell, ohne Secrets/webhookIds — Stand 29.08.2026, Issue #15) |
| `docs/n8n/workflow-terminbuchung-v2-IONOS.json` | Historisch (28.08.2026, noch mit DeepSeek/Ollama) |
| `docs/n8n-workflow-terminbuchung-v2.json` | Historisch (Spiegel des IONOS-Exports, mit DeepSeek) |
| `docs/n8n/workflow-terminbuchung-v2-pre-IONOS-backup.json` | Rollback-Punkt (Stand VOR IONOS-Migration, mit Google) |
| `docs/HERMES_IONOS_N8N_MIGRATION.md` | Migrations-Auftrag + E2E-Ergebnisse (9/9) |
| `docs/HERMES_N8N_TERMINBUCHUNG.md` | Übergabe-Doku (aktuell, Issue #15) |
| Website-Repo `/root/skalantech-hub` | Flask-App, Booking-Formular in `index.html` + `main.js` |

## 10. E2E-VERIFIKATION (Issue #15, 2026-08-29, Task t_22e3ac08)

- **Erfolgspfad (deterministisch):** Webhook-POST freier Slot → `{"success":true,"booked":true,"date":...,"time":...}` (HTTP 200). Execution 448: 14 Nodes — `Bestätigungstext bauen` (aiEmail deterministisch) → `ICS erzeugen` (Binary `text/calendar`, `skalantech-erstgespraech.ics`) → `Bestätigung an Kunde` → **IONOS akzeptiert** (`250 Requested mail action okay`, accepted: [Kunde]) + `Benachrichtigung Xavier` + Telegram. KEIN DeepSeek-/Ollama-Node in der Execution.
- **Belegt-Pfad:** gleicher Slot erneut → `{"success":false,"message":"Der gewünschte Termin ist leider bereits belegt. Bitte wählen Sie eine andere Zeit."}` (Doppelbuchungsschutz intakt).
- **Ungültig-Pfad:** ungültige E-Mail → `{"success":false,"message":"Name und eine gültige E-Mail-Adresse sind erforderlich."}` + HTTP 400.
- **SENTINEL-Parallel-E2E:** Executions 445/446/447 (SENTINEL Privacy-E2E, Slot 25.11.2026) — gleicher deterministischer Pfad, Kundenmail an `sentinel-e2e@example.invalid` von IONOS mit „invalid DNS MX“ abgelehnt (Fixture-Domain ohne MX — kein Workflow-Fehler; `onError` degradiert sauber).
- Test-Bookings danach entfernt (Bookings: 0, keine Test-Leads).

## 11. NÄCHSTE SCHRITTE (optional, nichts blockiert)

1. Alte Google-Credentials (`GDSnPRh9olMLb8hC`, `a06hhqHnYwuiVbBU`) nach CEO-Freigabe löschen — vom aktiven Workflow ungenutzt.
2. DeepSeek-Credential `7IagYDgNYUewRxw1` prüfen: wird nur noch von Demo-Workflows (400/401/402) genutzt — Demo-Standardpfad ist separates Ticket (PRIVACY_DATAFLOW_REMEDIATION.md, „Offene Punkte“).
3. Datenschutztext auf Website ERST nach finalem Demo-Umbau (VELA t_28c1c61a) aktualisieren.
4. Follow-up-Touchpoints (T-24h/T+1d/T+7d) laut Lead-Funnel-Spez (CLOSER-Texte, interne Telegram-Zustellung) verdrahten.
