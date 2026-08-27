"""Skalantech Hub — Public routes."""
import json
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from urllib import request as urlrequest

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, redirect, url_for, jsonify, Response, abort
from app.models import Settings, Link, Project, ContactMessage, Lead
from app.extensions import db
from app.seo_pages import LANDING_PAGES, LANDING_ORDER
from app.branchen import BRANCH_ORDER
from app.wissen import ARTICLES, ARTICLE_ORDER, ARTICLE_PUBLISHED
from app.blueprints.analytics import _record_event

public_bp = Blueprint("public", __name__)

# ── n8n-Terminwebhook (intern, Tailscale) ─────────────────────────────
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/skalantech-termin")

# ── SEO: indexierbare Seiten für Sitemap & robots ──────────────────────
SITE_URL = "https://skalantech.store"

SITEMAP_PAGES = [
    {"loc": "/", "priority": "1.0"},
    {"loc": "/koeln", "priority": "0.8"},
    *[{"loc": f"/{slug}", "priority": "0.8"} for slug in LANDING_ORDER],
    *[{"loc": f"/branchen/{slug}", "priority": "0.8"} for slug in BRANCH_ORDER],
    {"loc": "/wissen", "priority": "0.7"},
    *[{"loc": f"/wissen/{slug}", "priority": "0.7"} for slug in ARTICLE_ORDER],
    {"loc": "/faq", "priority": "0.6"},
]

ROBOTS_TXT = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /login
Disallow: /auth
Disallow: /test-footer

Sitemap: {SITE_URL}/sitemap.xml
"""


def _forward_to_n8n(name, email, company, topic, message, preferred_day, preferred_time):
    """Send a booking request to the n8n workflow.

    Returns a dict:
        success : bool  — True only when n8n explicitly returns ``success:true``.
        status  : str   — "confirmed" (n8n ok) | "slot_taken" (n8n success:false)
                          | "invalid_response" (n8n lieferte kein valides JSON/HTTP-Fehler)
                          | "unreachable" (n8n down/timeout).
        message : str   — human-readable (bei "slot_taken" 1:1 die n8n-Message).
    """
    payload = {
        "name": name,
        "email": email,
        "company": company,
        "topic": topic or "Erstgespräch",
        "message": message,
        "preferred_day": preferred_day,
        "preferred_time": preferred_time,
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                parsed = None
            # Nur ein explizites success:true im JSON zählt als Buchung.
            # n8n liefert bei internen Workflow-Fehlern (z. B. Kalender-Credential
            # abgelaufen) HTTP 200 mit leerem/Fehler-Body — das ist eine echte
            # n8n-Störung (invalid_response), keine „belegt“-Antwort.
            if parsed is None or resp.status >= 400:
                return {
                    "success": False,
                    "status": "invalid_response",
                    "message": "Termindienst hat keine gültige Antwort geliefert.",
                }
            if parsed.get("success") is True:
                return {"success": True, "status": "confirmed", "message": parsed.get("message", "ok")}
            # success:false = Slot belegt / ungültiger Wunsch (normaler Nutzerpfad).
            return {
                "success": False,
                "status": "slot_taken",
                "message": parsed.get("message", "Der gewünschte Termin ist leider nicht verfügbar."),
            }
    except Exception:
        # n8n nicht erreichbar (down/timeout) — Anfrage bleibt in der DB, kein Block für den Nutzer
        return {
            "success": False,
            "status": "unreachable",
            "message": "Termindienst nicht erreichbar.",
        }

# ── Contact form rate-limiting (in-memory, single-instance) ──────────────
_CONTACT_LIMITS: dict[str, list[float]] = {}
_CONTACT_MAX = 3          # max messages per IP
_CONTACT_WINDOW = 3600    # sliding window in seconds (1 hour)

_SERVICE_CHOICES = {
    "Infrastruktur & Cloud",
    "Prozessautomatisierung",
    "KI-Agenten & RAG",
    "Betrieb & Reliability",
    "System-Check / Beratung",
    "Erstgespräch",
    "Etwas anderes",
}


def _client_ip() -> str:
    """Get real client IP behind reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _check_contact_limit(ip: str) -> bool:
    """Sliding-window rate limit. Returns True if allowed."""
    now = time.time()
    window_start = now - _CONTACT_WINDOW

    timestamps = _CONTACT_LIMITS.get(ip, [])
    # Prune old entries
    timestamps = [t for t in timestamps if t > window_start]

    if len(timestamps) >= _CONTACT_MAX:
        _CONTACT_LIMITS[ip] = timestamps
        return False

    timestamps.append(now)
    _CONTACT_LIMITS[ip] = timestamps
    return True


def _send_email(name: str, email: str, text: str) -> bool:
    """Send contact notification via Gmail SMTP. Returns True on success."""
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_pass:
        return False  # SMTP not configured — just save to DB

    msg = MIMEText(
        f"Neue Kontaktanfrage von {name} ({email}):\n\n{text}",
        "plain", "utf-8",
    )
    msg["Subject"] = f"Skalantech Kontakt: {name}"
    msg["From"] = gmail_user
    msg["To"] = gmail_user

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, [gmail_user], msg.as_string())
        return True
    except Exception:
        return False


@public_bp.route("/")
def index():
    settings = Settings.get()
    links = (
        Link.query
        .filter_by(visible=True)
        .order_by(Link.position.asc(), Link.id.asc())
        .all()
    )
    projects = (
        Project.query
        .filter_by(visible=True)
        .order_by(Project.position.asc(), Project.id.asc())
        .all()
    )
    today = time.strftime("%Y-%m-%d")
    max_booking_day = time.strftime("%Y-%m-%d", time.localtime(time.time() + 90 * 86400))
    return render_template("index.html", settings=settings, links=links, projects=projects, today=today, max_booking_day=max_booking_day)


# ── SEO Landingpages (eine View, mehrere explizite Routen) ────────────────
def _landing_map():
    """Landing-Daten + fertige URLs für Templates."""
    return {
        s: {**p, "slug": s, "url": url_for(f"public.landing_{s.replace('-', '_')}")}
        for s, p in LANDING_PAGES.items()
    }


def _utm_campaign(slug: str) -> str:
    """UTM-Kampagnen-Slug: Branchen → branche_{slug}, Service-Seiten → {slug}."""
    if slug.startswith("branchen-"):
        return "branche_" + slug[len("branchen-"):]
    return slug


