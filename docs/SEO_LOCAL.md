# Local SEO — Vorbereitung für skalantech.store

Stand: 2026-08-16 · Grundsatz: **nur echte Daten, keine erfundene Adresse,
keine Fake-Bewertungen.**

## 1. Ist-Situation (NAP-Konsistenz, geprüft)

| Ort | Daten |
|---|---|
| Impressum | Xavier Escalante Castellar · Eifelstraße 33 · 51109 Köln · Deutschland · E-Mail · Tel. 0176 77879366 |
| Footer (Website) | Köln · Remote in DACH |
| Settings.location (DB) | Köln, Germany |
| FAQ | Remote in Deutschland/DACH, vor Ort nach Absprache |

**Bewertung:** Konsistent (Name/Ort/E-Mail). Für GBP relevant ist die Adresse
aus dem Impressum. Kein Widerspruch gefunden.

**Bekannter Bug:** `tel:`-Link im Impressum ist maskiert (`tel:+491****9366`)
→ href defekt. Für NAP-Konsistenz und Mobile-Conversion fixen (manuell oder
bei nächstem Deploy durch mich).

## 2. Ist Local SEO sinnvoll?

**Ja, bedingt.** Skalantech arbeitet remote in DACH, aber:
- Sitz in Köln + regionale B2B-Dienstleistung → lokale Suchen ("IT-Dienstleister Köln", "KI-Beratung Köln") haben Relevanz
- Google Business Profile (GBP) erhöht Vertrauen und liefert lokale Sichtbarkeit
- Priorität: **niedriger als nationale B2B-Keywords** → P2/P3

## 3. Google Business Profile — Vorbereitung (Login nötig → Xavier)

Wenn bereit:
1. https://business.google.com → Konto mit Google-Konto anlegen (empfohlen: xyescaescalante@gmail.com oder geschäftliche Adresse)
2. Unternehmenstyp: "Dienstleistungen" / Einzelunternehmer
3. Name: **Skalantech** (kein Keyword im Namen!)
4. Adresse: **Eifelstraße 33, 51109 Köln** (echte Daten — Einzelunternehmer mit Sitz)
   - Option "Dienstleistungsgebiet": Köln + Remote (DACH) — wichtig, da remote gearbeitet wird
5. Telefon: 0176 77879366 · Website: https://skalantech.store
6. Kategorien: **IT-Dienstleister** (primary) · Secondary: Beratungsdienst für Informationstechnologie, Softwareentwickler, KI-Beratung (falls verfügbar)
7. Beschreibung (kurz, faktenbasiert):
   "Skalantech unterstützt Unternehmen bei IT-Infrastruktur, Prozessautomatisierung und der Integration von KI in bestehende Systeme – remote in DACH, mit Sitz in Köln."
8. Leistungen eintragen: IT-Infrastruktur, KI-Integration, KI-Automatisierung, KI-Agenten, n8n-Workflows, Self-hosted KI
9. Verifizierung: Postkarte/Video — dauert Tage; danach Beiträge + Leistungsfotos

**Bewertungen:** Nur organisch entstehen lassen. Nicht aktiv einsammeln.

## 4. Regionale Keywords (P3, nach GBP-Aktivierung)
- "IT-Dienstleister Köln" · "IT-Beratung Köln" · "KI-Beratung Köln" · "n8n Dienstleister"
- Für diese Keywords später ggf. eine lokale Landingpage /regionen/koeln (nur wenn GBP live und Suchnachfrage belegt)

## 5. Nächste Schritte
- [ ] `tel:`-Link im Impressum fixen (durch mich, beim nächsten Deploy — ist bereits identifiziert)
- [ ] GBP anlegen + verifizieren (Xavier, Login nötig)
- [ ] NAP nach GBP-Erstellung erneut abgleichen
- [ ] Regionale Keywords in GSC beobachten (sobald aktiv)
