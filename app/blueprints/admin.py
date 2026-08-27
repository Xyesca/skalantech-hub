"""Skalantech Hub — Admin CRUD routes."""
from datetime import datetime, timezone

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import (
    Settings, Link, Project, Admin, ContactMessage,
    Lead, LeadNote, PIPELINE_STAGES, PIPELINE_TERMINAL, PIPELINE_FLOW, LOST_REASONS,
)
from app.utils.uploads import save_upload, delete_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
_VIDEO_EXT = {"mp4", "webm", "mov"}


# ── Auth guard for every admin request ────────────────────────────────────
@admin_bp.before_request
def _require_login():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login", next=request.path))


# ── Root redirect ─────────────────────────────────────────────────────────
@admin_bp.route("/")
def root():
    return redirect(url_for("admin.settings"))


# ══════════════════════════════════════════════════════════════════════════
# Settings
# ══════════════════════════════════════════════════════════════════════════
@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    s = Settings.get()

    if request.method == "POST":
        s.name = request.form.get("name", "").strip()[:120] or s.name
        s.tagline = request.form.get("tagline", "").strip()[:240]
        s.location = request.form.get("location", "").strip()[:120]
        s.about = request.form.get("about", "").strip()

        hero_file = request.files.get("hero_file")
        if hero_file and hero_file.filename:
            ext = hero_file.filename.rsplit(".", 1)[-1].lower() if "." in hero_file.filename else ""
            if ext in _IMAGE_EXT:
                saved = save_upload(hero_file, _IMAGE_EXT)
                if saved:
                    delete_upload(s.hero_path)
                    s.hero_path = saved
                    s.hero_type = "image"
            elif ext in _VIDEO_EXT:
                saved = save_upload(hero_file, _VIDEO_EXT)
                if saved:
                    delete_upload(s.hero_path)
                    s.hero_path = saved
                    s.hero_type = "video"
            else:
                flash("Dateiformat nicht unterstützt.", "error")

        if request.form.get("remove_hero") == "1":
            delete_upload(s.hero_path)
            s.hero_path = ""
            s.hero_type = "none"

        db.session.commit()
        flash("Gespeichert.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", settings=s)


# ══════════════════════════════════════════════════════════════════════════
# Password
# ══════════════════════════════════════════════════════════════════════════
@admin_bp.route("/password", methods=["POST"])
def change_password():
    current = request.form.get("current_password", "")
    new = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    admin = Admin.query.filter_by(username=session.get("username")).first()
    if not admin or not check_password_hash(admin.password_hash, current):
        flash("Aktuelles Passwort ist falsch.", "error")
    elif len(new) < 8:
        flash("Neues Passwort muss mindestens 8 Zeichen haben.", "error")
    elif new != confirm:
        flash("Die neuen Passwörter stimmen nicht überein.", "error")
    else:
        admin.password_hash = generate_password_hash(new)
        db.session.commit()
        flash("Passwort geändert.", "success")

    return redirect(url_for("admin.settings"))


# ══════════════════════════════════════════════════════════════════════════
# Links
# ══════════════════════════════════════════════════════════════════════════
@admin_bp.route("/links", methods=["GET", "POST"])
def links():
    if request.method == "POST":
        label = request.form.get("label", "").strip()
        url_val = request.form.get("url", "").strip()
        platform = request.form.get("platform", "link")
        position = int(request.form.get("position") or 0)
        if not label or not url_val:
            flash("Label und URL sind erforderlich.", "error")
        else:
            db.session.add(Link(
                label=label, url=url_val,
                platform=platform, position=position, visible=True,
            ))
            db.session.commit()
            flash("Link hinzugefügt.", "success")
        return redirect(url_for("admin.links"))

    all_links = Link.query.order_by(Link.position.asc(), Link.id.asc()).all()
    return render_template("admin/links.html", links=all_links)


@admin_bp.route("/links/<int:link_id>/edit", methods=["POST"])
def links_edit(link_id):
    link = db.get_or_404(Link, link_id)
    link.label = request.form.get("label", link.label).strip()
    link.url = request.form.get("url", link.url).strip()
    link.platform = request.form.get("platform", link.platform)
    link.position = int(request.form.get("position") or link.position)
    db.session.commit()
    flash("Link aktualisiert.", "success")
    return redirect(url_for("admin.links"))


@admin_bp.route("/links/<int:link_id>/toggle", methods=["POST"])
def links_toggle(link_id):
    link = db.get_or_404(Link, link_id)
    link.visible = not link.visible
    db.session.commit()
    return redirect(url_for("admin.links"))


