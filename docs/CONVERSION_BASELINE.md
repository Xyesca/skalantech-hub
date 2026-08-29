# Conversion-Baseline & Homepage-Conversion-Optimierung (P0)

**Datum:** 2026-08-27
**Verantwortlich:** LUMINA (UX/UI & Conversion Architecture), Daten: PULSE/GSC
**Status:** Baseline vor Hero-/CTA-/Trust-Optimierung gemessen; Optimierung deployed.

## 1. 5-Sekunden-Test (vorher)

| Frage | Bewertung | Befund |
|---|---|---|
| Was? | teilweise | H1 = Benefit („IT, Automatisierung und KI, die im Alltag wirklich funktionieren“), aber Leistung erst im Lead sichtbar |
| Für wen? | ✗ | Nur „Unternehmen“ — keine Zielgruppe (KMU/Mittelstand) im Hero |
| Problem? | ✓ | Pain-Liste im Hero (manuelle Prozesse, Systeme, KI-Unsicherheit) |
| Warum Skalantech? | ✗ | Kein Differenzierer im Hero; Signal-Bar zeigte schwache Claims („100% remote-fähig“, „3 echte Projekte“) |
| Nächster Schritt? | ✓ | CTA „Potenzial-Check buchen“ prominent (Header + Hero) — seit Customer-First-Relaunch (t_345e37a3); Events unverändert `demo_started` |

## 2. Conversion-Baseline (vor Optimierung, gemessen 2026-08-27)

### Traffic (GSC, sc-domain:skalantech.store, 28 Tage bis 2026-08-23)
- **Klicks:** 0
- **Impressions:** 49 (Desktop 41, Mobile 8)
- **CTR:** 0 %
- **Ø Position:** ~70–90 (Long-Tail, Property frisch)
- **Sitemap:** 16 URLs submitted, 0 indexed (Stand 2026-08-22 — Google hat noch nicht indexiert)

### Leads (First-Party-DB, contact_messages)
- **Gesamt:** 10 Nachrichten, davon **0 externe Leads** (alle Test-Einträge vom Betreiber, 2026-08-13 bis 2026-08-17)
- **Attribution:** UTM-Felder vorhanden (source/medium/campaign), keine echten Kanal-Daten bisher

### Terminbuchung (n8n-Workflow)
- Webhook `/webhook/skalantech-termin` aktiv (WF 50fo5b3SqQjmEVrX), aber keine echten Buchungen in der Baseline-Periode

### Fazit Baseline
- **Conversion Rate Besuch → Lead:** aktuell **0 %** (kein organischer Traffic, keine echten Leads)
- **Einordnung:** Property ist jung; organischer Traffic startet erst nach Google-Indexierung. Baseline ist daher eine **Null-Baseline** — Zielwerte gelten ab erstem realem Traffic.

## 3. Umgesetzte P0-Maßnahmen (Hero + CTA + Trust)

1. **Eyebrow** → „Skalantech · Xavier Escalante — IT-Infrastruktur, Automation & KI“ (Marke + Person + Leistung in 1 Zeile)
2. **Lead** → Zielgruppe explizit: „Für kleine und mittelständische Unternehmen…“ + Nutzenversprechen (täglich nutzen statt nur Konzept)
3. **Trust-Block im Hero** (neu, `.hero__trust`):
   - Direkt vom Gründer — kein Vertriebsteam
   - 7+ Jahre IT-Praxiserfahrung
   - Self-Hosting & Datensouveränität statt Vendor-Lock-in
4. **Signal-Bar** → schwache Claims ersetzt: „7+ Jahre IT-Praxiserfahrung“, „6+ selbst gehostete Produkte“, „100% persönlich · direkter Draht zum Gründer“
5. **Mobile:** Trust-Block auf <680px als 1-Spalten-Grid (gut lesbar); Rest-Layout unverändert responsiv
6. **Tests:** `test_homepage_contains_conversion_and_seo_content` um neue Conversion-Phrasen erweitert
7. **Cache-Buster:** CSS/JS `?v=13` → `?v=14`

## 4. Zielwerte (nach Optimierung, ab erstem realem Traffic)

| Metrik | Baseline | Ziel (30 Tage nach Indexierung) |
|---|---|---|
| Besuch → Kontakt/Lead | 0 % | ≥ 1,0 % |
| CTA-Klickrate Hero (Potenzial-Check) | n/a | ≥ 2,5 % der Besucher |
| Terminbuchungs-Startrate | n/a | ≥ 40 % der Formular-Besucher |
| Absprungrate Homepage | n/a | < 60 % |

## 5. Messung

- GSC-Wochenreport (PULSE, `gsc_report.py`) — Traffic/Klicks/CTR/Position
- First-Party-Attribution in `contact_messages` (UTM) — Lead-Quellen
- n8n-Executions (Terminbuchung) — Buchungs-Conversion
- DoD erfüllt: Mobile + Desktop geprüft (Screenshots im Task-Workspace), Baseline gemessen, Hero/CTA/Trust optimiert
