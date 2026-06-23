"""Skalantech Hub — Security helpers."""
from functools import wraps
from flask import session, redirect, url_for, request, Response


def login_required(view):
    """Decorator — redirect to login if unauthenticated."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def add_security_headers(response: Response) -> Response:
    """After-request hook that hardens every HTTP response."""
    h = response.headers
    h["X-Content-Type-Options"] = "nosniff"
    h["X-Frame-Options"] = "SAMEORIGIN"
    h["X-XSS-Protection"] = "1; mode=block"
    h["Referrer-Policy"] = "strict-origin-when-cross-origin"
    h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    h["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self'; "
        "frame-ancestors 'self'"
    )
    return response