@admin_bp.route("/links/<int:link_id>/delete", methods=["POST"])
def links_delete(link_id):
    link = db.get_or_404(Link, link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link gelöscht.", "success")
    return redirect(url_for("admin.links"))


# ══════════════════════════════════════════════════════════════════════════
# Projects / Apps
# ══════════════════════════════════════════════════════════════════════════
@admin_bp.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        url_val = request.form.get("url", "").strip()
        position = int(request.form.get("position") or 0)
        if not title:
            flash("Titel ist erforderlich.", "error")
        else:
            image_path = save_upload(request.files.get("image"), _IMAGE_EXT) or ""
            db.session.add(Project(
                title=title, description=description,
                url=url_val, image_path=image_path,
                position=position, visible=True,
            ))
            db.session.commit()
            flash("Projekt hinzugefügt.", "success")
        return redirect(url_for("admin.projects"))

    all_projects = Project.query.order_by(Project.position.asc(), Project.id.asc()).all()
    return render_template("admin/projects.html", projects=all_projects)


@admin_bp.route("/projects/<int:project_id>/edit", methods=["POST"])
def projects_edit(project_id):
    project = db.get_or_404(Project, project_id)
    project.title = request.form.get("title", project.title).strip()
    project.description = request.form.get("description", project.description).strip()
    project.url = request.form.get("url", project.url).strip()
    project.position = int(request.form.get("position") or project.position)
    new_image = save_upload(request.files.get("image"), _IMAGE_EXT)
    if new_image:
        delete_upload(project.image_path)
        project.image_path = new_image
    db.session.commit()
    flash("Projekt aktualisiert.", "success")
    return redirect(url_for("admin.projects"))


@admin_bp.route("/projects/<int:project_id>/toggle", methods=["POST"])
def projects_toggle(project_id):
    project = db.get_or_404(Project, project_id)
    project.visible = not project.visible
    db.session.commit()
    return redirect(url_for("admin.projects"))


@admin_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
def projects_delete(project_id):
    project = db.get_or_404(Project, project_id)
    delete_upload(project.image_path)
    db.session.delete(project)
    db.session.commit()
    flash("Projekt gelöscht.", "success")
    return redirect(url_for("admin.projects"))


# ══════════════════════════════════════════════════════════════════════════
# Messages
# ══════════════════════════════════════════════════════════════════════════
@admin_bp.route("/messages")
def messages():
    all_msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    for m in all_msgs:
        if not m.is_read:
            break  # only mark first batch
    return render_template("admin/messages.html", messages=all_msgs)


@admin_bp.route("/messages/<int:msg_id>/read", methods=["POST"])
def mark_message_read(msg_id):
    msg = db.get_or_404(ContactMessage, msg_id)
    msg.is_read = True
    db.session.commit()
    flash("Nachricht als gelesen markiert.", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:msg_id>/delete", methods=["POST"])
def delete_message(msg_id):
    msg = db.get_or_404(ContactMessage, msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Nachricht gelöscht.", "success")
    return redirect(url_for("admin.messages"))


# ══════════════════════════════════════════════════════════════════════════
# CRM — Vertriebs-Pipeline
# ══════════════════════════════════════════════════════════════════════════

def _parse_dt(value):
    """YYYY-MM-DD oder ISO-8601 → datetime (UTC, reines Datum = Tagesbeginn)."""
    if not value:
        return None
    v = str(value).strip()
    try:
        if len(v) == 10 and v.count("-") == 2:
            return datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None


def _fmt_dt(value):
    if not value:
        return ""
    return value.strftime("%Y-%m-%dT%H:%M")


def _author() -> str:
    return session.get("username") or "admin"


@admin_bp.route("/crm")
def crm():
    """Pipeline-Board: Funnel-Zähler, fällige Follow-ups, Leads je Stufe."""
    status = (request.args.get("status") or "").strip()
    if status not in PIPELINE_STAGES:
        status = ""

    all_leads = Lead.query.filter_by(is_archived=False).order_by(Lead.updated_at.desc()).all()
    counts = {stage: 0 for stage in PIPELINE_STAGES}
    for lead in all_leads:
        counts[lead.status] = counts.get(lead.status, 0) + 1

    due = sorted(
        (l for l in all_leads if l.followup_overdue),
        key=lambda l: l.next_followup_at or datetime.max.replace(tzinfo=timezone.utc),
    )
    won = counts.get("won", 0)
    lost = counts.get("lost", 0)
    open_value = sum(
        (l.value_estimate or 0)
        for l in all_leads if l.status in ("qualified", "discovery", "proposal")
    )

    if status:
        shown = [l for l in all_leads if l.status == status]
    else:
        shown = [l for l in all_leads if l.status not in PIPELINE_TERMINAL]

    return render_template(
        "admin/crm.html",
        stages=PIPELINE_STAGES, flow=PIPELINE_FLOW, leads=shown,
        counts=counts, due=due, won=won, lost=lost, open_value=open_value,
        status=status, terminal=PIPELINE_TERMINAL,
    )


@admin_bp.route("/crm/new", methods=["GET", "POST"])
def crm_new():
    if request.method == "POST":
        name = " ".join(request.form.get("name", "").split())
        email = request.form.get("email", "").strip().lower()
        if not name or not email or "@" not in email:
            flash("Name und gültige E-Mail sind erforderlich.", "error")
            return render_template("admin/crm_form.html", lead=None, stages=PIPELINE_STAGES)

        lead = Lead(
            name=name, email=email,
            company=request.form.get("company", "").strip()[:160],
            phone=request.form.get("phone", "").strip()[:60],
            service=request.form.get("service", "").strip()[:120],
            message=request.form.get("message", "").strip(),
            status=(request.form.get("status") or "lead").strip() or "lead",
            value_estimate=max(0, int(request.form.get("value_estimate") or 0)),
            next_followup_at=_parse_dt(request.form.get("next_followup_at")),
        )
        db.session.add(lead)
        db.session.flush()
        note = request.form.get("note", "").strip()
        if note:
            lead.add_note(note, author=_author())
        db.session.commit()
        flash("Lead angelegt.", "success")
        return redirect(url_for("admin.crm_detail", lead_id=lead.id))

    return render_template("admin/crm_form.html", lead=None, stages=PIPELINE_STAGES)


@admin_bp.route("/crm/<int:lead_id>")
def crm_detail(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    return render_template(
        "admin/crm_detail.html", lead=lead,
        stages=PIPELINE_STAGES, lost_reasons=LOST_REASONS,
        fmt_dt=_fmt_dt, parse_dt=_parse_dt,
    )


@admin_bp.route("/crm/<int:lead_id>/edit", methods=["POST"])
def crm_edit(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    lead.name = " ".join(request.form.get("name", lead.name).split())[:120]
    lead.email = request.form.get("email", lead.email).strip().lower()[:254]
    lead.company = request.form.get("company", "").strip()[:160]
    lead.phone = request.form.get("phone", "").strip()[:60]
    lead.service = request.form.get("service", "").strip()[:120]
    lead.message = request.form.get("message", "").strip()
    lead.value_estimate = max(0, int(request.form.get("value_estimate") or 0))

    new_status = (request.form.get("status") or lead.status).strip()
    if new_status in PIPELINE_STAGES and new_status != lead.status:
        reason = request.form.get("lost_reason", "").strip()
        note = request.form.get("status_note", "").strip()
        lead.set_status(new_status, reason=reason or note, author=_author())

    lead.next_followup_at = _parse_dt(request.form.get("next_followup_at"))
    lead.last_contact_at = _parse_dt(request.form.get("last_contact_at"))

    note = request.form.get("note", "").strip()
    if note:
        lead.add_note(note, author=_author())

    db.session.commit()
    flash("Lead aktualisiert.", "success")
    return redirect(url_for("admin.crm_detail", lead_id=lead.id))


@admin_bp.route("/crm/<int:lead_id>/note", methods=["POST"])
def crm_note(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    body = request.form.get("body", "").strip()
    if not body:
        flash("Notiz ist leer.", "error")
    else:
        lead.add_note(body, author=_author())
        lead.last_contact_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Notiz hinzugefügt.", "success")
    return redirect(url_for("admin.crm_detail", lead_id=lead.id))


@admin_bp.route("/crm/<int:lead_id>/status", methods=["POST"])
def crm_status(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    new_status = (request.form.get("status") or "").strip()
    if new_status not in PIPELINE_STAGES:
        flash("Ungültiger Status.", "error")
    else:
        reason = request.form.get("lost_reason", "").strip()
        lead.set_status(new_status, reason=reason, author=_author())
        lead.last_contact_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f"Status → {PIPELINE_STAGES[new_status]}.", "success")
    return redirect(url_for("admin.crm_detail", lead_id=lead.id))


@admin_bp.route("/crm/<int:lead_id>/followup", methods=["POST"])
def crm_followup(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    lead.next_followup_at = _parse_dt(request.form.get("next_followup_at"))
    db.session.commit()
    flash("Follow-up gesetzt.", "success")
    return redirect(url_for("admin.crm_detail", lead_id=lead.id))


@admin_bp.route("/crm/<int:lead_id>/archive", methods=["POST"])
def crm_archive(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    lead.is_archived = not lead.is_archived
    db.session.commit()
    flash("Lead archiviert." if lead.is_archived else "Lead reaktiviert.", "success")
    return redirect(url_for("admin.crm_detail", lead_id=lead.id))


@admin_bp.route("/crm/<int:lead_id>/delete", methods=["POST"])
def crm_delete(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    db.session.delete(lead)
    db.session.commit()
    flash("Lead gelöscht.", "success")
    return redirect(url_for("admin.crm"))
