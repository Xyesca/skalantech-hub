# Datenschutz- und KI-Datenfluss-Remediation für Skalantech

Stand: 2026-08-29

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
Der aktuelle n8n-Workflow `workflow-terminbuchung-v2-IONOS.json` baut aus Name, Unternehmen, Thema und Nachricht einen KI-Prompt und ruft DeepSeek auf; lokales Ollama ist nur Backup. Dadurch werden echte personenbezogene Angaben aus dem Booking-Pfad an DeepSeek übertragen.

### Live-Demos
Die aktuellen Demo-Workflows rufen DeepSeek primär auf und nutzen lokales Ollama als Fallback. Die UI weist zwar darauf hin, keine echten personenbezogenen/vertraulichen Daten einzugeben, technisch kann ein Besucher trotzdem Freitext übermitteln.

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
- Terminverwaltung
- organisatorische E-Mails
- Lieferanten-/Praxisbedarfsrechnungen
- interne Aufgaben
- Dokumentrouting ohne medizinische Bewertung

Nicht als Standard-Cloud-KI-Use-Case positionieren:
- Diagnose
- Therapieempfehlung
- Medikamentenentscheidung
- freie Verarbeitung von Patientenakten / Befunden durch unbewertete Drittanbieter-LLMs

Wenn medizinische/gesundheitsbezogene Inhalte erkannt werden:
- `human_review_required=true`
- keine fachliche Antwort durch Demo/Assistent
- keine Weiterleitung an Drittland-LLM

## IONOS

Vor dem Datenschutz-Go-Live intern dokumentieren:
1. genaue IONOS-Produkte: Domain, Mail, VPS/Cloud Server, ggf. Backups
2. Vertragsdatum und AVV-Status
3. tatsächlich gewählte Serverregion
4. Backup-/Snapshot-Region
5. Administrationszugriffe
6. technische und organisatorische Maßnahmen
7. Lösch-/Retention-Konzept

IONOS weist darauf hin, dass bei Verarbeitung personenbezogener Daten auf seinen Systemen ein AVV nach Art. 28 DSGVO erforderlich ist; für neuere Verträge ist dieser laut IONOS seit 19.07.2022 Bestandteil der AGB. Trotzdem soll Hermes den konkreten Account/Vertrag prüfen und den Nachweis intern ablegen.

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

## Abnahme

Vor Production:
- [ ] Terminworkflow enthält keinen externen LLM-Aufruf
- [ ] DeepSeek aus Booking-Datenfluss entfernt
- [ ] Demo-Standardpfad lokal oder explizit getrennt
- [ ] IONOS Produkt/Region/AVV dokumentiert
- [ ] tatsächliche Empfänger/Provider inventarisiert
- [ ] Retention n8n/DB/Logs festgelegt
- [ ] Datenschutzerklärung stimmt mit Code/Workflows überein
- [ ] Rechtsgrundlagen/Drittlandtransfer juristisch geprüft
- [ ] Gesundheitsdaten-Sperre getestet
- [ ] SENTINEL führt Privacy-E2E durch
