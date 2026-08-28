# Skalantech AI Consultant

## Ziel

Der Website-Chat ist kein Fake-Mitarbeiter, sondern ein transparent gekennzeichneter **KI-Assistent von Skalantech**. Er soll Geschäftsprozesse verstehen, erste Automationsmuster erklären, reale Skalantech-Projekte/Demos zeigen und bei echtem Interesse zur Business-Analyse führen.

## Architektur

```text
Browser
  -> POST /api/ai-consultant/message
  -> Flask: Validation + Rate Limit + Session-ID
  -> optional interner n8n Webhook
  -> LLM / Knowledge / CRM-Aktionen in n8n
  -> normalisierte Antwort
  -> Browser
```

Der Browser spricht **niemals direkt mit n8n**. Ohne n8n-Verbindung bleibt der Chat über einen deterministischen lokalen Fallback nutzbar und verweist auf reale Skalantech-Demos.

## Aktivierung des n8n-Orchestrators

Auf dem VPS in `.env` setzen:

```env
N8N_AI_CONSULTANT_WEBHOOK_URL=http://127.0.0.1:5678/webhook/skalantech-ai-consultant
```

Danach den Skalantech-Container neu starten. Der Webhook bleibt intern auf Loopback/Tailscale; keine öffentliche n8n-URL in den Browser geben.

## Request an n8n

```json
{
  "message": "Wir übertragen Kundenanfragen manuell ins CRM.",
  "conversation_id": "c08af...",
  "page": "/automationen",
  "channel": "skalantech-web",
  "language": "de",
  "policy": "...serverseitig definierte Leitplanken..."
}
```

## Erwartete n8n-Antwort

```json
{
  "reply": "Das eignet sich für einen Ablauf ...",
  "suggestions": [
    "Welches CRM nutzen Sie?",
    "Wie viele Anfragen kommen pro Woche?"
  ],
  "action": {
    "label": "MailAgent live testen",
    "url": "/demos#mailagent"
  }
}
```

Flask akzeptiert nur interne, allowlist-basierte CTA-Ziele. Externe URLs aus einer LLM-Antwort werden verworfen.

## Verbindliche Agentenregeln

Der n8n-/LLM-Agent muss:

- sich als KI-Assistent verhalten und nie behaupten, ein menschlicher Mitarbeiter zu sein;
- keine Kunden, Mitarbeiter, Teamgrößen, Preise, Einsparungen, Referenzen oder Fähigkeiten erfinden;
- nur reale Skalantech-Demos/Leistungen empfehlen;
- keine Passwörter, API-Keys, Gesundheitsdaten oder andere sensible Daten anfordern;
- bei unklaren Anforderungen zuerst den Prozess verstehen: Trigger, Systeme, Daten, Ziel;
- bei hohem Kaufinteresse die 30-minütige Business-Analyse anbieten;
- keine autonomen Änderungen an Kundensystemen aus einem anonymen Website-Chat auslösen.

## Empfohlener n8n-Flow für ORBIT

1. Webhook `skalantech-ai-consultant`
2. Input-Validation
3. Session/Conversation Context laden
4. Intent klassifizieren
5. Knowledge-Kontext zu Leistungen, Projekten, Demos und FAQ laden
6. LLM mit festem System-Prompt
7. Structured Output erzwingen
8. optional Lead-Intent markieren
9. Antwort als JSON zurückgeben
10. sensible Inhalte nicht dauerhaft protokollieren

Später kann der Flow bei eindeutiger Zustimmung des Besuchers einen Lead an das vorhandene CRM übergeben. Kontaktdaten sollen dafür in einem klar getrennten Opt-in-Schritt erfasst werden, nicht beiläufig aus dem Chat extrahiert werden.

## Vorhandene reale CTA-Ziele

- `/demos#invoiceflow`
- `/demos#offerai`
- `/demos#mailagent`
- `/demos`
- `/automationen`
- `/#termin`

## Security / Privacy

- 1.500 Zeichen pro Nachricht
- 30 Requests pro Stunde über Flask-Limiter
- Conversation-ID validiert und serverseitig ersetzbar
- kein Drittanbieter-Chat-Script
- kein Chat-Cookie; ID nur in `sessionStorage`
- keine direkte n8n-Exposition
- n8n-Antworten werden normalisiert
- externe CTA-URLs werden blockiert
- lokale Fallback-Antworten funktionieren auch bei n8n-/LLM-Ausfall

Vor Production sollte SENTINEL zusätzlich Prompt-Injection, XSS, lange Inputs, n8n-Ausfall, Timeouts und Mobile UX E2E prüfen.

## Zuständigkeiten des Skalantech-Teams

- **ATLAS:** Wissensstruktur / Use Cases
- **VELA:** Tonalität / B2B-Copy
- **LUMINA:** Widget UX / Accessibility
- **NOVA:** Flask + Frontend Integration
- **ORBIT:** n8n-Orchestrator + LLM + optionale CRM-Aktionen
- **SENTINEL:** Security / Prompt-Injection / Datenschutz / E2E
- **PULSE:** Chat-Funnel-Events
- **CLOSER:** Lead-Qualifizierung und Übergabe zur Business-Analyse

Hermes koordiniert den Rollout und merged/deployed erst nach den jeweiligen Freigaben.