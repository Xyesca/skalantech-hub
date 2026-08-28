# Follow-up-Textbausteine Lead-Funnel (T0 – T+7d)

Status: **Bereit, Versand intern** · Autor: CLOSER (Sales) · Quelle: LEAD_FUNNEL_SPEC §5 (LUMINA, t_16fb5e2d)
Task: t_0751c0ab · Datum: 2026-08-27

## 1. Kanal-Regel (verbindlich)

| Touchpoint | Zeitpunkt | Kanal heute | Kanal nach Freigabe (Level B) |
|---|---|---|---|
| T0 Bestätigung | sofort nach Buchung | n8n-Gmail (KI-generiert, existiert) | n8n-Gmail |
| T-24h Erinnerung | 24 h vor Termin | intern Telegram | Kunden-Mail/Telegram |
| T+1d No-Show | 1 Tag nach verpasstem Termin | intern Telegram | Kunden-Mail/Telegram |
| T+7d Discovery-Nachfass | 7 Tage nach Discovery | intern Telegram | Kunden-Mail/Telegram |

**Kein Kunden-Versand aktivieren.** T-24h/T+1d/T+7d laufen bis zur Freigabe ausschließlich
über den internen Telegram-Kanal (`TELEGRAM_HOME_CHANNEL`, Fallback AiGents
`-1003956152501`). Die Kunden-Texte unten sind fertig formuliert und können nach Freigabe
1:1 übernommen werden.

## 2. Ton (Skalantech / Xavier-Stil — gilt für alle Bausteine)

- Deutsch, direkt, floskel-frei. Kurze, klare Sätze.
- KEINE KI-Phrasen: kein „Ich hoffe, diese Nachricht erreicht Sie gut“, kein „Gerne
  stehe ich für Fragen zur Verfügung“, kein „Zögern Sie nicht“, kein „In der heutigen
  digitalen Welt“.
- Kein Pathos, keine Übertreibungen, keine Marketing-Sprache.
- Professionell + persönlich. Wie ein Dienstleister, der seinen Job kennt.
- Keine Füllwörter am Satzanfang („gerne“, „sehr gerne“, „natürlich“).
- Value vor Feature: Wenn Erkenntnisse kommuniziert werden, in Zeit/Geld/Fehlern
  ausdrücken, nicht in Technik.

## 3. Platzhalter-Referenz

| Platzhalter | Bedeutung | Format / Beispiel | Quelle |
|---|---|---|---|
| `{{name}}` | Vorname/Name des Leads | „Max Mustermann“ | CRM-Lead `name` |
| `{{firma}}` | Firma des Leads | „Mustermann GmbH“ | CRM-Lead `company` |
| `{{termin}}` | Termin (Datum + Uhrzeit, Berlin) | „Do., 03.09.2026, 14:00 Uhr“ | Kalender-Event / Lead-Notiz |
| `{{meeting_link}}` | Meeting-/Videocall-Link | „https://meet.…“ | Kalender-Event (nicht im Query-String der Seite, D8) |
| `{{erkenntnisse}}` | Erkenntnisse aus Discovery | 1–3 kurze Sätze, konkret | Lead-Notiz nach Discovery (CLOSER) |
| `{{naechster_schritt}}` (optional) | Konkreter nächster Schritt | „Ich sende Ihnen das Angebot bis Freitag.“ | manuell / CRM-Kontext |
| `{{neuer_termin_vorschlag}}` (optional) | Neuer Terminvorschlag nach No-Show | „Do., 10.09.2026, 09:30 Uhr“ | Kalender / manuell |
| `{{kalender_link}}` (optional, T0) | Kalender-Einladung/ICS-Link | URL | n8n-Kalender-Node |

Hinweis Datenmodell: Das CRM-Lead-Modell führt aktuell keine Spalten für
`meeting_at`/`meeting_link`. Termin-Daten kommen aus dem Kalender-Event bzw. aus der
Lead-Notiz. Für den automatisierten Platzhalter-Fill in T-24h/T+1d sollte das CRM
(z. B. Notiz-Konvention `Termin: <ISO> | Link: <url>` oder spätere Spalten) die Werte
führen — Umsetzung ist nicht Teil dieser Task.

## 4. T0 — Bestätigungs-Mail (n8n, sofort)

