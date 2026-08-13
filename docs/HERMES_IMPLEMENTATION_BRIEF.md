# Hermes Implementation Brief – Skalantech Relaunch

## Auftrag

Setze den in diesem Stand enthaltenen Skalantech-Relaunch vollständig und ohne eigenmächtige Änderungen am Live-Host um. Ziel ist eine professionellere, klarere und vertrauenswürdigere B2B-Service-Website als die bisherige Referenz – mit Fokus auf qualifizierte Projektanfragen für IT-Infrastruktur, Automation und produktive KI-Systeme.

Die Website soll ruhig, präzise und hochwertig wirken. Kein Dark-Cyber-Look, kein Matrix-Grün, keine austauschbare Agenturästhetik und keine erfundenen Leistungskennzahlen.

## Sicherheitsgrenze

- Ausgangspunkt auf GitHub war `master` bei Commit `08386621f504e8a41e209079af4f059408ea0663`.
- Bestehende Docker-, Host-Network-, Port-, Firewall-, Caddy- und Tailscale-Fixes beibehalten.
- Keine Änderungen an `/etc/caddy/Caddyfile` vornehmen.
- Den alten Caddy-Container oder sonstige Serverressourcen nur nach einer separaten, ausdrücklichen Freigabe von Xavier löschen.
- Erst lokal bzw. in einer isolierten Preview prüfen. Danach mit nachvollziehbarem Rollback deployen.

## Positionierung und Conversion-Ziel

### Kernversprechen

**IT, die läuft. Automation, die Arbeit abnimmt.**

Subline:

> Ich modernisiere Infrastruktur, automatisiere Abläufe und bringe KI-Agenten zuverlässig in den Betrieb – von der ersten Analyse bis zur dokumentierten Übergabe.

Primärer CTA: **Projekt unverbindlich anfragen**  
Sekundärer CTA: **Leistungen ansehen**

### Verifizierbare Vertrauenssignale

- 7+ Jahre Infrastrukturpraxis
- Open-Source-first, ohne unnötigen Lock-in
- Deutsch, Englisch und Spanisch
- Köln und remote in DACH
- 100 % remote-fähig
- 6+ selbst gehostete Produkte
- 3 echte Projekte im Portfolio
- Live-Stack: Hermes, n8n, DebtPilot AI, Docker, Caddy, Tailscale

Keine Zufriedenheitsquoten, Kundenanzahlen, Workflow-Zahlen oder andere Social-Proof-Aussagen ergänzen, wenn sie nicht belegt sind.

## Informationsarchitektur

Die Startseite in dieser Reihenfolge umsetzen:

1. Sticky Navigation mit klarem Projekt-CTA
2. Hero mit Nutzenversprechen, zwei CTAs und drei belastbaren Fakten
3. kompakter Proof-/Live-Stack-Streifen
4. Differenzierung: praxisnahe Systeme statt Folienarchitektur
5. vier Leistungen
6. transparenter Vier-Schritte-Prozess
7. drei Formen der Zusammenarbeit
8. echte Projekte
9. Über Xavier / Arbeitsweise
10. kurze FAQ
11. qualifizierendes Kontaktformular
12. Footer mit Leistungen, Kontakt und Rechtlichem

Jeder Abschnitt soll eine konkrete Nutzerfrage beantworten. CTAs sollen den Besucher schrittweise zur Projektanfrage führen, ohne aggressiven Sales-Druck.

## Leistungen

1. **Infrastruktur modernisieren**  
   Microsoft 365, Azure, Active Directory, VMware, Hyper-V, Linux, Migration, Hardening, Backup und Dokumentation.

2. **Prozesse automatisieren**  
   n8n, Python, PowerShell, APIs, Freigaben, Fehlerpfade, Monitoring und Self-Hosting.

3. **KI-Agenten produktiv machen**  
   Agenten, RAG, lokale Sprachmodelle, Tool-Anbindung, Guardrails, Tests und Human-in-the-loop.

4. **Betrieb verlässlich aufsetzen**  
   Docker, Linux, sichere Deployments, Monitoring, Logging, Recovery, Runbooks, Schulung und Übergabe.

