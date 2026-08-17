# Google Search Console Verification für skalantech.store

## Status: TXT-Record gesetzt & propagiert (2026-08-17)

Der TXT-Record `google-site-verification=gly9Ag9wNe6cRlpyQrLC-P740gHuou5p5FMhTJfOFaY`
wurde bei IONOS gesetzt und ist über öffentliche DNS-Server (8.8.8.8, 1.1.1.1) sichtbar.
Nächster Schritt in GSC: **„Verifizieren"** klicken → danach Sitemap
`https://skalantech.store/sitemap.xml` unter **Sitemaps** einreichen.

> Hinweis: Der Verifikationswert ist ein Domain-Verifikations-Token (kein Zugangs-Secret)
> und steht öffentlich im DNS. Er dient nur der Inhaberschafts-Bestätigung gegenüber Google.

## Ersteinrichtung (falls noch nicht durchgeführt)

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
