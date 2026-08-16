# SEO-Audit & Umsetzung — skalantech.store (2026-08-16)

## P0 (behoben)
| Punkt | Vorher | Nachher |
|---|---|---|
| Sitemap | Hartcodiert, nur `/` + `/faq` | Dynamisch aus indexierbaren Seiten (12 URLs), `lastmod` + `priority` |
| robots.txt | `Allow: /` ohne Disallows | `Disallow: /admin /login /auth /test-footer` + Sitemap-Referenz |
| Landingpages | Keine | 6 differenzierte SEO-Seiten (siehe unten) |
| Wissensstruktur | Keine | `/wissen` + 3 Artikel |
| `/test-footer` | Route + 500 (Template fehlte), indexierbar | Route entfernt → 404, robots-Disallow bleibt |
| 404-Seite | Fehlte (Default) | Custom-404 mit Links zu Top-Seiten, `noindex` |
| Interne Verlinkung | Nur One-Pager-Anker + Footer | Service-Cards → Landingpages, Footer → 6 Leistungsseiten, Artikel → Leistungsseiten |

## P1 (behoben)
| Punkt | Maßnahme |
|---|---|
| FAQPage-Schema | Startseite (5 Fragen), /faq (6 Fragen), jede Landingpage (3 Fragen) — nur sichtbare FAQs |
| Service-Schema | Pro Landingpage (`Service` mit Provider-Verweis auf ProfessionalService) |
| BreadcrumbList | Landingpages, Wissen, Artikel |
| Article-Schema | Artikel (`Article` mit Autor/Publisher-Referenz) |
| twitter:title / twitter:description | Ergänzt (fehlten) |
| Canonical-Korrektheit | Unterseiten setzen explizite Canonicals; Default bleibt Startseite |

## P2 (bewertet, bewusst NICHT umgesetzt)
| Punkt | Bewertung |
|---|---|
| Bild-Optimierung | Bereits stark: WebP/AVIF, srcset/sizes, width/height, fetchpriority=high im Hero, Lazy Loading bei Work-Bildern. Kein Handlungsbedarf. |
| Performance | Kein Framework, kein Google Fonts, kein CDN, 49 KB CSS / 10 KB JS. SEO-Layer fügt ~0 externen Request hinzu. |
| Impressum noindex | Bewusste Entscheidung der bestehenden Seite — belassen (rechtlich üblich, kein Ranking-Ziel). |
| tel:-Link im Impressum | `tel:+491\*\*\*\*9366` maskiert → defekter href. Kein SEO-Thema; manueller Fix empfohlen. |

## Landingpages (Keyword → URL)
| URL | Suchintention |
|---|---|
| /it-infrastruktur | IT-Infrastruktur für Unternehmen (Server, Docker, Netzwerk, Monitoring, Backup) |
| /ki-integration | KI in bestehende Systeme integrieren (APIs, LLMs, Daten, Datenschutz) |
| /ki-automatisierung | Geschäftsprozesse automatisieren (Rechnungen, Berichte, E-Mail, Datenabgleich) |
| /ki-agenten | KI-Agenten für Unternehmen (autonome Workflows, RAG, Wissensassistent) |
| /n8n-automatisierung | n8n Workflow-Automatisierung / n8n selbst hosten (Integrationen, Datenschutz) |
| /lokale-ki | Lokale / selbst gehostete KI (Datenschutz, keine Cloud-Abhängigkeit, Ollama) |

Abgrenzung: Jede Seite adressiert eine andere Suchintention (Prozess vs. Technologie vs.
Betriebsmodell). Keine doppelten Texte — verifiziert durch Test
`test_landing_pages_are_not_duplicate_content`.

## Wissensartikel
- /wissen/was-ist-ein-ki-agent — Informational (Definition, Abgrenzung, Einsatz)
- /wissen/n8n-selbst-hosten — Informational + Long-tail (n8n, Self-Hosting)
- /wissen/lokale-ki-vs-cloud-ki — Vergleich / Entscheidungshilfe

Alle Artikel verlinken auf die passende Leistungsseite + CTA (Terminbuchung).

## Nächste Phase (Vorschlag)
1. Google Search Console (DNS-TXT oder HTML-Datei — siehe GSC_VERIFICATION.md, Code dort ist ein Platzhalter!) + Bing Webmaster Tools.
2. Keyword-Ranking-Baseline (GSC nach ~2 Wochen Indexierung).
3. Content-Strategie: 2–4 Artikel/Monat entlang der Keyword-Cluster; interne Verlinkung ausbauen.
4. Backlink-/Zitationsaufbau regional (Köln) + lokale Landingpage-Feinschliff für GBP.
