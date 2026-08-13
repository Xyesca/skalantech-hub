# Hermes Übergabe – Skalantech Terminbuchung mit n8n + lokaler KI

## Ziel

Die bestehende Terminbuchung auf `skalantech.store` soll produktiv über den bereits vorhandenen n8n-Workflow laufen. Die Website sendet Terminwünsche an:

`POST http://127.0.0.1:5678/webhook/skalantech-termin`

Die vollständige überarbeitete Workflow-Datei liegt im Repository unter:

`docs/n8n-workflow-terminbuchung-v2.json`

Bestehender produktiver Workflow:

- Workflow-ID: `50fo5b3SqQjmEVrX`
- Webhook-Pfad: `skalantech-termin`
- Zeitzone: `Europe/Berlin`
- Google Calendar Credential: `GDSnPRh9olMLb8hC`
- Kalender: `xyescaescalante@gmail.com`
- Gmail Credential: `a06hhqHnYwuiVbBU`
- Lokales KI-Modell: `lfm25`

## Was v2 verbessert

1. Saubere Europe/Berlin-Zeitberechnung inklusive Sommer-/Winterzeit.
2. Nur Montag bis Freitag.
3. Nur die auf der Website angebotenen 30-Minuten-Slots.
4. Maximal 90 Tage im Voraus.
5. Google-Calendar-Availability verwendet `timeMin` / `timeMax`.
6. Google-Calendar-Event erzeugt einen Google-Meet-Link.
7. Kunde wird als Attendee hinzugefügt; Google sendet die Kalendereinladung (`sendUpdates=all`).
8. Der HTTP-Erfolg an das Website-Formular wird nach erfolgreicher Kalenderbuchung nicht mehr von Ollama/Gmail blockiert.
9. Ollama erzeugt nur einen kurzen persönlichen Absatz; Datum, Uhrzeit, Meet-Link und Signatur sind deterministisch.
10. Prompt-Injection-Schutz: Kundentext wird als unvertrauenswürdige Eingabe behandelt.
11. KI-Ausfall führt zu einem festen Fallback-Text statt zu einer fehlgeschlagenen Buchung.
12. Gmail-Fehler dürfen eine bereits erfolgreiche Kalenderbuchung nicht zurückrollen.

## Infrastruktur

- n8n läuft auf dem VPS im Container `apps-n8n-1` mit Host-Netzwerk.
- Website/Flask verwendet `N8N_WEBHOOK_URL`.
- `.env.example` enthält jetzt die Soll-Konfiguration:
  `N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/skalantech-termin`
- Ollama soll bevorzugt ausschließlich über Loopback erreichbar sein:
  `http://127.0.0.1:11434/api/chat`

Falls Ollama aktuell nur über seine Docker-IP erreichbar ist, die Docker-IP nur temporär verwenden und anschließend auf ein stabiles Loopback-Port-Mapping umstellen. Port 11434 nicht öffentlich exponieren.

## Hermes – Implementierungsauftrag

1. Vor jeder Änderung den bestehenden n8n-Workflow `50fo5b3SqQjmEVrX` sichern/exportieren.
2. `docs/n8n-workflow-terminbuchung-v2.json` prüfen und in den bestehenden Workflow übernehmen. Keinen zweiten aktiven Produktionsworkflow mit demselben Webhook-Pfad anlegen.
3. Bestehende Google-Calendar-Credentials unverändert weiterverwenden.
4. Prüfen, dass `Verfügbarkeit prüfen` exakt `timeMin={{$json.startIso}}` und `timeMax={{$json.endIso}}` verwendet.
5. Prüfen, dass `Event anlegen` 30 Minuten bucht, den Kunden als Attendee setzt, Google Meet erzeugt und `sendUpdates=all` nutzt.
6. Ollama-Verbindung bevorzugt auf `http://127.0.0.1:11434/api/chat` bereitstellen. Modell `lfm25` verwenden.
7. Das Gmail-Credential ist möglicherweise abgelaufen. Nicht versuchen, OAuth-Tokens manuell zu manipulieren. Xavier verbindet es bei Bedarf in der n8n-Oberfläche neu.
8. Kalenderbuchung muss unabhängig von Gmail/Ollama funktionieren.
9. Workflow nach API-/DB-Änderungen deaktivieren und wieder aktivieren, damit n8n die aktive Version neu lädt.
10. `docker restart apps-n8n-1` nicht verwenden.
11. Website nicht auf einen öffentlichen n8n-Webhook umstellen; internen Loopback-Aufruf beibehalten.
12. Keine Secrets oder OAuth-Tokens ins Git-Repository schreiben.

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
