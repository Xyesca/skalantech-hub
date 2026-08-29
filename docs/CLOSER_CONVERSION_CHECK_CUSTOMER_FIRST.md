# CLOSER Conversion-Check: Weg Problem → Beweis → Potenzial-Check (Customer-First)

**Datum:** 2026-08-28 · **Prüfer:** CLOSER (B2B Sales & Conversion) · **Referenz:** `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md`
**Geprüfter Stand:** Branch `feat/customer-first-website` @ `ea99da9` (Proposal-Merge + ATLAS IA-Check eingespielt)
**Scope:** kompletter Verkaufsfluss (Homepage, Navigation, /demos, /automationen, /koeln, SEO-Landingpages, Branchen, ROI-Widget, Buchungsformular) — nicht nur die Homepage.

---

## Ergebnis

**Verdict: FIXES** — noch keine Freigabe „Conversion ✓“.

Der zentrale Homepage-Funnel erfüllt die Kundenlogik jetzt vollständig (Problem → Beweis → Potenzial-Check, CTA konsistent, Einstiegshürde 30 Min/kostenlos, keine Tool-Sprache im Hero). Aber der Verkaufsfluss ist **site-weit nicht konsistent**: /demos, /automationen, /koeln, SEO-Landingpages, Branchen-LPs und das ROI-Widget verwenden weiterhin „Business-Analyse“/„Erstgespräch“-CTAs und teils Technik-Sprache. Ein Lead, der über die Live-Demos kommt, verlässt den Kundenfluss in die alte Sprache.

---

## Kriterien-Check

### Kriterium 1 — Führt die Seite Kunden von Problem → Beweis (Demos/Projekte) → Potenzial-Check?

**Homepage: ✓ ERFÜLLT** — Reihenfolge entspricht Proposal Punkt 1–13:
Hero (Nutzen) → Typische Ausgangslagen (Problem, `#pain-points`) → Lösungen als Ergebnisse → Branchen (`#branchen`) → Live-Demos (Beweis, `#demos`) → ROI → Vorgehen (`#process`) → Gebaute Lösungen (Nachweise, `#work`) → Über → Geschäftsführung → FAQ → 30-Minuten-Potenzial-Check (`#termin`) → Projektanfrage (`#contact`).
Nachweis-Karten im Format Ausgangslage/Gebaut/Nutzen; DeepDive/DebtPilot/Hermes korrekt aus dem Funnel entfernt.

**Verkaufsfluss gesamt: ✗ NICHT durchgängig** — /demos (der Beweis-Schritt!) endet im Offer-Strip mit altem CTA (siehe Kriterium 2) und erklärt den „Sicherer Datenweg“ mit Flask/n8n (siehe Kriterium 4). Der Weg bricht auf der Demoseite aus der Kundensprache aus.

### Kriterium 2 — CTA konsistent „Kostenlosen Potenzial-Check buchen“

**Homepage: ✓** Hero exakt „Kostenlosen Potenzial-Check buchen“, Header/Nav „Potenzial-Check buchen“, Process „Potenzial-Check buchen“, Booking-Button „Potenzial-Check anfragen“, Footer „Potenzial-Check“.

**Rest: ✗ 8 Fundstellen mit Alt-Copy:**

| Datei | Zeile | Alt-CTA |
|---|---|---|
| `app/templates/demos.html` | 98 | „Kostenlose Business-Analyse“ |
| `app/templates/automationen.html` | 21 | „Kostenlose Business-Analyse“ |
| `app/templates/local_koeln.html` | 170 | „Kostenlose Business-Analyse“ |
| `app/seo_pages.py` | 314/316/418/420 | „Kostenlose Business-Analyse“, „Jetzt Business-Analyse buchen“, „Kostenlose Business-Analyse?“ |
| `app/branchen.py` | 177 | „Business-Analyse für Ihre Werkstatt“ |
| `app/seo_pages.py` | 477/478 | ROI-Widget „Kostenloses Erstgespräch“ (dritter CTA-Name!) |
| `app/blueprints/public.py` | 307 | Default `cta_primary` „Kostenlose Business-Analyse“ |
| `app/templates/index.html` | 301 | verstecktes Feld `service="Business-Analyse"` (geht an CRM/n8n/Follow-up) |

### Kriterium 3 — Einstiegshürde niedrig (30 Min, kostenlos)

**✓ ERFÜLLT** — Booking-Section „30-Minuten-Potenzial-Check“, „kostenlos & unverbindlich“, „ein konkreter Ablauf statt allgemeinem KI-Pitch“; FAQ „kostenlosen 30-minütigen Potenzial-Check“; Demos-Offer-Strip „In 30 Minuten prüfen wir…“. Semantik passt, nur das Label heißt teils noch „Business-Analyse“ (Kriterium 2).

### Kriterium 4 — Keine Tool-/Technik-Sprache im Verkaufsfluss

