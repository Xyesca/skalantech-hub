# Analytics & Conversion Tracking — Event-Spezifikation (PULSE)

**Stand:** 2026-08-28 · **Verantwortlich:** PULSE (Analytics) · **Status:** implementiert + verifiziert (P0) — Lead-Funnel-Erweiterung (booking_error/booking_confirmed) verifiziert (t_14c947e2); Rebrand-Review Issue #3 (t_debcb0eb): `case_study_click`/`demo_clicked` ergänzt, `service_viewed`-/`case_study_viewed`-Selektoren auf aktuelle Karten-Klassen erweitert (`.usecase-card`/`.pain-card`/`.project-card`); P1 `roi_calculated` für ROI-Rechner `/rechner` finalisiert + live verifiziert (t_28ab613d); Customer-First: Footer-CTA neu getrackt (demo_started/footer, t_345e37a3) und **C15 (t_5d32a4a3): service-Label kanonisch „Potenzial-Check“ — Alt-Labels „Business-Analyse“/„Erstgespräch“ werden serverseitig gemappt (§0), keine Breaking-Change an Event-Namen**

## 0. service-Label „Potenzial-Check“ — Kanonisierung & Kompatibilität (C15, t_5d32a4a3)

Die sichtbare CTA-Copy wurde im Rahmen des Customer-First-Relaunchs (Branch
`feat/customer-first-website`, Referenz `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md`)
von „Business-Analyse buchen“ auf „Potenzial-Check buchen“ umbenannt. Damit auch
Analytics-Events, CRM-Pipeline und Follow-up-Texte dieselbe Sprache sprechen, ist
**„Potenzial-Check“ das kanonische service-Label des Buchungs-Funnels**. Alt-Labels
werden serverseitig beim Formular-POST kanonisiert (CLOSER C15 / ATLAS F15):

| Eingang (Formular/API) | Kanonisches Label | Wo |
|---|---|---|
| `Business-Analyse` (Booking-Hidden-Field, alte Landingpages) | `Potenzial-Check` | `SERVICE_LABEL_MAP` in `app/models.py`, angewendet in `public.contact()` + `crm_api.reserve_booking()` |
| `Erstgespräch` (CRM-Historie, Alt-Formulare) | `Potenzial-Check` | dito |

**Konsequenzen für die Events** (eine Buchung, ein Label):
- `lead_created.props.service`, `demo_completed.props.service` und
  `meeting_booked.props.service` tragen nach der Kanonisierung denselben Wert
  („Potenzial-Check“) — vorher war die Kette inkonsistent (`Business-Analyse`
  → `Erstgespräch` → `Erstgespräch`).
- Das n8n-`topic` und `Booking.topic` verwenden ebenfalls das kanonische Label
  (`BOOKING_SERVICE_LABEL`), ebenso der Default in `crm_api` und `models.Booking`.
- Historische Daten behalten ihre alten Werte — für Reports gilt die Mapping-
  Tabelle oben („Potenzial-Check“ ≡ „Business-Analyse“ ≡ „Erstgespräch“/30-min-Check).

**Keine Breaking-Change:** Alle Event-Namen (`booking_confirmed`, `lead_created`,
`demo_*`, …) und die Props-Kontrakte bleiben unverändert — nur der service-Wert
ist vereinheitlicht. `demo_started` wird weiterhin über Klassen-/Href-Selektoren
gefeuert (`.header-cta`, `a[href='#termin']`), nicht über den sichtbaren Text;
die Labels (`header`/`hero`/`section`/`footer`) sind positionsbasiert.
Der Footer-CTA „Potenzial-Check“ (`base.html`, Kontakt-Spalte, `/#termin`) wird
als `demo_started` mit `label: "footer"` getrackt (t_345e37a3).

## 1. Architektur

First-Party, cookie-less, ohne externen Dienst:

```
Browser (analytics.js)
  │  sendBeacon / fetch (JSON, gleiche Origin)
  ▼
POST /analytics/event  (Blueprint app/blueprints/analytics.py, CSRF-exempt)
  │  Allowlist + Feld-Limits + Payload-Limit (8 KB) + Rate-Limit (120/min/IP)
  ▼
SQLite: analytics_events  (Modell AnalyticsEvent)
```

