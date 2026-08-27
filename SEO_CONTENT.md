# SEO Content für skalantech.store

Stand: 2026-08-27 — aktualisiert nach SEO-Umsetzung + Branchen-Landingpages (Stage 5).

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

Indexierbare Seiten (16):

- https://skalantech.store/ (priority 1.0)
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
- https://skalantech.store/faq (0.6)

Nicht indexiert (noindex/Disallow): /impressum, /datenschutz, /agb, /login, /admin, /auth, /uploads/*.

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
