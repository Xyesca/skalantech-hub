"""Skalantech Hub — Upload handling with MIME validation."""
import os
import uuid

from werkzeug.utils import secure_filename
from flask import current_app

# Expected MIME types per extension
_MIME_MAP = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mov": "video/quicktime",
}


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _validate_mime(file_storage, allowed_exts: set) -> bool:
    """Validate extension AND content-type header."""
    if not file_storage or not file_storage.filename:
        return False

    ext = _ext(file_storage.filename)
    if ext not in allowed_exts:
        return False

    expected = _MIME_MAP.get(ext)
    ct = file_storage.content_type or ""
    if expected and ct and ct != "application/octet-stream":
        if ct != expected:
            return False
    return True


def save_upload(file_storage, allowed_exts: set) -> str | None:
    """Save an uploaded file after validation. Returns the stored filename or None."""
    if not _validate_mime(file_storage, allowed_exts):
        return None

    safe_name = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    path = os.path.join(upload_dir, unique_name)
    file_storage.save(path)
    return unique_name


def delete_upload(filename: str | None) -> None:
    """Delete an uploaded file by name (no-op when filename is falsy)."""
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass
