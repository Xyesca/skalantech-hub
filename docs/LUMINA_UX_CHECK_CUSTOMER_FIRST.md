# LUMINA UX-Freigabe: Customer-First Website (PR #12)

**Datum:** 2026-08-28 · **Prüfer:** LUMINA (UX/UI & Conversion) · **Referenz:** `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md` (Branch `proposal/customer-first-website-restructure`)
**Geprüfter Stand:** Branch `feat/customer-first-website` — Commit `7553bc0` (LUMINA-Umsetzung) auf Proposal-Merge `89b1dfd` + VELA-Copy `b0ef114`

---

## Ergebnis

**Freigabe 'UX ✓'** — Struktur, visuelle Hierarchie, Mobile Navigation und Conversion Flow entsprechen dem Proposal.

Umsetzung (Commit `7553bc0`, 3 Dateien):
- `app/templates/index.html` — Geschäftsführungs-Sektion kompakt
- `app/static/css/style.css` — Kompakt-Stile + Projekt-Prominenz (49 Zeilen)
- `app/templates/base.html` — Cache-Buster `?v=26`

---

## 1) Neue Homepage-Reihenfolge (Proposal Punkt 1–13)

Per Headless-Chromium-CDP verifiziert — DOM-Reihenfolge `main > section`:

| # | Proposal | Sektion (live) | Status |
|---|---|---|---|
| 1 | Hero | `#top` „Weniger manuelle Arbeit…“ | ✓ |
| 2 | Wiedererkennung | `#pain-points` „Typische Ausgangslagen“ | ✓ |
| 3 | Lösungen als Ergebnisse | `#services` „Digitalisierung, die im Tagesgeschäft ankommt“ | ✓ |
| 4 | Branchenbeispiele | `#branchen` Handwerk/Arztpraxen/Kfz/Immobilien | ✓ |
| 5 | direkt testbare Live-Beispiele | `#demos` InvoiceFlow/OfferAI/MailAgent | ✓ |
| 6 | ROI-Rechner | `#rechner` ROI-Widget | ✓ |
| 7 | Vorgehen | `#process` „Mit einem klaren Problem starten“ | ✓ |
| 8 | gebaute Lösungen / Nachweise | `#work` „Gebaute Lösungen“ (4 Karten) | ✓ |
| 9 | Über Skalantech | `#about` | ✓ |
| 10 | Geschäftsführung KLEIN | `#geschaeftsfuehrung` | ✓ |
| 11 | FAQ | `#faq` | ✓ |
| 12 | Potenzial-Check | `#termin` 30-Minuten-Buchung | ✓ |
| 13 | Projektanfrage | `#contact` | ✓ |

## 2) Visuelle Hierarchie

### Geschäftsführung KLEIN (Proposal: „bewusst klein, kein Foto als zentrales Element“)
- Name jetzt **H3 statt H2** → Desktop-Font 33,6 px statt vorher 64,8 px (Mobile 24 px statt 46,8 px)
- Section-Padding reduziert auf 72 px (Standard 120 px) via `.section--lead`
- Karte ruhig via `.project-card--quiet` (kein Schatten, transparent)
- **Kein Foto, keine Biografie, keine Zertifikatswand** — `img`-Count in Sektion = 0
- Technischer Kontext (n8n/Python/M365) bleibt bewusst nur hier (Proposal-konform)

### Projekte / Gebaute Lösungen prominent
- Grid auf 2 Spalten umgestellt (`.credential-grid--projects`) → 4 Karten als sauberes 2×2-Raster statt 3+1-Orphan
- Karten bekommen Kontrast: `--paper`-Hintergrund auf weißer Section, **3 px Accent-Top-Border**, Hover-Lift + stärkerer Schatten
- Badges in Endkundensprache („Rechnungsverarbeitung“, „Angebotsvorbereitung“, „Postfach & Bearbeitung“)

## 3) Mobile Navigation — getestet (390 / 768 / 1440 px)

| Prüfpunkt | Ergebnis |
|---|---|
| Hamburger sichtbar ≤860 px (`display: block`) | ✓ |
| Klick öffnet Menü (`aria-expanded=true`, `.is-open`, `body.menu-open`) | ✓ |
| Nav-Links: Lösungen · Branchen · Live-Demos · Projekte · Über uns | ✓ 5 Links |
| Escape schließt Menü (Focus zurück auf Button) | ✓ |
| Link-Klick schließt Menü | ✓ (main.js) |
| Horizontales Overflow | 0 px auf allen 3 Viewports (auch bei offenem Menü) |
| Anker-Ziele (`#services #branchen #work #about #termin`) | alle vorhanden |
| Header-CTA: Desktop „Potenzial-Check buchen“, Mobile „Potenzial-Check“ | ✓ (`.header-cta__full`/`__short`-Swap) |
| Desktop-Nav (1440 px): horizontale Links, kein Hamburger | ✓ |

## 4) CTA-System: „Potenzial-Check buchen“ als Primäraktion

| Position | Text (live verifiziert) |
|---|---|
| Header | „Potenzial-Check buchen“ |
| Hero primär | „Kostenlosen Potenzial-Check buchen ↗“ |
| Vorgehen | „Potenzial-Check buchen ↗“ |
| Booking-Button | „Potenzial-Check anfragen“ |
| Footer | „Potenzial-Check“ |
| Sekundär (Hero) | „Live-Beispiele ansehen“ |

Kein „Business-Analyse“-CTA mehr in Homepage/Navigation/Footer. (Restliche Fundstellen in `/demos`, `/automationen`, SEO-LPs sind CLOSER C1–C11 → NOVA/FORGE-Scope.)

---

## Regression

- `pytest tests/` (ohne audit_live/audit_trust): **147 passed, 156 subtests** — grün
- Live-Render auf Dev-Instanz (Port 5051): `style.css?v=26`, `section-heading--compact`, Name „Xavier Escalante Castellar“ vorhanden

---

## Handoff

- **FORGE/NOVA:** CLOSER-Fixes C1–C11 (demos/automationen/SEO-LPs/`service`-Feld) liegen außerhalb des Homepage-Funnels und sind dort zu übernehmen.
- **PULSE:** Analytics-Nomenklatur „Business-Analyse“→„Potenzial-Check“ (CLOSER C15, VELA-Hinweis) — das versteckte `service`-Feld im Booking-Formular trägt weiterhin `Business-Analyse` (Backend-/n8n-Kompatibilität).
- **SENTINEL:** Regressionstests bereits auf neue Copy aktualisiert (Commit `2866017`) — läuft parallel.
