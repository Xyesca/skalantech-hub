# Hermes Übergabe – Skalantech Terminbuchung mit n8n + lokaler KI

## Ziel

Die bestehende Terminbuchung auf `skalantech.store` soll produktiv über den bereits vorhandenen n8n-Workflow laufen. Die Website sendet Terminwünsche an:

`POST http://127.0.0.1:5678/webhook/skalantech-termin`

Die vollständige überarbeitete Workflow-Datei liegt im Repository unter:

`docs/n8n/workflow-terminbuchung-v2-IONOS.json` (Google-frei, IONOS SMTP — Stand 08/2026)

Bestehender produktiver Workflow:

- Workflow-ID: `50fo5b3SqQjmEVrX`
- Webhook-Pfad: `skalantech-termin`
- Zeitzone: `Europe/Berlin`
- **Mail-Transport: IONOS SMTP** (`IONOS Skalantech Mail` Credential, smtp.ionos.de:465 SSL, Absender `xyesca@skalantech.store`)
- **Booking-Store: Website-DB** (`POST http://127.0.0.1:5000/api/crm/bookings/reserve`, atomar via UNIQUE-Constraint)
- Lokales KI-Modell: `lfm25` (Backup); DeepSeek primär

## Was v2 (IONOS) verbessert / geändert

1. Saubere Europe/Berlin-Zeitberechnung inklusive Sommer-/Winterzeit.
2. Nur Montag bis Freitag.
3. Nur die auf der Website angebotenen 30-Minuten-Slots.
4. Maximal 90 Tage im Voraus.
5. **Google Calendar komplett entfernt.** Slot-Prüfung + Buchung laufen jetzt über den atomaren Reserve-Endpoint der Website (UNIQUE-Constraint auf `start_at_utc`; parallele Doppelbuchung → genau eine gewinnt).
6. **Gmail komplett entfernt.** Alle 4 Mail-Nodes nutzen Send Email / IONOS SMTP; Absender + Reply-To = `xyesca@skalantech.store`.
7. Kunde bekommt eine **RFC-5545-ICS-Einladung** als Anhang (Code-Node `ICS erzeugen`, binary property `data`).
8. Der HTTP-Erfolg an das Website-Formular wird nach erfolgreicher Slot-Reservierung nicht mehr von KI/Mail blockiert.
9. KI erzeugt nur einen kurzen persönlichen Absatz; Datum, Uhrzeit und Signatur sind deterministisch.
10. Prompt-Injection-Schutz: Kundentext wird als unvertrauenswürdige Eingabe behandelt.
11. KI-Ausfall führt zu einem festen Fallback-Text statt zu einer fehlgeschlagenen Buchung.
12. SMTP-/Mail-Fehler dürfen eine bereits bestätigte Buchung nicht zurückrollen (Buchung ist committed, bevor Mails rausgehen).

## Infrastruktur

- n8n läuft auf dem VPS im Container `apps-n8n-1` mit Host-Netzwerk.
- Website/Flask verwendet `N8N_WEBHOOK_URL`.
- `.env.example` enthält jetzt die Soll-Konfiguration:
  `N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/skalantech-termin`
- Ollama soll bevorzugt ausschließlich über Loopback erreichbar sein:
  `http://127.0.0.1:11434/api/chat`

Falls Ollama aktuell nur über seine Docker-IP erreichbar ist, die Docker-IP nur temporär verwenden und anschließend auf ein stabiles Loopback-Port-Mapping umstellen. Port 11434 nicht öffentlich exponieren.

## Hermes – Implementierungsauftrag