## Zusammenarbeit

- **System-Check** – Bestandsaufnahme, Einordnung und priorisierte Roadmap
- **Delivery-Projekt** – klar abgegrenzte Umsetzung bis zur getesteten Dokumentation
- **Engineering-Partner** – laufende technische Begleitung und Optimierung

## Projekte

Die drei realen Projekte erhalten Vorrang vor generischen Demos:

1. **DeepDive** – Open-Source; Videos transkribieren, per KI analysieren und als PDF, HTML oder Audio exportieren. Link: `https://github.com/Xyesca/deepdive`
2. **DebtPilot AI** – Self-hosted Plattform mit lokalen Modellen, RAG-Dokumentenanalyse und modularer Architektur
3. **AI Job Agent** – Stellen finden, Anforderungen analysieren und personalisierte Bewerbungen mit KI erstellen

Wenn echte Screenshots verfügbar sind, diese optimiert als WebP/AVIF einbauen. Keine KI-generierten Produktoberflächen verwenden, die wie echte Screenshots wirken.

## Designsystem

### Stil

- Light Professional: Slate/Weiß mit kräftigem Blau
- große, klare Typografie und starke Informationshierarchie
- weiße Karten mit feinen Grenzen und weichen Schatten
- helle Editor-/Systemdarstellung statt Terminal-Cyberpunk
- tiefe Navy-Flächen nur gezielt für Prozess, Kontakt und Footer
- großzügiger Weißraum, erkennbare Fokuszustände und ruhige Mikroanimationen

### Kernfarben

| Token | Wert | Zweck |
| --- | --- | --- |
| Ink | `#0F172A` | Headlines und Haupttext |
| Page | `#F6F8FC` | Seitenhintergrund |
| Surface | `#FFFFFF` | Karten und Formulare |
| Primary | `#1D4ED8` | Logo und Kernaktionen |
| Accent | `#4F7CFF` | UI-Akzente |
| Signal | `#60A5FA` | Details und Knotenpunkte |
| Soft Blue | `#EEF4FF` | ruhige Akzentflächen |

Keine externen Webfonts, UI-CDNs oder Tracking-Skripte hinzufügen.

## Logo

Das neue Logo ist ein reduziertes **S als durchgehender Systempfad mit zwei Knotenpunkten**. Es steht für Skalantech, Integration und Automation.

Assets:

- `app/static/brand/skalantech-mark.svg`
- `app/static/brand/skalantech-mark-tile.svg`
- `app/static/brand/skalantech-logo.svg`
- `app/static/brand/skalantech-logo-reverse.svg`
- `app/static/favicon.svg`
- `app/static/logo.svg` als kompatibler bestehender Einstiegspunkt
- Regeln und Farben: `app/static/brand/README.md`

In Navigation und Footer die Bildmarke als SVG laden und den Namen als echten HTML-Text setzen. Das hält die Darstellung responsiv und barrierearm.

## Bildwelt

Es wurden zwei eigene, KI-generierte Markenmotive erstellt. Sie zeigen Infrastruktur, Workflow und Rechenkern als verbundenes System; sie zeigen kein reales Kundenprojekt und kein vermeintliches Porträt von Xavier.

- `app/static/img/skalantech-systems.webp` – 960 × 1200, About-/Editorial-Visual
- `app/static/img/skalantech-systems-480.webp` – responsive 480 × 600 Variante
- `app/static/img/skalantech-og.jpg` – 1200 × 630 für Open Graph und Social Sharing

Die Assets sind bereits komprimiert und ohne Text, Logos oder fremde Marken. Das About-Visual mit korrektem Alt-Text und `srcset` verwenden. Das breite Motiv als `og:image` und `twitter:image` hinterlegen.

Ein echtes, professionelles Foto von Xavier wäre langfristig die bessere Wahl für den About-Bereich. Sobald eines vorliegt, das Editorial-Visual dort ersetzen; das Social-Motiv kann bestehen bleiben.

## Relevante Implementierungsdateien

