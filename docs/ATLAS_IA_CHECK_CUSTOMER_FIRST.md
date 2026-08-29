# ATLAS IA-Check: Customer-First Website (PR #12 Proposal)

**Datum:** 2026-08-28 · **Prüfer:** ATLAS (Growth/SEO) · **Referenz:** `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md` (Branch `proposal/customer-first-website-restructure`)
**Geprüfter Stand:** Branch `feat/customer-first-website` (Basis `master` @ a8237d2, VOR Proposal-Merge)

---

## Ergebnis

**Freigabe 'Strategy ✓' mit Fix-Liste** — nicht bedingungslos.

Die Grundausrichtung des Proposals (Kundenproblem → Ergebnis → Lösungsweg → Nachweis → niedrige Einstiegshürde) ist kundenlogisch korrekt, SEO-kompatibel und passt zum bestehenden Skeleton. Die aktuelle Homepage folgt der Ziel-Reihenfolge bereits zu ~70 % (Hero → Wiedererkennung → Lösungen → Demos → Vorgehen → Nachweise → Über → FAQ → Buchung → Projektanfrage). Es fehlen aber zwei Blöcke, eine Section ist falsch platziert, ein Bereich ist doppelt, und die Kundenlogik wird an mehreren Stellen durch Tool-Sprache verletzt.

**Verstoß-Schwere:** 1× kritisch (Kundenlogik Hero), 3× hoch (Signal-Bar, Demos-Sprache, About-Tool-Liste), Rest mittel/strukturell.

---

## 1. Struktur-Abgleich: Proposal-Reihenfolge vs. Ist

| # | Proposal | Ist (index.html) | Status |
|---|---|---|---|
| 1 | Hero: konkreter Geschäftsnutzen | Hero `#top` | ⚠ Position ✓, Copy/Visual verletzt Kundenlogik (F8/F9) |
| 2 | Wiedererkennung: Zeit-/Reibungsverluste | Use-Cases `#use-cases` | ✓ passt („Nicht KI einführen. Einen Engpass entfernen.“) |
| 3 | Lösungen als Ergebnisse | Services/Leistungen `#services` | ⚠ Position ✓, Copy Tool-lastig (F11) |
| 4 | Branchenbeispiele | — **fehlt** | ✗ F1 |
| 5 | direkt testbare Live-Beispiele | Demos `#demos` | ⚠ Position ✓, Copy = alte Technik-Sprache (F10) |
| 6 | ROI-Rechner als unterstützendes Werkzeug | ROI `#rechner` | ✗ Position falsch: aktuell nach Use-Cases, Ziel nach Demos (F2) |
| 7 | Vorgehen mit kleinem, risikoarmen Einstieg | Process `#process` | ✓ passt (CTA-Rename F13) |
| 8 | gebaute Lösungen / Nachweise | `#work` (Eigene Systeme) + `#nachweise` | ✗ doppelt, Proposal will EINE Section (F3) |
| 9 | Über Skalantech: Prinzipien statt Tool-Liste | About `#about` | ⚠ Reihenfolge falsch (kommt vor Nachweise), Tool-Liste (F4/F12) |
| 10 | Geschäftsführung & technische Leitung | — **fehlt** | ✗ F5 |
| 11 | FAQ | FAQ `#faq` | ✓ passt (Titel-Rename F13) |
| 12 | Potenzial-Check | Booking `#termin` | ⚠ „Business-Analyse“-Wording (F13) |
| 13 | konkrete Projektanfrage | Contact `#contact` | ✓ passt |

**Zusätzlich im Ist, aber laut Proposal zu entfernen:**
- Signal-Bar „Live-Stack: n8n · Python · Docker · Tailscale · Caddy · LLMs“ (Proposal-Removal-Liste: „Live-Stack als Signal-Bar“, „dominante Tool-Listen“) → F6

---

## 2. Kundenlogik-Validierung (Tool-Sprache als Hauptnutzen)

**Kritisch — Hero (F8/F9):**
- Lead (Z.47–49): „…verbindet E-Mails, Formulare, CRM, Dokumente, Websites und interne Systeme **mit n8n, APIs und KI**“ → n8n im Primärnutzen, Verstoß gegen „keine n8n/Docker/Python-Sprache als Hauptnutzen“.
- Hero-Visual (Z.70–88): System-Diagramm mit Core-Label „n8n · APIs“, Badge „KI-Agenten“, aria-label mit n8n → Tool-Diagramm statt Nutzen-Darstellung.
- Trust-Items (Z.63–67) weichen von der verbindlichen Trust-Copy des Proposals ab.
- Meta-Description (Z.4): „…mit n8n, KI, APIs und Self-Hosting“ → für SERP-Snippet benefit-first umformulieren, Keywords (Automatisierung, KI, KMU) beibehalten (SEO-Note, low priority).