1. Vor jeder Änderung den bestehenden n8n-Workflow `50fo5b3SqQjmEVrX` sichern/exportieren (Rollback: `docs/n8n/workflow-terminbuchung-v2-pre-IONOS-backup.json`).
2. `docs/n8n/workflow-terminbuchung-v2-IONOS.json` prüfen und in den bestehenden Workflow übernehmen. Keinen zweiten aktiven Produktionsworkflow mit demselben Webhook-Pfad anlegen.
3. IONOS-SMTP-Credential (`IONOS Skalantech Mail`) verwenden; kein Gmail/Google mehr.
4. Prüfen, dass `Slot reservieren` exakt `POST http://127.0.0.1:5000/api/crm/bookings/reserve` mit X-API-Key (Credential `Skalantech CRM API`) aufruft.
5. Prüfen, dass die Kundenmail den ICS-Anhang (binary property `data`) enthält und Reply-To `xyesca@skalantech.store` ist.
6. Ollama-Verbindung bevorzugt auf `http://127.0.0.1:11434/api/chat` bereitstellen. Modell `lfm25` verwenden.
7. Booking-Endpoint der Website ist Source of Truth; Buchung wird VOR dem Mailversand committed.
8. Buchung muss unabhängig von KI/Mail funktionieren.
9. Workflow nach API-/DB-Änderungen deaktivieren und wieder aktivieren, damit n8n die aktive Version neu lädt.
10. `docker restart apps-n8n-1` nicht verwenden.
11. Website nicht auf einen öffentlichen n8n-Webhook umstellen; internen Loopback-Aufruf beibehalten.
12. Keine Secrets oder OAuth-Tokens ins Git-Repository schreiben.

## Telegram-Benachrichtigung

Bei jeder erfolgreichen Terminbuchung sendet der Workflow eine Benachrichtigung an den Telegram-Kanal **„AiGents"** (`-1003956152501`):

- Bot: `@CarEmmBot` (HermesGambito) — Token aus `~/.hermes/.env` (`TELEGRAM_BOT_TOKEN`)
- n8n-Credential: `u9Q39TmSaAZEhFTX` (Typ `telegramApi`)
- Node: **„Telegram: Buchung bestätigt"** — hängt parallel zu „Antwort: Erfolg"/„KI-Prompt bauen"/„Benachrichtigung Xavier" am „Event-Kontext zusammenführen"
- Inhalt: Name, Unternehmen, E-Mail, Datum/Uhrzeit, Thema, Nachricht, Meet-Link
- `onError: continueRegularOutput` → Telegram-Ausfall blockiert die Buchung nie
- Nur bei **erfolgreicher** Buchung (nach Event-Anlage); Terminkonflikte lösen keine Telegram-Nachricht aus

## E2E-Tests

Hermes soll mindestens diese Tests durchführen und protokollieren:

- Freier Slot: HTTP success, Event vorhanden, korrekte Uhrzeit, 30 Minuten, Meet-Link vorhanden, Attendee vorhanden.
- Belegter Slot: kein zweites Event, verständliche Fehlermeldung.
- Wochenende: Validierungsfehler.
- Nicht angebotene Uhrzeit: Validierungsfehler.
- Vergangener Termin: Validierungsfehler.
- Mehr als 90 Tage: Validierungsfehler.
- Sommerzeit: z. B. 11:00 Europe/Berlin erscheint auch als 11:00 lokaler Kalendertermin.
- Ollama nicht erreichbar: Kalenderbuchung bleibt erfolgreich; KI-Zusatz darf den Website-Request nicht fehlschlagen lassen.
- Gmail nicht verbunden: Google-Kalendereinladung und Event funktionieren weiterhin.
- Website AJAX: Benutzer erhält nach erfolgreicher Buchung eine klare Erfolgsmeldung.

## Website-Hinweis

Die Terminbuchung befindet sich aktuell in der Sektion `#termin`. Die allgemeine Projektanfrage befindet sich in `#contact`. Hermes soll CTA-Links und Navigation prüfen, damit Nutzer für eine Terminbuchung gezielt nach `#termin` geführt werden. Keine zweite konkurrierende Terminbuchung in `#contact` bauen, außer es wird bewusst UX-seitig zusammengeführt.

## Abschlussmeldung von Hermes

Nach Umsetzung bitte zurückmelden:

- aktive Workflow-ID und Version
- welche Dateien/Services geändert wurden
- ob Ollama über `127.0.0.1:11434` erreichbar ist
- ob Google Meet erstellt wird
- E2E-Testergebnisse
- ob Gmail noch manuell reconnectet werden muss
- Git-Commit(s) der Website-Anpassungen
- offene Risiken oder bewusst nicht umgesetzte Punkte
