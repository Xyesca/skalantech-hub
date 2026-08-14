# n8n-Workflow: Skalantech Terminanfrage (KI)

**Übergabedokument für Verbesserung** — Stand: 2026-08-13, Version `57ec36bd` (aktiv)

---

## 1. ZWECK

Die Website **skalantech.store** (Flask-App, Docker-Container `skalantech`) hat ein Buchungsformular. Beim Absenden POSTet Flask an den n8n-Webhook:

```
POST http://127.0.0.1:5678/webhook/skalantech-termin
```

Der Workflow soll: Eingabe validieren → Kalender-Verfügbarkeit prüfen → Termin in Google Kalender anlegen → **KI-generierte Bestätigungs-Mail** an den Kunden schreiben → Xavier benachrichtigen → HTTP-Antwort ans Formular.

---

## 2. AKTUELLER FLOW (19 Nodes)

```
Webhook (POST /skalantech-termin)
  → Validieren & Slot (Code: parst Input, berechnet startIso/endIso)
    → Gültig? (IF: $json.valid === true)
      ├─ TRUE → Slot gewünscht? (IF: $json.hasSlot === true)
      │          ├─ TRUE → Verfügbarkeit prüfen (Google Calendar availability)
      │          │          → Kontext wiederherstellen (Code: mergt Request-Daten + available)
      │          │            → Slot frei? (IF: $json.available === true)
      │          │              ├─ TRUE → Event anlegen (Google Calendar create)
      │          │              │          → KI-Prompt bauen (Code: baut ollamaBody)
      │          │              │            → KI-Antwort schreiben (HTTP POST → Ollama)
      │          │              │              → KI-Mail extrahieren (Code: content → aiEmail)
      │          │              │                → Bestätigung an Kunde (Gmail)
      │          │              │                  → Benachrichtigung Xavier (Gmail)
      │          │              │                    → Antwort: Erfolg (respondToWebhook)
      │          │              └─ FALSE → Info Xavier (belegt) → Antwort: Belegt
      │          └─ FALSE → Info Xavier (ohne Termin) → Antwort: Ohne Termin
      └─ FALSE → Antwort: Ungültig
```

