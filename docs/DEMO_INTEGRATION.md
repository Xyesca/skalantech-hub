# Demo-Integration — InvoiceFlow · OfferAI · MailAgent (P0)

Stand: 2026-08-27. Betrifft die produktiven Demo-Workflows in n8n und ihre
Einbindung auf den vier Branchen-Landingpages.

## 1. Produktive Demos (n8n)

Drei Demo-Workflows laufen **aktiv** in der selbstgehosteten n8n-Instanz
(`127.0.0.1:5678`, extern nur über Tailscale `ubuntu.piranha-gray.ts.net:9443`):

| Produkt      | Workflow-ID | Webhook (intern)          | Eingabe-Feld | Funktion                                     |
|--------------|-------------|---------------------------|--------------|----------------------------------------------|
| InvoiceFlow  | `400`       | `/webhook/demo-invoice`   | `invoice`    | Rechnungstext → strukturierte Rechnungsdaten  |
| OfferAI      | `401`       | `/webhook/demo-offer`     | `inquiry`    | Kundenanfrage → Angebotsentwurf (JSON)        |
| MailAgent    | `402`       | `/webhook/demo-mail`      | `mail`       | E-Mail → Klassifikation + Antwortvorschlag    |
| Lead-Erfassung | `8Xol9ORELU3HN29V` | `/webhook/lead-erfassung` | Formularfelder | Demo-/Kontakt-Leads validieren + ablegen |

- KI-Extraktion: **DeepSeek (primär)**, **Ollama lfm25 (Backup-Failover)**.
- Detail-Architektur, Schemata, Guardrails: siehe Demo-README aus
  `t_fa590264` (InvoiceFlow/OfferAI/MailAgent) bzw. `t_eb982f36`
  (Baustein „Lead-Erfassung").
- Alle Webhooks sind **nicht öffentlich**: n8n bindet auf Loopback, Zugriff
  nur über den Tailscale-Tunnel (Level-C-Freigabe für Public-Exposure steht aus).

## 2. Landingpage-Integration (Flask)

Auf den vier Branchen-Seiten (`/branchen/handwerk`, `/branchen/kfz`,
`/branchen/kanzleien`, `/branchen/immobilien`) rendert `_render_landing`
(`app/blueprints/public.py`) eine **Live-Demo-Sektion** (`id="demo"`):

- `page["demo"]` wird nur für `branchen-*`-Slugs gesetzt — Service-Seiten
  bleiben unverändert.
- Produktliste (InvoiceFlow/OfferAI/MailAgent) + Auswahl-Dropdown
  (`demo_type`) + Kontaktformular (`#demo-form`, CSRF + Honeypot).
- Formular wird per AJAX an die Route **`POST /demo`** gesendet
  (`app/blueprints/public.py` → `public.demo`).

## 3. Lead-Erfassung — Datenfluss

```
Landingpage (#demo-form)
  └─ POST /demo  (CSRF, Honeypot, Rate-Limit, Validierung)
       ├─ Lead in Flask-DB (Source of Truth) — Leads dedupliziert per E-Mail
       ├─ Analytics-Event "lead_created" (serverseitig, First-Party-Attribution)
       ├─ n8n "Lead-Erfassung" via N8N_LEAD_WEBHOOK_URL (best-effort)
       └─ Gmail-Notification (best-effort, silent)
```

- `N8N_LEAD_WEBHOOK_URL` (Default `http://127.0.0.1:5678/webhook/lead-erfassung`)
  ist ein reiner Default im Code; kein Secret, keine `.env`-Pflicht.
- n8n-Ausfall blockiert die Anfrage **nicht** — der Lead ist vorher bereits in
  der Flask-DB gespeichert (D3-Queued-Muster, konsistent zu `/contact`).
- n8n-Baustein dedupliziert zusätzlich per E-Mail und legt Leads in
  `/home/node/.n8n-files/leads.json` ab (dateibasiert, DB als Folgeschritt).

## 4. Sicherheit / Perimeter

- Tailscale-only bleibt bis CEO-Freigabe (Demos, n8n, Admin).
- Public erreichbar ist ausschließlich `skalantech.store` (Hub :80/:443, SEO).
- `/demo` trägt dieselben Schutzmechanismen wie `/contact`: CSRF, Honeypot,
  In-Memory-Rate-Limit (3/IP/Stunde), Eingabe-Längen-Caps.
- **DSGVO**: Demo-/Booking-Pfad verlangt **keine** erzwungene Einwilligung —
  Verarbeitung stützt sich auf Art. 6 Abs. 1 lit. b DSGVO (vorvertragliche
  Maßnahme). Statt Pflicht-Checkbox ein Hinweistext + Link zur
  Datenschutzerklärung (erzwungene Einwilligung wäre nach Art. 7 Abs. 4 DSGVO
  angreifbar). Nur das klassische Kontaktformular behält die serverseitige
  Privacy-Checkbox-Prüfung.
- Analytics: `form_field_error` + `form_success_view` sind in den Allowlists
  (`analytics.py` ANALYTICS_EVENTS + `analytics.js` EVENT_NAMES) aufgenommen.

## 5. Test-Evidenz

- **Unit/Integration**: `tests/test_demo.py` (6 Tests) — Rendering, valide
  Anfrage, Validierung, Honeypot, n8n-unreachable-Fallback.
  Gesamtsuite: `pytest tests/ -q` → 101 passed, 137 subtests.
- **E2E (Live, 2026-08-27)**: GET `/branchen/handwerk` (CSRF-Token aus
  `#demo-form`) → POST `/demo` → HTTP 200 `success:true`; Lead in Flask-DB
  (`leads`, service="Demo: InvoiceFlow …", campaign="branche_handwerk")
  verifiziert; n8n-Execution `239` (workflow `8Xol9ORELU3HN29V`)
  `status=success`, Lead in `leads.json`. Testdaten anschließend entfernt.

## 6. Betrieb / Rollback

- Redeploy: `docker compose up -d --build skalantech`.
- n8n-Workflows sind die Single Source of Truth ihrer JSONs
  (`wf-demo-*.json`, `block-lead-erfassung.json`); Rollback über n8n-Versionen
  oder JSON-Neuaufbau.
- Verifikation Live: `curl -s https://skalantech.store/branchen/handwerk | grep -c 'id="demo"'` → 1.
