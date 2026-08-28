# Hermes Execution Board — Skalantech

Stand: 2026-08-28

Ziel: Hermes koordiniert die spezialisierten Bot-Teams. Xavier erhält nur Entscheidungen, Credential-Anfragen und einen kurzen Abschlussbericht.

## Prioritätsregel

`P0 Betrieb/Sicherheit → P1 Conversion/Umsatz → P2 Skalierung`

Keine neue Spielerei bauen, solange ein P0 offen ist.

## Teamrollen

| Bot | Verantwortung |
| --- | --- |
| ORBIT | n8n, Integrationen, Mail, Webhooks, Automationsbetrieb |
| NOVA | Flask/Python, Datenmodelle, APIs, Deployment-Code |
| SENTINEL | Security, Datenschutz, E2E, Rollback, Abnahme |
| LUMINA | UX/UI, Responsive, Accessibility, Conversion-Design |
| VELA | B2B-Copy, Positionierung, Angebot, CTA |
| ATLAS | Markt-/Wettbewerbsanalyse, Use Cases, Angebotsarchitektur |
| PULSE | Analytics, Funnel, Conversion-Baseline, Reporting |
| CLOSER | Lead-Pipeline, Follow-ups, Sales-Prozess |

## P0 — jetzt ausführen

### 1. IONOS + Google-freie Terminbuchung

GitHub Issue: `#2`

Owner: ORBIT + SENTINEL + NOVA

Quelle: `docs/HERMES_IONOS_N8N_MIGRATION.md`

DoD:

- IONOS SMTP Credential in n8n gesetzt
- Kunden- und interne Mails von `xyesca@skalantech.store`
- keine Gmail-Sende-Nodes im aktiven Terminworkflow
- keine Google-Calendar-Nodes im aktiven Terminworkflow
- persistente, atomare Slot-Buchung
- `.ics`-Einladung erzeugen und senden
- parallele Doppelbuchung verhindert
- Lead bleibt bei n8n/SMTP-Ausfall erhalten
- finaler Workflow ohne Secrets nach `docs/n8n/` exportiert

CEO-Aktion nur wenn nötig: Passwort des IONOS-Postfachs direkt in n8n Credential eingeben. Nie in GitHub/Chat speichern.

### 2. Öffentliche Live-Demos deployen

Owner: ORBIT + NOVA + SENTINEL

Code ist in diesem Branch vorbereitet:

- `/demos`
- `/api/demos/invoiceflow`
- `/api/demos/offerai`
- `/api/demos/mailagent`

DoD:

- Flask kann intern `127.0.0.1:5678/webhook/demo-*` erreichen
- alle drei Beispiele E2E erfolgreich
- n8n nicht öffentlich exponiert
- Rate-Limit aktiv
- keine internen Fehlerdetails im Browser
- Demo-Aufrufe in Logs nachvollziehbar

## P1 — direkt nach P0

### 3. Homepage-CRO / AutomaticProcess-Benchmark

GitHub Issue: `#3`

Owner: ATLAS + VELA + LUMINA + NOVA

Im Branch bereits umgesetzt:

- outcome-orientierter Hero
- sechs konkrete Use Cases auf der Startseite
- vier Leistungsbereiche
- Live-Demos prominent
- `/automationen` mit 12 Use Cases
- CTA auf 30-Minuten-Business-Analyse vereinheitlicht

Hermes prüft nach Deployment nur noch Desktop/Mobile, Linkpfade und reale Conversion-Daten. Keine Copy aus der Referenzseite übernehmen.

### 4. Funnel-Messung

Owner: PULSE + CLOSER

Messkette:

`page_view → use_case/demo → form_start → lead_created → meeting_booked → qualified → proposal → won/lost`

Wöchentlich nur diese CEO-KPIs melden:

- Besucher
- Demo-Nutzung
- Leads
- gebuchte Gespräche
- qualifizierte Leads
- Angebote
- Won/Lost
- Umsatz-Pipeline

Keine Vanity-Metrics als Hauptziel.

### 5. Zentrales Rate-Limiting

GitHub Issue: `#4`

Owner: NOVA + SENTINEL

Redis oder anderer gemeinsamer Store, nur intern erreichbar. In-Memory-Limits danach entfernen/vereinheitlichen.

## P2 — nach ersten echten Funnel-Daten

### 6. PostgreSQL + Migrationen

GitHub Issue: `#5`

Owner: NOVA + SENTINEL

SQLite erst ersetzen, wenn Backup, Restore, Migration und Rollback getestet sind. Alembic/Flask-Migrate statt ad-hoc `ALTER TABLE` beim Start.

### 7. Angebotsproduktisierung

Owner: ATLAS + VELA + CLOSER

Aus realen Anfragen drei klar kaufbare Einstiege formen:

1. Automation Audit
2. Automation Build / MVP
3. Operate & Grow

Preise nur veröffentlichen, wenn Scope und Marge belastbar sind.

## Arbeitsregeln für Hermes

1. Nie direkt auf `master` entwickeln.
2. Branch → Tests → PR → Review → Merge.
3. Keine Secrets in GitHub.
4. Vor n8n-Produktionsänderungen Export/Backup.
5. Keine Firewall-, Caddy- oder Tailscale-Änderung ohne Notwendigkeit und Rollback.
6. Bestehende Leads/Daten niemals für Tests löschen oder überschreiben.
7. Testdaten eindeutig markieren und nach E2E entfernen.
8. Bei externen SaaS-Abhängigkeiten zuerst Self-Hosting/Standardprotokolle prüfen, aber Wirtschaftlichkeit vor Ideologie.
9. KI nie für deterministische Validierung, Slot-Locking oder Sicherheitsentscheidungen verwenden.
10. CEO nur bei Credentials, Kostenentscheidung, Rechts-/Risikoentscheidung oder Blocker fragen.

## CEO-Abschlussformat

Maximal 10 Zeilen:

- Ampel Gesamtstatus
- Deployment Commit
- Website E2E
- Demos 3/3
- IONOS Mail
- Booking
- Google-Abhängigkeiten Restzahl
- Leads/Funnel funktionsfähig
- offene Risiken
- einzige nötige CEO-Aktion