### 4.1 Stil-Prompt für die n8n-KI-Mail (als Konstante im Workflow)

Ersetzt den `systemPrompt` im Node „KI-Prompt bauen“ (n8n-Workflow
`n8n-workflow-terminbuchung.json`). Betreff setzt weiterhin der Gmail-Node:
`Terminanfrage Skalantech: {{name}}` (unverändert lassen).

```
Du bist der persönliche Assistent von Xavier Escalante, Inhaber von Skalantech
(IT, Automatisierung und KI für Unternehmen, Köln). Du beantwortest Terminanfragen,
die über die Website skalantech.store eingehen.

STIL-REGELN (unbedingt einhalten):
- Schreibe auf Deutsch, natürlich und direkt.
- KEINE KI-Floskeln: kein „Ich hoffe, diese Nachricht erreicht Sie gut“, kein
  „Gerne stehe ich für Fragen zur Verfügung“, kein „Zögern Sie nicht“, kein
  „In der heutigen digitalen Welt“.
- Kein Pathos, keine Übertreibungen, keine Marketing-Sprache.
- Kurze, klare Sätze. Professionell, persönlich, warm.
- Keine Füllwörter am Satzanfang („gerne“, „sehr gerne“, „natürlich“).
- Antworte NUR mit dem E-Mail-Text als einfaches HTML mit <p>-Absätzen.
  Keine Betreffzeile, keine Signatur (Signatur + Betreff setzt der Workflow separat).

INHALT (Pflicht, in dieser Reihenfolge):
1. Terminbestätigung mit Datum und Uhrzeit (aus der Anfrage).
2. Ein Satz zur Kalender-Einladung: „Die Kalendereinladung kommt separat per E-Mail.“
3. GENAU EIN Satz Vorbereitung — konkret, unaufdringlich. Festwert:
   „Bringen Sie gern ein Beispiel aus Ihrem Alltag mit — daran zeigen wir,
   was sich bei Ihnen konkret automatisieren lässt.“
4. Nichts weiter. Keine Links außer dem übergebenen Kalender-Link, keine Anhänge.
```

### 4.2 Fallback-Text (Node „KI-Mail extrahieren“, wenn Ollama nichts liefert)

```
<p>Hallo {{name}},</p>
<p>Ihre Terminanfrage ist eingegangen. Ihr Wunschtermin: <strong>{{termin}}</strong>
(30 Minuten, online).</p>
<p>Die Kalendereinladung kommt separat per E-Mail.</p>
<p>Bringen Sie gern ein Beispiel aus Ihrem Alltag mit — daran zeigen wir,
was sich bei Ihnen konkret automatisieren lässt.</p>
<p>Xavier Escalante<br>Skalantech, Köln</p>
```

## 5. T-24h — Erinnerung (intern Telegram)

### 5.1 Interner Alarmtext (was im Kanal ankommt)

```
<b>T-24h · Terminerinnerung fällig</b>

{{name}} · {{firma}}
Termin: {{termin}}
Meeting-Link: {{meeting_link}}

→ Erinnerung an den Kunden senden. Kanal intern bis Freigabe.
```

### 5.2 Kunden-Text (nach Freigabe 1:1 versendbar)

```
Hallo {{name}},

kurze Erinnerung: Unser Gespräch ist am {{termin}} (online).

Meeting-Link: {{meeting_link}}

Falls die Zeit nicht mehr passt: Einfach auf diese Nachricht antworten,
wir verschieben.

Xavier Escalante · Skalantech
```

## 6. T+1d — No-Show-Nachfass (intern Telegram)

### 6.1 Interner Alarmtext

```
<b>T+1d · No-Show</b>

{{name}} · {{firma}}
Verpasster Termin: {{termin}}

→ Kalender prüfen, neuen Terminvorschlag nennen und Lead als „qualified“ halten.
Kanal intern bis Freigabe.
```

### 6.2 Kunden-Text (nach Freigabe 1:1 versendbar)

```
Hallo {{name}},

Sie haben den Termin am {{termin}} verpasst. Kein Problem — das passiert.

Neuer Vorschlag: {{neuer_termin_vorschlag}}

Passt Ihnen diese Zeit? Einfach kurz antworten, dann ist der Slot fix.

Xavier Escalante · Skalantech
```

