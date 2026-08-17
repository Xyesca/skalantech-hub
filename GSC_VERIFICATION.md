# Google Search Console Verification für skalantech.store

## Status: KOMPLETT EINGERICHTET (2026-08-17)

1. ✅ Domain-Property `sc-domain:skalantech.store` verifiziert (DNS-TXT)
2. ✅ Service Account `gsc-reader@skalantech-seo.iam.gserviceaccount.com` mit vollem Zugriff (API-Zugang für Hermes)
   - Key: `/root/.hermes/gsc_service_account.json` (chmod 600, NIE committen)
   - Python-venv: `/root/.venvs/gsc/` (google-auth)
3. ✅ Sitemap `https://skalantech.store/sitemap.xml` per API eingereicht (Status 204) und von Google verarbeitet: 14 URLs, keine Fehler
4. ✅ URL-Inspektion für alle 14 indexierbaren Seiten angestoßen (per API)
5. ✅ Baseline unter `/root/.hermes/data/seo/gsc_YYYYMMDD.json` — Startwert 0 Daten (Property frisch)
6. ✅ Wochenreport-Cron (Sonntag 9 Uhr) nutzt echte GSC-Daten via `gsc_report.py`

## Skripte (VPS)
- `/root/.hermes/scripts/gsc_report.py` — Baseline/Report (Search Analytics, Sitemaps, Inspection)
- `/root/.hermes/scripts/gsc_inspect.py` — URL-Inspektion aller Hauptseiten
- `/root/.hermes/scripts/gsc_submit_sitemap.py` — Sitemap einreichen
- Aufruf immer mit `/root/.venvs/gsc/bin/python`

## Ersteinrichtung (falls neu durchzuführen)

1. Öffne https://search.google.com/search-console
2. Wähle als Property-Typ **"Domain"** und gib `skalantech.store` ein.
3. Wähle die Verifikationsmethode **DNS TXT Record** (empfohlen — funktioniert ohne Änderung an der Website).
4. Logge dich in dein DNS-Panel ein (vermutlich IONOS).
5. Erstelle einen neuen TXT-Eintrag:
   - Host/Name: `@` (oder leer / `skalantech.store`)
   - Typ: `TXT`
   - Wert/Data: **den echten Code, den die GSC dir anzeigt** (z. B. `google-site-verification=xxxxxxxxxxxxxxxx`)
6. In der GSC auf "Verifizieren" klicken.

## Alternative: HTML-Datei-Methode

Falls du die HTML-Methode bevorzugst: Die GSC bietet eine Datei wie
`google<hash>.html` zum Download an. Diese Datei kannst du unter
`app/static/` ablegen — sie ist dann über `https://skalantech.store/<dateiname>`
erreichbar. DNS-Methode ist trotzdem robuster (bleibt bei Rebuilds erhalten).

## Bing Webmaster Tools

1. https://www.bing.com/webmasters — Microsoft-Konto verwenden (Xavier hat Microsoft 365).
2. "Import aus Google Search Console" wählen, sobald GSC verifiziert ist.
3. Alternativ: XML-Datei-Verifikation oder CNAME — Code ebenfalls aus der Bing-UI übernehmen.
