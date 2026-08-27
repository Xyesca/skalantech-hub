#!/usr/bin/env python3
"""Skalantech CRM — Follow-up-Poller (tägliche Automation).

Pollt die CRM-API des Skalantech Hub (`GET /api/crm/leads?due_followup=1`)
und alarmiert den internen Vertriebs-Kanal per Telegram, wenn Follow-ups
fällig sind. Optional: Leads, deren Follow-up seit N Tagen überfällig ist,
werden automatisch auf `lost` (Keine Rückmeldung) gesetzt.

Betrieb: Hermes-Cron „crm-followup-daily" (täglich 08:00 UTC, no_agent).
Manuell:  python3 scripts/crm_followup.py [--dry-run]

Keine externen Abhängigkeiten (nur stdlib). Sendet NIE E-Mails an Kunden —
nur interne Telegram-Erinnerung. Secrets kommen aus .env-Dateien und werden
nicht ausgegeben.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HUB_ENV = "/root/skalantech-hub/.env"
HERMES_ENV = "/root/.hermes/.env"
API_BASE = "http://localhost:5000/api/crm"
REPORT_DIR = "/root/skalantech-hub/instance/followup"
FALLBACK_CHAT_ID = "-1003956152501"  # Telegram-Kanal „AiGents" (n8n-Terminbuchung nutzt denselben)
AUTO_LOST_AFTER_DAYS = int(os.environ.get("CRM_AUTO_LOST_AFTER_DAYS", "0"))


def load_env(path):
    """Lese KEY=VALUE-Zeilen aus einer .env-Datei (ohne Werte auszugeben)."""
    values = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    values[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return values


def http_json(method, url, headers=None, payload=None, timeout=10):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return e.code, {"error": body}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": str(e)}


def telegram_send(token, chat_id, text):
    """Sende eine HTML-Nachricht an den Telegram-Kanal. Returns (ok, detail)."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    status, data = http_json(
        "POST", url,
        headers={"Content-Type": "application/json"},
        payload={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
        timeout=15,
    )
    if status == 200:
        return True, "ok"
    return False, str(data.get("error", data))[:200]