- `app/templates/base.html` – Metadaten, Navigation, Logo, strukturierte Daten, Footer
- `app/templates/index.html` – vollständige Conversion-Startseite
- `app/static/css/style.css` – responsives Designsystem
- `app/static/js/main.js` – Navigation, Reveals, Formular-UX, Zähler und Fehler-Fallback
- `app/blueprints/public.py` – öffentliche Routen und Kontaktverarbeitung
- `app/config.py` und `app/utils/security.py` – sichere Defaults und Security-Header
- `app/templates/legal/*.html` – konsistentes Layout der Rechtstexte
- `seed.py` – ehrliche Projekt-Fallbacks
- `schema-website.json` und `schema-person.json` – strukturierte Daten
- `.env.example` und `README.md` – Betrieb und Konfiguration
- `tests/test_public.py` – Regressionstests

## Formular und Sicherheit

- CSRF aktiv lassen
- Honeypot-Feld beibehalten
- serverseitige Längen- und Auswahlvalidierung beibehalten
- maximal drei valide Kontaktanfragen pro IP und Stunde
- Nachricht auch ohne SMTP sicher in SQLite speichern
- Security-Header beibehalten: CSP, HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Permissions-Policy`, `Referrer-Policy`
- Admin-Cookies in Produktion nur über HTTPS
- keine Secrets committen

Hinweis: Das aktuelle Rate-Limit ist In-Memory und damit für eine einzelne Instanz geeignet. Bei mehreren Gunicorn-Instanzen/Containern auf Redis oder einen anderen gemeinsamen Store umstellen.

## Qualitätsanforderungen

- Mobile-first ab 320 px, ohne horizontales Scrollen
- sinnvolle Tab-Reihenfolge, Skip-Link und sichtbare Fokuszustände
- Navigation per Tastatur und Screenreader bedienbar
- `prefers-reduced-motion` respektieren
- Bilder mit festen Dimensionen, `srcset`, Lazy Loading und passenden Alt-Texten
- CTA und Formularzustände auch ohne Animation verständlich
- keine Layout-Verschiebungen durch Bilder oder Fonts
- Lighthouse-Zielwerte als Orientierung: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95

## Abnahme

Aktueller Paketstatus vor Übergabe: **6 automatisierte Tests bestanden**, Python-Quellen erfolgreich kompiliert, SVG-Dateien als valides XML geprüft und alle neuen Brand-/Bildassets über Flask mit dem erwarteten MIME-Type ausgeliefert.

Vor einem Deployment mindestens ausführen:

```bash
python -m unittest discover -v
```

Zusätzlich prüfen:

```bash
python -m compileall app tests
```

Manuelle Abnahme:

- Desktop: 1440 × 900
- Tablet: 768 × 1024
- Mobil: 390 × 844 und 320 × 568
- Navigation, alle CTAs, FAQ, Kontaktformular und Rechtsseiten
- `/robots.txt` und `/sitemap.xml`
- Open-Graph-Vorschau mit absoluter Bild-URL
- keine 404 für Logo, Favicon, Bilder, CSS, JavaScript und Zertifikats-PDF

## Deployment-Reihenfolge

1. Backup von Datenbank und aktueller Konfiguration erstellen.
2. Image/Container in einer isolierten Preview bauen.
3. Tests und manuelle Responsive-Prüfung durchführen.
4. Deploy mit bestehender Compose-/Caddy-/Tailscale-Konfiguration.
5. Healthcheck lokal und von außen durchführen.
6. Formularzustellung und Speicherung einmal kontrolliert testen.
7. Bei Abweichungen auf den vorherigen Containerstand zurückrollen.

## Definition of Done

- Light-Professional-UX vollständig umgesetzt
- neues Logo überall konsistent eingesetzt
- neue Bildassets ohne 404 ausgeliefert
- ausschließlich belegbare Claims und echte Projekte sichtbar
- Kontaktformular sicher und verständlich
- alle automatisierten Tests grün
- Desktop und Mobil visuell abgenommen
- externe Erreichbarkeit von `https://skalantech.store/` geprüft
- keine ungeplante Änderung an Firewall, Caddy oder Tailscale
