"""Skalantech Hub — Admin CRUD routes."""
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import Settings, Link, Project, Admin, ContactMessage
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
