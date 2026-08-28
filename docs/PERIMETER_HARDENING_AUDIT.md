# Security-Audit: Öffentlicher Perimeter — Skalantech Hub (2026-08-27)

> Karte: t_9b14d915 · Reviewer: SENTINEL (QA, Security & Reliability)
> CEO-Freigabe: Website (Hub :80/:443) bleibt öffentlich (SEO), ALLES andere Tailscale-only.

## Zusammenfassung

| # | Prüfpunkt | Status |
|---|-----------|--------|
| 1 | Security-Header (CSP, HSTS, XFO, nosniff, Referrer-Policy) | ✅ Aktiv (App + Caddy) |
| 2 | Rate-Limiting öffentliche Routen (Login, Formulare, Terminbuchung) | ✅ Aktiv |
| 3 | Fail2Ban verifiziert + Jail HTTP-404-Scans | ✅ Aktiv (sshd + neu caddy-404) |
| 4 | Admin/Dashboard/Demos nur Tailscale | ✅ Verifiziert (externe Port-Checks) |
| 5 | Keine Secrets/Env in öffentlichen Fehlerseiten | ✅ Verifiziert + 500-Handler ergänzt |
| 6 | Monitoring 404/500-Alarm | ✅ Neu: http_alert.py + Cron (10 min) |
| 7 | Input-Validation öffentliche Formulare | ✅ Verifiziert |

## 1. Security-Header

Edge-verifiziert (`curl -sI https://skalantech.store/`):

- `Content-Security-Policy` — default-src 'self'; script/style 'self'
  (Admin/Login erlauben 'unsafe-inline' für Legacy-Templates), frame-ancestors
  'none', form-action 'self', object-src 'none', base-uri 'self'
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `X-Frame-Options: DENY` · `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cross-Origin-Opener-Policy: same-origin` · `Cross-Origin-Resource-Policy: same-origin`
- `Permissions-Policy` (camera/mic/geo/payment/usb deaktiviert)
- Kein `Server`-Header (Caddy `-Server`, gunicorn-Header gestrippt)

Quelle: app/utils/security.py (`after_request`), Caddyfile (HSTS/nosniff/
Referrer/-Server am Edge als Defense-in-Depth).

## 2. Rate-Limiting öffentlicher Routen