**Hoch — Signal-Bar (F6):**
- Z.99: Live-Stack-Aufzählung = genau die „dominante Tool-Liste“, die das Proposal entfernt. Zahlen (3 Demos / 6+ Systeme / 100 % eigene Server) sind nur kundenorientiert neu aufsetzbar, nicht als Tool-Bar.

**Hoch — Demos-Section (F10):**
- Z.163: „Drei **n8n-Workflows** zeigen typische Muster. Die Demos laufen hinter der Website; die **n8n-Instanz** selbst bleibt intern geschützt.“ → Technik vor Kundennutzen, widerspricht Issue-#10-Endkundensprache.
- Karten: InvoiceFlow „Rechnungstext wird in Felder zerlegt…“, OfferAI „…strukturierten Entwurf…“ → „strukturiert“ ist exakt das Wort, das Issue #10 aus den Demos entfernt hat.

**Hoch — About (F12):**
- Z.232 expertise-list: „Linux & Docker · Microsoft 365 / Azure · n8n · Python / PowerShell · APIs & Webhooks · AI Agents & RAG · Self-Hosting“ → Tool-Liste statt Prinzipien; Proposal liefert verbindliche Prinzipien-Copy.

**Mittel — Services (F11):**
- Z.151 „n8n-Workflows, APIs, Webhooks…“, Z.154 „Linux, Docker, Cloud/Hybrid…“ → als „Leistungen“-Beschreibung Tool-lastig; Proposal will „Lösungen als Ergebnisse“.

**Erlaubt (bleibt):**
- Technologie-Zeilen in den Nachweis-Karten (Z.247/255/263/271/…) — Technik beantwortet „Wie?“, ist im Nachweis-Kontext vertrauensbildend. Format aber auf Ausgangslage/Gebaut/Nutzen umstellen, Technologie sekundär (F14).
- Tech-Kontext-Zeile in der neuen Geschäftsführungs-Section (Proposal erlaubt n8n · Python · M365/Azure · APIs · selbst gehostete KI NUR dort) (F5).

---

## 3. Abgrenzung Issue #10 (Demos-Sprache)

- `/demos` (Branch `feat/demo-spec-issue10`, gemergt in master @ a8237d2) spricht bereits Endkundensprache: „Sehen Sie, was im Arbeitsalltag automatisch vorbereitet werden kann“, „echte KMU-Abläufe“, „vollständig fiktiv“, Branchen-Buttons, „Was passiert danach?“, Ergebnisstatus statt „Strukturiert“, kein Preis, Safety für Gesundheitswesen. ✓
- **Homepage-Demo-Section nutzt noch die ALT-Sprache** (s. o., F10) → einziger Konfliktpunkt. Kein fachlicher Konflikt, nur Angleichung nötig.
- Empfehlung: Homepage-Karten-Copy 1:1 aus den DEMOS-Daten (`automation_showcase.py` / `demos.html`) übernehmen — eine Quelle der Wahrheit, kein zweiter Copy-Stand.
- Hero-Sekundär-CTA „Live-Demos testen“ → Proposal „Live-Beispiele ansehen“ (F8). Nav-Item „Live-Demos“ passt zum Proposal.

---

## 4. Navigation (base.html, Z.86–100)

| Aktuell | Proposal | Maßnahme |
|---|---|---|
| Automationen, Websites & Apps, Rechner, Leistungen, Projekte, Über Skalantech | Lösungen · Branchen · Live-Demos · Projekte · Über uns | Hauptnav auf 5 Items straffen; „Branchen“ ergänzen; Rechner/technische LPs aus Hauptnav (Footer + SEO bleiben) — F7 |
| CTA „Business-Analyse buchen“ | CTA „Potenzial-Check buchen“ | F13 |

---

## 5. Fix-Liste (nach Agenten-Zuständigkeit)

