# Claim-Audit repo-weit — Issue #16 (P1)

**Status:** ABGESCHLOSSEN · **Freigabe: Security/QA ✓**
**Datum:** 2026-08-29 · **Verantwortlich:** SENTINEL
**Scope:** Alle verkaufsrelevanten Claims im Repo `Xyesca/skalantech-hub` (Stand `master`, nach PR #14)
**Regel:** Zahlen nur mit Quelle, echter Messung oder klar als Nutzereingabe/Rechenbeispiel. Pauschale Aussagen (DSGVO, Datenverbleib, Zeitangaben) nur mit Qualifizierung.

---

## 1. Prüfmethode

1. Repo-weiter Grep über `app/` (Templates, Copy-Dicts, JS) + `README.md` + `docs/` auf die im Issue genannten Claim-Muster.
2. Abgleich der Claims gegen die reale Systemlage (Container, n8n-Workflows, Demo-Output-Verträge, Datenschutzerklärung).
3. Belastbare Aussagen → behalten. Nicht belastbare → präzisiert oder entfernt (in diesem Commit).
4. Verifikation: `pytest` (151 passed, 178 subtests) nach den Änderungen.

---

## 2. Findings — nicht belastbar, behoben (dieser Commit)

| # | Claim (vorher) | Fundort | Bewertung | Fix (nachher) |
|---|---|---|---|---|
| C1 | „Die Fehlerquote … sinkt dadurch auf nahe null" | app/wissen.py (ki-agenten) | Keine gemessene Basis; InvoiceFlow ist Demo, keine Produktionsmessung | Präzisiert: manuelle Übertragungsarbeit sinkt deutlich; Fehlerquote wird im Betrieb gemessen |
| C2 | „Rechnungen werden innerhalb von Minuten statt Tagen verarbeitet" | app/wissen.py (ki-agenten) | Unbewiesene Zeitangabe | Präzisiert: Demo verarbeitet in Sekunden; „im Betrieb ist das Ziel, Bearbeitungszeiten von Tagen auf Minuten zu senken" |
| C3 | „OfferAI … gleicht die benötigten Teile mit der Lagerdatenbank ab, berechnet die Preise nach den hinterlegten Konditionen" | app/wissen.py (ki-agenten) | **Widerspricht Produktlogik**: Demo-OfferAI erfindet ausdrücklich keine Preise/Mengen/Arbeitszeiten (automation_showcase.py + DEMO_SPEC Issue #10); kein Lagerabgleich vorhanden | Korrigiert auf Demo-Realität: fasst Leistungsumfang zusammen, erkennt fehlende Angaben, bereitet Entwurf vor; Kalkulation/Freigabe beim Menschen |
| C4 | „Die Bearbeitungszeit verkürzt sich von Stunden auf wenige Minuten" (OfferAI) | app/wissen.py (ki-agenten) | Unbewiesen | „Der Entwurf entsteht in der Demo in Minuten statt in Stunden" |
| C5 | „Der kleinste n8n-Cloud-Tarif kostet rund 50 Euro pro Monat und erlaubt 2.500 Workflow-Ausführungen" (3×) | app/wissen.py (n8n-selbst-hosten, n8n-vs-power-automate, kosten-roi) | **Falsche Zahlen** (Stand 2026): Starter ≈ 20–25 €/2.500 Ausf., Pro ≈ 50 €/10.000 Ausf. (n8n.io pricing + unabhängige Quellen) | Korrigiert: Starter 20–25 €/2.500, Pro ≈ 50 €/10.000, „Stand 2026" |
| C6 | „Dies ist der einzige Weg, wie Kanzleien … KI rechtssicher … integrieren können" | app/wissen.py (lokale-ki-vs-cloud-ki) | „einzige Weg" absolut; Cloud-KI kann mit AVV ebenfalls rechtssicher sein | „… ist das der sicherste Weg, KI datenschutzrechtlich kontrolliert zu integrieren" |
| C7 | „… sind lokale Open-Source-Modelle heute oft genauso präzise wie ihre Cloud-Konkurrenten" | app/wissen.py (lokale-ki-vs-cloud-ki) | Keine gemessene Basis | „… oft mit Cloud-Konkurrenten vergleichbar – die genaue Eignung … wird vorab getestet" |
| C8 | „Antwortraten … die die Leistung klassischer Cloud-Modelle bei weitem übertreffen" | app/wissen.py (lokale-ki-vs-cloud-ki) | Unbelegt | „… für viele Anwendungen mit Cloud-Modellen vergleichbar" |
| C9 | „Letzteres beherrschen lokale Modelle fehlerfrei" | app/wissen.py (lokale-ki-vs-cloud-ki) | Absolut-Claim | „in der Regel zuverlässig – konkrete Qualität wird an Ihren Daten getestet" |
| C10 | „reduziert No-Shows spürbar" | app/wissen.py (welche-prozesse) | „spürbar" ohne Messung | „reduziert No-Shows (Umfang wird im Betrieb gemessen)" |
| C11 | „Das ist kein Einzelfall, sondern die typische Ausgangslage in Betrieben" (2×) | app/wissen.py (welche-prozesse, kosten-roi) | Unbelegte Verallgemeinerung; Zahlen sind ROI-Rechner-Defaults | Explizit als „konservatives Rechenbeispiel, keine Garantie; echte Zahlen im Potenzial-Check" markiert |
| C12 | „setzen den ersten Quick-Win in Tagen um – nicht in Quartalen" | app/wissen.py (welche-prozesse) | Zeitversprechen ohne Garantie | „in der Regel innerhalb weniger Wochen; konkreter Zeitrahmen wird vor dem Start vereinbart" |
| C13 | Handwerk-Titel/Description/H1/Quick-Win: „Angebote in Minuten statt Stunden", „vollständiges Angebot – mit Ihren Preisen" | app/branchen.py (handwerk) | Demo liefert Entwurf ohne Preise; „vollständiges Angebot mit Preisen" = Produktlogik-Widerspruch | Durchgängig „Angebotsentwürfe in Minuten"; Preise/Kalkulation bei Freigabe durch den Menschen |
| C14 | hero_trust „Fixpreis, Einstieg in Tagen" | app/branchen.py (handwerk) | „Einstieg in Tagen" nicht garantiert | „Fixpreis vorab"; Zeitrahmen wird vor Start vereinbart (FAQ präzisiert) |
| C15 | „Ihre Daten bleiben bei Ihnen" (FAQ) | app/branchen.py (handwerk) | Pauschal, solange externe KI-Provider (DeepSeek) im Spiel | „kontrollierbar: auf Wunsch vollständig bei Ihnen (Self-Hosting), sonst datenschutzkonform angebunden; etwaige Provider vorab offengelegt" |
| C16 | „Daten werden nicht an fremde KI-Dienste geschickt" (Kfz-FAQ) | app/branchen.py (kfz) | Falsch pauschal: eigene Infrastruktur nutzt DeepSeek (Datenschutzerklärung) | „können vollständig lokal verarbeitet werden; wo KI-Dienste angebunden werden, nur datenschutzkonform und vorab offengelegt" |
| C17 | „Datenabfluss ist damit ausgeschlossen" (Kanzlei-FAQ) | app/branchen.py (kanzleien) | Absolut-Claim; externe Provider (auch DeepSeek) nicht ausgeschlossen | „bei der lokalen Variante … Datenabfluss an Dritte ausgeschlossen; wo kontrollierte Umgebung angebunden wird, Provider/Datenwege vorab offen" |
| C18 | Kanzlei-Lead „Berufsrecht, DSGVO und KI-VO bleiben gewahrt" + ROI „bleiben gewahrt" | app/branchen.py (kanzleien) | Rechts-Zusage pauschal | „werden im Projekt geprüft und adressiert" |
| C19 | „DSGVO-konform" pauschal (Description/Trust Kfz + Immobilien; H1 Kanzlei) | app/branchen.py (kfz, kanzleien, immobilien) | Pauschal, ohne Betriebsmodell-Qualifizierung | „datenschutzkonform" / „DSGVO-konform betreibbar" / Trust-Label „Datenschutz" mit „lokale Verarbeitung auf Wunsch/möglich" |
| C20 | „Exposés in Minuten statt Stunden" (Immobilien, 4×) | app/branchen.py (immobilien) | Keine gemessene Basis, kein Demo-Nachweis | „Exposé-Entwürfe in Minuten"; „erster Entwurf … Sie prüfen und passen an" |
| C21 | „Keine Weitergabe · keine echten Daten" (Demos-Seite, Schritt 04) | app/templates/demos.html | **Widerspruch zur Datenschutzerklärung** (Demo-Texte werden an DeepSeek übermittelt) | „Keine Speicherung · keine echten Daten" |
| C22 | „Verarbeiten · automatisiert & fehlerfrei" (Automationen-Seite) | app/templates/automationen.html | „fehlerfrei" absolut, nicht haltbar | „automatisiert & geprüft" |
| C23 | „n8n — 50 workflows live" (Terminal-Animation) | app/static/js/terminal.js | Real belegt: Terminbuchung + 3 Demo-Workflows (≈4–5), nicht 50 | „n8n — Kern-Workflows live" (Datei wird aktuell nicht gerendert — toter Code, Claim trotzdem korrigiert) |
| C24 | „DSGVO-konform" pauschal / „DSGVO-konform, ohne Datenabfluss" (4×) | app/seo_pages.py (ki-agenten, websites-apps) | Pauschal; „ohne Datenabfluss" nur bei lokalen Modellen | „lokal betreibbar, ohne Datenabfluss" / „Datenschutzkonform betreibbar" / „datenschutzkonforme Verarbeitung" |
| C25 | „DSGVO-konform" pauschal (Köln-LP, 4×) | app/templates/local_koeln.html | Pauschal | „datenschutzkonform" / „DSGVO-konform betreibbar" |

---

## 3. Geprüfte Claims — belastbar, behalten

| Claim | Fundort | Beleg |
|---|---|---|
| „6+ selbst gebaute Produkte live" / „6+ Produkte in Betrieb" / Signal-Bar „6+ eigene digitale Systeme und Prototypen" | branchen.py (handwerk hero_trust, trust), index.html | Real: Skalantech Hub, InvoiceFlow, OfferAI, MailAgent, Terminbuchung (n8n), ROI-Rechner, DeepDive, DebtPilot, Hermes Agent; 14 Container live (`docker ps`) |
| „3 direkt testbare Live-Beispiele" (Signal-Bar) | index.html | 3 n8n-Demos (400/401/402) öffentlich erreichbar |
| „Terminbuchung heute im Einsatz" / „Live-Proof: produktive n8n-Terminbuchung" | branchen.py (handwerk, kfz) | n8n-Workflow `50fo5b3SqQjmEVrX` aktiv; Terminbuchung auf der Website nutzbar |
| „Fixpreis vorab" / „Fixpreis, vorab vereinbart" | branchen.py, seo_pages.py | Geschäftsmodell-Aussage (Angebotsform), kein Leistungsversprechen |
| ROI-Rechner: „Ihre Angaben bleiben auf Ihrem Gerät", „Schätzung auf Basis Ihrer Angaben", „Automatisierungsgrad = Ihre Annahme — kein Versprechen" | seo_pages.py, roi_rechner_widget.html, roi-rechner.js | Rechner läuft clientseitig; Defaults klar als Nutzereingabe/Rechenbeispiel markiert; Verifikation docs/ROI_RECHNER.md |
| ROI-Branchenrechner-Disclaimer „Konservative Schätzung aus Ihren Eingaben – anpassbar, keine Garantie" | branchen.py (roi_calculator) | Klare Qualifizierung |
| ROI-Notes „Angaben sind typische Projekterfahrungen, keine Garantie" | branchen.py (alle 4 Branchen) | Qualifiziert Zeit-/Nutzen-Erfahrungswerte |
| „520 Stunden … 33.800 € pro Jahr" (Handwerk-Rechenbeispiel) | wissen.py (welche-prozesse, kosten-roi) | Als ROI-Rechner-Defaults deklariert, Formel nachvollziehbar; jetzt zusätzlich „keine Garantie" |
| „Sieben Artikel live" | SEO_CONTENT.md | Verifiziert: `WISSEN_ARTIKEL` enthält 7 Artikel |
| E-Rechnung-Rechtsstand (01.01.2025 Empfang, 2027/2028 Versand, XRechnung/ZUGFeRD, ZDH-Umfrage) | branchen.py (handwerk) | Bereits in vorherigem QA-Gate gegen BMF/IHK verifiziert |
| „keine Cookies, keine IP-Adressen, keine personenbezogenen Inhalte" (Analytics) | datenschutz.html, analytics.py | First-Party-Only, Server-Event-Allowlist (docs/ANALYTICS_EVENTS.md) |
| Preise „ab 4.900 €" / „ab 490 €/Monat" mit „Einstiegswerte … individuelles Angebot nach Audit" | seo_pages.py (websites-apps) | „ab"-Preise + pricing_note als Einstiegswerte qualifiziert |
| „Keine externen Tracker", „Eigentum bleibt bei Ihnen", „kein Vendor-Lock-in" | seo_pages.py (websites-apps) | Belegt durch Template-Scan (keine gtag/plausible/hotjar/matomo) + Angebotsmodell |

---

## 4. Bewusst nicht als Claim gewertet

- **wissen.py-Fachartikel-Aussagen** ohne Verkaufscharakter (z. B. Architektur-Beschreibungen von KI-Agenten, technische Voraussetzungen n8n) — beschreiben Technik, keine Leistungszusagen. Wo sie Grenzen zur Zusage überschritten (C6–C12), wurden sie trotzdem präzisiert.
- **docs/**-Dokumente (intern, nicht öffentlich): ROI_RECHNER.md, DEMO_INTEGRATION.md etc. — kein Kundenkontakt.
- **n8n-Workflow-JSONs** — interne Konfiguration, keine Claims.

---

## 5. Verifikation

- `pytest tests/ -x -q` (ohne audit_live/audit_trust): **151 passed, 178 subtests passed** ✅
- Tests `test_branchen.py` an neue Handwerk-Texte (Angebotsentwürfe) angepasst ✅
- Keine Secrets/Webhook-Leaks durch die Änderungen (nur Copy/Texte) ✅

## 6. Rest-Risiken / Hinweise (Nicht-Blocker)

1. **terminal.js** ist aktuell toter Code (kein Template bindet `terminal-body` ein). Wenn die Terminal-Animation je reaktiviert wird: Zahlen aktuell halten („Docker 14 containers up" stimmt heute; Workflow-Zahl dynamisch halten).
2. **n8n-Cloud-Preise** sind volatil — der „Stand 2026"-Vermerk sollte bei der nächsten Content-Pflege gegengeprüft werden.
3. **Kfz-/Immobilien-ROI-Aussagen** („Termine platzen seltener", „keine hängt mehr fest") bleiben als Erfahrungswerte stehen — durch roi_note abgedeckt; bei ersten echten Kundenzahlen durch Messwerte ersetzbar.
4. **„Angebotsentwurf in Minuten"** ist durch die Live-Demo belegt; ein „fertiges Angebot in Minuten" (inkl. Preisfindung) wird bewusst nicht mehr behauptet — Konsistenz mit Issue #10 (keine Preis-Halluzination).

---

## 7. Ergebnis

- **Claim-Audit-Doku:** vorliegend (diese Datei)
- **Freigabe:** **Security/QA ✓** — keine kritischen Findings offen; alle nicht belastbaren Verkaufs-Claims präzisiert oder entfernt
- **Commit:** siehe Git-Historie (`docs: security — Issue #16 Claim-Audit repo-weit (t_610bd6ce)`)
- **Follow-up-Empfehlung:** VELA-Copy-Review der geänderten Passagen (Formulierungskonsistenz), Deployment nach CEO-Freigabe; danach Live-Sichtprüfung 404/500-frei.