def telegram_get_me(token):
    """Prüfe, ob das Bot-Token gültig ist."""
    status, data = http_json("GET", f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    return status == 200 and data.get("ok") is True


def esc(v):
    return str(v or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _as_utc(dt):
    """SQLite liefert naive datetimes — als UTC interpretieren."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def fmt_dt(iso):
    if not iso:
        return "–"
    try:
        dt = _as_utc(datetime.fromisoformat(str(iso).replace("Z", "+00:00")))
        return dt.astimezone().strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return str(iso)


def overdue_days(iso, now):
    try:
        dt = _as_utc(datetime.fromisoformat(str(iso).replace("Z", "+00:00")))
        return max(0, int((now - dt).total_seconds() // 86400))
    except ValueError:
        return 0


def build_message(leads, now):
    lines = [
        "<b>CRM · Follow-ups fällig</b>",
        f"{len(leads)} Lead(s) warten auf Kontakt:",
        "",
    ]
    for i, lead in enumerate(leads, 1):
        overdue = overdue_days(lead.get("next_followup_at"), now)
        tag = f" ⚠️ {overdue} Tag(e) überfällig" if overdue > 0 else ""
        lines.append(
            f"{i}. <b>{esc(lead.get('name'))}</b>"
            + (f" · {esc(lead.get('company'))}" if lead.get("company") else "")
            + (f" · {esc(lead.get('service'))}" if lead.get("service") else "")
            + f"{tag}\n"
            f"   Stufe: {esc(lead.get('status_label'))}"
            + (f" · Wert: {lead.get('value_estimate', 0):,} €" if lead.get("value_estimate") else "")
            + f"\n   Follow-up: {fmt_dt(lead.get('next_followup_at'))}"
            + f"\n   Angelegt: {fmt_dt(lead.get('created_at'))}"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CRM Follow-up-Poller")
    parser.add_argument("--dry-run", action="store_true", help="Nichts senden/ändern, nur Report")
    args = parser.parse_args()
    dry_run = args.dry_run or os.environ.get("CRM_DRY_RUN", "0") == "1"

    hub_env = load_env(HUB_ENV)
    hermes_env = load_env(HERMES_ENV)

    api_key = hub_env.get("CRM_API_KEY", "")
    bot_token = hermes_env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = hermes_env.get("TELEGRAM_HOME_CHANNEL", "") or FALLBACK_CHAT_ID

    if not api_key:
        print("ERROR: CRM_API_KEY fehlt in %s" % HUB_ENV)
        return 2

    # Bot-Token prüfen (kein Secret im Output)
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN fehlt in %s" % HERMES_ENV)
        return 2
    if not dry_run and not telegram_get_me(bot_token):
        print("WARN: Telegram-Bot nicht erreichbar (Token ungültig?) — nur Report")
        bot_token = ""

    now = datetime.now(timezone.utc)

    # 1) Fällige Follow-ups abrufen
    status, data = http_json(
        "GET", f"{API_BASE}/leads?due_followup=1",
        headers={"X-API-Key": api_key}, timeout=15,
    )
    if status != 200:
        print(f"ERROR: API {status}: {data.get('error', data)}")
        return 2

    leads = data.get("leads", [])
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, datetime.now(timezone.utc).strftime("%Y%m%d.json"))
    report = {
        "run_at": now.isoformat(),
        "dry_run": dry_run,
        "due_count": len(leads),
        "leads": leads,
    }

    if not leads:
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2, default=str)
        print("OK: keine fälligen Follow-ups (Report %s)" % report_path)
        return 0

    # 2) Telegram-Alarm (interner Kanal, kein Kunden-Versand)
    sent = 0
    if not dry_run and bot_token:
        msg = build_message(leads, now)
        # Telegram-Limit 4096 Zeichen — bei Bedarf aufteilen
        chunks = [msg[i:i + 3900] for i in range(0, len(msg), 3900)]
        for chunk in chunks:
            ok, detail = telegram_send(bot_token, chat_id, chunk)
            if ok:
                sent += 1
            else:
                print(f"WARN: Telegram-Send fehlgeschlagen: {detail}")
                break
    elif dry_run:
        msg = build_message(leads, now)
        n_chunks = max(1, (len(msg) + 3899) // 3900)
        print(f"DRY-RUN: würde {n_chunks} Telegram-Nachricht(en) an {chat_id} senden")
    report["telegram_sent"] = sent

    # 3) Optional: überfällige Leads automatisch auf lost setzen
    auto_lost = []
    if AUTO_LOST_AFTER_DAYS > 0 and not dry_run:
        for lead in leads:
            od = overdue_days(lead.get("next_followup_at"), now)
            if od >= AUTO_LOST_AFTER_DAYS:
                patch_status, patch_data = http_json(
                    "PATCH", f"{API_BASE}/leads/{lead['id']}",
                    headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                    payload={
                        "status": "lost",
                        "lost_reason": "Keine Rückmeldung",
                        "note": f"Automatisch verloren nach {od} Tagen ohne Reaktion (Follow-up-Poller)",
                    },
                    timeout=10,
                )
                if patch_status == 200:
                    auto_lost.append(lead["id"])
                else:
                    print(f"WARN: Auto-Lost Lead {lead['id']} fehlgeschlagen: {patch_data.get('error', patch_data)}")
    elif AUTO_LOST_AFTER_DAYS > 0 and dry_run:
        auto_lost = [l["id"] for l in leads if overdue_days(l.get("next_followup_at"), now) >= AUTO_LOST_AFTER_DAYS]
        print(f"DRY-RUN: würde {len(auto_lost)} Lead(s) als lost markieren (Threshold {AUTO_LOST_AFTER_DAYS} Tage)")
    report["auto_lost"] = auto_lost

    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, default=str)

    print(f"OK: {len(leads)} fällige Follow-up(s), Telegram-Sends: {sent}, Auto-Lost: {len(auto_lost)} (Report {report_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
