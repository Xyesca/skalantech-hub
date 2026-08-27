# n8n-Workflow: Skalantech Terminanfrage (KI) v2

**Übergabedokument für Verbesserung** — Stand: 2026-08-27, aktive Version `470807b9-dc16-439a-a301-2bcb56e018ac` (25 Nodes)

---

## 1. ZWECK

Die Website **skalantech.store** (Flask-App, Docker-Container `skalantech`) hat ein Buchungsformular. Beim Absenden POSTet Flask an den n8n-Webhook:

```
POST http://127.0.0.1:5678/webhook/skalantech-termin
```

Der Workflow: Eingabe validieren → Kalender-Verfügbarkeit prüfen → Termin in Google Kalender anlegen → **nicht-blockierende Parallel-Kette** (HTTP-Antwort ans Formular + KI-Mail + Benachrichtigungen). Die Buchung (Kalender-Event) hängt NICHT an Gmail/Telegram/KI — siehe D4.

---

## 2. AKTUELLER FLOW (25 Nodes)

```
Webhook (POST /skalantech-termin)
  → Validieren & Slot (Code: parst Input, DST-Validierung Europe/Berlin, 30-Min-Slots)
    → Gültig? (IF: $json.valid === true)
      ├─ TRUE → Slot gewünscht? (IF: $json.hasSlot === true)
      │          ├─ TRUE → Verfügbarkeit prüfen (Google Calendar availability)
      │          │          → Kontext wiederherstellen (Code: mergt Request + available)
      │          │            → Slot frei? (IF: $json.available === true)
      │          │              ├─ TRUE → Event anlegen (Google Calendar create, Meet + Attendee)
      │          │              │          → Event-Kontext zusammenführen (Code: + eventId/meetLink)
      │          │              │            → [PARALLEL, nicht-blockierend]:
      │          │              │               ├─ Antwort: Erfolg (respondToWebhook success:true)
      │          │              │               ├─ KI-Prompt bauen → DeepSeek Antwort (primär)
      │          │              │               │    → KI-Fallback prüfen → DeepSeek OK?
      │          │              │               │       ├─ true  → KI-Mail extrahieren
      │          │              │               │       └─ false → Ollama Backup (127.0.0.1:11434)
      │          │              │               │                   → Ollama Ergebnis übernehmen → KI-Mail extrahieren
      │          │              │               │   → Bestätigung an Kunde (Gmail, best-effort)
      │          │              │               ├─ Benachrichtigung Xavier (Gmail, best-effort)
      │          │              │               └─ Telegram: Buchung bestätigt (best-effort)
      │          │              └─ FALSE → Info Xavier (belegt, Gmail) → Antwort: Belegt
      │          └─ FALSE → Info Xavier (ohne Termin, Gmail) → Antwort: Ohne Termin
      └─ FALSE → Antwort: Ungültig (HTTP 400)
```

**WICHTIG — D4 (Gmail-Entkopplung, umgesetzt):** `Antwort: Erfolg` (respondToWebhook `success:true`) hängt **NICHT** an Gmail. Es ist ein direkter Parallel-Zweig von `Event-Kontext zusammenführen` — sobald das Kalender-Event angelegt ist, kommt `success:true`, unabhängig davon ob Gmail/KI/Telegram fehlschlagen. Alle nicht-kritischen Nodes (Gmail, KI-HTTP, Telegram) haben `onError: continueRegularOutput` + bounded retry (`retryOnFail: true, maxTries: 2`). Ein toter Gmail-Credential degradiert zur Fehler-Item-Ausgabe, blockiert aber nie die Buchung.

**Response-Vertrag (unverändert):** `{success, message, booked, date, time}` — `success:false` NUR bei „belegt“/„ungültig“ (bzw. fehlender Name/E-Mail). Bei Gmail-Fehler weiterhin `success:true`.

---

## 3. INFRASTRUKTUR (kritisch für Änderungen)

