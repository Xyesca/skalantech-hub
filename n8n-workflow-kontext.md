# n8n-Workflow: Skalantech Terminanfrage (KI) v2

**Übergabedokument** — Stand: 2026-08-28, aktive Version `f7079e0f-405a-4a55-9536-28be324ae872` (25 Nodes), **Google-frei** (IONOS-Mail-Migration, Issue #2)

---

## 1. ZWECK

Die Website **skalantech.store** (Flask-App, Docker-Container `skalantech`) hat ein Buchungsformular. Beim Absenden POSTet Flask an den n8n-Webhook:

```
POST http://127.0.0.1:5678/webhook/skalantech-termin
```

Der Workflow: Eingabe validieren → Slot atomar in der Website-DB reservieren → **nicht-blockierende Parallel-Kette** (HTTP-Antwort ans Formular + KI-Mail + ICS + Benachrichtigungen). Buchungserfolg hängt NICHT an Mail/Telegram/KI — siehe D4.

**Seit 2026-08-28 vollständig Google-frei:** Kein Google Calendar, kein Gmail mehr. Termin-Source-of-Truth ist die Website-DB (Model `Booking`, atomarer Reserve-Endpoint), Mails gehen über IONOS SMTP (Absender `xyesca@skalantech.store`), ICS-Einladung wird per Code-Node erzeugt.

---

## 2. AKTUELLER FLOW (25 Nodes, Version f7079e0f)

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
      │          │              │           ├─ KI-Prompt bauen → DeepSeek Antwort (primär)
      │          │              │           │    → KI-Fallback prüfen → DeepSeek OK?
      │          │              │           │       ├─ true  → KI-Mail extrahieren
      │          │              │           │       └─ false → Ollama Backup (127.0.0.1:11434)
      │          │              │           │                   → Ollama Ergebnis übernehmen → KI-Mail extrahieren
      │          │              │           │   → ICS erzeugen → Bestätigung an Kunde (IONOS SMTP, best-effort)
      │          │              │           ├─ Benachrichtigung Xavier (IONOS SMTP, best-effort)
      │          │              │           └─ Telegram: Buchung bestätigt (best-effort)
      │          │              └─ FALSE → Antwort: Belegt + Info Xavier (belegt, IONOS SMTP)
      │          └─ FALSE → Antwort: Ohne Termin + Info Xavier (ohne Termin, IONOS SMTP)
      └─ FALSE → Antwort: Ungültig (HTTP 400)
```

**WICHTIG — D4 (Erfolg von Mail/KI/Telegram entkoppelt, verifiziert 2026-08-28):** `Antwort: Erfolg` (respondToWebhook `success:true`) ist ein **direkter Parallel-Zweig** von `Event-Kontext zusammenführen` — sobald die Slot-Reservierung committed ist, kommt `success:true`, unabhängig davon ob SMTP/KI/Telegram fehlschlagen. Alle nicht-kritischen Nodes (Mail, KI-HTTP, Telegram) haben `onError: continueRegularOutput` + bounded retry (`retryOnFail: true, maxTries: 2`). Ein toter SMTP-/KI-/Telegram-Dienst degradiert zur Fehler-Item-Ausgabe, blockiert aber nie die Buchung.

**Response-Vertrag (unverändert):** `{success, message, booked, date, time}` — `success:false` NUR bei „belegt“/„ungültig“ (bzw. fehlender Name/E-Mail). Bei Mail-/KI-Fehler weiterhin `success:true`.

**Slot-Reservierung (Google-frei, concurrency-sicher):** `Slot reservieren` ruft intern `POST http://127.0.0.1:5000/api/crm/bookings/reserve` auf (Flask, network_mode host). Der Endpoint nutzt den UNIQUE-Constraint auf `bookings.start_at_utc`: atomarer INSERT, kein SELECT-then-INSERT. Belegt → IntegrityError → HTTP 409 `{success:false, booked:false, message: "Der gewünschte Termin ist leider bereits belegt. …"}` → Workflow antwortet `success:false` mit exakt dieser Message (D2, 1:1 im Formular).

---

## 3. INFRASTRUKTUR (kritisch für Änderungen)

| Komponente | Details |
|---|---|
| **n8n** | Docker-Container `apps-n8n-1`, `network_mode: host`, Port `127.0.0.1:5678` |
| **n8n-UI** | `https://ubuntu.piranha-gray.ts.net:9443` (Caddy-TLS, Tailscale) |
| **n8n-Login** | `xyesca1989@googlemail.com` |
| **Booking-Source-of-Truth** | Website-DB `/root/skalantech-hub/instance/app.db`, Tabelle `bookings` (UNIQUE `start_at_utc`), Endpoint `/api/crm/bookings/reserve` |
| **Mail (IONOS SMTP)** | Credential `1sxzxuHJkBmhTkzw` „IONOS Skalantech Mail“ (smtp.ionos.de:465 SSL, User `xyesca@skalantech.store`) ✅ — 4 Sende-Nodes: Bestätigung Kunde, Benachrichtigung Xavier, Info ohne Termin, Info belegt |
| **CRM-API (Reserve)** | Credential `f5bCobxCf8Tnremf` „Skalantech CRM API“ (httpHeaderAuth) ✅ |
| **DeepSeek (KI primär)** | HTTP-Request `https://api.deepseek.com/chat/completions`, Credential `7IagYDgNYUewRxw1` (httpHeaderAuth) ✅ |
| **Ollama (KI Backup)** | `http://127.0.0.1:11434/api/chat` via socat-Loopback → Container `debtpilot-ollama-1` (IP 172.22.0.2), Modell `lfm25` — erreichbar (0.32.5), Timeout = Node-Default (300 s), `num_ctx: 4096` im ollamaBody |
| **Telegram** | Credential `u9Q39TmSaAZEhFTX` (Bot HermesGambito), Chat `-1003956152501` |
| **Google-Credentials (ALT, UNGENUTZT)** | `GDSnPRh9olMLb8hC` „Skalantech Kalender (Terminbuchung)“ + `a06hhqHnYwuiVbBU` „Gmail account“ — **weiterhin abgelaufen, aber vom aktiven Workflow NICHT mehr verwendet** (Google komplett entfernt). Können nach CEO-Freigabe gelöscht werden. |

---

## 4. BEKANNTE PROBLEME / OFFENE PUNKTE (nach Priorität)

### ✅ P0 ERLEDIGT: Google-Abhängigkeit komplett entfernt (2026-08-28)
Früherer Blocker „Kalender-Credential needs to be reconnected“ ist **obsolet**: Der Workflow nutzt kein Google Calendar mehr (Website-DB statt Kalender, ICS statt Google-Meet). Gmail ist durch IONOS SMTP ersetzt. Ein Reconnect der alten Google-Credentials ist für die Terminbuchung **nicht mehr nötig** — nur noch falls andere Workflows sie nutzen (der Workflow „Google Kalender Assistent“ hat ein eigenes Credential `HtlDWDVotsN04Zg8`).

### ✅ Ollama-Pfad (Backup-KI) — getestet 2026-08-28
- **Erreichbar:** `127.0.0.1:11434/api/chat` → antwortet (Version `0.32.5`), Modell `lfm25:latest` (2.7B Q4_K_M) geladen.
- **Parameter (live im Workflow):** `think: false`, `keep_alive: 10m`, `temperature: 0.2`, `num_predict: 140`, `num_ctx: 4096` (lädt in ~8 s statt >3 min bei Default 65536). Node-Timeout: Node-Default (300 s) — ausreichend (Antwort in ~11 s).
- **Antwortformat:** `{message: {content, thinking}}` — bestätigt.
- **⚠️ lfm25-Quirk (bestätigt):** `message.content` ist **LEER** bei `num_predict: 140` (`done_reason: length`, Antwort steht in `message.thinking`, engl. CoT) — **trotz `think: false`**. Der Workflow liest NUR `content` und fällt auf den deutschen Standard-Satz zurück („Danke für die kurze Einordnung…“). `thinking` wird NIEMALS in Kunden-Mails eingebaut. KI bleibt Best-Effort, blockiert nie die Buchung. (Optionaler Fix: `num_predict` erhöhen, dann liefert lfm25 auch `content`.)

### ℹ️ Code-Node hat KEIN `fetch`/`$helpers`
In dieser n8n-Version ist `$helpers.httpRequest()` im Code-Node NICHT definiert. KI-Calls laufen über **HTTP-Request-Node** (Best Practice). Keine Code-Node-HTTP-Aufrufe einbauen.

### ℹ️ Reserve-Endpoint statt Google-Calendar-availability
Slot-Prüfung + Sperre passiert atomar im Website-Endpoint `/api/crm/bookings/reserve` (UNIQUE-Constraint, IntegrityError → 409). Kein 0-Items-Problem, keine Race Conditions (parallel getestet: nur 1 Buchung gewinnt).

---

## 5. VALIDIERUNGSDETAILS („Validieren & Slot“)

- Akzeptiert: `name`, `email`, `company`, `topic`, `message`, `preferred_day` (YYYY-MM-DD), `preferred_time` (HH:MM)
- Fehlerfall: kein Name/ungültige E-Mail → `{valid:false, error:...}` → Antwort: Ungültig (400)
- Kein preferred_day/time → `{valid:true, hasSlot:false}` → „Ohne Termin“-Pfad
- Slot vorhanden → `{valid:true, hasSlot:true, startIso, endIso, displayDate, displayTime}`
- **Terminlänge 30 Min**, Zeitzone Europe/Berlin (DST-Round-trip-Validierung), nur Mo–Fr, max 90 Tage voraus, erlaubte Zeiten 09:00–16:30 (30-min-Raster)

---

## 6. KI-STILVORGABE (System-Prompt in „KI-Prompt bauen“)

Erzwingt Xaviers No-Bullshit-Stil (Deutsch, direkt, keine KI-Floskeln, 1–2 Sätze, kein HTML). Enthält zusätzlich eine **Prompt-Injection-Schutz-Sektion** (Kundentexte = unvertraute Daten). Antwort wird HTML-escaped in „KI-Mail extrahieren“.

---

## 7. DEPLOY-HINWEISE (wie man Änderungen aktiviert)

**Kritisch:** Nach einer Änderung muss der Workflow deaktiviert+aktiviert werden, damit der laufende Webhook-Prozess die neue Node-Definition lädt. Zwei Wege:

### Weg A — Public API (n8n ≥1.119, funktioniert mit API-Key, 2026-08-27 verifiziert)
```bash
# PUT veröffentlicht direkt (activeVersionId == versionId danach)
curl -X PUT "$BASE/api/v1/workflows/50fo5b3SqQjmEVrX" \
  -H "X-N8N-API-KEY: ***" -H "Content-Type: application/json" \
  -d '{"name":"...","nodes":[...],"connections":{...},"settings":{"executionOrder":"v1","timezone":"Europe/Berlin","callerPolicy":"workflowsFromSameOwner"}}'
```
**Pitfall:** `settings` ist im PUT-Schema PFLICHT, akzeptiert aber nur `executionOrder`/`timezone`/`callerPolicy` — NICHT `binaryMode`/`timeSavedMode`/`availableInMCP` (sonst 400 „additional properties“). `nodes`+`connections` MÜSSEN vollständig sein (sonst landen Nodes ohne `operation`/`resource` im Draft → kaputter Workflow beim nächsten Publish). Die `activeVersion` (vollständige, korrekte Nodes) bekommst du per `GET /api/v1/workflows/{id}` unter `activeVersion`.

### Weg B — interner REST (Session-Cookie)
Wie bisher: `PATCH /rest/workflows/<id>` mit vollem Objekt → `POST /rest/workflows/<id>/deactivate` → `POST /rest/workflows/<id>/activate {"versionId":"..."}`.

- Workflow-ID: `50fo5b3SqQjmEVrX`
- **Container-Restart `docker restart apps-n8n-1` ist durch Guard blockiert** — nie versuchen.

---

## 8. WEBSITE-SEITIG (Flask)

- `app/blueprints/public.py` → `/contact`-Endpoint: POSTet JSON an `http://127.0.0.1:5678/webhook/skalantech-termin`
- `app/blueprints/crm_api.py` → `/api/crm/bookings/reserve` (atomare Slot-Reservierung, 201/409) + `/api/crm/bookings` (Liste)
- Lead wird VOR dem n8n-Call committet (Lead-Verlust bei n8n/SMTP-Ausfall ausgeschlossen, D3)
- skalantech-Container läuft mit `network_mode: host` (erreicht n8n über 127.0.0.1:5678 und sich selbst über 127.0.0.1:5000)

---

## 9. ZUGEHÖRIGE DATEIEN

| Datei | Inhalt |
|---|---|
| `docs/n8n/workflow-terminbuchung-v2-IONOS.json` | **Kanonicher Export** (aktuell, ohne Secrets) — entspricht Live-DB (verifiziert 2026-08-28) |
| `docs/n8n-workflow-terminbuchung-v2.json` | Spiegel des kanonischen Exports (für Kompatibilität) |
| `docs/n8n/workflow-terminbuchung-v2-pre-IONOS-backup.json` | Rollback-Punkt (Stand VOR IONOS-Migration, mit Google) |
| `docs/HERMES_IONOS_N8N_MIGRATION.md` | Migrations-Auftrag + E2E-Ergebnisse (9/9) |
| Website-Repo `/root/skalantech-hub` | Flask-App, Booking-Formular in `index.html` + `main.js` |

---

## 10. E2E-VERIFIKATION (2026-08-28, frisch, Task t_cff1caf7)

- **Erfolgspfad:** Webhook-Curl Mo 31.08. 10:00 → `{"success":true,"booked":true,"date":"31.08.2026","time":"10:00"}` (HTTP 200), Booking `20260831T100000` in Website-DB (confirmed), Execution 299: alle 17 Nodes success inkl. `Bestätigung an Kunde` + `Benachrichtigung Xavier` (IONOS SMTP) + Telegram. DeepSeek primär OK.
- **Belegt-Pfad:** gleicher Slot erneut → `{"success":false,"message":"Der gewünschte Termin ist leider bereits belegt. Bitte wählen Sie eine andere Zeit."}` (Executions 300/301, exakt D2).
- **Ungültig-Pfad:** ungültige E-Mail → `{"success":false,"message":"Name und eine gültige E-Mail-Adresse sind erforderlich."}` + HTTP 400.
- **Ollama-Backup:** `127.0.0.1:11434/api/chat` live getestet mit Workflow-Parametern (10.8 s, Format bestätigt, lfm25-Quirk wie dokumentiert).
- Test-Booking danach entfernt (Bookings: 0, keine Test-Leads).
- Migration-E2E (0f14362): 9/9 — freier Slot, Doppelbuchung, parallele Doppelbuchung, Wochenende, ungültige Uhrzeit, Vergangenheit, >90 Tage, DST, SMTP-down → Buchung bleibt gespeichert.

## 11. NÄCHSTE SCHRITTE (optional, nichts blockiert)

1. Alte Google-Credentials (`GDSnPRh9olMLb8hC`, `a06hhqHnYwuiVbBU`) nach CEO-Freigabe löschen — vom aktiven Workflow ungenutzt.
2. lfm25-Quirk lösen (`num_predict` erhöhen), damit die Backup-KI-Mail nicht immer den Fallback-Text nutzt.
3. Follow-up-Touchpoints (T-24h/T+1d/T+7d) laut Lead-Funnel-Spez (CLOSER-Texte, interne Telegram-Zustellung) verdrahten.