- **Keine Cookies** — Session-ID liegt nur in `sessionStorage` (Tab-Session, kein Cookie).
- **Keine IP-Speicherung** — es wird keine IP in die DB geschrieben.
- **Keine personenbezogenen Inhalte** — Name/E-Mail/Nachricht werden nie als Event gespeichert.
- **Kein externer Tracker** — die Events bleiben auf dem eigenen Server (skalantech.store).
- **User-Agent** wird serverseitig (nicht vom Client) erfasst → spätere Bot-Filterung in Dashboards.

## 2. Event-Taxonomie

| Event | Bedeutung | Quelle | props (Beispiele) |
|---|---|---|---|
| `page_view` | Seite geladen (Funnel-Nenner) | Client (on load) | — |
| `demo_started` | CTA „Potenzial-Check“ geklickt (Header/Hero/Sektion) | Client (click) | `{"label": "header"\|"hero"\|"section"\|"footer"}` |
| `demo_completed` | Termin-Anfrage erfolgreich abgeschickt (Formular ok) | **Server** (Formular-POST) | `{"service": "Potenzial-Check"}` |
| `contact_clicked` | Kontakt-CTA / mailto geklickt | Client (click) | `{"label": "mailto"\|"nav"\|"<Service>"}` |
| `calendar_opened` | Datumsauswahl im Buchungsformular geöffnet (1×/Session) | Client (focus/click `#booking-day`) | — |
| `meeting_booked` | n8n-Terminwebhook bestätigt Buchung (`success:true`) | **Server** (n8n-Response) | `{"day": "...", "time": "...", "service": "Potenzial-Check"}` |
| `booking_error` | n8n down/timeout oder ungültige Antwort — **nur** bei echter Störung, **nie** bei „Slot belegt“ (normaler Nutzerpfad) | **Server** (n8n-Fehlerklassifikation) | `{"reason": "unreachable"\|"invalid_response"}` |
| `booking_confirmed` | Bestätigungsansicht im `.booking-box` sichtbar (Erfolg oder queued) — 1×/Submit | Client (main.js `showBookingSuccess`) | `{"status": "confirmed"\|"queued"}` |
| `service_viewed` | Leistungs-Karte im Viewport (1×/Session) | Client (IntersectionObserver) | `{"label": "<Karten-Titel>"}` |
| `case_study_viewed` | Projekt-Karte im Viewport (1×/Session) — `.work-card` **und** `.project-card` (Nachweise, Issue #3) | Client (IntersectionObserver) | `{"label": "<Projekt-Titel>"}` |
| `case_study_click` | Klick auf Projekt-Link im Nachweise-Bereich (Issue #3, Studio-Rebrand) | Client (data-track) | `{"label": "DeepDive"}` |
| `demo_clicked` | Live-Demo geöffnet — Hero, Demo-Karten oder Projekt-Nachweis (Issue #3) | Client (data-track) | `{"label": "hero"\|"invoiceflow"\|"offerai"\|"mailagent"}` |
| `roi_calculated` | ROI-Rechner ausgelöst (P1-Widget `/rechner` + Homepage; Debounce 800 ms, Throttle 3 s, Session-Cap 20, **nicht** beim Seiten-Load) | Client (roi-rechner.js) | `{"process":"angebote","source":"rechner","minutes":30,"frequency":5,"error_share":10,"rate":55,"automation_share":70,"hours_per_week":2.75,"hours_per_year":129.25,"annual_cost":7100,"savings_hours":90,"savings_euro":5000,"action":"recalc"\|"cta"}` |
| `lead_created` | Kontaktanfrage erfolgreich gespeichert (Lead in CRM); `service` ist kanonisiert (Buchung → „Potenzial-Check“, §0) | **Server** (Formular-POST) | `{"service": "<Anliegen>"}` |
| `hero_cta_click` | Hero-Primär-CTA auf Landingpages (LUMINA-Spez) | Client (data-track) | `{"label": "hero"}` |
| `quickwin_cta_click` | Quick-Win-Karten-CTA Angebot/Termine (LUMINA-Spez) | Client (data-track) | `{"label": "quickwin-1\|quickwin-3"}` |
| `erechnung_cta_click` | E-Rechnung-CTA, Stufe 3 Dringlichkeit (LUMINA-Spez) | Client (data-track) | `{"label": "quickwin-2"\|"erechnung"}` |
| `faq_open` | FAQ-Accordion geöffnet (LUMINA-Spez) | Client (data-track auf `<summary>`) | `{"label": "faq-<n>"}` |
| `check_cta_click` | Stufe-0-CTA „5-Minuten-Check“ im FAQ-Fuß (LUMINA-Spez) | Client (data-track) | `{"label": "faq-check"}` |
| `form_start` | Erstes Input im Kontakt-/Buchungsformular (1×/Formular) | Client (input) | `{"form": "booking-form"\|"contact-form"}` |
| `form_submit` | Formular abgeschickt (Client-Signal; Conversions serverseitig) | Client (submit) | `{"form": "booking-form"\|"contact-form"}` |
| `roi_slider_start` | Erste Slider-Interaktion im ROI-Rechner (1×/Session) — **Legacy** (roi-calculator.js, Branchen-Landingpages) | Client (roi-calculator.js) | — |
| `roi_calculated` | Rechner-Ergebnis als Bucket — **Legacy** (roi-calculator.js, Branchen-Landingpages); namensgleich mit dem P1-Event, unterscheidbar an `props.bucket` (P1-Events haben `props.action`) | Client (roi-calculator.js) | `{"bucket": "h_lt_150"\|"h_150_400"\|"h_gt_400"}` |
| `roi_cta_click` | Personalisierter Ergebnis-CTA (Legacy-Widget) bzw. Angebots-Karten-CTA (`/websites-apps`) | Client (data-track) | `{"label": "<bucket>"\|"offer-<n>"}` |

**ROI-Kontext:** Das P1-Widget (`roi-rechner.js`, `/rechner` + Homepage) sendet `roi_calculated` mit der vollen Props-Liste — nur Zahlen/Slugs, keine personenbezogenen Daten; `source` = `rechner`\|`homepage`, `action` = `recalc`\|`cta`. Der P1-CTA baut `/?utm_source=organic&utm_medium=rechner&utm_campaign=roi-rechner&utm_content=<page\|homepage>#termin` (Query VOR Fragment, **kein** `roi_context`-Param). Das Legacy-Widget (`roi-calculator.js`, Branchen-Landingpages) sendet dagegen NUR den Bucket (`roi_calculated` mit `props.bucket`, `roi_cta_click`) und übergibt `roi_context` ans Buchungsformular (Server-Whitelist `{h_lt_150, h_150_400, h_gt_400}`, Lead-Message „ROI-Rechner: &lt;bucket&gt;“). **Quelle der Wahrheit bleiben serverseitige Conversions** (`form_submit`, `lead_created`); ROI-Events sind anonyme Dashboard-Signale, nicht an Leads gestitcht.

**Wichtig:** `lead_created`, `demo_completed`, `meeting_booked` und `booking_error` werden serverseitig beim
Formular-POST geschrieben (gekoppelt an den DB-Write). Sie gehen nie verloren, auch wenn der
Client kein JavaScript ausführt. Die übrigen Events kommen vom Client (UX-/Interaktions-Signale).

**Funnel-Definition (KPI-Basis, Lead-Funnel Demo → Termin):**
`page_view` → `demo_started` → `calendar_opened` → `form_submit` → `demo_completed` → `meeting_booked`
(in der DB zusätzlich `lead_created` zwischen `form_submit` und `demo_completed` — serverseitiger
Lead-Write, gehört zur Funnel-Wahrheit, nicht zur Conversion-Kette).
Nebenfunnel: `page_view` → `contact_clicked`/`service_viewed` → `lead_created`.
Fehlerpfad: `… → demo_completed` + `booking_error {reason: unreachable|invalid_response}` (n8n-Störung,
Lead bleibt gespeichert, `booking.status=queued`). „Slot belegt“ = `success:false`-Antwort, **kein**
`booking_error`-Event.

**ROI-Mikro-Funnel „gerechnet → gehandelt“ (P1-Rechner):**
`roi_calculated` → `roi_calculated {action:"cta"}` — Anteil der Rechner-Nutzer, die das Ergebnis
mit dem CTA weiterverfolgen. Nenner = alle P1-`roi_calculated`-Events (erkennbar an `props.action`;
Legacy-Bucket-Events aus `roi-calculator.js` haben kein `action`-Feld und zählen nicht mit).
SQLite-Snippet (Exec-Report):

```sql
-- „gerechnet → gehandelt“-Funnel (P1 ROI-Rechner, roi-rechner.js)
-- Nur P1-Events: props.action ist bei recalc/cta immer gesetzt,
-- Legacy (roi-calculator.js) sendet nur props.bucket → wird ausgefiltert.
SELECT
  COUNT(*) AS roi_calculated,
  SUM(CASE WHEN json_extract(props, '$.action') = 'cta' THEN 1 ELSE 0 END) AS roi_cta,
  ROUND(100.0
        * SUM(CASE WHEN json_extract(props, '$.action') = 'cta' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 1) AS cta_quote_pct
FROM analytics_events
WHERE event = 'roi_calculated'
  AND json_extract(props, '$.action') IS NOT NULL
  AND created_at >= datetime('now', '-7 days');
```

Zusatz-KPI: Durchschnitt `savings_euro` (nur aggregiert auswerten — Events sind anonym und nicht
an Leads gestitcht; hohe Werte = Qualifizierungs-Signal für Potenzial-Checks).

## 3. Attribution & Funnel-Stitching

- `analytics.js` erfasst beim **ersten Seitenaufruf der Session** (First-Touch):
  `utm_source`, `utm_medium`, `utm_campaign` (URL), `referrer` (document.referrer),
  `landing` (Pfad) → `sessionStorage["skalantech:session"]`.
- Jedes Event trägt die `session_id` + Attribution.
- Beim Formular-Submit injiziert `analytics.js` die Werte als Hidden-Fields
  (`session_id`, `utm_source`, `utm_medium`, `utm_campaign`) → der Server speichert sie an
  `ContactMessage`/`Lead` (`session_id`-Spalten) und schreibt die Conversion-Events mit
  derselben `session_id`. Damit lassen sich Sessions über den ganzen Funnel stitchen.

## 4. Endpoint

`POST /analytics/event` — JSON (empfohlen, sendBeacon) oder form-encoded.

| Verhalten | Status |
|---|---|
| Gültiges Event | `204 No Content` |
| Unbekanntes Event | `204` (still verworfen — kein Client-Retry) |
| Kaputtes JSON / ungültige props | `400` |
| Payload > 8 KB / props > 2000 Zeichen | `413` |
| GET | `405` |
| Rate-Limit | `120/min/IP` (flask-limiter) |

CSRF-exempt (Beacon hat kein Session-Token); stattdessen Allowlist + Limits.

## 5. Verifikation

- `tests/test_analytics.py` — Endpoint, Allowlist (inkl. `booking_error`/`booking_confirmed`), Limits,
  CSRF-Exemption, serverseitige Conversion-Events inkl. Attribution, **Funnel-Kette**
  (`page_view → demo_started → calendar_opened → form_submit → lead_created → demo_completed
  → meeting_booked` in einer Session), `booking_error`-Pfade (unreachable/invalid_response),
  „Slot belegt“-Pfad (kein Event), Client-Kontrakt (analytics.js/main.js), Template-Integration.
- Live-Verifikation (2026-08-27, t_14c947e2): Flask-Test-Instanz mit Wegwerf-DB + Mock-n8n
  (lokaler HTTP-Server, `success:true`-Antwort) — Funnel-Kette per HTTP-POST durchgespielt,
  Events in `analytics_events` per SQL nachgewiesen; `booking_error`-Pfad (Mock antwortet
  nicht / 500) ebenfalls nachgewiesen. Testdaten danach aufgeräumt (DB gelöscht).
- Manueller Smoke-Test: Flask-Dev-Server, `curl`-POST auf `/analytics/event`, DB-Read-back;
  Browser-Load der Startseite → `page_view`-Beacon + CTA-Klick → `demo_started` in der DB.
- ROI-Rechner P1 (2026-08-28, t_28ab613d): `tests/test_analytics.py` deckt `roi_calculated`
  mit voller Props-Liste (action=recalc UND cta → 204 + DB-Read-back mit Zahlentyp-Check)
  und den roi-rechner.js-Props-Kontrakt ab. Live-Verifikation auf
  https://skalantech.store/rechner (Headless Chrome: Slider-Interaktion → recalc-Event,
  CTA-Klick → cta-Event), beide Zeilen in der Produktions-DB (`instance/app.db`,
  `analytics_events`) mit korrekten Props nachgewiesen; Test-Zeilen danach entfernt (P0-Muster).

## 6. Offene Punkte / Roadmap

- **Dashboard** (Admin-Ansicht für analytics_events) folgt als eigener Task.
- **Bot-Filterung** im Reporting über `user_agent`.
- **Retention/Aufräumen:** Events wachsen — Archivierungs-Job ab ~50k Zeilen einplanen.

## 7. Datenschutz

Disclosure in `app/templates/legal/datenschutz.html` („Technische Bereitstellung & anonyme
Nutzungsauswertung“). Footer-Trust-Line („Keine externen Tracker“, „Keine Tracking-Cookies“)
bleibt wahr: First-Party-Endpoint, keine Cookies.