| Komponente | Details |
|---|---|
| **n8n** | Docker-Container `apps-n8n-1`, `network_mode: host`, Port `127.0.0.1:5678` |
| **n8n-UI** | `https://ubuntu.piranha-gray.ts.net:9443` (Caddy-TLS, Tailscale) |
| **n8n-Login** | `xyesca1989@googlemail.com` |
| **Google-Kalender** | Konto `xyescaescalante@gmail.com`, Credential-ID `GDSnPRh9olMLb8hC` „Skalantech Kalender (Terminbuchung)“ — **ABGELAUFEN, MUSS NEU VERBUNDEN WERDEN** ⚠️⚠️ |
| **Gmail** | Credential-ID `a06hhqHnYwuiVbBU` „Gmail account“ — **ABGELAUFEN, MUSS NEU VERBUNDEN WERDEN** ⚠️ |
| **DeepSeek (KI primär)** | HTTP-Request `https://api.deepseek.com/chat/completions`, Credential `7IagYDgNYUewRxw1` (httpHeaderAuth) ✅ |
| **Ollama (KI Backup)** | `http://127.0.0.1:11434/api/chat` via socat-Loopback → Container `debtpilot-ollama-1` (IP 172.22.0.2), Modell `lfm25` |
| **Telegram** | Credential `u9Q39TmSaAZEhFTX` (Bot HermesGambito), Chat `-1003956152501` |

---

## 4. BEKANNTE PROBLEME / OFFENE PUNKTE (nach Priorität)

### ⚠️⚠️ P0: Google-CALENDAR-Credential „needs to be reconnected" (NEU 2026-08-27)
**Fehler:** `The credential "Skalantech Kalender (Terminbuchung)" needs to be reconnected.` — am Node `Verfügbarkeit prüfen`.
**Folge:** Die **komplette Buchungskette ist aktuell unterbrochen** — ohne Kalender-Credential scheitert der Flow VOR der Event-Anlage, d.h. es gibt aktuell KEINE `success:true`-Buchung über die Website.
**Ursache:** OAuth-Refresh-Token abgelaufen/revoked (Kalender-Token, getrennt vom Gmail-Token).
**Lösung:** n8n-UI → Credentials → „Skalantech Kalender (Terminbuchung)" → Reconnect → Google-OAuth-Flow (Konto `xyescaescalante@gmail.com`). **Kann nicht per API — braucht Browser-Session des Users.**

### ⚠️ P0: Gmail-Credential „needs to be reconnected"
**Fehler:** `The credential "Gmail account" needs to be reconnected.` bei allen 4 Gmail-Nodes (Bestätigung Kunde, Benachrichtigung Xavier, Info ohne Termin, Info belegt).
**Folge:** Nur die E-Mail-Benachrichtigungen fehlen — die Buchung selbst ist davon **unabhängig** (D4).
**Lösung:** n8n-UI → Credentials → „Gmail account" → Reconnect → Google-OAuth-Flow. **User-Aktion, nicht per API.**

