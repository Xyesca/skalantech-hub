# LUMINA UX-Freigabe: /wissen 5-Säulen (Issue #16)

**Datum:** 2026-08-29 · **Prüfer:** LUMINA (UX/UI & Conversion) · **Referenz:** Issue #16
**Geprüfter Stand:** Branch `feat/issue16-wissen-saeulen` — Basis `f1eab5b` (Merge PR #14)

---

## Ergebnis

**Freigabe 'UX ✓'** — /wissen ist in 5 Content-Säulen strukturiert, Technik ist nicht mehr der
erste Einstieg, jeder Artikel hat einen klaren nächsten Schritt, Mobile/Desktop-UX verifiziert.

Umsetzung (6 Dateien + 4 Verifikations-Skripte):
- `app/wissen.py` — `PILLARS` (5 Säulen, Reihenfolge verbindlich) + `next_step` je Artikel
- `app/blueprints/public.py` — `pillars=PILLARS` an /wissen übergeben
- `app/templates/wissen.html` — Säulen-Layout mit Artikel-/Branchen-/Aktions-Karten
- `app/templates/article.html` — Nächster-Schritt-Block als primärer CTA (Termin = sekundär)
- `app/templates/partials/wissen_next_step.html` — URL-Makro (Demo/Prozess/Branche/Potenzial)
- `app/static/css/style.css` — Säulen-Header, Step-Zeile, Aktions-Karten, responsive (MOS-Akzent)
- `scripts/verify_issue16_wissen.py` · `scripts/lumina_ux_check_issue16.py` ·
  `scripts/lumina_console_check_issue16.py` · `scripts/lumina_a11y_check_issue16.py`

---

## 1) 5 Content-Säulen (verbindliche Reihenfolge)

Per Headless-Chromium-CDP über 4 Viewports verifiziert (DOM-Reihenfolge):

| # | Säule | Artikel / Karten | Status |
|---|---|---|---|
| 1 | Praxis & Prozesse | welche-prozesse-ki-automatisierung · rag-wissensassistenten + Karte „Automationen im Überblick“ → /automationen | ✓ |
| 2 | Branchen | 4 Branchenkarten → /branchen/handwerk, /kfz, /kanzleien, /immobilien | ✓ |
| 3 | Datenschutz & Kontrolle | lokale-ki-vs-cloud-ki · n8n-selbst-hosten | ✓ |
| 4 | Kosten & Entscheidung | kosten-roi-ki-automatisierung · n8n-vs-power-automate + Karte „Potenzial-Check“ → /rechner | ✓ |
| 5 | Technik erklärt | was-ist-ein-ki-agent (letzte Säule, NICHT erster Einstieg) | ✓ |

Technik-Stand letzte Position: `technik-erklaert` ist die letzte `.wissen-pillar`-Section im DOM (verifiziert).

## 2) Nächster Schritt je Artikel

Jeder Artikel endet mit genau einem primären CTA („Nächster Schritt“), Ziel-URLs antworten 200:

| Artikel | nächster Schritt | Typ |
|---|---|---|
| was-ist-ein-ki-agent | /ki-agenten („KI-Agenten im Überblick“) | Prozessseite |
| n8n-selbst-hosten | /n8n-automatisierung | Prozessseite |
| lokale-ki-vs-cloud-ki | /lokale-ki | Prozessseite |
| n8n-vs-power-automate | /rechner („Potenzial-Check starten“) | Potenzial-Check |
| welche-prozesse-ki-automatisierung | /rechner | Potenzial-Check |
| rag-wissensassistenten | /ki-agenten | Prozessseite |
| kosten-roi-ki-automatisierung | /rechner | Potenzial-Check |

Artikel-CTA-Hierarchie: Nächster Schritt (accent) → Termin vereinbaren (quiet, sekundär) →
Service-/Branchenseite (quiet). Auf /wissen zeigt jede Artikelkarte die Step-Zeile
„Nächster Schritt → Ziel“.

## 3) Mobile/Desktop-UX (Headless-Chromium-CDP, 4 Viewports)

| Viewport | /wissen Grid | next-step Zeilen | Overflow-X | CTA-Höhe |
|---|---|---|---|---|
| 1440×1000 | 3 Spalten | 7 | nein | 52 px |
| 768×1024 | 2 Spalten | 7 | nein | 52 px |
| 390×844 | 1 Spalte | 7 | nein | 52 px |
| 360×740 | 1 Spalte | 7 | nein | 52 px |

Zusätzlich: JS-/Console-Check ohne Fehler auf /wissen + allen 7 Artikeln; A11y-Stichprobe
(1×h1, aria-labelledby je Säule, keine Icon-only-Links) bestanden. Touch-Ziele ≥ 44 px.
Mobile: Säulen-Header stapeln (Nummern-Pill + Titel), Buttons full-width.

## 4) Regression

`python -m unittest discover` — 151 Tests, alle grün (inkl. /wissen-Render-Tests, Article-Schema).

## 5) Hinweise

- `ARTICLE_ORDER` bleibt für Sitemap/Backend unverändert; die Anzeige-Reihenfolge kommt aus `PILLARS`.
- Branchen-Säule enthält noch keine eigenen Artikel — Karten verlinken auf die bestehenden
  Branchen-Landingpages; neue Artikel können später per `PILLARS`-Eintrag ergänzt werden.
- Deployment: PR `feat/issue16-wissen-saeulen` nach Merge deployen (gunicorn-Restart).