**Homepage: ✓** Hero-Lead ohne n8n, Signal-Bar ohne Live-Stack, Services als Ergebnisse, Technologie nur in der Geschäftsführungs-Section (Proposal-konform).

**Rest: ✗ 3 Fundstellen Technik-Sprache im Verkaufsfluss:**

| Datei | Zeile | Befund |
|---|---|---|
| `app/templates/demos.html` | 24–32 | „Sicherer Datenweg: Browser · Eingabe / Flask · Validierung + Rate-Limit / n8n intern · Workflow / Ergebnis · zurück im Browser“ — genau die technische Erklärung vor dem Kundennutzen, die Proposal entfernt |
| `app/templates/automationen.html` | 28–30 | „Trigger · Mail, Formular, Datei, API“ / „Verarbeiten · n8n, Python, KI“ |
| `app/templates/local_koeln.html` | 4/7/10/166/190/194 | n8n/Linux/Docker/Tailscale in Meta-Descriptions + Primärtext (SEO-LP, aber CTA/Sprache im Funnel) |

Hinweis: Technik-Listen auf reinen SEO-Spezialseiten (n8n-Automatisierung, KI-Agenten, IT-Infrastruktur) bleiben laut Proposal erlaubt — nicht Teil dieser Kritik.

---

## Fix-Liste (CLOSER, nach Agenten-Zuständigkeit)

### NOVA (Templates/Integration)
- **C1** `demos.html` Z.98: CTA → „Kostenlosen Potenzial-Check buchen“ (Link bleibt `#termin`).
- **C2** `demos.html` Z.24–32: „Sicherer Datenweg“-Box → Endkundensprache (z. B. „Ihre Eingabe wird verarbeitet und geprüft – ohne echte Kundendaten“); kein Flask/n8n/Rate-Limit.
- **C3** `demos.html` Z.50: Badge „Live-Workflow“ → „Live-Beispiel“ (konsistent zur Homepage).
- **C4** `automationen.html` Z.21: CTA → „Kostenlosen Potenzial-Check buchen“.
- **C5** `automationen.html` Z.28–30: Tech-Steps → Ergebnis-Sprache.
- **C6** `local_koeln.html` Z.170: CTA → „Kostenlosen Potenzial-Check buchen“; Meta-/Primärtexte Tool-Sprache reduzieren.
- **C7** `seo_pages.py` Z.314/316/418/420: alle Landingpage-CTAs → „Kostenlosen Potenzial-Check buchen“ / „Potenzial-Check buchen“.
- **C8** `seo_pages.py` Z.477/478: ROI-Widget-CTA „Kostenloses Erstgespräch“ → „Kostenlosen Potenzial-Check buchen“; Note-Text anpassen.
- **C9** `branchen.py` Z.177: CTA → „Kostenlosen Potenzial-Check buchen“.
- **C10** `public.py` Z.307: Default `cta_primary` → „Kostenlosen Potenzial-Check buchen“.
- **C11** `index.html` Z.301: verstecktes Feld `service="Business-Analyse"` → Entscheidung: auf „Potenzial-Check“ umstellen UND n8n/CRM/Follow-up-Mapping mitziehen, ODER bewusst kompatibel halten (Proposal-Vor-Merge-Punkt). Empfehlung CLOSER: umstellen + Mapping dokumentieren, damit CRM-Pipeline (P1) und Follow-up-Texte (T0–T7) dieselbe Sprache sprechen.

### SENTINEL (Tests/CI)
- **C12** Uncommittete Test-Updates (`test_public.py`, `test_websites_apps.py`, `test_analytics.py`) committen — CI ist auf committed Stand rot (alte Asserts „Kostenlose Business-Analyse“/„Business-Analyse buchen“).
- **C13** Regressionstests für die neuen verbindlichen Kerntexte („Kostenlosen Potenzial-Check buchen“, „30-Minuten-Potenzial-Check“) + Assert, dass „Business-Analyse“/„Erstgespräch“-CTAs im Funnel nicht zurückkehren.
- **C14** Nach C1–C11: Copy-Asserts für demos/automationen/landingpages aktualisieren.

### PULSE (Analytics)
- **C15** `ANALYTICS_EVENTS.md`-Taxonomie: `service`-Label „Business-Analyse“/„Erstgespräch“ → „Potenzial-Check“ mappen oder Kompatibilität dokumentieren (deckt sich mit ATLAS F15).

---

## Nicht im Scope

- Kein Merge/Deploy — Vor-Merge-Punkte (Mobile-Nav, E2E, CI grün) bleiben beim Skalantech-Team.
- SEO-Bewertung (ATLAS) und Struktur-Check sind in `docs/ATLAS_IA_CHECK_CUSTOMER_FIRST.md` dokumentiert — dieses Dokument ergänzt den Conversion-/Sales-Blickwinkel.
