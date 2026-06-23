"""Skalantech Hub — Public routes."""
from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, redirect, url_for
from app.models import Settings, Link, Project, ContactMessage
from app.extensions import db

public_bp = Blueprint("public", __name__)


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
    return render_template("index.html", settings=settings, links=links, projects=projects)


@public_bp.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message_text = request.form.get("message", "").strip()
    
    if name and email and message_text:
        msg = ContactMessage(name=name, email=email, message=message_text)
        db.session.add(msg)
        db.session.commit()
        flash("Nachricht erfolgreich gesendet. Ich melde mich bald!", "success")
    else:
        flash("Bitte fülle alle Felder aus.", "error")
        
    return redirect(url_for("public.index", _anchor="contact"))


@public_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve user-uploaded media from the instance/uploads directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
