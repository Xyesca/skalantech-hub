# SEO Content für skalantech.store

Stand: 2026-08-16 — aktualisiert nach SEO-Umsetzung.

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

Indexierbare Seiten (12):

- https://skalantech.store/ (priority 1.0)
- https://skalantech.store/it-infrastruktur (0.8)
- https://skalantech.store/ki-integration (0.8)
- https://skalantech.store/ki-automatisierung (0.8)
- https://skalantech.store/ki-agenten (0.8)
- https://skalantech.store/n8n-automatisierung (0.8)
- https://skalantech.store/lokale-ki (0.8)
- https://skalantech.store/wissen (0.7)
- https://skalantech.store/wissen/was-ist-ein-ki-agent (0.7)
- https://skalantech.store/wissen/n8n-selbst-hosten (0.7)
- https://skalantech.store/wissen/lokale-ki-vs-cloud-ki (0.7)
- https://skalantech.store/faq (0.6)

Nicht indexiert (noindex/Disallow): /impressum, /datenschutz, /agb, /login, /admin, /auth, /uploads/*.

## Schema.org JSON-LD

- Startseite: `ProfessionalService` + `Person` + `WebSite` (in base.html, global) + `FAQPage` (5 sichtbare FAQs)
- /faq: `FAQPage` (6 sichtbare FAQs)
- Landingpages: `Service` + `BreadcrumbList` + `FAQPage` (je 3)
- /wissen: `CollectionPage` + `BreadcrumbList`
- Artikel: `Article` + `BreadcrumbList`
- Keine Fake-Reviews, kein AggregateRating.

## Open Graph / Twitter

- og:type, og:locale, og:site_name, og:title, og:description, og:url, og:image (1200x630) auf allen Seiten
- twitter:card, twitter:title, twitter:description, twitter:image
- Canonical explizit pro Unterseite.

## Meta-Descriptions

Pro Seite individuell (siehe app/seo_pages.py + Template-Blöcke). Kein Keyword-Stuffing.
