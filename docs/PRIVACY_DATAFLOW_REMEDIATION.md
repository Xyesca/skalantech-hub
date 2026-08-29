# Datenschutz- und KI-Datenfluss-Remediation für Skalantech

Stand: 2026-08-29 · Verifikation: SENTINEL (t_337ef776 / Issue #15)
Basis: `docs/PRIVACY_DATAFLOW_REMEDIATION.md` auf `origin/proposal/customer-first-website-restructure` (verbindliche Referenz).
Diese Fassung ergänzt die Referenz um die **SENTINEL-Realitätsprüfung vom 29.08.2026** (Abschnitt „SENTINEL-Verifikation") und dokumentiert Abweichungen.

Hinweis: Dies ist eine technische/organisatorische Arbeitsgrundlage und **keine individuelle Rechtsberatung**. Vor produktiver Veröffentlichung der finalen Datenschutzerklärung sollte die tatsächliche Datenverarbeitung mit einer datenschutzrechtlich qualifizierten Stelle geprüft werden.

## Ausgangslage im aktuellen Master

### Website / Hosting
- `skalantech.store` läuft auf eigener Anwendung / VPS-Infrastruktur.
- IONOS wird für Domain/Mail/Server eingesetzt.
- First-Party-Analytics speichert laut Code keine IP-Adresse und keine Formularinhalte.
- Keine externen Webfonts/klassischen Werbetracker im aktuellen Template.

### Kontaktformular
- Name, E-Mail, optional Unternehmen, Anliegen und Nachricht werden in der Skalantech-Datenbank gespeichert.
- Interne Benachrichtigung erfolgt über IONOS SMTP.
- Normale Kontaktanfragen werden nicht automatisch an DeepSeek gesendet, sofern kein `book_slot=1`-Pfad ausgelöst wird.

### Terminbuchung
Der n8n-Workflow `Skalantech Terminanfrage (KI) v2` (`50fo5b3SqQjmEVrX`, aktiv) baut aus Name, Unternehmen, Thema und Nachricht einen KI-Prompt und ruft **DeepSeek primär** auf; lokales Ollama ist nur Backup. Dadurch werden echte personenbezogene Angaben aus dem Booking-Pfad an DeepSeek übertragen.

**SENTINEL-Befund 29.08.2026, 10:35 UTC:** Der LIVE-aktive Workflow (Published-Graph `f7079e0f-405a-4a55-9536-28be324ae872`, versionCreatedAt 2026-08-28 09:30 UTC — VOR Issue #15) enthielt den DeepSeek-Pfad **weiterhin**:
`KI-Prompt bauen → DeepSeek Antwort (https://api.deepseek.com/chat/completions, Credential „DeepSeek API Header" 7IagYDgNYUewRxw1) → KI-Fallback prüfen → DeepSeek OK? → (false) Ollama Backup`.
Die Entfernung lief im parallelen NEXUS-Task `t_22e3ac08`.

**SENTINEL-Nachprüfung 29.08.2026, 10:47 UTC (nach NEXUS-Cutover):** Der LIVE-aktive Workflow wurde um 10:37:08 UTC neu aktiviert (Published-Graph `e72a7a12-f6d3-4c41-a7bb-0fb1cc255c71`). **Alle LLM-Nodes sind entfernt** (KI-Prompt bauen, DeepSeek Antwort, KI-Fallback prüfen, DeepSeek OK?, Ollama Backup, Ollama Ergebnis übernehmen, KI-Mail extrahieren). Ersatz: deterministischer Node **„Bestätigungstext bauen"** (Code, Template-Bausteine, kein LLM-Aufruf; Kommentar im Code: „Deterministische Bestätigungsmail (kein LLM im Terminpfad — Issue #15)"). Pfad: `Event-Kontext → Bestätigungstext bauen → ICS erzeugen → Bestätigung an Kunde (IONOS SMTP)`.

Hinweis: Der Repo-Export `docs/n8n/workflow-terminbuchung-v2-IONOS.json` war zum Nachprüfzeitpunkt noch der Stand vom 28.08. 09:42 (mit DeepSeek) — Aktualisierung läuft bei NEXUS (t_22e3ac08, Status running).

### Live-Demos
Die Demo-Workflows 400 (InvoiceFlow), 401 (OfferAI), 402 (MailAgent) rufen in den Exporten `docs/n8n/demo-*.json` DeepSeek primär auf und nutzen lokales Ollama als Fallback. Die UI weist zwar darauf hin, keine echten personenbezogenen/vertraulichen Daten einzugeben, technisch kann ein Besucher trotzdem Freitext übermitteln.

**SENTINEL-Befund 29.08.2026:** Exporte bestätigt: alle drei Demo-Workflows haben die Struktur `Prompt & Validierung → DeepSeek Antwort → DeepSeek prüfen → DeepSeek OK? → (false) Ollama Backup`. Damit ist DeepSeek im Demo-Standardpfad PRIMÄR — Abweichung von der Zielarchitektur „Modus A: lokale Modellverarbeitung als Standard" (siehe unten).

## Warum der aktuelle Termin-Pfad unnötig riskant ist

Die KI erzeugt im Booking-Workflow nur einen kurzen personalisierten Absatz für eine Terminbestätigung. Diese Aufgabe rechtfertigt aus Skalantech-Sicht keine Übertragung von Name, E-Mail/Unternehmenskontext und freiem Nachrichtentext an einen Drittland-Anbieter.

DeepSeek erklärt in seiner veröffentlichten Privacy Policy, dass Informationen auf Servern in der Volksrepublik China gespeichert werden können. Für personenbezogene Daten außerhalb des EWR müssen nach DSGVO zusätzlich zum normalen Verarbeitungszweck auch die Anforderungen für Drittlandtransfers sauber geprüft und abgesichert werden.

**Empfehlung:** Der produktive Terminpfad wird vollständig von externen generativen KI-Diensten entkoppelt.

## P0-Zielarchitektur

```text
Besucher
  -> Flask Formular
  -> Skalantech DB / Booking Store
  -> internes n8n
  -> deterministische Bestätigungs-Mail via IONOS
  -> ICS-Termineinladung

KEIN LLM im Terminpfad
```

Der Bestätigungstext wird aus einer festen, professionellen Vorlage erzeugt. Personalisierung beschränkt sich auf bereits erforderliche Termin-/Kontaktdaten.

## P0 Demo-Architektur

Für öffentliche Demos zwei Betriebsmodi zulassen:

### Modus A — Datenschutzfreundlicher Standard
- lokale Modellverarbeitung auf Skalantech-Infrastruktur
- fiktive Beispieltexte
- kein Versand an externe KI-Anbieter

### Modus B — externer Modellprovider nur wenn ausdrücklich benötigt
Vor produktiver Verwendung:
- Vertrag/AVV bzw. Provider-DPA prüfen
- Datenstandort und Unterauftragsverarbeiter prüfen
- Drittlandtransfermechanismus dokumentieren
- Daten minimieren / pseudonymisieren
- Gesundheitsdaten, Berufsgeheimnisse und andere besonders sensible Inhalte sperren
- transparente Nutzerinformation vor Eingabe

Für die öffentliche Showcase-Seite ist **Modus A** vorzuziehen.

## Gesundheitswesen

Arztpraxen sind als Zielgruppe sinnvoll, aber Skalantech soll dort zunächst **administrative Prozesse** positionieren:
- Terminmanagement
- Rechnungs-/Abrechnungshilfen
- Dokumenten- und Postbearbeitung
- Übergabe zwischen Praxissystemen

Ausdrücklich gesperrt im KI-Pfad (auch lokal):
- Therapieempfehlung
- Medikamentenentscheidung
- freie Verarbeitung von Patientenakten / Befunden durch unbewertete Drittanbieter-LLMs

Wenn medizinische/gesundheitsbezogene Inhalte erkannt werden:
- `human_review_required=true`
- keine fachliche Antwort durch Demo/Assistent
- keine Weiterleitung an Drittland-LLM

## IONOS — SENTINEL-Realitätsprüfung (29.08.2026)

Referenz-Checkliste (aus dem Proposal) mit Ist-Befunden:

| # | Prüfpunkt | Soll (Referenz) | IST-Befund 29.08.2026 | Status |
|---|-----------|------------------|------------------------|--------|
| 1 | genaue IONOS-Produkte | Domain, Mail, VPS/Cloud Server, ggf. Backups | Domain `skalantech.store`, Mail (smtp.ionos.de:465 / imap.ionos.de:993), VPS (IONOS Cloud/Server, AS8560 IONOS SE), kein IONOS-Backup-Produkt auf dem Server nachweisbar | ✅/⚠️ teilweise |
| 2 | Vertragsdatum und AVV-Status | AVV nach Art. 28 DSGVO; laut IONOS seit 19.07.2022 Bestandteil der AGB | Konkreter Vertrags-/Account-Nachweis liegt nicht auf dem Server; **im IONOS-Kundenportal zu verifizieren** (offen) | ⚠️ offen |
| 3 | tatsächlich gewählte Serverregion | dokumentieren | **Frankfurt am Main, DE** (IP 217.160.53.90, ipinfo: AS8560 IONOS SE, Frankfurt/Hessen, Europe/Berlin) | ✅ verifiziert |
| 4 | Backup-/Snapshot-Region | dokumentieren | Kein lokaler Nachweis über IONOS-Snapshots/Backup-Region (kein ionosctl/Backup-Skript, keine Backup-Cron-Jobs); `/var/backups` enthält nur System-Debian-Dateien; **Snapshot-/Backup-Konfiguration im IONOS-Portal zu prüfen** (offen) | ⚠️ offen |
| 5 | Administrationszugriffe | dokumentieren | VPS-Root (ubuntu), Tailscale (100.119.11.64), n8n lokal (127.0.0.1:5678), Caddy, Redis nur 127.0.0.1; keine öffentlichen Admin-Ports | ✅ verifiziert |
| 6 | TOMs | dokumentieren | Teilweise: Container-Isolation, Redis lokal gebunden, gunicorn nur 127.0.0.1, Tailscale-Only-Netz (siehe PERIMETER_HARDENING_AUDIT.md); vollständige TOM-Liste nicht im Repo | ⚠️ teilweise |
| 7 | Lösch-/Retention-Konzept | dokumentieren | **n8n: keine Prune-Env gesetzt** (EXECUTIONS_DATA_PRUNE_* fehlt im Container-Env) → n8n-Defaults gelten; DB enthält 311 Executions (älteste 2026-08-17), 0 soft-deleted; **Retention-Konzept für n8n/DB/Logs offen** | ⚠️ offen |

### Mail-Produkt (verifiziert)
- SMTP: `smtp.ionos.de:465` (TLS, Zertifikat IONOS SE, Montabaur/DE, gültig bis 22.11.2026)
- IMAP: `imap.ionos.de:993`
- Absender/Postfach: `xyesca@skalantech.store` (Absender „Xavier Escalante")
- Produktklasse: IONOS-Mail (Business-Postfach im Rahmen des IONOS-Kontos)
- Region: IONOS-Rechenzentrum Deutschland (Montabaur / Frankfurt), Verarbeitung EU

### n8n-Retention (SENTINEL-Befund)
- n8n-Container (`apps-n8n-1`, Image `docker.n8n.io/n8nio/n8n:latest`) ohne explizite Prune-Konfiguration
- DB: `/root/apps/n8n/database.sqlite` (SQLite, WAL), 311 Executions gespeichert
- Älteste Execution: 2026-08-17; keine Löschläufe sichtbar (0 soft-deleted)
- **PII-Risiko:** Execution-Daten des Booking-Workflows enthalten Name, E-Mail, Nachricht (siehe Execution #439 Beispiel-Payload) und bleiben ohne Prune-Konfiguration potenziell unbegrenzt bzw. nach n8n-Default (EXECUTIONS_DATA_MAX_AGE, Default 336 h) liegen
- **Empfehlung:** Prune explizit setzen (`EXECUTIONS_DATA_PRUNE_ENABLED=true`, `EXECUTIONS_DATA_MAX_AGE` auf z. B. 168 h, `EXECUTIONS_DATA_PRUNE_MAX_COUNT` begrenzen), PII-freie Logs sicherstellen

### Logging / keine PII in Logs (SENTINEL-Befund)
- gunicorn Access-Log (`--access-logfile -`): enthält nur Pfad/Status/User-Agent, **keine POST-Bodies, keine PII** ✅
- Flask-Code: kein PII-Logging von Formulardaten gefunden (grep über `app/`); einziger print-Block ist das temporäre Admin-Startpasswort beim ersten Boot (kein Kunden-PII) ✅
- n8n: Log-Level nicht als Debug gesetzt; PII liegt in Execution-**Daten** (DB), nicht in Logs — trotzdem Retention setzen (siehe oben)
- **Fazit:** Aktuell keine PII in Debug-/Error-Logs nachweisbar. **Keine Änderung nötig, aber Prune-Konfiguration ergänzen.**

## Vercel vs. eigener IONOS/VPS

Vercel ist nicht per se datenschutzwidrig. Vercel bietet einen DPA und internationale Transfermechanismen, nennt in seinem DPA aber primäre Processing-Facilities in den USA. Compute kann in Frankfurt laufen, jedoch ist das Gesamt-Datenmodell nicht allein durch die ausgewählte Function-Region bestimmt.

Skalantech muss Vercel daher nicht kopieren. Der eigene IONOS/VPS-Stack ist ein sinnvoller Differenzierungsfaktor, wenn er professionell betrieben wird.

Kundenbotschaft:
> `Kontrollierbare Datenwege und flexible Betriebsmodelle – mit europäischem Hosting und lokalen Komponenten, wenn der Anwendungsfall es erfordert.`

Nicht ohne technische Prüfung behaupten:
- `100 % alle Daten in Deutschland`
- `DSGVO-konform` als pauschales Produktmerkmal
- `Daten verlassen niemals unsere Infrastruktur`, solange externe KI-/Mail-/DNS-/Provider-Dienste beteiligt sind

## Datenschutzerklärung — notwendige Kapitel

Die finale öffentliche Datenschutzerklärung sollte mindestens sauber trennen:
1. Verantwortlicher
2. Hosting / IONOS
3. Server-Logdaten
4. First-Party-Analytics
5. Kontaktformular
6. Terminbuchung
7. E-Mail-Kommunikation
8. öffentliche Live-Demos
9. AI Consultant (erst nach Rollout)
10. externe KI-Anbieter **nur wenn tatsächlich produktiv personenbezogene Daten erhalten**
11. Speicherdauer / Löschkonzept
12. Rechtsgrundlagen
13. Empfänger / Auftragsverarbeiter
14. Drittlandtransfers
15. Betroffenenrechte
16. Beschwerderecht bei der zuständigen Aufsichtsbehörde
17. Stand/Änderungen

## Wichtige Textregel

Die Datenschutzerklärung darf nicht einfach alle Modelle aufzählen, die Skalantech theoretisch einsetzen könnte. Sie muss die **tatsächlichen produktiven Verarbeitungsvorgänge** erklären.

Beispiel:
- Wenn Gemini nur intern für Entwicklungsaufgaben ohne Website-Nutzerdaten verwendet wird, gehört es nicht automatisch in die Website-Datenschutzerklärung.
- Wenn OpenAI/DeepSeek Daten eines Website-Besuchers über einen produktiven Chat erhält, muss dieser Vorgang transparent beschrieben werden.

## Technische Schutzmaßnahmen

- externe LLMs nie direkt aus dem Browser aufrufen
- Provider-Keys ausschließlich serverseitig/n8n Credentials
- PII-Filter/Datenminimierung vor externem Modell
- Prompt-/Response-Logging minimieren oder deaktivieren
- n8n Execution Data Retention definieren
- keine sensiblen Payloads in Debug-Logs
- verschlüsselte Backups
- Restore-Test
- Admin/N8n nur private Zugänge / Tailscale
- Least Privilege für Credentials
- Provider-Ausfall darf nicht zur ungeprüften Fallback-Weitergabe an einen anderen Cloud-Anbieter führen
- Data-Flow-Inventar pro Workflow

## Abnahme-Checkliste — SENTINEL-Status (29.08.2026)

| # | Kriterium | Status |
|---|-----------|--------|
| 1 | Terminworkflow enthält keinen externen LLM-Aufruf | ✅ ERFÜLLT (nach NEXUS-Cutover 10:37 UTC; aktiver Graph `e72a7a12` ohne LLM-Nodes) |
| 2 | DeepSeek aus Booking-Datenfluss entfernt | ✅ ERFÜLLT (Live-Workflow; Export-Aktualisierung läuft bei NEXUS t_22e3ac08) |
| 3 | Demo-Standardpfad lokal oder explizit getrennt | ❌ NOCH NICHT — Demos DeepSeek-primär (separater Punkt, siehe Offene Punkte) |
| 4 | IONOS Produkt/Region/AVV dokumentiert | ⚠️ Teilweise — Region/Mail verifiziert; AVV- und Backup-Nachweis im IONOS-Portal offen |
| 5 | tatsächliche Empfänger/Provider inventarisiert | ✅ DeepSeek (nur noch Demos), IONOS Mail, Telegram (Buchungsbenachrichtigung), Redis lokal; Ollama im Terminpfad entfernt |
| 6 | Retention n8n/DB/Logs festgelegt | ⚠️ Offen — n8n-Pruning nicht konfiguriert |
| 7 | Datenschutzerklärung stimmt mit Code/Workflows überein | ⚠️ Text erwähnt DeepSeek noch (aktuell nur noch für Demos korrekt); NACH finalem Demo-Umbau durch VELA (t_28c1c61a) aktualisieren |
| 8 | Rechtsgrundlagen/Drittlandtransfer juristisch geprüft | ⚠️ Offen (externe DS-Beratung) |
| 9 | Gesundheitsdaten-Sperre getestet | ⚠️ Offen — ist in Demo-Prompts vorgesehen, Test ausstehend |
| 10 | SENTINEL führt Privacy-E2E durch | ✅ GRÜN 29.08.2026, 10:47 UTC (Execution #445) — kein Request an externe LLM-Domain |

## SENTINEL Privacy-E2E (29.08.2026)

**Ziel:** Booking-POST darf zu KEINEM Request an eine externe LLM-Domain führen (DeepSeek/OpenAI/Gemini/OpenRouter).

**Methode:**
1. Statische Analyse des LIVE-aktiven Workflow-Graphen (`50fo5b3SqQjmEVrX`, Published-Version) auf externe HTTP-Aufrufe.
2. Prüfung des Flask-Booking-Codes (`app/blueprints/public.py`, `_forward_to_n8n`) auf direkte externe LLM-Aufrufe.
3. Prüfung aller n8n-Credentials auf externe LLM-Provider.
4. Dynamischer Test: Booking-POST gegen den aktiven Webhook, Beobachtung ob ein externer LLM-Request ausgelöst wird.

**Ergebnis Ist-Zustand (10:35 UTC, vor NEXUS-Cutover):**

```
Booking-POST (book_slot=1, gültiger Slot)
  -> Flask _forward_to_n8n -> http://127.0.0.1:5678/webhook/skalantech-termin   (KEIN externer Call in Flask ✅)
  -> n8n: Validieren & Slot -> Gültig? -> Slot gewünscht? -> Slot reservieren (intern ✅)
  -> Kontext wiederherstellen -> Slot frei? -> Event-Kontext
  -> KI-Prompt bauen
  -> DeepSeek Antwort  https://api.deepseek.com/chat/completions   ❌ EXTERNE LLM-DOMAIN
  -> KI-Fallback prüfen -> DeepSeek OK? -> (false) Ollama Backup (127.0.0.1:11434)
  -> KI-Mail extrahieren -> ICS -> Bestätigung an Kunde (IONOS SMTP)
```

**Zwischenverdict 10:35 UTC: ❌ ROT** — Booking-POST mit gültigem freiem Slot führte zu einem Request an `api.deepseek.com` (Ausgangsbefund von Issue #15).

**Ergebnis Nach-Cutover (10:47 UTC, dynamischer Test, Execution #445):**

```
Booking-POST (book_slot=1, gültiger Slot 2026-11-25 09:00)
  -> Flask _forward_to_n8n -> http://127.0.0.1:5678/webhook/skalantech-termin
  -> Validieren & Slot -> Gültig? -> Slot gewünscht? -> Slot reservieren (intern: 127.0.0.1:5000 CRM API) ✅
  -> Kontext wiederherstellen -> Slot frei? -> Event-Kontext
  -> Bestätigungstext bauen (Code, deterministisch, KEIN LLM) ✅
  -> ICS erzeugen (Base64 text/calendar) ✅
  -> Bestätigung an Kunde (IONOS SMTP smtp.ionos.de:465) ✅
  -> Benachrichtigung Xavier (IONOS SMTP) ✅
  -> Telegram: Buchung bestätigt (Telegram Bot, dokumentierte Notification) ✅
  -> Antwort: Erfolg (HTTP 200, success:true) ✅
```

Ausgeführte Nodes (14/14, alle success): Webhook, Validieren & Slot, Gültig?, Slot gewünscht?, Slot reservieren, Kontext wiederherstellen, Slot frei?, Event-Kontext zusammenführen, Bestätigungstext bauen, ICS erzeugen, Bestätigung an Kunde, Antwort: Erfolg, Benachrichtigung Xavier, Telegram: Buchung bestätigt.

**Verdict: ✅ GRÜN — Booking-POST führt zu KEINEM Request an eine externe LLM-Domain (kein DeepSeek/OpenAI/Gemini/OpenRouter/Ollama im ausgeführten Pfad).** Einzige externe Kontakte: IONOS SMTP (Bestätigungs-/Benachrichtigungsmail, EU) und Telegram (Buchungsbenachrichtigung an internen Kanal) — beide dokumentiert und kein LLM. Flask-Code (`_forward_to_n8n`) ruft ausschließlich den internen n8n-Webhook (127.0.0.1:5678) auf.

**Keine PII in Logs:** ✅ (siehe Abschnitt Logging).

**Testdaten-Hinweis:** Test-Booking mit `SENTINEL Privacy-E2E` / `sentinel-e2e@example.invalid` für 2026-11-25 09:00 angelegt; Testslot in der CRM-DB reserviert (booking_id `20261125T090000`). Keine echte PII verwendet.

## Offene Punkte / nächste Schritte

1. **NEXUS (t_22e3ac08):** DeepSeek-Node aus aktivem Terminworkflow entfernen, Export `docs/n8n/workflow-terminbuchung-v2-IONOS.json` aktualisieren, Workflow aktivieren.
2. **SENTINEL:** Privacy-E2E nach Cutover erneut ausführen (erwartet: GRÜN).
3. **NEXUS/SENTINEL:** Demo-Workflows 400/401/402 auf Modus A (Ollama primär, DeepSeek nur explizit) umstellen oder getrennt dokumentieren.
4. **Xavier/CEO:** IONOS-Kundenportal — AVV-Nachweis (Vertrag), Backup-/Snapshot-Konfiguration und Region verifizieren; Nachweis intern ablegen.
5. **NEXUS:** n8n-Pruning setzen (EXECUTIONS_DATA_PRUNE_ENABLED/MAX_AGE/MAX_COUNT) und dokumentieren.
6. **VELA (t_28c1c61a):** Datenschutztext NACH technischem Cutover aktualisieren (DeepSeek-Absatz dann entfernen/anpassen).
7. **SENTINEL:** Backup/Restore-Test dokumentieren (offen, sobald Backup-Region im IONOS-Portal bestätigt).
