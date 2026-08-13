# Google Search Console Verification für skalantech.store

Befolge diese Schritte, um die Inhaberschaft der Domain zu verifizieren:

1. Öffne die Google Search Console: https://search.google.com/search-console
2. Wähle als Property-Typ "Domain" und gib "skalantech.store" ein.
3. Wähle die Verifikationsmethode: **DNS TXT Record** (oft empfohlen).
4. Logge dich in dein DNS-Panel ein (vermutlich IONOS).
5. Erstelle einen neuen TXT-Eintrag für deine Domain:
   - Host/Name: `@` (oder leer/skalantech.store)
   - Typ: `TXT`
   - Wert/Data: `google-site-verification=SkalanTech_a8f9b2d3c4e5_GSC_Verify`

*Alternativ: HTML-Datei-Methode*
Falls du die HTML-Methode bevorzugst, lade eine Datei namens `googleSkalanTech_a8f9b2d3c4e5_GSC_Verify.html` herunter und lege sie im Verzeichnis `app/static/` ab (stelle sicher, dass Flask statische Dateien im Root-Pfad der Domain richtig serviert, andernfalls ist DNS besser).
