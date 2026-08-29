# VELA Copy-Freigabe: Customer-First Website (PR #12)

**Datum:** 2026-08-28 · **Prüfer:** VELA (B2B Content & Communication) · **Referenz:** `docs/CUSTOMER_FIRST_WEBSITE_PROPOSAL.md` (Branch `proposal/customer-first-website-restructure`)
**Geprüfter Stand:** Branch `feat/customer-first-website` — Templates `app/templates/index.html` + `app/templates/base.html`

---

## Ergebnis

**Freigabe 'Copy ✓'** — die verbindlichen Texte aus dem Proposal sind 1:1 übernommen.

Die Copy folgt der Kundenlogik `Kundenproblem → gewünschtes Ergebnis → nachvollziehbarer Lösungsweg → sichtbarer Nachweis → niedrige Einstiegshürde` und nicht der alten Tool-first-Perspektive.

---

## Verifikation (maschinell, Exit 0)

Check-Skript: `scripts/vela_copy_check_pr12.py` (whitespace-tolerant, prüft verbindliche Texte + Removal-Liste)

### Verbindliche Blöcke — alle vorhanden

| Bereich | Status |
|---|---|
| Hero-Eyebrow „Digitale Prozesse für kleine und mittelständische Unternehmen“ | ✓ |
| Hero-H1 „Weniger manuelle Arbeit. Mehr Zeit für Kunden, Team und Wachstum.“ | ✓ |
| Hero-Lead (verbindlicher Wortlaut) | ✓ |
| Hero-Primär-CTA „Kostenlosen Potenzial-Check buchen“ | ✓ |
| Hero-Sekundär-CTA „Live-Beispiele ansehen“ | ✓ |
| Hero-Trust (3 Punkte: bestehende Systeme, klar abgegrenzter Prozess, nachvollziehbar dokumentiert) | ✓ |
| Navigation: Lösungen · Branchen · Live-Demos · Projekte · Über uns | ✓ |
| Nav-CTA „Potenzial-Check buchen“ | ✓ |
| Über Skalantech: H2 + Lead + Ergänzung + 4 Prinzipien | ✓ |
| Geschäftsführung & technische Leitung: Xavier Escalante Castellar, kleine Copy, technischer Kontext nur hier | ✓ |
| Gebaute Lösungen: Skalantech Hub, InvoiceFlow, OfferAI, MailAgent (je Ausgangslage → Gebaut → Nutzen) | ✓ |
| FAQ, Potenzial-Check-Buchung, Projektanfrage in Endkundensprache | ✓ |

### Entfernt laut Proposal — nicht mehr vorhanden

| Element | Status |
|---|---|
| Zertifikats-/Lebenslauf-Trust-Elemente | ✓ entfernt |
| Live-Stack als Signal-Bar | ✓ entfernt |
| Tool-Listen im Hero (n8n · APIs etc.) | ✓ entfernt |
| DeepDive / DebtPilot als Homepage-Funnel-Nachweis | ✓ entfernt (separate Projektseiten bleiben möglich) |
| doppelte Bereiche „Eigene Systeme“ + „Nachweise“ | ✓ zu einer Sektion „Gebaute Lösungen“ konsolidiert |
| alte Hero-Copy („Arbeit, die heute Zeit frisst…“), „Kostenlose Business-Analyse“ | ✓ ersetzt |

---

## Hinweise / Schnittstellen

- Die technische Wortwahl (n8n, Python, Microsoft 365 / Azure, APIs, selbst gehostete KI-Systeme) erscheint **bewusst nur** im Geschäftsführungs-Bereich — wie im Proposal vorgegeben.
- Der Buchungs-Endpunkt trägt intern weiterhin den Service-Wert `Business-Analyse` (Backend-/n8n-Kompatibilität). Die sichtbare Kunden-Copy ist durchgängig „Potenzial-Check“; das Mapping der CTA-Analytics von „Business-Analyse“ auf „Potenzial-Check“ ist Gegenstand der PULSE-/FORGE-Abstimmung.
- Keine sprachlichen Inkonsistenzen innerhalb von `index.html`/`base.html` gefunden; keine Anpassung über die Proposal-Texte hinaus vorgenommen.

---

## Handoff an nachgelagerte Lanes

- **LUMINA / FORGE:** Struktur- und CSS-Feinschliff (z. B. Kompakt-Stil Geschäftsführung, Mobile Navigation) läuft parallel — Copy bleibt unangetastet.
- **PULSE:** Funnel-Events auf „Potenzial-Check“-Nomenklatur mappen.
- **SENTINEL / CLOSER:** Regressionstests wurden bereits auf die neue Copy aktualisiert (Commit 2866017); Conversion-Check läuft (CLOSER-Verify C1–C15).