> **Nachtrag (Issue #4, 2026-08-28):** Storage ist jetzt zentral (Redis)
> statt `memory://` — Limits gelten exakt über alle 4 gunicorn-Worker.
> Siehe Abschnitt „Zentrales Rate-Limiting“ unten.

- `/login` (POST): flask-limiter 5/min + Account-Lockout 5×→5 min (DB, shared
  über Worker) — primärer Brute-Force-Schutz
- `/contact` (POST): flask-limiter 3/h/IP (Redis, zentral) + Honeypot +
  Feld-Limits — Terminbuchung läuft durch `/contact` und ist abgedeckt
- `/demo` (POST): flask-limiter 3/h/IP (Redis, zentral) — Demo-Anfragen der
  Branchen-Landingpages
- `/api/demos/<slug>` (POST): 8/h/IP (Redis, zentral) — n8n-Demos sind teuer
  (LLM), bewusst eng
- `/analytics/event` (POST): 120/min + Event-Allowlist + Payload-Limit 8 KB
- Storage: `skalantech-redis` Container (Host-Netzwerk, nur `127.0.0.1:6379`,
  AOF), Strategie `moving-window`; bei Breach 429-JSON für API/AJAX, sonst
  Flash + Redirect
- n8n-Webhooks selbst bleiben intern (127.0.0.1)

### Zentrales Rate-Limiting (Issue #4)

Problem: `memory://`-Storage ist pro gunicorn-Worker — mit `-w 4` war das
effektive Limit `Limit × 4` und pro Worker getrennt. Lösung: Redis als
zentraler Storage (`RATELIMIT_STORAGE_URI=redis://127.0.0.1:6379/0`), der
Kontaktformular-Limiter wurde von In-Memory-Dict auf flask-limiter
vereinheitlicht. Verifiziert durch `tests/test_ratelimit_storage.py`:
8 Requests verteilt auf 2 App-Instanzen erlaubt, 9. → 429; Counter überlebt
App-Neuinitialisierung (= Worker-Restart).

**Fail-safe:** `swallow_errors=false`, kein In-Memory-Fallback → bei
Redis-Ausfall antworten rate-limitierte Routen mit HTTP 500 (fail-closed),
Limits werden nie stillschweigend umgangen. Docker: `restart:
unless-stopped` + Healthcheck (siehe README „Zentrales Rate-Limiting“).

## 3. Fail2Ban

- Verifiziert: fail2ban 1.1.0 aktiv, Jail `sshd` (3 Versuche → 24 h, banaction
  ufw) — zum Audit-Zeitpunkt 2 aktive Bans (88.151.33.203, 176.65.139.181)
- CrowdSec läuft parallel (primäre IDS, Firewall-Bouncer) — kein Konflikt
- **Neu: Jail `caddy-404`** — 20× 404 in 10 min → 1 h Ban via UFW. Filter
  matcht Caddy-JSON-Access-Log (`"status":404`, datepattern `{epoch}`).
  Filter per `fail2ban-regex` getestet; Ban/Unban via Test-IP verifiziert
  (UFW-REJECT-Regel gesetzt + entfernt).

## 4. Admin/Dashboard/Demos: Tailscale-only verifiziert

Externe TCP-Checks (check-host.net, 3 Nodes je Port) auf 217.160.53.90:

| Port | Dienst | Extern | Ergebnis |
|------|--------|--------|----------|
| 443 | skalantech.store (CEO-Freigabe) | 200 OK | ✅ öffentlich gewollt |
| 3443 | DebtPilot-Demo | Connection timed out | ✅ Tailscale-only |
| 9443 | n8n (Admin) | Connection timed out | ✅ Tailscale-only |
| 9119 | Hermes-Dashboard | Connection timed out | ✅ Tailscale-only |

Absicherung:
- UFW: public nur 80/443/8644 (Webhook); Rest nur tailscale0
- DOCKER-USER: non-Tailscale-Traffic → DROP
- gunicorn bindet 127.0.0.1:5000 (nur Caddy-Host)
- Caddy: interne Sites (`:3443`, `:9443`) jetzt explizit `bind 100.119.11.64`
  (Defense-in-Depth: lauschen nicht mehr auf Public-Interfaces)

**Tote Subdomains:** dashboard/n8n/vault.skalantech.store haben öffentliche
CNAME-Records auf die Public-IP, aber keinen Dienst dahinter. dashboard lieferte
vorher **leeres HTTP 200** (SEO-irreführend). Fix: Caddy-Catch-all
`*.skalantech.store` → sauberes 404. **Offen (Level C, CEO/IONOS):** die
CNAME-Records selbst löschen (DNS-Änderung, benötigt IONOS-Zugriff).

## 5. Keine Secrets/Env in Fehlerseiten

- Verifiziert: `.env`/`.env.example`-Secrets nicht im Repo (`.gitignore`,
  `git ls-files`), instance/*.db ignoriert, Docker-Image schließt instance/ +
  .env aus (`.dockerignore`)
- 404-Seite: generisch, kein Traceback/Pfad/Env (Test abgesichert)
- **Neu: 500-Handler + 500.html** — generische Seite, Exception wird weiterhin
  in docker logs geloggt, aber nie im Response gerendert (DEBUG=False in
  Production)
- Caddy-Log redacted Set-Cookie automatisch (`"Set-Cookie":["REDACTED"]`)
- Regressionstests: tests/test_error_pages.py (404/500 leaken nichts)

## 6. Monitoring 404/500

- **Neu: Caddy-Access-Log** für skalantech.store → /var/log/caddy/skalantech-access.log
- **Neu: http_alert.py** (Watchdog): 5xx im 10-min-Fenster → 🔴,
  404-Spike (≥60 Anfragen oder ≥25 Pfade) → 🟡; leer = still
- **Neu: Cron** `780e40df5639` (alle 10 min, no_agent, → Telegram)

## 7. Input-Validation öffentlicher Formulare

- Kontaktformular: Feld-Limits (Name 120, E-Mail 254, Firma 160, Nachricht
  5000), Service-Allowlist, Honeypot, Privacy-Check, CSRF aktiv
- CRM-API: X-API-Key via `hmac.compare_digest` (timing-safe), Feld-Limits,
  Status-Allowlist, _MAX_LEADS=200
- Analytics: Event-Allowlist, Payload-Limit, Rate-Limit
- Uploads (Admin): Extension + MIME-Validierung, `secure_filename`, UUID-Namen,
  MAX_CONTENT_LENGTH=50 MB
- Login: `_safe_next_url` verhindert Open-Redirect

## Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| /etc/caddy/Caddyfile | Access-Log öffentliche Site, `bind 100.119.11.64` interne Sites, Catch-all `*.skalantech.store` → 404 |
| /etc/fail2ban/filter.d/caddy-404.conf | Neu: 404-Filter für Caddy-JSON-Log |
| /etc/fail2ban/jail.local | Neu: Jail caddy-404 (20×/10 min → 1 h) |
| app/__init__.py | 500-Error-Handler (generische Seite) |
| app/templates/500.html | Neu: 500-Seite (keine Interna) |
| tests/test_error_pages.py | Neu: Leak-Tests 404/500 + Header auf Fehlerseiten |
| ~/.hermes/profiles/sentinel/scripts/http_alert.py | Neu: 404/500-Alert-Monitor |

## Verifikation

- pytest: 83 passed, 127 subtests
- Externe Ports 3443/9443/9119: Timeout (check-host.net DE/IN/US, ES/ID, PL/UA)
- skalantech.store / und /login: 200 mit allen Security-Headern
- dashboard.skalantech.store: 404 (vorher leeres 200)
- fail2ban: 2 Jails aktiv, caddy-404 Ban/Unban getestet
- http_alert.py: synthetischer 5xx-Log → Alert ausgegeben

## Offene Punkte (Level C / CEO)

1. CNAME-Records dashboard/n8n/vault.skalantech.store bei IONOS löschen
   (DNS-Änderung)
2. Tailscale-only für /login + /admin sobald Admin-Geräte alle im Tailnet
   (bereits als Empfehlung aus t_3124abb3 dokumentiert)
3. Hermes-Dashboard bindet 0.0.0.0:9119 (UFW blockt public) — auf
   127.0.0.1 umbinden als Defense-in-Depth (Hermes-Konfig)
4. ✅ **Erledigt (Issue #4, 2026-08-28):** Kontaktformular-Limiter von
   In-Memory-Dict auf flask-limiter vereinheitlicht + zentraler Redis-Storage
   (siehe Abschnitt „Zentrales Rate-Limiting“).
