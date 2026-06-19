"""
Skalantech Hub — Persönliche Visitenkarte + Admin-Dashboard
Flask + SQLite + Docker
"""
import os
import secrets
import time
import uuid
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort, send_from_directory
)
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, Admin, Settings, Link, Project

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEO_EXT = {"mp4", "webm", "mov"}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", "50")) * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

db.init_app(app)

# ---------------------------------------------------------------------------
# Brute-Force Schutz
# ---------------------------------------------------------------------------
_login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def _client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


def _is_locked(ip):
    count, locked_until = _login_attempts.get(ip, (0, 0))
    return locked_until > time.time()


def _register_failed_attempt(ip):
    count, _ = _login_attempts.get(ip, (0, 0))
    count += 1
    locked_until = time.time() + LOCKOUT_SECONDS if count >= MAX_ATTEMPTS else 0
    _login_attempts[ip] = (count, locked_until)


def _clear_attempts(ip):
    _login_attempts.pop(ip, None)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------
@app.context_processor
def inject_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return {"csrf_token": session["_csrf_token"]}


def check_csrf():
    token = session.get("_csrf_token")
    sent = request.form.get("csrf_token")
    if not token or not sent or not secrets.compare_digest(token, sent):
        abort(400, description="Ungültiges Formular-Token.")


# ---------------------------------------------------------------------------
# Icons (inline SVG)
# ---------------------------------------------------------------------------
ICONS = {
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56 0-.27-.01-1.17-.02-2.13-3.2.7-3.88-1.36-3.88-1.36-.52-1.34-1.28-1.69-1.28-1.69-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.03 1.78 2.71 1.26 3.37.97.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.18 1.18a10.9 10.9 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.77.11 3.06.74.81 1.19 1.83 1.19 3.09 0 4.42-2.7 5.39-5.27 5.68.41.36.78 1.06.78 2.15 0 1.55-.01 2.8-.01 3.18 0 .31.21.67.8.56C20.21 21.38 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 5.82c-.92-.8-1.5-1.96-1.6-3.27h-3.1v13.6c0 1.67-1.36 3.02-3.03 3.02a3.03 3.03 0 0 1-3.03-3.02 3.03 3.03 0 0 1 3.03-3.03c.3 0 .58.04.85.12V10.1a6.3 6.3 0 0 0-.85-.06A6.18 6.18 0 0 0 3.65 16.2 6.18 6.18 0 0 0 9.87 22.4a6.18 6.18 0 0 0 6.18-6.18V9.1a8.3 8.3 0 0 0 4.85 1.55V7.55a4.9 4.9 0 0 1-4.3-1.73z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="2.5" width="19" height="19" rx="5"/><circle cx="12" cy="12" r="4.3"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "app": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.5"/></svg>',
    "website": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M9.5 14.5l5-5M8.2 16.8l-1.4 1.4a3.5 3.5 0 0 1-5-5l2.8-2.8a3.5 3.5 0 0 1 5-.1M15.8 7.2l1.4-1.4a3.5 3.5 0 0 1 5 5l-2.8 2.8a3.5 3.5 0 0 1-5 .1"/></svg>',
}


@app.template_global()
def icon_svg(platform):
    return Markup(ICONS.get(platform, ICONS["link"]))


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def save_upload(file_storage, allowed_exts):
    if not file_storage or not file_storage.filename:
        return None
    ext = _ext(file_storage.filename)
    if ext not in allowed_exts:
        return None
    safe_name = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(path)
    return unique_name


def delete_upload(filename):
    if not filename:
        return
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Öffentliche Seite
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    settings = Settings.get()
    links = Link.query.filter_by(visible=True).order_by(Link.position.asc(), Link.id.asc()).all()
    projects = Project.query.filter_by(visible=True).order_by(Project.position.asc(), Project.id.asc()).all()
    return render_template("index.html", settings=settings, links=links, projects=projects)


