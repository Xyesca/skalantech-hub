# GSC-Baseline skalantech.store

> P0-Verifikation 2026-08-27 — echte Google-Search-Console-Daten, keine Schätzungen.
> Datenquelle: `/root/.hermes/data/seo/gsc_20260827.json` (generiert von `gsc_report.py`).

## Status-Übersicht (27.08.2026)

| Bereich | Status |
|---|---|
| Eigentum | ✅ Domain-Property `sc-domain:skalantech.store`, Service Account `siteFullUser` |
| Sitemap | ✅ `https://skalantech.store/sitemap.xml` eingereicht (PUT 204), **16 URLs**, 0 Fehler |
| Crawling | ✅ `seo_monitor.py` Exit 0 — alle Checks grün (16 Seiten 200, Legal noindex, Canonical, JSON-LD, robots.txt, Sitemap, 404 mit noindex, keine Broken Links) |
| Keyword-Baseline | ✅ Echte GSC-Daten 28d (27.07.–27.08.2026): 36 Queries, 136 Impressions |
| Indexierung | ⏳ URL-Inspection-API liefert noch `UNSPECIFIED` (0/16 Status), Sitemap `indexed: 0` — Property ist jung (erste Daten 17.08.), Google verarbeitet asynchron. Dokumentierter Startwert, kein Fehler. |

## Kennzahlen 28 Tage (27.07.–27.08.2026)

- **Queries:** 36 | **Klicks:** 0 | **Impressions:** 136 | **CTR:** 0,00 % | **Ø-Position:** 82,5
- **Devices:** Desktop 117 Imp. (Ø 81,9) | Mobile 28 Imp. (Ø 85,6)
- **Länder:** DE 103 | AT 8 | IN 7 | ID 5 | CH 4 | PH 4

### Top-Queries (nach Impressions)

| Query | Imp. | Klicks | Ø-Pos |
|---|---|---|---|
| n8n automatisierung | 24 | 0 | 87,5 |
| ki integration bestehende systeme | 12 | 0 | 89,2 |
| n8n hosting | 12 | 0 | 67,5 |
| ki datenintegration | 11 | 0 | 97,5 |
| ki agenten unternehmen | 8 | 0 | 96,2 |
| n8n implementierung | 8 | 0 | 83,8 |
| ki agenten für unternehmen | 6 | 0 | 86,7 |
| n8n automatisierung österreich | 6 | 0 | 75,8 |
| n8n selbst hosten | 6 | 0 | 52,7 |
| n8n selber hosten | 4 | 0 | 45,5 |
| self hosted n8n | 4 | 0 | 64,2 |
| ki-cloud-integration software | 3 | 0 | 100,0 |

### Seiten (nach Impressions)

| Seite | Imp. | Klicks | Ø-Pos |
|---|---|---|---|
| /n8n-automatisierung | 42 | 0 | 83,3 |
| /ki-integration | 38 | 0 | 93,9 |
| /wissen/n8n-selbst-hosten | 32 | 0 | 60,9 |
| /ki-agenten (www-Variante) | 24 | 0 | 92,6 |
| /it-infrastruktur | 7 | 0 | 92,9 |
| /ki-automatisierung | 1 | 0 | 81,0 |
| /wissen/n8n-vs-power-automate | 1 | 0 | 10,0 |

## Interpretation

- **0 Klicks = normal fürs Alter.** Property verifiziert seit 17.08., erste Daten vor ~2 Wochen. Positionen 40–100 = Discovery-Phase.
- **Nächste Ranking-Kandidaten** (bereits < Top-60): `n8n selber hosten` (45,5), `n8n selbst hosten` (52,7), `was ist n8n` (59), `n8n hosting` (67,5), `n8n kosten` (67).
- **n8n-Cluster ist der stärkste Hebel** — 4 der Top-10-Queries und 2 der Top-4-Seiten. Content-Cluster-Strategie (n8n-Automatisierung, Self-Hosting, Implementierung) bestätigt.
- **KI-Integration/Datenintegration** zweiter Hebel (`ki integration bestehende systeme` 12 Imp., `ki datenintegration` 11 Imp.).
- **www-Variante** `/ki-agenten` taucht mit 24 Imp. auf: Canonical zeigt korrekt auf Apex, aber 301 www→apex wäre sauberer (separates Task, kein Blocker).

## Infrastruktur (wiederholbar)

- Skripte: `/root/.hermes/scripts/gsc_report.py` (Report/Baseline), `gsc_inspect.py` (URL-Inspektion), `gsc_submit_sitemap.py` (Sitemap) — Aufruf: `/root/.venvs/gsc/bin/python`
- Daten: `/root/.hermes/data/seo/gsc_YYYYMMDD.json` (root-lesbar, enthält Nutzer-Suchanfragen)
- Cron: **SEO-Wochenreport** (So 05:00 UTC, Job `7058bdbcb695`, Skill google-search-console) | **SEO-Watchdog** täglich 06:00 UTC (Job `5ad7f3904575`, no_agent, `seo_watchdog.sh` → `seo_monitor.py --quiet`)
- KB: diese Datei + `GSC_VERIFICATION.md` (Hub) | Obsidian `03 Knowledge/SEO/GSC-Baseline-skalantech.md` (RAG)

## Verifikationsprotokoll (27.08.2026, Task t_9af843ce)

1. **Eigentum:** GET `/webmasters/v3/sites` → `sc-domain:skalantech.store` mit `permissionLevel: siteFullUser` ✅
2. **Sitemap:** PUT `.../sitemaps/https://skalantech.store/sitemap.xml` → 204; Status: `errors: 0`, `contents.submitted: 16` ✅
3. **Report:** `gsc_report.py` läuft durch, schreibt JSON, kompakte Summary auf stdout ✅
4. **Monitor:** `seo_monitor.py` → Exit 0, „alle Checks grün" (inkl. 404-Seite mit noindex) ✅
5. **Hinweis Erreichbarkeit:** `https://skalantech.store` ist vom VPS aus NICHT per öffentlicher IP erreichbar (Hairpin-NAT: Verbindung zur eigenen öffentlichen IP → „No route to host"). Kein Site-Problem — Google lädt die Sitemap nachweislich (lastDownloaded 27.08. 13:31 UTC), Container `skalantech` healthy, lokal `127.0.0.1:5000` = 200. SEO-Checks laufen daher lokal (`seo_monitor.py` nutzt BASE `http://127.0.0.1:5000`).
