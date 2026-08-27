# Analytics & Conversion Tracking — Event-Spezifikation (PULSE)

**Stand:** 2026-08-27 · **Verantwortlich:** PULSE (Analytics) · **Status:** implementiert + verifiziert (P0) — Lead-Funnel-Erweiterung (booking_error/booking_confirmed) verifiziert (t_14c947e2)

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
| `demo_started` | CTA „Erstgespräch“ geklickt (Header/Hero/Sektion) | Client (click) | `{"label": "header"\|"hero"\|"section"}` |
| `demo_completed` | Termin-Anfrage erfolgreich abgeschickt (Formular ok) | **Server** (Formular-POST) | `{"service": "Erstgespräch"}` |
| `contact_clicked` | Kontakt-CTA / mailto geklickt | Client (click) | `{"label": "mailto"\|"nav"\|"<Service>"}` |
| `calendar_opened` | Datumsauswahl im Buchungsformular geöffnet (1×/Session) | Client (focus/click `#booking-day`) | — |
| `meeting_booked` | n8n-Terminwebhook bestätigt Buchung (`success:true`) | **Server** (n8n-Response) | `{"day": "...", "time": "...", "service": "Erstgespräch"}` |
| `booking_error` | n8n down/timeout oder ungültige Antwort — **nur** bei echter Störung, **nie** bei „Slot belegt“ (normaler Nutzerpfad) | **Server** (n8n-Fehlerklassifikation) | `{"reason": "unreachable"\|"invalid_response"}` |
| `booking_confirmed` | Bestätigungsansicht im `.booking-box` sichtbar (Erfolg oder queued) — 1×/Submit | Client (main.js `showBookingSuccess`) | `{"status": "confirmed"\|"queued"}` |
| `service_viewed` | Leistungs-Karte im Viewport (1×/Session) | Client (IntersectionObserver) | `{"label": "<Karten-Titel>"}` |
| `case_study_viewed` | Projekt-Karte im Viewport (1×/Session) | Client (IntersectionObserver) | `{"label": "<Projekt-Titel>"}` |
| `roi_calculated` | ROI-Rechner ausgelöst | Client (Widget-API, folgt) | z. B. `{"savings_hours": 8}` |
| `lead_created` | Kontaktanfrage erfolgreich gespeichert (Lead in CRM) | **Server** (Formular-POST) | `{"service": "<Anliegen>"}` |
| `hero_cta_click` | Hero-Primär-CTA auf Landingpages (LUMINA-Spez) | Client (data-track) | `{"label": "hero"}` |
| `quickwin_cta_click` | Quick-Win-Karten-CTA Angebot/Termine (LUMINA-Spez) | Client (data-track) | `{"label": "quickwin-1\|quickwin-3"}` |
| `erechnung_cta_click` | E-Rechnung-CTA, Stufe 3 Dringlichkeit (LUMINA-Spez) | Client (data-track) | `{"label": "quickwin-2"\|"erechnung"}` |
| `faq_open` | FAQ-Accordion geöffnet (LUMINA-Spez) | Client (data-track auf `<summary>`) | `{"label": "faq-<n>"}` |
| `check_cta_click` | Stufe-0-CTA „5-Minuten-Check“ im FAQ-Fuß (LUMINA-Spez) | Client (data-track) | `{"label": "faq-check"}` |
| `form_start` | Erstes Input im Kontakt-/Buchungsformular (1×/Formular) | Client (input) | `{"form": "booking-form"\|"contact-form"}` |
| `form_submit` | Formular abgeschickt (Client-Signal; Conversions serverseitig) | Client (submit) | `{"form": "booking-form"\|"contact-form"}` |
| `roi_slider_start` | Erste Slider-Interaktion im ROI-Rechner (1×/Session) | Client (roi-calculator.js) | — |
| `roi_calculated` | Rechner-Ergebnis als Bucket (nie Rohwert, keine PII) | Client (roi-calculator.js) | `{"bucket": "h_lt_150"\|"h_150_400"\|"h_gt_400"}` |
| `roi_cta_click` | Personalisierter Ergebnis-CTA des ROI-Rechners | Client (data-track) | `{"label": "<bucket>"}` |

**ROI-Kontext (LUMINA-Spez):** Der Ergebnis-CTA übergibt nur den Bucket als `roi_context`-Query-Parameter ans Buchungsformular; serverseitig gegen feste Whitelist `{h_lt_150, h_150_400, h_gt_400}` validiert und als „ROI-Rechner: &lt;bucket&gt;“ in die Lead-Message übernommen. **Niemals** fließt der Rohwert (Stunden/€) in Tracking oder Lead — Client-Events (`roi_calculated`, `roi_cta_click`) sind reine Dashboard-Signale, Quelle der Wahrheit bleiben serverseitige Conversions (`form_submit`, `lead_created`).

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

## 6. Offene Punkte / Roadmap

- **Dashboard** (Admin-Ansicht für analytics_events) folgt als eigener Task.
- **Bot-Filterung** im Reporting über `user_agent`.
- **Retention/Aufräumen:** Events wachsen — Archivierungs-Job ab ~50k Zeilen einplanen.

## 7. Datenschutz

Disclosure in `app/templates/legal/datenschutz.html` („Technische Bereitstellung & anonyme
Nutzungsauswertung“). Footer-Trust-Line („Keine externen Tracker“, „Keine Tracking-Cookies“)
bleibt wahr: First-Party-Endpoint, keine Cookies.