@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("admin_settings"))

    if request.method == "POST":
        ip = _client_ip()
        if _is_locked(ip):
            flash("Zu viele Fehlversuche. Bitte später erneut versuchen.", "error")
            return render_template("login.html"), 429

        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            _clear_attempts(ip)
            session.clear()
            session["logged_in"] = True
            session["username"] = admin.username
            next_url = request.args.get("next") or url_for("admin_settings")
            return redirect(next_url)

        _register_failed_attempt(ip)
        flash("Benutzername oder Passwort falsch.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Admin: Settings
# ---------------------------------------------------------------------------
@app.route("/admin")
@login_required
def admin_root():
    return redirect(url_for("admin_settings"))


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    settings = Settings.get()

    if request.method == "POST":
        check_csrf()
        settings.name = request.form.get("name", "").strip()[:120] or settings.name
        settings.tagline = request.form.get("tagline", "").strip()[:240]
        settings.location = request.form.get("location", "").strip()[:120]
        settings.about = request.form.get("about", "").strip()

        hero_file = request.files.get("hero_file")
        if hero_file and hero_file.filename:
            ext = _ext(hero_file.filename)
            if ext in IMAGE_EXT:
                saved = save_upload(hero_file, IMAGE_EXT)
                if saved:
                    delete_upload(settings.hero_path)
                    settings.hero_path = saved
                    settings.hero_type = "image"
            elif ext in VIDEO_EXT:
                saved = save_upload(hero_file, VIDEO_EXT)
                if saved:
                    delete_upload(settings.hero_path)
                    settings.hero_path = saved
                    settings.hero_type = "video"
            else:
                flash("Dateiformat nicht unterstützt.", "error")

        if request.form.get("remove_hero") == "1":
            delete_upload(settings.hero_path)
            settings.hero_path = ""
            settings.hero_type = "none"

        db.session.commit()
        flash("Gespeichert.", "success")
        return redirect(url_for("admin_settings"))

    return render_template("admin/settings.html", settings=settings)


@app.route("/admin/password", methods=["POST"])
@login_required
def admin_password():
    check_csrf()
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

    return redirect(url_for("admin_settings"))


# ---------------------------------------------------------------------------
# Admin: Links
# ---------------------------------------------------------------------------
@app.route("/admin/links", methods=["GET", "POST"])
@login_required
def admin_links():
    if request.method == "POST":
        check_csrf()
        label = request.form.get("label", "").strip()
        url_value = request.form.get("url", "").strip()
        platform = request.form.get("platform", "link")
        position = int(request.form.get("position") or 0)
        if not label or not url_value:
            flash("Label und URL sind erforderlich.", "error")
        else:
            db.session.add(Link(label=label, url=url_value, platform=platform, position=position, visible=True))
            db.session.commit()
            flash("Link hinzugefügt.", "success")
        return redirect(url_for("admin_links"))

    links = Link.query.order_by(Link.position.asc(), Link.id.asc()).all()
    return render_template("admin/links.html", links=links)


@app.route("/admin/links/<int:link_id>/edit", methods=["POST"])
@login_required
def admin_links_edit(link_id):
    check_csrf()
    link = Link.query.get_or_404(link_id)
    link.label = request.form.get("label", link.label).strip()
    link.url = request.form.get("url", link.url).strip()
    link.platform = request.form.get("platform", link.platform)
    link.position = int(request.form.get("position") or link.position)
    db.session.commit()
    flash("Link aktualisiert.", "success")
    return redirect(url_for("admin_links"))


@app.route("/admin/links/<int:link_id>/toggle", methods=["POST"])
@login_required
def admin_links_toggle(link_id):
    check_csrf()
    link = Link.query.get_or_404(link_id)
    link.visible = not link.visible
    db.session.commit()
    return redirect(url_for("admin_links"))


@app.route("/admin/links/<int:link_id>/delete", methods=["POST"])
@login_required
def admin_links_delete(link_id):
    check_csrf()
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link gelöscht.", "success")
    return redirect(url_for("admin_links"))


# ---------------------------------------------------------------------------
# Admin: Projects / Apps
# ---------------------------------------------------------------------------
@app.route("/admin/projects", methods=["GET", "POST"])
@login_required
def admin_projects():
    if request.method == "POST":
        check_csrf()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        url_value = request.form.get("url", "").strip()
        position = int(request.form.get("position") or 0)
        if not title:
            flash("Titel ist erforderlich.", "error")
        else:
            image_path = save_upload(request.files.get("image"), IMAGE_EXT) or ""
            db.session.add(Project(title=title, description=description, url=url_value, image_path=image_path, position=position, visible=True))
            db.session.commit()
            flash("Projekt hinzugefügt.", "success")
        return redirect(url_for("admin_projects"))

    projects = Project.query.order_by(Project.position.asc(), Project.id.asc()).all()
    return render_template("admin/projects.html", projects=projects)


@app.route("/admin/projects/<int:project_id>/edit", methods=["POST"])
@login_required
def admin_projects_edit(project_id):
    check_csrf()
    project = Project.query.get_or_404(project_id)
    project.title = request.form.get("title", project.title).strip()
    project.description = request.form.get("description", project.description).strip()
    project.url = request.form.get("url", project.url).strip()
    project.position = int(request.form.get("position") or project.position)
    new_image = save_upload(request.files.get("image"), IMAGE_EXT)
    if new_image:
        delete_upload(project.image_path)
        project.image_path = new_image
    db.session.commit()
    flash("Projekt aktualisiert.", "success")
    return redirect(url_for("admin_projects"))


@app.route("/admin/projects/<int:project_id>/toggle", methods=["POST"])
@login_required
def admin_projects_toggle(project_id):
    check_csrf()
    project = Project.query.get_or_404(project_id)
    project.visible = not project.visible
    db.session.commit()
    return redirect(url_for("admin_projects"))


@app.route("/admin/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def admin_projects_delete(project_id):
    check_csrf()
    project = Project.query.get_or_404(project_id)
    delete_upload(project.image_path)
    db.session.delete(project)
    db.session.commit()
    flash("Projekt gelöscht.", "success")
    return redirect(url_for("admin_projects"))


# ---------------------------------------------------------------------------
# Erststart: Admin anlegen
# ---------------------------------------------------------------------------
def ensure_admin_seeded():
    with app.app_context():
        db.create_all()
        if Admin.query.count() == 0:
            username = os.environ.get("ADMIN_USERNAME", "xyesca25")
            password = os.environ.get("ADMIN_PASSWORD")
            if not password:
                password = secrets.token_urlsafe(12)
                print("=" * 60)
                print(f" Kein ADMIN_PASSWORD in .env gefunden.")
                print(f" Temporäres Passwort für '{username}': {password}")
                print(" Bitte in .env setzen und Container neu starten!")
                print("=" * 60)
            db.session.add(Admin(username=username, password_hash=generate_password_hash(password)))
            db.session.commit()


ensure_admin_seeded()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
