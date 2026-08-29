# FORGE Engineering-Freigabe: Issue #16 — Templates/Routing (NOVA)

**Datum:** 2026-08-29 · **Prüfer:** FORGE (Lead Web & Product Engineer) · **Referenz:** Issue #16, ATLAS t_cc9ece66, VELA t_60d2d86f, CLOSER t_794e4e23, LUMINA t_ad27115a
**Geprüfter Stand:** Branch `feat/issue16-customer-first-consolidation` — HEAD siehe Git-Log (inkl. NOVA-Commit)

---

## Ergebnis

**Engineering-Freigabe 'Engineering ✓'** für den NOVA-Anteil von Issue #16 (Templates/Routing): Navigation umgestellt, Zielgruppen-Profile A–E auf der Homepage abgebildet, FAQ kundenorientiert (VELA-Copy integriert), Über-uns ohne Zertifikate verifiziert. Keine Funktionsregression: 153/153 Tests grün (Baseline 151 + 2 neue Issue-#16-Guards).

Hinweis zur Gesamt-DoD: Die /wissen-5-Säulen-Struktur liegt bei LUMINA (Branch `feat/issue16-wissen-saeulen`, t_ad27115a) und muss vor dem Merge in diesen Consolidation-Branch übernommen werden. Der /wissen-Route-Link in der Navigation ist hier bereits verdrahtet.

---

## Verifikation (maschinell, Exit 0)

### 1. Navigation umgestellt (ATLAS-Vorgabe, verbindliche Reihenfolge)
- `app/templates/base.html`: Hauptnav = **Lösungen · Für wen · Live-Demos · Wissen · Über uns** + Header-CTA „Potenzial-Check buchen“
- Reihenfolge maschinell geprüft (Test `test_issue16_nav_order_and_fuer_wen_profiles`): Positionen sortiert, „Branchen“/„Projekte“ nicht mehr im Hauptmenü
- Keine Regression: „Gebaute Lösungen“ (`#work`) als Footer-Link ergänzt, Branchen-Landingpages bleiben im Footer
- Alle Anker existieren: `#services`, `#fuer-wen`, `#demos`, `#work`, `#about`, `#termin` (Exit 0)

### 2. Zielgruppen-Profile A–E auf der Homepage (ATLAS)
- Sektion `#fuer-wen` (ersetzt `#branchen`): fünf Prozessprofile A–E statt Branchenliste
  - A) Viele Anfragen & Termine · B) Außendienst, Service & Flotte · C) Dokumenten- & wissensintensive Büros (mit Berufsgeheimnis-Hinweis: keine fachliche Entscheidung durch generische KI) · D) Handel, E-Commerce & Auftragsabwicklung · E) Projekt- & Vertriebsdienstleister
- Leitfrage „Welche Arbeit wiederholt sich bei Ihnen jede Woche?“ als H2 (CLOSER/ATLAS)
- CTA-Links: Live-Beispiele → `/demos`, Potenzial prüfen → `#termin`
- Wiederverwendung bestehender Klassen (`usecase-section`/`usecase-grid`/`usecase-card`/`about-links`) → kein neues CSS, Mobile-Verhalten unverändert (3/2-Spalten-Wrap, mobile 1-spaltig)

### 3. FAQ kundenorientiert (VELA-Copy, t_60d2d86f)
- `/faq` + Homepage-FAQ: 6 kundenorientierte Fragen (Eignung, Software-Ersatz, Datenverarbeitung, menschliche Kontrolle, Kosten, Zusammenarbeit) statt Technik-/Tool-Fragen
- Hosting-Sprache gemäß Vorgabe: „kontrollierbare Datenwege und flexible Betriebsmodelle – von europäischem Hosting bis zu lokalen KI-Komponenten“ (keine unbelegte „alles in Deutschland“-Behauptung)
- Kleine Konsistenz-Korrektur: Homepage-FAQ-Einleitung „Vier Fragen“ → „Die Fragen“ (6 Einträge)
- Regressions-Guard `test_issue16_faq_customer_oriented`: alte Technikfragen („Welche Technologien setzt du ein?“, „Arbeitest du remote?“) entfernt

### 4. Über-uns ohne Zertifikate
- `#about` = organisationsbezogen (Prinzipien statt Tool-Liste), `#geschaeftsfuehrung` kompakt (kein Lebenslauf, kein Portrait als Sales-Element, keine Zertifikatswand)
- Einziger „Zertifikat“-Fund ist die bewusste Copy „Statt Lebenslauf und Zertifikaten stehen konkrete Systeme im Vordergrund“ (gewollt, kein Regress)

### 5. Keine Funktionsregression (153/153 Tests)
- Terminbuchung: Hidden-Field `service="Potenzial-Check"`, Booking-Formular, CSRF, Slot-Pfad intakt
- Demos `/demos`, `/automationen`, Demo-APIs unverändert; ROI-Rechner (`/rechner`, Widget, `roi_calculated`) unverändert
- Analytics: Footer-CTA `data-track="demo_started"` intakt; keine Event-Allowlist-Änderung (PULSE-Anteil separat, t_1a33186c)
- Komplette Suite: `python -m unittest discover -v` → **Ran 153 tests, OK** (CI-Env: FLASK_ENV=development, SECRET_KEY, ADMIN_USERNAME/PASSWORD)
- Statische Assets, Sitemap, robots.txt unverändert

---

## Merge-Hinweise

- LUMINA-Branch `feat/issue16-wissen-saeulen` (t_ad27115a) für die /wissen-5-Säulen in den Consolidation-Branch mergen
- PULSE (t_1a33186c), CLOSER (t_794e4e23), SENTINEL (t_610bd6ce) laufen parallel; deren Freigaben nach Merge erneut mit Testsuite prüfen
- Vor Production-Deploy: Cache-Buster-CSS bei Bedarf erhöhen (aktuell `?v=26`, nur Templates geändert)
