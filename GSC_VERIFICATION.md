# Google Search Console Verification für skalantech.store

> ⚠️ **WICHTIG:** Der untenstehende Verifikationswert ist ein **PLATZHALTER**
> (Beispiel-String). Du musst den **echten** Verifikationscode direkt aus der
> Google Search Console übernehmen — sonst schlägt die Verifikation fehl.

## Schritt für Schritt

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
