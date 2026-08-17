# SSL-Zertifikat skalantech.store — Betrieb & Erneuerung

## Aktueller Stand (installiert 2026-08-17)
- **Zertifikat:** Sectigo Wildcard `*.skalantech.store` (+ Bare-Domain, SAN geprüft: `DNS:*.skalantech.store, DNS:skalantech.store`)
- **Chain:** `/etc/caddy/certs/skalantech.store.crt` (Blatt + Intermediate, 2 Zertifikate — Kette via openssl verifiziert: OK)
- **Key:** `/etc/caddy/certs/skalantech.store.key` (`caddy:caddy`, `600` — privater Schlüssel NIE in Git/Chat/Logs)
- **Gültig:** 17.08.2026 → **13.02.2027**
- **Installiert:** Caddyfile-Block `skalantech.store, www.skalantech.store` → `tls /etc/caddy/certs/skalantech.store.crt /etc/caddy/certs/skalantech.store.key`
- **Watchdog:** Hermes-Cron `cert_watchdog.py` täglich 07:00 UTC — silent, meldet ab 30 Tage vor Ablauf an Telegram (Job `5712f89a0e56`)
- **Backup der vorherigen Caddyfile:** `/etc/caddy/Caddyfile.bak-sectigo`

## Erneuerung (~Januar 2027, sobald der Watchdog warnt)
1. Neues Zertifikat + Key von Sectigo/Anbieter holen (Key bleibt identisch, wenn dieselbe CSR/Keypair verwendet wird).
2. Dateien ersetzen:
   - `/etc/caddy/certs/skalantech.store.crt` = **neues Blatt + aktuelle Intermediate** in einer Datei
     (Intermediate-URL aus dem AIA-Feld des neuen Zertifikats lesen: `openssl x509 -in cert -noout -text | grep -A2 "CA Issuers"`)
   - `/etc/caddy/certs/skalantech.store.key` = privater Schlüssel (nur falls neu)
3. Permissions setzen:
   ```bash
   chown caddy:caddy /etc/caddy/certs/skalantech.store.crt /etc/caddy/certs/skalantech.store.key
   chmod 644 /etc/caddy/certs/skalantech.store.crt
   chmod 600 /etc/caddy/certs/skalantech.store.key
   ```
4. Validieren + neu laden:
   ```bash
   caddy validate --config /etc/caddy/Caddyfile
   systemctl reload caddy
   ```
5. Verifizieren:
   ```bash
   echo | openssl s_client -connect skalantech.store:443 -servername skalantech.store -showcerts \
     | openssl x509 -noout -dates -issuer
   curl -s -o /dev/null -w "%{http_code}\n" https://skalantech.store
   ```

## Warum kein Let's Encrypt?
Bezahltes Sectigo-Zertifikat auf Wunsch von Xavier (Compliance/Kundenanforderung).
Konsequenz: **manuelle Erneuerung nötig** (Let's Encrypt erneuert sich automatisch).
Der tägliche Watchdog-Cron deckt das ab — keine stille Ausfallfalle.