def _build_jsonld(page: dict, page_url: str) -> str:
    """Service + BreadcrumbList + FAQPage als einzeln valides JSON (kein Fake)."""
    graph = [
        {
            "@type": "Service",
            "@id": f"{page_url}#service",
            "name": page["breadcrumb"],
            "description": page["description"],
            "serviceType": page["breadcrumb"],
            "provider": {"@id": f"{SITE_URL}/#business"},
            "areaServed": {"@type": "Country", "name": "Deutschland"},
            "url": page_url,
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{page_url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": page["breadcrumb"], "item": page_url},
            ],
        },
    ]
    faqs = page.get("faqs")
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{page_url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def _render_landing(slug: str):
    """Render a SEO landing page from seo_pages.py."""
    if slug not in LANDING_PAGES:
        abort(404)
    page = dict(LANDING_PAGES[slug])
    path = url_for(f"public.landing_{slug.replace('-', '_')}")
    page["slug"] = slug
    page["url"] = path
    page["canonical_url"] = SITE_URL + path

    # CTA-Texte (Defaults für Service-Seiten; Branchen liefern eigene)
    page.setdefault("cta_primary", "Kostenloses Erstgespräch")
    page.setdefault("cta_secondary", "Projekt besprechen")
    page.setdefault("cta_final_title", "Klingt nach Ihrem Thema?")
    page.setdefault("cta_final_text", "30 Minuten, unverbindlich. Wir klären, ob und wie Skalantech Sie unterstützen kann.")
    page.setdefault("cta_final", page["cta_primary"])
    # cta_mid ist branchen-spezifisch (Momentum-CTA nach ROI) — kein Default,
    # damit Service-Seiten unverändert bleiben.

    # CTA-Ziele mit UTM. Query VOR Fragment (#termin/#contact) — sonst gehen
    # die UTM-Parameter verloren (Fragment wird nicht an den Server gesendet).
    query = f"utm_source=organic&utm_medium=landing&utm_campaign={_utm_campaign(slug)}"
    base = url_for("public.index")
    page["cta_termin_url"] = f"{base}?{query}#termin"
    page["cta_contact_url"] = f"{base}?{query}#contact"

    # Related-Artikel (/wissen) auflösen → {slug, title, url}
    page["related_articles_resolved"] = [
        {"slug": a_slug, "title": ARTICLES[a_slug]["h1"], "url": url_for("public.article", slug=a_slug)}
        for a_slug in page.get("related_articles", [])
        if a_slug in ARTICLES
    ]

    # Strukturierte Daten als einzeln valides JSON (kein Fake)
    page["jsonld"] = _build_jsonld(page, page["canonical_url"])

    return render_template(
        "landing.html",
        landing_page=page,
        landing_map=_landing_map(),
    )


@public_bp.route("/it-infrastruktur")
def landing_it_infrastruktur():
    return _render_landing("it-infrastruktur")


@public_bp.route("/ki-integration")
def landing_ki_integration():
    return _render_landing("ki-integration")


@public_bp.route("/ki-automatisierung")
def landing_ki_automatisierung():
    return _render_landing("ki-automatisierung")


@public_bp.route("/ki-agenten")
def landing_ki_agenten():
    return _render_landing("ki-agenten")


@public_bp.route("/n8n-automatisierung")
def landing_n8n_automatisierung():
    return _render_landing("n8n-automatisierung")


@public_bp.route("/lokale-ki")
def landing_lokale_ki():
    return _render_landing("lokale-ki")


# ── Branchen-Landingpages (explizite Routen, kein Catch-All) ──────────
@public_bp.route("/branchen/handwerk")
def landing_branchen_handwerk():
    return _render_landing("branchen-handwerk")


@public_bp.route("/branchen/kfz")
def landing_branchen_kfz():
    return _render_landing("branchen-kfz")


@public_bp.route("/branchen/kanzleien")
def landing_branchen_kanzleien():
    return _render_landing("branchen-kanzleien")


@public_bp.route("/branchen/immobilien")
def landing_branchen_immobilien():
    return _render_landing("branchen-immobilien")


@public_bp.route("/koeln")
def landing_koeln():
    return render_template(
        "local_koeln.html",
        landing_map=_landing_map(),
    )


# ── Wissensstruktur ────────────────────────────────────────────────────
@public_bp.route("/wissen")
def wissen():
    return render_template(
        "wissen.html",
        article_map=ARTICLES,
        article_order=ARTICLE_ORDER,
        article_published=ARTICLE_PUBLISHED,
        landing_map=_landing_map(),
    )


@public_bp.route("/wissen/<slug>")
def article(slug: str):
    if slug not in ARTICLES:
        abort(404)
    article_data = {**ARTICLES[slug], "slug": slug}
    return render_template(
        "article.html",
        article_data=article_data,
        article_published=ARTICLE_PUBLISHED,
        landing_map=_landing_map(),
    )


@public_bp.route("/robots.txt")
def robots_txt():
    """Serve crawler instructions from the canonical application route."""
    return Response(ROBOTS_TXT, mimetype="text/plain")


@public_bp.route("/sitemap.xml")
def sitemap_xml():
    """Sitemap generated from the explicit indexable-pages list."""
    today = time.strftime("%Y-%m-%d")
    urls = "\n".join(
        f'  <url><loc>{SITE_URL}{p["loc"]}</loc><lastmod>{today}</lastmod><priority>{p["priority"]}</priority></url>'
        for p in SITEMAP_PAGES
    )
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""
    return Response(content, mimetype="application/xml")


# ── Legal Pages ──────────────────────────────────────────────────────
@public_bp.route("/impressum")
def impressum():
    settings = Settings.get()
    return render_template("legal/impressum.html", settings=settings)

@public_bp.route("/datenschutz")
def datenschutz():
    settings = Settings.get()
    return render_template("legal/datenschutz.html", settings=settings)

@public_bp.route("/agb")
def agb():
    settings = Settings.get()
    return render_template("legal/agb.html", settings=settings)

@public_bp.route("/faq")
def faq():
    settings = Settings.get()
    return render_template("legal/faq.html", settings=settings)

@public_bp.route("/contact", methods=["POST"])
def contact():
    name = " ".join(request.form.get("name", "").split())
    email = request.form.get("email", "").strip()
    company = " ".join(request.form.get("company", "").split())
    service = request.form.get("service", "").strip()
    message_text = request.form.get("message", "").strip()
    privacy = request.form.get("privacy", "")
    honeypot = request.form.get("website", "").strip()

    # Quietly accept obvious bot submissions without storing or sending them.
    if honeypot:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=True, message="Vielen Dank. Ihre Anfrage wurde übermittelt.")
        return redirect(url_for("public.index", _anchor="contact"))

    # ── Validierung ──────────────────────────────────────────────────
    errors = []
    if not name or len(name) > 120:
        errors.append("Bitte geben Sie einen gültigen Namen ein.")
    if not email or "@" not in email or len(email) > 254:
        errors.append("Bitte geben Sie eine gültige E-Mail-Adresse ein.")
    if len(company) > 160:
        errors.append("Der Unternehmensname ist zu lang.")
    if service and service not in _SERVICE_CHOICES:
        errors.append("Bitte wählen Sie ein gültiges Anliegen aus.")
    if not message_text:
        errors.append("Bitte beschreiben Sie kurz Ihre Ausgangslage.")
    if len(message_text) > 5000:
        errors.append("Nachricht ist zu lang (max. 5000 Zeichen).")
    if privacy != "accepted":
        errors.append("Bitte bestätigen Sie die Datenschutzerklärung.")

    # ── Rate-Limiting ────────────────────────────────────────────────
    if not errors:
        ip = _client_ip()
        if not _check_contact_limit(ip):
            errors.append("Zu viele Anfragen. Bitte versuchen Sie es später erneut.")

    if errors:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message='; '.join(errors)), 400
        for err in errors:
            flash(err, "error")
        return redirect(url_for("public.index", _anchor="contact"))

    # ── Speichern + optional E-Mail ──────────────────────────────────
    # ROI-Kontext (LUMINA-Spez): NUR validierter Bucket aus dem Rechner,
    # nie ein Rohwert — serverseitig gegen feste Whitelist geprüft.
    roi_context = (request.form.get("roi_context") or "").strip()
    ROI_BUCKETS = {"h_lt_150", "h_150_400", "h_gt_400"}
    if roi_context not in ROI_BUCKETS:
        roi_context = ""

    context = []
    if company:
        context.append(f"Unternehmen: {company}")
    if service:
        context.append(f"Anliegen: {service}")
    if roi_context:
        context.append(f"ROI-Rechner: {roi_context}")
    stored_message = "\n".join(context + ([""] if context else []) + [message_text])

    # First-Party-Attribution: UTM-Parameter + Referrer (keine Cookies,
    # kein Tracker — nur technische Metadaten dieser einen Anfrage).
    # analytics.js legt die beim Seitenaufruf erfassten UTM-/Session-Werte
    # als Hidden-Fields ins Formular (Fallback: Query-String des POST).
    session_id = (request.form.get("session_id") or request.args.get("session_id") or "").strip()[:64]
    source = (request.form.get("utm_source") or request.args.get("utm_source") or "").strip()[:120]
    medium = (request.form.get("utm_medium") or request.args.get("utm_medium") or "").strip()[:60]
    campaign = (request.form.get("utm_campaign") or request.args.get("utm_campaign") or "").strip()[:160]
    referrer = (request.referrer or "").strip()[:512]

    msg = ContactMessage(
        name=name, email=email, message=stored_message,
        source=source, medium=medium, campaign=campaign, referrer=referrer,
        session_id=session_id,
    )
    db.session.add(msg)

    # ── CRM: Lead aus der Kontaktanfrage erzeugen/aktualisieren ──────
    # Dedupe per E-Mail — wiederholte Anfragen aktualisieren denselben Lead.
    lead = Lead.query.filter_by(email=email, is_archived=False).first()
    if lead is None:
        lead = Lead(name=name, email=email, status="lead", session_id=session_id)
        db.session.add(lead)
    elif not lead.session_id:
        # First-Touch: Session nur setzen, wenn noch keine bekannt ist
        lead.session_id = session_id
    lead.company = company
    lead.service = service
    lead.message = message_text
    if source:
        lead.source = source
    if medium:
        lead.medium = medium
    if campaign:
        lead.campaign = campaign
    if referrer:
        lead.referrer = referrer
    lead.last_contact_at = datetime.now(timezone.utc)
    db.session.commit()

    # ── Analytics: Conversion-Events (serverseitig — verlustsicher, auch
    # ohne JavaScript-Client; Spezifikation: docs/ANALYTICS_EVENTS.md) ──
    _attribution = dict(
        page="/", session_id=session_id,
        source=source, medium=medium, campaign=campaign, referrer=referrer,
    )
    _record_event("lead_created", props={"service": service or "allgemein"}, **_attribution)

    _send_email(name, email, stored_message)  # silent — don't block on failure

    # ── Terminanfrage: Webhook an n8n (nur bei Terminwunsch) ─────────
    n8n_result = None
    if request.form.get("book_slot") == "1":
        # Anfrage angenommen (unabhängig vom n8n-Status) = Demo-Flow abgeschlossen
        _record_event("demo_completed", props={"service": "Erstgespräch"}, **_attribution)
        day = request.form.get("preferred_day", "").strip()
        slot = request.form.get("preferred_time", "").strip()
        n8n_result = _forward_to_n8n(
            name=name, email=email, company=company,
            topic=service or "Erstgespräch", message=message_text,
            preferred_day=day, preferred_time=slot,
        )
        if n8n_result and n8n_result.get("success"):
            # Erfolgreiche Buchung = qualifizierter Lead (Discovery folgt im Termin)
            if lead.status != "qualified":
                lead.set_status("qualified", reason="Termin über skalantech.store gebucht", author="Website")
            lead.add_note(f"Terminwunsch bestätigt: {day} {slot}".strip(), author="Website")
            lead.last_contact_at = datetime.now(timezone.utc)
            db.session.commit()
            # n8n hat bestätigt = echte Buchung
            _record_event(
                "meeting_booked",
                props={"day": day, "time": slot, "service": "Erstgespräch"},
                **_attribution,
            )
        elif n8n_result and n8n_result.get("status") in ("unreachable", "invalid_response"):
            # n8n down/timeout/invalid → Lead ist bereits gespeichert (kein Verlust).
            # booking_error NUR bei echter n8n-Störung — nicht bei „Slot belegt“.
            reason = "unreachable" if n8n_result.get("status") == "unreachable" else "invalid_response"
            _record_event("booking_error", props={"reason": reason}, **_attribution)
        # status == "slot_taken": normaler Nutzerpfad — kein Event, Lead bleibt "lead".

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if n8n_result is not None:
            if n8n_result.get("success"):
                booking = {
                    "day": request.form.get("preferred_day", "").strip(),
                    "time": request.form.get("preferred_time", "").strip(),
                    "status": "confirmed",
                }
                return jsonify(
                    success=True,
                    message="Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.",
                    booking=booking,
                )
            if n8n_result.get("status") in ("unreachable", "invalid_response"):
                # D3: Lead gespeichert, kein 409 — queued-Erfolgsansicht.
                booking = {
                    "day": request.form.get("preferred_day", "").strip(),
                    "time": request.form.get("preferred_time", "").strip(),
                    "status": "queued",
                }
                return jsonify(
                    success=True,
                    message="Ihre Anfrage ist angekommen — wir melden uns innerhalb von 24 h mit einem Terminvorschlag.",
                    booking=booking,
                )
            # D2: Slot belegt → n8n-Message 1:1, success:false, HTTP 200 (kein 409).
            return jsonify(
                success=False,
                message=n8n_result.get("message", "Der gewünschte Termin ist leider nicht verfügbar."),
            )
        return jsonify(success=True, message='Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.')

    # ── Non-AJAX-Fallback (ohne JavaScript) ───────────────────────────
    if n8n_result is not None:
        if n8n_result.get("success"):
            flash("Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.", "success")
        elif n8n_result.get("status") in ("unreachable", "invalid_response"):
            flash("Ihre Anfrage ist angekommen — wir melden uns innerhalb von 24 h mit einem Terminvorschlag.", "success")
        else:
            flash(n8n_result.get("message", "Der gewünschte Termin ist leider nicht verfügbar."), "error")
        return redirect(url_for("public.index", _anchor="termin"))
    flash("Vielen Dank. Ihre Anfrage wurde erfolgreich gesendet.", "success")
    return redirect(url_for("public.index", _anchor="contact"))


@public_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve user-uploaded media from the instance/uploads directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
