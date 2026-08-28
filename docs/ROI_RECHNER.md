# ROI-Rechner (P1) — Implementierungs-Notiz

Status: live (skalantech.store/rechner + Homepage-Sektion `#rechner`)
Task: t_59ece745 (FORGE) · Design/Struktur: t_ce7fda15 (LUMINA) · Copy: t_8a6f04a7 (VELA)

## Was gebaut wurde

| Datei | Änderung |
|---|---|
| `app/blueprints/public.py` | Route `GET /rechner` (`public.landing_rechner`), Sitemap-Eintrag `{"loc": "/rechner", "priority": "0.8"}`, `copy` an `index()` |
| `app/seo_pages.py` | `ROI_RECHNER_COPY` (61 Slots, VELA-Endfassung) + `ROI_RECHNER_FAQS` (6 Paare) |
| `app/templates/rechner.html` | Neue Seite: SEO-Meta, Service+Breadcrumb+FAQPage-Schema, Hero, Widget, „So funktioniert's“, FAQ, Abschluss-CTA |
| `app/templates/partials/roi_rechner_widget.html` | Widget-Markup (1× für /rechner + Homepage, kein Drift) |
| `app/templates/index.html` | `section--roi` (`id="rechner"`) nach Pain/usecase, vor `section--services` |
| `app/templates/base.html` | Nav-Link „Rechner“, Footer-Link „ROI-Rechner“, `roi-rechner.js?v=1`, Cache-Buster style.css v19→v20 |
| `app/static/js/roi-rechner.js` | Vanilla-Widget: Auto-Init `[data-roi-rechner]`, Formel exakt 03 §1, Events 03 §5 + 04 |
| `app/static/css/style.css` | Widget-Komponenten ans Ende (mobile-first, Breakpoints 900/680/400) |
| `tests/test_rechner.py` | 11 Tests (Route, Homepage, Sitemap, FAQ-Schema 1:1, CTA-UTM, JS-Serving, node --check, Nav/Footer, Formel-Defaults, Edge Cases, Regression) |
| `docs/ROI_RECHNER.md` | diese Notiz |

## Formel (03 §1, exakt)

```
gesamt_pro_woche_h = (min/60 × Häufigkeit) × (1 + Fehlerquote/100)
gesamt_pro_jahr_h  = gesamt_pro_woche_h × 47
Jahreskosten       = gesamt_pro_jahr_h × Stundensatz
Einsparung_h       = gesamt_pro_jahr_h × Automatisierungsgrad/100
Einsparung_€       = Einsparung_h × Stundensatz
```
Rundung: € auf 100 € (`Math.round(x/100)*100`, Kleinstwerte < 100 € exakt),
Stunden auf ganze Zahl, h/Woche 1 Dezimale, h/Jahr 2 Dezimalen.
Defaults (30 min · 5×/Woche · 10 % · 55 €/h · 70 %) → **7.100 €/Jahr · 5.000 € · 90 h** (verifiziert, 07_VERIFIKATION).

## Events (`roi_calculated`, Allowlist bereits vorhanden)

- `action:"recalc"`: Debounce 800 ms + Throttle max 1×/3 s, **nicht** beim Seiten-Load
- `action:"cta"`: einmalig beim CTA-Klick mit finalen Werten
- Session-Cap: max 20/Session (sessionStorage `skalantech:roi_count:<source>`)
- Props: process, source (`rechner`|`homepage`), minutes, frequency, error_share, rate,
  automation_share, hours_per_week, hours_per_year, annual_cost, savings_hours, savings_euro, action
- Guard: `if (window.SkalantechAnalytics && SkalantechAnalytics.track)` — Widget läuft ohne Tracker

CTA-URL: `/?utm_source=organic&utm_medium=rechner&utm_campaign=roi-rechner&utm_content=<page|homepage>#termin`
(Query VOR Fragment — UTM geht nicht verloren).

## Verifikation (vor Deploy, Headless-Chrome CDP)

- Initial /rechner: 7.100 € · 5.000 € · 90 h; Slider 30→60: 14.200 € · 10.000 € · 181 h ✓
- Genau 1 `roi_calculated` (recalc) nach Slider-Interaktion, 0 beim Load; 1× (cta) beim CTA-Klick ✓
- Homepage-Instanz `data-source="homepage"`: identisch, utm_content=homepage ✓
- Mobile 390 px: 1 Spalte, kein horizontaler Overflow, CTA sichtbar (50 px) ✓
- Desktop 1440 px: 2 Spalten, Ergebnis sticky (top 96 px), kein Overflow ✓
- Console: keine Fehler; node --check: OK; pytest: 116 passed (11 neue) ✓

## Deployment

- Branch `feat/roi-rechner` → Push auf `origin/master` (GitHub als Backup)
- `docker compose up -d --build skalantech` (aus dem Worktree, .env + instance via Symlink)
- Live-Check: `https://skalantech.store/rechner` HTTP 200, Homepage `#rechner`-Sektion

## Technische Schuld / Hinweise

- Das ältere Handwerk-Widget `roi-calculator.js` (Bucket-Tracking) bleibt unverändert
  und wird separat auf Branchen-Landingpages genutzt — nicht verwechseln.
- PULSE (t_28ab613d) verifiziert `roi_calculated` live in der Produktions-DB nach Deploy.