### ✅ Ollama-Pfad (Backup-KI) — getestet 2026-08-27
- **Erreichbar:** `127.0.0.1:11434/api/chat` → antwortet (Version `0.32.5`), via socat-Loopback → `debtpilot-ollama-1`.
- **lfm25 lädt:** mit `num_ctx` 2048/4096 in ~8–10 s (load_duration), Gesamtantwort ~16 s. **OHNE num_ctx (Default 65536) lädt es >3 min und bricht ab** (Memory-Druck: Swap 3.9/4 GB belegt, 2.2 GB RAM verfügbar) — das war der Grund für den früheren „ungetestet"/Timeout-Zustand.
- **FIX angewandt (live):** `KI-Prompt bauen` setzt jetzt `num_ctx: 4096` im `ollamaBody`; `Ollama Backup`-Node-Timeout auf `60000` ms erhöht (war 20000). Damit läuft der Backup-Pfad durch statt zu timeouten.
- **Antwortformat:** `{message: {content, thinking}}` — bestätigt.
- **⚠️ lfm25-Quirk (bestätigt):** `message.content` ist **LEER**, die Antwort steht in `message.thinking` (engl. Chain-of-Thought) — **trotz `think: false`**. Der Workflow liest NUR `content` und fällt auf den deutschen Standard-Satz zurück („Danke für die kurze Einordnung…"). `thinking` wird NIEMALS in Kunden-Mails eingebaut. KI bleibt Best-Effort, blockiert nie die Buchung.

### ℹ️ Code-Node hat KEIN `fetch`/`$helpers`
In dieser n8n-Version ist `$helpers.httpRequest()` im Code-Node NICHT definiert. KI-Calls laufen über **HTTP-Request-Node** (Best Practice). Keine Code-Node-HTTP-Aufrufe einbauen.

### ℹ️ Availability-Operation statt getAll
`googleCalendar` resource=calendar operation=availability liefert immer `{available: true|false}` (kein 0-Items-Problem). Beibehalten.

---

## 5. VALIDIERUNGSDETAILS („Validieren & Slot")

- Akzeptiert: `name`, `email`, `company`, `topic`, `message`, `preferred_day` (YYYY-MM-DD), `preferred_time` (HH:MM)
- Fehlerfall: kein Name/ungültige E-Mail → `{valid:false, error:...}` → Antwort: Ungültig (400)
- Kein preferred_day/time → `{valid:true, hasSlot:false}` → „Ohne Termin"-Pfad
- Slot vorhanden → `{valid:true, hasSlot:true, startIso, endIso, displayDate, displayTime}`
- **Terminlänge 30 Min**, Zeitzone Europe/Berlin (DST-Round-trip-Validierung), nur Mo–Fr, max 90 Tage voraus, erlaubte Zeiten 09:00–16:30 (30-min-Raster)

---

## 6. KI-STILVORGABE (System-Prompt in „KI-Prompt bauen")

Erzwingt Xaviers No-Bullshit-Stil (Deutsch, direkt, keine KI-Floskeln, 1–2 Sätze, kein HTML). Enthält zusätzlich eine **Prompt-Injection-Schutz-Sektion** (Kundentexte = unvertraute Daten). Antwort wird HTML-escaped in „KI-Mail extrahieren".

---

## 7. DEPLOY-HINWEISE (wie man Änderungen aktiviert)

**Kritisch:** Nach einer Änderung muss der Workflow deaktiviert+aktiviert werden, damit der laufende Webhook-Prozess die neue Node-Definition lädt. Zwei Wege:

### Weg A — Public API (n8n ≥1.119, funktioniert mit API-Key, 2026-08-27 verifiziert)
```bash
# PUT veröffentlicht direkt (activeVersionId == versionId danach)
curl -X PUT "$BASE/api/v1/workflows/50fo5b3SqQjmEVrX" \
  -H "X-N8N-API-KEY: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"...","nodes":[...],"connections":{...},"settings":{"executionOrder":"v1","timezone":"Europe/Berlin","callerPolicy":"workflowsFromSameOwner"}}'
```
**Pitfall:** `settings` ist im PUT-Schema PFLICHT, akzeptiert aber nur `executionOrder`/`timezone`/`callerPolicy` — NICHT `binaryMode`/`timeSavedMode`/`availableInMCP` (sonst 400 „additional properties"). `nodes`+`connections` MÜSSEN vollständig sein (sonst landen Nodes ohne `operation`/`resource` im Draft → kaputter Workflow beim nächsten Publish). Die `activeVersion` (vollständige, korrekte Nodes) bekommst du per `GET /api/v1/workflows/{id}` unter `activeVersion`.

### Weg B — interner REST (Session-Cookie)
Wie bisher: `PATCH /rest/workflows/<id>` mit vollem Objekt → `POST /rest/workflows/<id>/deactivate` → `POST /rest/workflows/<id>/activate {"versionId":"..."}`.

- Workflow-ID: `50fo5b3SqQjmEVrX`
- **Container-Restart `docker restart apps-n8n-1` ist durch Guard blockiert** — nie versuchen.

---

## 8. WEBSITE-SEITIG (Flask)

- `app/blueprints/public.py` → `/contact`-Endpoint: POSTet JSON an `http://127.0.0.1:5678/webhook/skalantech-termin`
- Fallback bei Fehler: Anfrage in SQLite + HTTP 409 „Termindienst nicht erreichbar" (wird durch FORGE auf D3/D7-Vertrag umgebaut)
- skalantech-Container läuft mit `network_mode: host`

---

## 9. ZUGEHÖRIGE DATEIEN

| Datei | Inhalt |
|---|---|
| `docs/n8n-workflow-terminbuchung-v2.json` | Kompletter Workflow (25 Nodes, aktuell, mit num_ctx-Fix) |
| Website-Repo `/root/skalantech-hub` | Flask-App, Booking-Formular in `index.html` + `main.js` |

---

## 10. NÄCHSTE SCHRITTE

1. **Kalender-Credential reconnecten** (User-Aktion, P0 — blockiert aktuell alle Buchungen)
2. **Gmail-Credential reconnecten** (User-Aktion, P0 — nur Benachrichtigungen)
3. Danach: E2E-Test mit Test-Termin (Webhook-Curl → Event → success:true → Gmail) + Test-Event wieder entfernen
4. lfm25-Quirk langfristig lösen (Modell/`think`-Handling), damit die KI-Mail nicht immer den Fallback-Text nutzt
