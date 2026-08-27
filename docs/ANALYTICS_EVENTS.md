# Analytics & Conversion Tracking — Event-Spezifikation (PULSE)

**Stand:** 2026-08-27 · **Verantwortlich:** PULSE (Analytics) · **Status:** implementiert + verifiziert (P0)

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
| `meeting_booked` | n8n-Terminwebhook bestätigt Buchung | **Server** (n8n-Response) | `{"day": "...", "time": "...", "service": "Erstgespräch"}` |
| `service_viewed` | Leistungs-Karte im Viewport (1×/Session) | Client (IntersectionObserver) | `{"label": "<Karten-Titel>"}` |
| `case_study_viewed` | Projekt-Karte im Viewport (1×/Session) | Client (IntersectionObserver) | `{"label": "<Projekt-Titel>"}` |
| `roi_calculated` | ROI-Rechner ausgelöst | Client (Widget-API, folgt) | z. B. `{"savings_hours": 8}` |
| `lead_created` | Kontaktanfrage erfolgreich gespeichert (Lead in CRM) | **Server** (Formular-POST) | `{"service": "<Anliegen>"}` |

**Wichtig:** `lead_created`, `demo_completed` und `meeting_booked` werden serverseitig beim
Formular-POST geschrieben (gekoppelt an den DB-Write). Sie gehen nie verloren, auch wenn der
Client kein JavaScript ausführt. Die übrigen Events kommen vom Client (UX-/Interaktions-Signale).

**Funnel-Definition (KPI-Basis):**
`page_view` → `demo_started` → `calendar_opened` → `demo_completed` → `meeting_booked`
sowie `page_view` → `contact_clicked`/`service_viewed` → `lead_created`.

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

- `tests/test_analytics.py` — Endpoint, Allowlist, Limits, CSRF-Exemption,
  serverseitige Conversion-Events inkl. Attribution, Template-Integration.
- Manueller Smoke-Test: Flask-Dev-Server, `curl`-POST auf `/analytics/event`, DB-Read-back;
  Browser-Load der Startseite → `page_view`-Beacon + CTA-Klick → `demo_started` in der DB.

## 6. Offene Punkte / Roadmap

- **ROI-Rechner-UI** fehlt noch (LUMINA/FORGE): Event-API ist bereit
  (`window.SkalantechAnalytics.track("roi_calculated", {...})`).
- **Dashboard** (Admin-Ansicht für analytics_events) folgt als eigener Task.
- **Bot-Filterung** im Reporting über `user_agent`.
- **Retention/Aufräumen:** Events wachsen — Archivierungs-Job ab ~50k Zeilen einplanen.

## 7. Datenschutz

Disclosure in `app/templates/legal/datenschutz.html` („Technische Bereitstellung & anonyme
Nutzungsauswertung“). Footer-Trust-Line („Keine externen Tracker“, „Keine Tracking-Cookies“)
bleibt wahr: First-Party-Endpoint, keine Cookies.
