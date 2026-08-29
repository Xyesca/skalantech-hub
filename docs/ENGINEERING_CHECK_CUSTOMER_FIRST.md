# FORGE Engineering-Freigabe: Customer-First Website (PR #12)

**Datum:** 2026-08-28 · **Prüfer:** FORGE (Lead Web & Product Engineer) · **Referenz:** `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md` (Branch `proposal/customer-first-website-restructure`)
**Geprüfter Stand:** Branch `feat/customer-first-website` — HEAD `811c478` (inkl. FORGE-Commit `c492566`)

---

## Ergebnis

**Freigabe 'Engineering ✓'** — technische Umsetzung ohne Funktionsregression. Templates, Navigation, CSS und CTA-Analytics sind integriert; Buchung, Demos, ROI-Rechner und Analytics funktionieren nachweislich.

---

## Verifikation (maschinell, Exit 0)

### 1. Navigation vereinfacht (Proposal §Verbindliche Navigation)
- `app/templates/base.html`: Nav = **Lösungen · Branchen · Live-Demos · Projekte · Über uns** + Header-CTA „Potenzial-Check buchen“ (mit Kurzform „Potenzial-Check“)
- ROI-Rechner, SEO-Landingpages, /websites-apps bleiben über Footer erreichbar (keine gleichwertigen Hauptnav-Einträge mehr)
- Alle Navigations-Anker existieren: `#services`, `#branchen`, `#work`, `#about`, `#termin`, `#demos`, `#rechner`, `#faq`, `#contact`, `#process` — maschinell geprüft (Exit 0)

### 2. Templates integriert ohne Funktionsregression
- **Terminbuchung:** Booking-Hidden-Field sendet `service="Business-Analyse"`; `_SERVICE_CHOICES` um `Potenzial-Check` + Alt-Wert `Business-Analyse` + neue Contact-Optionen (Proposal) erweitert → **400-Fehler behoben** (vorher: „Bitte wählen Sie ein gültiges Anliegen aus“ bei jeder Buchung). POST mit `book_slot=1` → 200 + `booking.status=confirmed` (verifiziert)
- **Contact-Formular:** alle neuen Select-Optionen (Manuellen Prozess vereinfachen, Kundenanfragen & Angebote, Rechnungen & Dokumente, Systeme & Daten verbinden, Website / Business-Anwendung, Stabiler IT-Betrieb) akzeptiert (verifiziert, 200)
- **Demos:** `/demos` + `/automationen` — Endkundensprache „Live-Beispiel“ statt „Live-Workflow“ (ATLAS F10/F13, Demo-Issue #10); Demos funktional unverändert (CSRF-exempt showcase_bp, `/api/demos/<slug>` intakt)
- **ROI-Rechner:** Sektion verschoben (Homepage-Reihenfolge nach Proposal), Widget + `roi-rechner.js` unverändert, `roi_source="homepage"` intakt (PULSE-Verifikation)
- **Analytics:** Event-Allowlist unverändert; `demo_started`/`demo_clicked`/`hero_cta_click`/`check_cta_click` Hooks intakt

### 3. Keine toten Links
- Alle `url_for`-Endpoints in allen Templates aufgelöst (62 Endpoints, Exit 0)
- Alle statischen hrefs (26) geprüft: keine toten Routen
- Alle internen Anker (Nav + Footer) existieren in index.html/base.html

### 4. CSS konsistent
- Alle Klassen aus index.html + base.html in `style.css`/`showcase.css` vorhanden (usecase-grid/usecase-card in showcase.css; pain-card/project-card/section--credentials/credential-grid in style.css)
- LUMINA-CSS (`section--lead`, `section-heading--compact`, `project-card--quiet`) committet (7553bc0), Cache-Buster `?v=26`
- Kein horizontaler Overflow, mobile Nav (menu-toggle + site-nav) strukturell unverändert

### 5. CTA-Analytics: bewusst kompatibel gehalten (PULSE-Abstimmung)
- Entscheidung (PULSE t_345e37a3): **kein Event-Rename** — „Business-Analyse“ → „Potenzial-Check“ ist reine Copy; Analytics-Selektoren sind klassen-/href-basiert
- `demo_started` feuert über `.header-cta` + `a[href='#termin']` (Labels header/hero/section unverändert)
- Hidden-Field `service="Business-Analyse"` bleibt → Server-Kette `lead_created`/`demo_completed`/`meeting_booked` mit `props.service="Business-Analyse"` stabil (E2E per POST verifiziert)
- Footer-CTA „Potenzial-Check“ mit `data-track="demo_started" data-track-label="footer"` (Commit 1882389, nicht zurückgedreht)
- Doku: `docs/ANALYTICS_EVENTS.md` §0

---

## Geänderte Dateien (FORGE c492566)

- `app/blueprints/public.py` — `_SERVICE_CHOICES` erweitert (Potenzial-Check + Alt-Wert + neue Optionen), Default-CTA „Kostenlosen Potenzial-Check buchen“
- `app/seo_pages.py` — CTA-Texte Websites-&-Apps auf Potenzial-Check
- `app/branchen.py` — CTA + FAQ-Texte auf Potenzial-Check
- `app/templates/demos.html` — CTA + „Live-Beispiel“
- `app/templates/automationen.html` — CTA + „Live-Beispiel“
- `app/templates/local_koeln.html` — CTA + FAQ-Terminologie

## Tests

- **148 passed, 161 subtests passed** (komplette Suite `python -m pytest tests/ -q`)
- Inkl. SENTINEL-/PULSE-Regression-Guards (C13, CTA-Mapping, Demo-Hooks)

---

## Hinweise für Merge

- Footer-Hook aus 1882389 (`data-track="demo_started" data-track-label="footer"`) nicht zurückdrehen
- Cache-Buster bei künftigen CSS-Änderungen erhöhen (aktuell v26)
- Branch noch nicht gepusht (kein upstream) — Push beim PR-Erstellen
