# Skalantech Benchmark vs. AutomaticProcess — Umsetzungsroadmap

Stand: 2026-08-28

## Ziel

Skalantech übernimmt die wirksamen Prinzipien von AutomaticProcess, ohne die Marke oder Texte zu kopieren. Ziel ist eine stärkere B2B-Positionierung für KMU: konkrete Automatisierungsfälle, einfache Sprache, klare Leistungsprodukte, sichtbare Demos und ein reibungsloser Weg vom Problem zum Erstgespräch.

## Was AutomaticProcess aktuell gut macht

Die Referenzseite führt sehr schnell vom Nutzen in konkrete Anwendungsfälle:

- Hero mit klarem Ergebnisversprechen statt Technikfokus
- explizit für KMU formuliert
- Leistungen als verständliche Kategorien: Automationen, Websites, CRM, Apps
- viele konkrete Beispiele statt abstrakter Capability-Listen
- einfacher 3-Schritte-Prozess
- direkte Terminbuchung
- Branchenbreite sichtbar
- Partner-/Langfristigkeitsbotschaft statt Projekt-Einmalgeschäft
- Förderhinweis als zusätzlicher Kaufanreiz

## Wo Skalantech stärker positioniert werden soll

Skalantech soll nicht wie eine generische Automationsagentur wirken. Die Differenzierung bleibt:

1. Infrastruktur + Automation + KI aus einer Hand
2. Self-Hosting und Datensouveränität
3. technische Umsetzung bis Betrieb, Monitoring und Recovery
4. echte produktive Demos statt nur Beratung
5. eigene CRM-/Analytics-/n8n-Infrastruktur
6. persönliche technische Verantwortung durch den Gründer
7. Websites und Business-Apps als Teil eines Geschäftsprozesses, nicht als Designprodukt

## Neue Kernbotschaft

**Weniger Handarbeit. Bessere Prozesse. Systeme, die weiterarbeiten.**

Unterzeile:

> Skalantech verbindet Ihre vorhandenen Systeme, automatisiert wiederkehrende Abläufe und baut KI dort ein, wo sie messbar Arbeit abnimmt — ohne unnötigen Systemwechsel.

Diese Aussage ist als Copy-Richtung zu verstehen. Vor Live-Schaltung VELA/LUMINA finalisieren lassen.

## Leistungsarchitektur

### 1. Automationen & KI-Agenten

Konkrete Outcomes statt Tool-Liste:

- Kundenanfragen automatisch erfassen und priorisieren
- Angebote aus Anfragen vorbereiten
- Dokumente auslesen und strukturiert weiterverarbeiten
- E-Mails klassifizieren und Antwortentwürfe erstellen
- interne Reports automatisch zusammenfassen
- Follow-ups und Aufgaben automatisch auslösen
- CRM-Daten zwischen Systemen synchronisieren

### 2. Websites & Business Apps

- conversion-orientierte Unternehmenswebsites
- Kunden-/Mitarbeiterportale
- interne Apps
- Lead-Funnels und ROI-Rechner
- Formulare → n8n → CRM

### 3. CRM & Vertriebsprozesse

Skalantech besitzt bereits eine eigene CRM-Pipeline. Diese Kompetenz soll sichtbar als Leistungsbaustein angeboten werden:

- Lead-Erfassung
- Qualifizierung
- Follow-up-Automation
- Termin-/Angebotsstatus
- Reporting
- Integrationen

### 4. IT-Infrastruktur & Betrieb

Dies bleibt der strategische Unterschied zu reinen Automationsagenturen:

- Docker/Linux
- Cloud/Hybrid
- Monitoring
- Backup/Recovery
- Security Hardening
- sichere Integrationen

## Homepage-Prioritäten

P0:

1. Hero stärker auf Zeitersparnis und Prozessnutzen ausrichten.
2. Direkt darunter 6–8 konkrete Automationsfälle zeigen.
3. Leistungen auf vier verständliche Produktbereiche verdichten: Automationen, Websites & Apps, CRM, Infrastruktur.
4. Live-Demos InvoiceFlow / OfferAI / MailAgent prominenter machen.
5. CTA durchgehend auf 30-Minuten-Business-Analyse / Erstgespräch vereinheitlichen.

P1:

6. Branchenmatrix erweitern: Handwerk, Kfz, Kanzleien, Immobilien; weitere Branchen erst nach echter Nachfrage.
7. Case Studies mit Vorher → Workflow → Ergebnis aufbauen.
8. Förderprogramme nur dann als Marketingelement aufnehmen, wenn Anspruch und Aussage rechtlich belastbar geprüft wurden.
9. Content/SEO auf konkrete Suchintentionen ausbauen, nicht auf generische KI-Begriffe.

## Conversion-Prinzip

Jede Seite soll diese Reihenfolge beantworten:

Problem → konkreter Prozess → Lösung → Demo/Beweis → erwarteter Nutzen → Risiko/Vertrauen → CTA.

Keine langen Technologie-Listen oberhalb des Nutzens.

## Messung

Primäre Funnel-Events:

`page_view → use_case_view → demo_started → demo_completed → calendar_opened → lead_created → meeting_booked → qualified → proposal → won`

CEO-KPIs:

- Besucher → Lead
- Lead → Termin
- Termin → Angebot
- Angebot → Won
- Umsatz pro Leadquelle
- häufigster Use Case
- häufigste Branche

## Bot-Team-Aufteilung

### ATLAS — Positionierung & Markt
- Benchmarking
- Angebotsarchitektur
- Branchen-/Use-Case-Priorisierung

### VELA — Copy & Sales
- Hero/CTA
- Use-Case-Texte
- Angebotsseiten
- Follow-up-Sequenzen

### LUMINA — UX/CRO
- Informationsarchitektur
- mobile Conversion
- Demo-/Booking-Flows

### NOVA — Engineering
- Website-Code
- Tests
- CI/CD
- Security
- Deployment

### ORBIT — Automation/n8n
- n8n Workflows
- IONOS Mail
- CRM-Integrationen
- Fehlerpfade / Monitoring

### SENTINEL — QA/Security
- Tests
- Secrets
- Auth
- Backup/Restore
- Release Gate

### PULSE — Analytics/SEO
- Funnel
- GSC
- Attribution
- SEO-Backlog

## Regel für Hermes

Hermes ist Orchestrator, nicht Alleinentwickler. Jede Aufgabe bekommt genau einen Owner-Bot, ein überprüfbares Ergebnis und ein GitHub-Issue. Kein direktes unkontrolliertes Arbeiten auf `master`.
