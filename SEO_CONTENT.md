# SEO Content für skalantech.store

Stand: 2026-08-28 — aktualisiert nach Blog-Start (3 Artikel aus Content-Cluster, Stage P1).

## robots.txt (serviert via Route /robots.txt)

```text
User-agent: *
Allow: /
Disallow: /admin
Disallow: /login
Disallow: /auth
Disallow: /test-footer

Sitemap: https://skalantech.store/sitemap.xml
```

## Sitemap (dynamisch via Route /sitemap.xml)

Indexierbare Seiten (24):

- https://skalantech.store/ (priority 1.0)
- https://skalantech.store/automationen (0.9)
- https://skalantech.store/demos (0.8)
- https://skalantech.store/koeln (0.8)
- https://skalantech.store/websites-apps (0.8)
- https://skalantech.store/it-infrastruktur (0.8)
- https://skalantech.store/ki-integration (0.8)
- https://skalantech.store/ki-automatisierung (0.8)
- https://skalantech.store/ki-agenten (0.8)
- https://skalantech.store/n8n-automatisierung (0.8)
- https://skalantech.store/lokale-ki (0.8)
- https://skalantech.store/branchen/handwerk (0.8)
- https://skalantech.store/branchen/kfz (0.8)
- https://skalantech.store/branchen/kanzleien (0.8)
- https://skalantech.store/branchen/immobilien (0.8)
- https://skalantech.store/wissen (0.7)
- https://skalantech.store/wissen/was-ist-ein-ki-agent (0.7)
- https://skalantech.store/wissen/n8n-selbst-hosten (0.7)
- https://skalantech.store/wissen/lokale-ki-vs-cloud-ki (0.7)
- https://skalantech.store/wissen/n8n-vs-power-automate (0.7)
- https://skalantech.store/wissen/welche-prozesse-ki-automatisierung (0.7)
- https://skalantech.store/wissen/rag-wissensassistenten (0.7)
- https://skalantech.store/wissen/kosten-roi-ki-automatisierung (0.7)
- https://skalantech.store/faq (0.6)

Nicht indexiert (noindex/Disallow): /impressum, /datenschutz, /agb, /login, /admin, /auth, /uploads/*.

## Wissen/Blog (Stage P1, Stand 2026-08-28)

Sieben Artikel live (je 800–1200 Wörter, Business-Nutzen first), alle in der
Sitemap, verlinkt über /wissen-Index + Related-Links auf den Landingpages.
Artikel-Dicts in `app/wissen.py` (ARTICLES + ARTICLE_ORDER), Template
`article.html` mit `Article`-JSON-LD (datePublished je Artikel gesetzt).

| Artikel | Slug | Primär-Intent | Related-Service |
|---|---|---|---|
| Was ist ein KI-Agent? | was-ist-ein-ki-agent | Informational (KI-Agenten) | /ki-agenten |
| n8n selbst hosten | n8n-selbst-hosten | Informational (n8n, Datenschutz) | /n8n-automatisierung |
| Lokale KI vs. Cloud-KI | lokale-ki-vs-cloud-ki | Informational (Datenschutz, Betrieb) | /lokale-ki |
| n8n vs. Power Automate | n8n-vs-power-automate | Informational (Vergleich) | /n8n-automatisierung |
| Welche Prozesse für KI-Automatisierung? | welche-prozesse-ki-automatisierung | Informational (Prozessauswahl) | /ki-automatisierung |
| RAG und Wissensassistenten | rag-wissensassistenten | Informational (RAG) | /ki-agenten |
| Kosten und ROI von KI-Automatisierung | kosten-roi-ki-automatisierung | Informational (ROI) | /ki-automatisierung |

Wortzahlen (2026-08-28, verifiziert): 977 / 834 / 882 / 1136 / 916 / 920 / 888.

GSC-Submit: Sitemap eingereicht 2026-08-28 (HTTP 204, isPending=False,
contents: 24 URLs). URL-Inspektion n8n-vs-power-automate: PASS (indexed);
neue URLs brauchen Crawl-Zeit (NEUTRAL/unknown ist normal nach Einreichung).

## Branchen-Landingpages (Stage 5)

Vier Branchenseiten, dict-driven wie die Service-Seiten (`app/branchen.py` →
`LANDING_BRANCHEN`, gemergt in `LANDING_PAGES` in `app/seo_pages.py`).
Explizite Routen `/branchen/{slug}` (kein Catch-All), Endpoint-Namen
`public.landing_branchen_*`.

| Seite | Dict-Schlüssel | Primär-Intent |
|---|---|---|
| /branchen/handwerk | branchen-handwerk | Prozess-Automatisierung im Betrieb |
| /branchen/kfz | branchen-kfz | Automatisierung rund um die Werkstattsoftware |
| /branchen/kanzleien | branchen-kanzleien | Lokale KI für Kanzlei + Steuerberatung (RA+StB) |
| /branchen/immobilien | branchen-immobilien | KI-Integration in Bestands-CRM |

Seitenstruktur: H1 → Problem → Lösung → Integration (nur Kfz/Immobilien) →
ROI → Zwischen-CTA → Einsatzmöglichkeiten → Vorgehen → Technologien → Trust →
FAQ → Related → Autor → Abschluss-CTA.

CTA-Ziel: `/#termin` + `/#contact` mit UTM
`utm_source=organic&utm_medium=landing&utm_campaign=branche_{slug}`
(Query VOR Fragment — sonst geht First-Party-Tracking verloren).

## Schema.org JSON-LD

- Startseite: `ProfessionalService` + `Person` + `WebSite` (in base.html, global) + `FAQPage` (5 sichtbare FAQs)
- /faq: `FAQPage` (6 sichtbare FAQs)
- Landingpages (Service + Branchen): `Service` + `BreadcrumbList` + `FAQPage` (je 3)
- /wissen: `CollectionPage` + `BreadcrumbList`
- Artikel: `Article` + `BreadcrumbList`
- Keine Fake-Reviews, kein AggregateRating.

## Open Graph / Twitter

- og:type, og:locale, og:site_name, og:title, og:description, og:url, og:image (1200x630) auf allen Seiten
- twitter:card, twitter:title, twitter:description, twitter:image
- Canonical explizit pro Unterseite.

## Meta-Descriptions

Pro Seite individuell (siehe app/seo_pages.py + app/branchen.py + Template-Blöcke).
Kein Keyword-Stuffing.
