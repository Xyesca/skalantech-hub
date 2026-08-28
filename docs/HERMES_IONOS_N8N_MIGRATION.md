# Hermes Auftrag — IONOS-Mail + Google-freie Terminbuchung in n8n

Stand: 2026-08-28

## Zielzustand

Für die öffentliche Skalantech-Kommunikation ausschließlich verwenden:

`xyesca@skalantech.store`

Googlemail/Gmail darf nach Abschluss dieses Auftrags weder als sichtbare Kontaktadresse noch als Mail-Transport für die Website-/n8n-Kommunikation verwendet werden. Auch Google Calendar soll aus dem produktiven Terminworkflow entfernt werden.

Wichtig: **Keinen eigenen Mailserver auf dem VPS installieren. Kein Thunderbird auf dem VPS.** Thunderbird ist nur ein Mail-Client. Das Postfach wird bereits von IONOS betrieben. n8n verbindet sich direkt mit IONOS SMTP/IMAP.

## Verifizierte IONOS-Serverdaten

- SMTP: `smtp.ionos.de`
- SMTP Port: `465`
- Verschlüsselung: SSL/TLS
- Alternative: Port `587` + STARTTLS
- IMAP: `imap.ionos.de`
- IMAP Port: `993`
- Verschlüsselung: SSL/TLS
- Benutzername: vollständige Mailadresse `xyesca@skalantech.store`
- Passwort: Passwort des IONOS-Postfachs

Secrets ausschließlich in n8n Credentials / VPS Secret Store. Niemals in GitHub committen.

## Phase 0 — Sicherung

Owner: SENTINEL + ORBIT

1. Aktiven Terminworkflow exportieren.
2. Workflow-ID und aktive Version protokollieren.
3. Bestehende Google-/Gmail-Credentials nur dokumentieren, nicht löschen, bis die neue Lösung E2E getestet ist.
4. DB/Workflow-Backup erstellen.
5. Rollback-Schritt dokumentieren.

## Phase 1 — IONOS SMTP in n8n

Owner: ORBIT

In n8n ein SMTP-Credential anlegen:

- Name: `IONOS Skalantech Mail`
- User: `xyesca@skalantech.store`
- Host: `smtp.ionos.de`
- Port: `465`
- SSL/TLS: aktiv
- Passwort: vom CEO sicher bereitgestellt

Danach alle Gmail-Sende-Nodes ersetzen durch generische **Send Email / SMTP** Nodes.

Pflichtpfade:

1. Terminbestätigung an Kunden
2. interne Benachrichtigung an `xyesca@skalantech.store`
3. Kontakt-/Demo-Benachrichtigungen
4. Follow-up-Mails, sofern bereits automatisiert

Absender/Reply-To:

`xyesca@skalantech.store`

Kein Googlemail-Absender und kein Gmail OAuth mehr.

## Phase 2 — Eingehende Mail optional über IMAP

Owner: ORBIT

Nur falls ein Mail-Agent eingehende Nachrichten benötigt:

- IMAP: `imap.ionos.de:993`
- SSL/TLS
- User: `xyesca@skalantech.store`

IMAP nicht für reine Website-Benachrichtigungen konfigurieren.

## Phase 3 — Google Calendar vollständig entfernen

Owner: ORBIT + NOVA

Ziel: Terminbuchung läuft ohne Google APIs.

### Empfohlene Architektur

Website → interner n8n Webhook → Validierung → Slot-Sperre → Buchung speichern → ICS erzeugen → IONOS SMTP → CRM aktualisieren → Telegram → HTTP response

### Booking Source of Truth

Bevorzugt eine persistente Datenbank / n8n Data Table mit mindestens:

- `booking_id`
- `start_at_utc`
- `end_at_utc`
- `timezone`
- `name`
- `email`
- `company`
- `topic`
- `status`
- `created_at`
- `lead_id`

Unique/Concurrency-Regel:

Ein Slot darf nur einmal als `confirmed` existieren. Race Conditions testen; ein simples vorheriges SELECT ohne atomare Sperre reicht nicht.

Falls n8n Data Table keine sichere atomare Eindeutigkeit garantiert, PostgreSQL verwenden.

### Termin-Einladung

Nach erfolgreicher Buchung eine RFC-5545-kompatible `.ics`-Einladung erstellen und über IONOS SMTP senden.

Die Mail enthält deterministisch:

- Datum
- Uhrzeit Europe/Berlin
- Dauer 30 Minuten
- Thema
- Kontakt `xyesca@skalantech.store`
- Meeting-Link nur wenn ein eigener Videokonferenzdienst vorhanden ist

Keinen Google-Meet-Link mehr erzeugen.

## Phase 4 — Website/CRM-Flows vereinheitlichen

Owner: NOVA + ORBIT

Die Website bleibt Source of Truth für Leads, n8n orchestriert Kommunikation und Terminprozess.

Für Kontakt-/Demo-/Booking-Pfade:

1. Lead zuerst sicher speichern.
2. n8n best-effort triggern.
3. Mail-/Telegram-Ausfall darf keinen Lead verlieren.
4. Booking gilt erst als bestätigt, wenn die Slot-Transaktion erfolgreich committed ist.
5. CRM-Status nach bestätigtem Termin auf `qualified` setzen.

Website soll keine Gmail-spezifische SMTP-Logik mehr benötigen. Bestehende `_send_email()`-Gmail-Funktion nach erfolgreicher n8n-Migration entfernen oder neutralisieren.

## Phase 5 — E2E-Abnahme

Owner: SENTINEL

Pflichttests:

- freier Slot → genau eine Buchung + IONOS-Mail
- Doppelbuchung → zweite Anfrage wird abgewiesen
- parallele Doppelbuchung → ebenfalls nur eine Buchung
- Wochenende → abgewiesen
- ungültige Uhrzeit → abgewiesen
- Vergangenheit → abgewiesen
- >90 Tage → abgewiesen
- Sommer-/Winterzeit Europe/Berlin korrekt
- SMTP down → Buchung bleibt gespeichert; Fehler wird geloggt und intern alarmiert
- n8n down → Website verliert Lead nicht
- Kundenmail kommt von `xyesca@skalantech.store`
- Reply-To = `xyesca@skalantech.store`
- kein Gmail-/Google-Calendar-Node mehr im aktiven Workflow
- keine Googlemail-Adresse mehr in öffentlicher Website

## Phase 6 — Aufräumen

Erst nach bestandenem E2E:

1. Gmail Nodes aus Workflow löschen.
2. Google Calendar Nodes löschen.
3. alte Credentials in n8n deaktivieren/löschen, wenn nicht anderweitig benötigt.
4. alte Workflow-JSONs im Repo als `legacy` kennzeichnen oder ersetzen.
5. Doku aktualisieren.
6. finalen Workflow exportieren und unter `docs/n8n/` versionieren — ohne Secrets.

## CEO-Abschlussbericht

Hermes berichtet nur:

- Status Ampel
- aktive Workflow-ID/Version
- IONOS SMTP: OK/FAIL
- Google-Abhängigkeiten: 0 oder Restliste
- Booking E2E: OK/FAIL
- Mail E2E: OK/FAIL
- relevante Commit-/PR-Links
- offene CEO-Aktion, falls Passwort/Credential manuell eingegeben werden muss

Keine internen Debug-Details, solange alles grün ist.
