# Hermes Übergabe – Skalantech Terminbuchung mit n8n (deterministisch, ohne LLM)

## Ziel

Die bestehende Terminbuchung auf `skalantech.store` läuft produktiv über den n8n-Workflow. Die Website sendet Terminwünsche an:

`POST http://127.0.0.1:5678/webhook/skalantech-termin`

**Aktueller Workflow-Export (Stand 29.08.2026, Issue #15):**

`docs/n8n/workflow-terminbuchung-v2-issue15-privacy.json` (Google-frei, IONOS SMTP, KEIN LLM im Terminpfad)

Historische Exporte:
- `docs/n8n/workflow-terminbuchung-v2-IONOS.json` (28.08.2026, noch mit DeepSeek/Ollama)
- `docs/n8n/workflow-terminbuchung-v2-pre-IONOS-backup.json` (vor IONOS-Migration)
- `docs/n8n-workflow-terminbuchung-backup-v1.json` (v1, Google/Gmail)

Bestehender produktiver Workflow:

- Workflow-ID: `50fo5b3SqQjmEVrX`
- Webhook-Pfad: `skalantech-termin`
- Zeitzone: `Europe/Berlin`
- **Mail-Transport: IONOS SMTP** (`IONOS Skalantech Mail` Credential, smtp.ionos.de:465 SSL, Absender `xyesca@skalantech.store`)
- **Booking-Store: Website-DB** (`POST http://127.0.0.1:5000/api/crm/bookings/reserve`, atomar via UNIQUE-Constraint auf `bookings.start_at_utc`)
- **Kein LLM im Terminpfad (Issue #15):** DeepSeek/Ollama entfernt; Bestätigungsmail deterministisch aus Template (Node `Bestätigungstext bauen`)

## Issue #15 — DeepSeek aus Booking-PII-Pfad entfernt (29.08.2026)

**Zielarchitektur:** Website Booking → Flask → Skalantech DB/Booking Store → internes n8n → deterministische Bestätigungs-Mail via IONOS + ICS. KEIN externes LLM im Terminpfad (kein DeepSeek, kein OpenAI/Gemini/OpenRouter).

Umgesetzt:
1. Alle LLM-Nodes entfernt: `KI-Prompt bauen`, `DeepSeek Antwort` (api.deepseek.com), `KI-Fallback prüfen`, `DeepSeek OK?`, `Ollama Backup`, `Ollama Ergebnis übernehmen`, `KI-Mail extrahieren`.
2. Neuer deterministischer Node **`Bestätigungstext bauen`** (Code): persönlicher Absatz wird aus Template-Bausteinen (Name, Firma, Thema, Nachricht) zusammengesetzt — kein LLM-Aufruf, kein Netzwerk, kein Prompt-Injection-Risiko. Kein `console.*` (keine PII in Logs).
3. Kette: `Event-Kontext zusammenführen → Bestätigungstext bauen → ICS erzeugen → Bestätigung an Kunde`. ICS-Anhang (RFC-5545, binary property `data`) unverändert.
4. Slot-/Doppelbuchungslogik unverändert (`Slot reservieren` → Flask-Endpoint, UNIQUE-Constraint; `Kontext wiederherstellen` → `Slot frei?`).
5. Workflow-Export bereinigt in `docs/n8n/workflow-terminbuchung-v2-issue15-privacy.json` (keine Credentials, keine webhookIds, keine Instanz-IDs).
6. Keine PII in Debug-/Error-Logs: keine console.*-Ausgaben; LLM-Pfad (PII-Sendung an DeepSeek) entfällt; Execution-Retention (unten) begrenzt Persistenz.
7. Execution-Retention geprüft: n8n-Defaults aktiv — Pruning EIN (`EXECUTIONS_DATA_PRUNE=true`), `EXECUTIONS_DATA_MAX_AGE=336h` (14 Tage). Keine Overrides in Compose/Container/DB. `redactionPolicy` wird von dieser n8n-Version (2.32.7, Community) nicht persistiert (per Public-API gesetzt, aber nicht in `workflow_entity.settings` gespeichert) — nicht nutzbar.

Verifikation (29.08.2026, Execution 445/446/448):
- Neuer Published-Graph `e72a7a12-f6d3-4c41-a7bb-0fb1cc255c71` (19 Nodes), alle Executions liefen mit dieser Version.
- Erfolgspfad: 14 Nodes, `Bestätigungstext bauen` → `ICS erzeugen` (Binary text/calendar) → `Bestätigung an Kunde` → IONOS akzeptiert (`250 Requested mail action okay`, accepted: [Kunde]).
- Doppelbuchung: zweiter POST auf gleichen Slot → `success:false`, „Der gewünschte Termin ist leider bereits belegt."
- Test-Bookings nach E2E wieder aus der Website-DB entfernt (0 Buchungen).

Rollback: n8n-Version-History (vorheriger Published-Graph `f7079e0f-405a-4a55-9536-28be324ae872`) bzw. Pre-Change-Kopie des Live-Exports (inkl. Nodes) inkl. Credential-Referenzen bei Bedarf aus n8n-History. Datenschutztext auf der Website wird ERST NACH technischem Cutover (und nach Demo-Umbau, siehe PRIVACY_DATAFLOW_REMEDIATION.md) aktualisiert.

## Was v2 (IONOS + Issue #15) verbessert / geändert

1. Saubere Europe/Berlin-Zeitberechnung inklusive Sommer-/Winterzeit.
2. Nur Montag bis Freitag.
3. Nur die auf der Website angebotenen 30-Minuten-Slots.
4. Maximal 90 Tage im Voraus.
5. **Google Calendar komplett entfernt.** Slot-Prüfung + Buchung laufen über den atomaren Reserve-Endpoint der Website (UNIQUE-Constraint auf `start_at_utc`; parallele Doppelbuchung → genau eine gewinnt).
6. **Gmail komplett entfernt.** Alle 4 Mail-Nodes nutzen Send Email / IONOS SMTP; Absender + Reply-To = `xyesca@skalantech.store`.
7. Kunde bekommt eine **RFC-5545-ICS-Einladung** als Anhang (Code-Node `ICS erzeugen`, binary property `data`).
8. Der HTTP-Erfolg an das Website-Formular wird nach erfolgreicher Slot-Reservierung nicht mehr von nachgelagerten Schritten blockiert.
9. **Bestätigungsmail vollständig deterministisch** (Node `Bestätigungstext bauen`): persönlicher Absatz aus Template-Bausteinen (Name, Firma, Thema, Nachricht); Datum, Uhrzeit und Signatur fest. KEIN LLM im Terminpfad (kein DeepSeek/OpenAI/Gemini/OpenRouter, kein Ollama).
10. Kein Prompt-Injection-Risiko mehr (kein LLM-Prompt aus Kundentexten).
11. Kein LLM-Ausfall-Risiko: deterministischer Node braucht kein Modell/Netzwerk.
12. SMTP-/Mail-Fehler dürfen eine bereits bestätigte Buchung nicht zurückrollen (Buchung ist committed, bevor Mails rausgehen; Mail-Nodes `onError: continueRegularOutput`).

## Infrastruktur

- n8n läuft auf dem VPS im Container `apps-n8n-1` mit Host-Netzwerk.
- Website/Flask verwendet `N8N_WEBHOOK_URL` (`http://127.0.0.1:5678/webhook/skalantech-termin`).
- `.env.example` enthält die Soll-Konfiguration:
  `N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/skalantech-termin`
- Ollama wird im Booking-Workflow NICHT mehr verwendet. Andere Workflows (Demos) nutzen ggf. weiterhin lokale Modelle; Loopback-Regel gilt dort: `http://127.0.0.1:11434/api/chat`, Port 11434 nicht öffentlich exponieren.

## Hermes – Implementierungsauftrag (Stand Issue #15)

1. Vor jeder Änderung den bestehenden n8n-Workflow `50fo5b3SqQjmEVrX` sichern/exportieren (Rollback-Punkt dokumentieren).
2. `docs/n8n/workflow-terminbuchung-v2-issue15-privacy.json` prüfen und in den bestehenden Workflow übernehmen. Keinen zweiten aktiven Produktionsworkflow mit demselben Webhook-Pfad anlegen.
3. IONOS-SMTP-Credential (`IONOS Skalantech Mail`) verwenden; kein Gmail/Google, kein DeepSeek/Ollama im Terminpfad.
4. Prüfen, dass `Slot reservieren` exakt `POST http://127.0.0.1:5000/api/crm/bookings/reserve` mit X-API-Key (Credential `Skalantech CRM API`) aufruft.
5. Prüfen, dass die Kundenmail den ICS-Anhang (binary property `data`) enthält und Reply-To `xyesca@skalantech.store` ist.
6. Bestätigungsmail muss deterministisch aus `Bestätigungstext bauen` kommen — KEIN LLM-Aufruf (Execution-Daten prüfen: Erfolgspfad = 14 Nodes, kein HTTP-Request an externe LLM-Domain).
7. Booking-Endpoint der Website ist Source of Truth; Buchung wird VOR dem Mailversand committed.
8. Buchung muss unabhängig von Mail funktionieren.
9. Workflow nach API-/DB-Änderungen deaktivieren und wieder aktivieren, damit n8n die aktive Version neu lädt (Public-API-PUT publiziert bei aktiven Workflows automatisch; trotzdem verifizieren).
10. `docker restart apps-n8n-1` nicht verwenden.
11. Website nicht auf einen öffentlichen n8n-Webhook umstellen; internen Loopback-Aufruf beibehalten.
12. Keine Secrets oder OAuth-Tokens ins Git-Repository schreiben. Exporte bereinigen (keine Credentials/webhookIds).

## Telegram-Benachrichtigung

Bei jeder erfolgreichen Terminbuchung sendet der Workflow eine Benachrichtigung an den Telegram-Kanal **„AiGents"** (`-1003956152501`):

- Bot: `@CarEmmBot` (HermesGambito) — Token aus `~/.hermes/.env` (`TELEGRAM_BOT_TOKEN`)
- n8n-Credential: `u9Q39TmSaAZEhFTX` (Typ `telegramApi`)
- Node: **„Telegram: Buchung bestätigt"** — hängt parallel zu „Antwort: Erfolg"/„Bestätigungstext bauen"/„Benachrichtigung Xavier" am „Event-Kontext zusammenführen"
- Inhalt: Name, Unternehmen, E-Mail, Datum/Uhrzeit, Thema, Nachricht
- `onError: continueRegularOutput` → Telegram-Ausfall blockiert die Buchung nie
- Nur bei **erfolgreicher** Buchung (nach Slot-Reservierung); Terminkonflikte lösen keine Telegram-Nachricht aus

## E2E-Tests

Hermes soll mindestens diese Tests durchführen und protokollieren:

- Freier Slot: HTTP success, Booking in Website-DB, korrekte Uhrzeit, 30 Minuten, ICS-Anhang, IONOS akzeptiert.
- Belegter Slot: kein zweites Booking, verständliche Fehlermeldung.
- Wochenende: Validierungsfehler.
- Nicht angebotene Uhrzeit: Validierungsfehler.
- Vergangener Termin: Validierungsfehler.
- Mehr als 90 Tage: Validierungsfehler.
- Sommerzeit: z. B. 11:00 Europe/Berlin erscheint auch als 11:00 im ICS (DTSTART/DTEND UTC korrekt).
- Kein LLM-Aufruf: Erfolgspfad-Execution enthält NUR die 14 deterministischen Nodes (kein DeepSeek/Ollama).
- IONOS nicht erreichbar: Buchung bleibt committed, Mail-Fehler blockieren den Website-Request nicht.
- Website AJAX: Benutzer erhält nach erfolgreicher Buchung eine klare Erfolgsmeldung.
- Nach E2E: Test-Bookings aus Website-DB löschen (0 Testzeilen).

## Website-Hinweis

Die Terminbuchung befindet sich aktuell in der Sektion `#termin`. Die allgemeine Projektanfrage befindet sich in `#contact`. Hermes soll CTA-Links und Navigation prüfen, damit Nutzer für eine Terminbuchung gezielt nach `#termin` geführt werden. Keine zweite konkurrierende Terminbuchung in `#contact` bauen, außer es wird bewusst UX-seitig zusammengeführt.

## Abschlussmeldung von Hermes

Nach Umsetzung bitte zurückmelden:

- aktive Workflow-ID und Version (Published-Graph)
- welche Dateien/Services geändert wurden
- dass die Bestätigungsmail deterministisch OHNE LLM erzeugt wird (Issue #15)
- ob IONOS-Mail + ICS-Anhang funktional sind (Execution-Beleg: `accepted`, `250`)
- ob die Slot-/Doppelbuchungslogik unverändert sicher ist (409-Pfad)
- E2E-Testergebnisse
- Git-Commit(s) der Website-Anpassungen
- offene Risiken oder bewusst nicht umgesetzte Punkte (Demo-Workflows 400/401/402 seit 30.08.2026 Modus A/Ollama lokal — siehe PRIVACY_DATAFLOW_REMEDIATION.md, t_57d9b794)