## 7. T+7d — Discovery-Nachfass (intern Telegram)

### 7.1 Interner Alarmtext

```
<b>T+7d · Discovery-Nachfass</b>

{{name}} · {{firma}}
Discovery: {{termin}}

Erkenntnisse:
{{erkenntnisse}}

→ Nächsten Schritt im CRM eintragen (Proposal vorbereiten). Kanal intern bis Freigabe.
```

### 7.2 Kunden-Text (nach Freigabe 1:1 versendbar)

```
Hallo {{name}},

kurz zusammengefasst, was wir am {{termin}} besprochen haben:

{{erkenntnisse}}

Nächster Schritt: {{naechster_schritt}}

Xavier Escalante · Skalantech
```

Beispiel `{{erkenntnisse}}` (value-basiert, keine Technik):

```
- Ihre Angebots-Erstellung bindet aktuell ca. zwei Tage pro Woche.
- Mit Automatisierung sinkt der Aufwand auf unter zwei Stunden — bei gleicher Qualität.
- Das spart Ihnen grob 1.500 € pro Monat an eingesetzter Zeit.
```

## 8. Integration (Poller / Cron / CRM)

- **T0:** n8n-Workflow (Node „KI-Prompt bauen“ → Ollama lfm25 → Gmail). Stil-Prompt aus §4.1
  als Konstante eintragen (NEXUS verdrahtet).
- **T-24h / T+1d / T+7d:** über `next_followup_at` im CRM steuern
  (`PATCH /api/crm/leads/<id>` mit `{ "next_followup_at": "<ISO>" }`).
  Zeitpunkte setzen:
  - T-24h: Termin − 24 h
  - T+1d: Termin + 1 Tag
  - T+7d: Discovery-Datum + 7 Tage
- **Poller:** `scripts/crm_followup.py` (Hermes-Cron `e43e2738d866`, täglich 08:00 UTC,
  no_agent) ruft `GET /api/crm/leads?due_followup=1` und alarmiert intern per Telegram.
  Die internen Alarmtexte (§5.1/§6.1/§7.1) sind die Zielform für fällige Leads; die
  Kunden-Texte (§5.2/§6.2/§7.2) werden erst nach Freigabe versendet.
- **Status-Logik:** Nach T+1d-Kontakt → Lead auf `qualified`; nach T+7d-Nachfass →
  `proposal` vorbereiten. Terminale Leads (won/lost) fallen automatisch aus dem
  Follow-up-Filter.

## 9. Definition of Done (diese Task)

- [x] Alle 4 Bausteine formuliert (T0, T-24h, T+1d, T+7d)
- [x] Platzhalter dokumentiert (§3)
- [x] T0-Stil-Prompt für n8n bereit (§4.1, als Konstanten nutzbar)
- [x] Datei im Repo: `docs/followup-texte.md` (Commit + Push, master)
- [x] Kein Kunden-Versand aktiviert — Versandkanal bleibt intern bis Freigabe

## 10. Anhang: service-Label-Mapping (C15, PULSE)

Damit CRM-Pipeline und Follow-up-Texte dieselbe Sprache sprechen wie die Website
(Customer-First: „Potenzial-Check“ statt „Business-Analyse“/„Erstgespräch“), gilt
seit C15 (t_5d32a4a3) ein kanonisches service-Label. Die Kanonisierung passiert
serverseitig beim Formular-POST (`SERVICE_LABEL_MAP` in `app/models.py`, angewendet
in `public.contact()` und `crm_api.reserve_booking()`):

| Eingang (Formular/API/CRM-Historie) | Kanonisches Label |
|---|---|
| `Business-Analyse` | `Potenzial-Check` |
| `Erstgespräch` | `Potenzial-Check` |

Konsequenzen für Follow-ups:

- Leads aus dem Buchungs-Funnel (30-Minuten-Potenzial-Check) führen `service`/`topic`
  = „Potenzial-Check“ — T0–T7-Texte dürfen den Begriff „Potenzial-Check“ verwenden.
- Alt-Leads mit „Business-Analyse“/„Erstgespräch“ im CRM sind identisch zu behandeln
  (Mapping beim Reporting, keine separate Behandlung nötig).
- Referenz: `docs/ANALYTICS_EVENTS.md` §0 (Analytics-Taxonomie).