### Struktur — LUMINA/NOVA
- **F1** Branchen-Sektion auf Homepage einfügen (nach Lösungen): 4 Karten Handwerk / Kfz-Werkstatt / Kanzleien & Steuerberatung / Immobilien, Links auf `/branchen/{handwerk,kfz,kanzleien,immobilien}` (existieren, Footer verlinkt bereits).
- **F2** ROI-Rechner von Position 4 (nach Use-Cases) nach Position 6 (nach Demos) verschieben.
- **F3** „Eigene Systeme“ (`#work`) + „Nachweise“ (`#nachweise`) zu EINER „Gebaute Lösungen“-Section konsolidieren: Skalantech Hub, InvoiceFlow, OfferAI, MailAgent im Format Ausgangslage/Gebaut/Nutzen. DeepDive, DebtPilot, Hermes Agent raus aus dem Homepage-Funnel → separate Projekt-/Technikseite.
- **F4** Reihenfolge: Nachweise (8) vor Über (9) — aktuell umgekehrt.
- **F5** Kleine Section „Geschäftsführung & technische Leitung“ nach Über: Name (Xavier Escalante Castellar), 1–2 Sätze, Tech-Kontext-Zeile NUR hier. Kein Lebenslauf, keine Zertifikate, kein Personenfoto als Sales-Element.
- **F6** Signal-Bar entfernen/ersetzen: Live-Stack-Tool-Liste raus; Zahlen nur kundenorientiert neu aufsetzen.
- **F7** Navigation: Hauptnav = Lösungen · Branchen · Live-Demos · Projekte · Über uns; ROI-Rechner + technische LPs aus Hauptnav.

### Copy — VELA
- **F8** Hero: verbindliche Copy übernehmen (Eyebrow, H1, Lead, Primär-CTA „Kostenlosen Potenzial-Check buchen“, Sekundär-CTA „Live-Beispiele ansehen“, 3 Trust-Items) — n8n aus dem Lead entfernen.
- **F9** Hero-Visual: Tool-Diagramm („n8n · APIs“-Core, KI-Agenten-Badge) durch ergebnisorientierte Darstellung ersetzen.
- **F10** Demos-Section: Issue-#10-Sprache übernehmen (kein „n8n-Workflows“, kein „n8n-Instanz intern geschützt“, kein „strukturiert“); Karten-Copy 1:1 aus DEMOS-Daten.
- **F11** Services → „Lösungen als Ergebnisse“: Tool-Namen aus Primärtexten (n8n-Workflows, Linux/Docker) durch Nutzenformulierung ersetzen.
- **F12** About: „Prinzipien statt Tool-Liste“ — verbindliche Copy (H2/Lead/Ergänzung/4 Prinzipien); expertise-list entfernen.
- **F13** Business-Analyse → Potenzial-Check überall: Hero-CTA, Process-CTA, FAQ-Titel „Vor der Business-Analyse“, Booking-Section, Nav-CTA, verstecktes Formularfeld `service="Business-Analyse"`.
- **F14** Nachweis-Karten: Format Ausgangslage/Gebaut/Nutzen; Technologie-Zeile sekundär.

### Analytics — PULSE
- **F15** `ANALYTICS_EVENTS.md`-Taxonomie + Formular-`service`-Label von „Business-Analyse“ auf „Potenzial-Check“ mappen oder bewusst kompatibel halten (Proposal-Vor-Merge-Punkt). Dabei bestehende Inkonsistenz bereinigen: Formular sendet `service="Business-Analyse"`, Taxonomie dokumentiert „Erstgespräch“.

### Tests — SENTINEL
- **F16** Copy-Asserts (`test_showcase.py`, `test_demo_spec.py`, Homepage-Tests) auf neue Copy aktualisieren; verbindliche Kerntexte als Regressionstests aufnehmen (Proposal-Vor-Merge-Punkt).

---

## 6. SEO-Bewertung (ATLAS)

- **Kein SEO-Verlust durch Proposal:** Ziel-H1 („Weniger manuelle Arbeit. Mehr Zeit für Kunden, Team und Wachstum.“) ist ebenso keyword-tragend wie der aktuelle H1; Nutzen-Sprache deckt Long-Tail-Intent („Prozesse automatisieren KMU“) besser ab als Tool-Sprache („n8n Agentur“) — passt zur Keyword-Datenbank (Automatisierung/KI/Prozesse > n8n-Retail).
- Branchen-Sektion (F1) stärkt interne Verlinkung zu den Branchen-LPs (Local-SEO-Kohärenz Köln/Handwerk/Kfz/…).
- Technische LPs (n8n-Automatisierung, KI-Agenten, IT-Infrastruktur) bleiben als SEO-Einstiegsseiten erhalten — nur aus der Hauptnav, nicht aus dem Index. ✓
- Meta-Description benefit-first umformulieren (SEO-Note zu F8).

---

## 7. Nicht im Scope

- `index.html` wird NICHT von ATLAS umgeschrieben — VELA macht Copy, LUMINA Struktur.
- Kein Merge/Deploy — Vor-Merge-Punkte (Tests, Mobile-Nav, E2E, CI) bleiben beim Skalantech-Team/Hermes.