**WICHTIG — IF-Branches:** In n8n ist `main[0]` = TRUE-Zweig, `main[1]` = FALSE-Zweig. Das ist korrekt gesetzt. (Früherer Bug: vertauschte Branches führten zu „Ungültige Eingabe" bei gültigem Input.)

---

## 3. INFRASTRUKTUR (kritisch für Änderungen)

| Komponente | Details |
|---|---|
| **n8n** | Docker-Container `apps-n8n-1`, **`network_mode: host`**, Port `127.0.0.1:5678` |
| **n8n-UI** | `https://ubuntu.piranha-gray.ts.net:9443` (Caddy-TLS, Tailscale) |
| **n8n-Login** | `xyesca1989@googlemail.com` (Passwort in n8n-DB, bcrypt) |
| **Google-Kalender** | Konto `xyescaescalante@gmail.com`, Credential-ID `GDSnPRh9olMLb8hC` (OAuth2, funktioniert ✅) |
| **Gmail** | Credential-ID `a06hhqHnYwuiVbBU` „Gmail account" — **ABGELAUFEN, MUSS NEU VERBUNDEN WERDEN** ⚠️ |
| **Ollama (KI)** | Docker-Container `debtpilot-ollama-1`, IP `172.22.0.2:11434`, Modell `lfm25` |
| **Webhook-Test** | `curl -X POST http://127.0.0.1:5678/webhook/skalantech-termin -H "Content-Type: application/json" -d '{"name":"Test","email":"t@t.de","preferred_day":"2026-08-21","preferred_time":"11:00"}'` |

---

## 4. BEKANNTE PROBLEME / OFFENE PUNKTE (nach Priorität)

### ⚠️ P1: Gmail-Credential „needs to be reconnected"
**Fehler:** `The credential "Gmail account" needs to be reconnected` bei allen 4 Gmail-Nodes.
**Ursache:** OAuth-Refresh-Token abgelaufen/revoked (Gmail-Token ist getrennt vom Kalender-Token).
**Lösung:** In n8n-UI → Credentials → „Gmail account" → Reconnect → Google-OAuth-Flow durchklicken. **Kann nicht per API gemacht werden — braucht Browser-Session des Users.**

### ⚠️ P1: Ollama-Erreichbarkeit aus n8n ungetestet
**Stand:** Der KI-Pfad (KI-Prompt bauen → HTTP-Request → KI-Mail extrahieren) ist eingebaut, aber der letzte E2E-Lauf schlug VOR dem HTTP-Node fehl (Gmail). Der HTTP-Request-Node `POST http://172.22.0.2:11434/api/chat` mit `jsonBody: "={{ $json.ollamaBody }}"` wurde noch nicht erfolgreich getestet.
**Zu prüfen:**
1. Kann n8n (host-Netzwerk) `172.22.0.2:11434` erreichen? (Host kann es — getestet ✅, aber n8n-Prozess = eigener Test nötig)
2. Liefert Ollama `{ message: { content: "..." } }` zurück? (Sollte, Modell antwortet)
3. Falls URL-Probleme: Alternative = Ollama-Node nativ (`@n8n/n8n-nodes-langchain.lmChatOllama`) mit Base-URL `http://172.22.0.2:11434`

### ⚠️ P2: Code-Node hat KEIN `fetch` und KEIN `$helpers`
**Erkenntnis aus Tests:** In dieser n8n-Version (2.69) ist `$helpers.httpRequest()` NICHT definiert im Code-Node. Deshalb wurde der KI-Call auf **HTTP-Request-Node** umgebaut (Best Practice). Keine Code-Node-HTTP-Aufrufe mehr einbauen!

### ⚠️ P2: „alwaysOutputData" am Google-Calendar-getAll-Node wirkungslos
**Erkenntnis:** `settings.alwaysOutputData: true` am getAll-Node verhinderte NICHT das 0-Items-Problem bei leerem Kalender. Deshalb wurde auf die **Availability-Operation** umgestellt (liefert immer `available: true/false`). Diese Architektur beibehalten.

### ℹ️ P3: Attendees-Format
**Erkenntnis:** `attendees: [{ email: ... }]` (Objekt-Array) → Fehler `attendee.split is not a function`. Korrekt: **String-Array** `attendees: ["={{ $json.email }}"]`. Ist gefixt.

### ℹ️ P3: Datenkontext nach API-Call
**Erkenntnis:** Der Availability-Node gibt NUR `{ available }` zurück — alle Request-Daten (name, email, startIso …) sind weg. Deshalb existiert „Kontext wiederherstellen" (mergt `$('Validieren & Slot').first().json` + `available`). Nicht entfernen!

---

## 5. VALIDIERUNGSDETAILS („Validieren & Slot")

- Akzeptiert: `name`, `email`, `company`, `topic`, `message`, `preferred_day` (YYYY-MM-DD), `preferred_time` (HH:MM)
- Fehlerfall: kein Name/ungültige E-Mail → `{ valid: false, error: '...' }` → Antwort: Ungültig
- Kein preferred_day/time → `{ valid: true, hasSlot: false }` → „Ohne Termin"-Pfad
- Slot vorhanden → `{ valid: true, hasSlot: true, startIso, endIso, dayStartIso, dayEndIso }`
- **Terminlänge: 30 Minuten** (`end = start + 30min`)

---

## 6. KI-STILVORGABE (System-Prompt in „KI-Prompt bauen")

Der Prompt erzwingt Xaviers No-Bullshit-Stil:
- Deutsch, natürlich, direkt
- KEINE KI-Floskeln („Ich hoffe, diese Nachricht erreicht Sie gut", „Gerne stehe ich zur Verfügung", „Zögern Sie nicht", „In der heutigen digitalen Welt")
- Kein Pathos, keine Marketing-Sprache
- Kurze klare Sätze, professionell + persönlich
- Antwort = HTML mit `<p>`-Absätzen, keine Betreffzeile

**Verbesserungsidee:** Stil-Regeln als Variablen/Constants oben im Code-Node, damit sie ohne Code-Grabschen editierbar sind.

---

## 7. DEPLOY-HINWEISE (wie man Änderungen aktiviert)

**Kritisch:** API-Änderungen (PATCH) landen in der DB, aber der **Workflow-Manager lädt sie erst nach Deaktivieren+Reaktivieren**. Der UI-Publish-Button ist bei API-Änderungen oft disabled. Funktioniert so:

```bash
# 1. Workflow per REST-API patchen (Session-Cookie aus n8n-Login nötig)
curl -b /tmp/n8n-cookies.txt -X PATCH http://127.0.0.1:5678/rest/workflows/<WF_ID> \
  -H "Content-Type: application/json" -d @workflow.json

# 2. Deaktivieren + Aktivieren (erzwingt Neuladen der Version)
curl -b /tmp/n8n-cookies.txt -X POST http://127.0.0.1:5678/rest/workflows/<WF_ID>/deactivate
VER=$(curl -b /tmp/n8n-cookies.txt http://127.0.0.1:5678/rest/workflows/<WF_ID> | jq -r .data.versionId)
curl -b /tmp/n8n-cookies.txt -X POST http://127.0.0.1:5678/rest/workflows/<WF_ID>/activate \
  -H "Content-Type: application/json" -d "{\"versionId\":\"$VER\"}"
```

- Workflow-ID: `50fo5b3SqQjmEVrX`
- Login-API: `POST /rest/login` mit `{"emailOrLdapLoginId":"...","password":"..."}` → Cookie-Jar speichern
- **Container-Restart `docker restart apps-n8n-1` ist durch Guard blockiert** — nie versuchen.

---

## 8. WEBSITE-SEITIG (Flask)

- `app/blueprints/public.py` → `/contact`-Endpoint: POSTet JSON an n8n-Webhook `http://127.0.0.1:5678/webhook/skalantech-termin`
- Fallback bei Fehler: Anfrage in SQLite-DB + HTTP 409 „Termindienst nicht erreichbar"
- skalantech-Container läuft mit **`network_mode: host`** (seit 2026-08-13) — erreicht n8n jetzt direkt
- Website bleibt öffentlich via Caddy (217.160.53.90 → 127.0.0.1:5000), **unverändert**

---

## 9. ZUGEHÖRIGE DATEIEN

| Datei | Inhalt |
|---|---|
| `n8n-workflow-terminbuchung.json` | Kompletter Workflow (19 Nodes) — HIER ANFASSEN |
| Website-Repo `/root/skalantech-hub` | Flask-App, Booking-Formular in `index.html` + `main.js` |
| `/tmp/n8n-cookies.txt` | n8n-Session (falls noch da) |

---

## 10. NÄCHSTE SCHRITTE (Empfehlung)

1. **Gmail-Credential reconnecten** (User-Aktion in n8n-UI, 2 Min)
2. **Ollama-Pfad E2E testen** (nach Gmail-Fix): Buchung → Event → KI-Mail → Gmail
3. Falls Ollama aus n8n nicht erreichbar: Ollama-Node nativ nutzen oder Ollama-Port auf Host publizieren
4. Stil-Prompt in Constants auslagern
5. Optional: Retry/Error-Handling für Ollama-Timeout (lfm25 kann bei erster Inferenz langsam sein)
