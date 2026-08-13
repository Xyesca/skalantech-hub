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

    # Public assets may be cached; authenticated and mutating routes may not.
    sensitive = (
        request.method != "GET"
        or request.path.startswith("/admin")
        or request.path.startswith("/login")
        or request.path.startswith("/logout")
    )
    if request.path.startswith("/static/"):
        h["Cache-Control"] = "public, max-age=604800, stale-while-revalidate=86400"
    elif sensitive:
        h["Cache-Control"] = "no-store, max-age=0"
    else:
        h["Cache-Control"] = "public, max-age=0, must-revalidate"

    # Browser hardening.
    h["X-Content-Type-Options"] = "nosniff"
    h["X-Frame-Options"] = "DENY"
    h["X-XSS-Protection"] = "0"
    h["Referrer-Policy"] = "strict-origin-when-cross-origin"
    h["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
        "interest-cohort=()"
    )
    h["Strict-Transport-Security"] = "max-age=31536000"
    h["Cross-Origin-Opener-Policy"] = "same-origin"
    h["Cross-Origin-Resource-Policy"] = "same-origin"
    h["Origin-Agent-Cluster"] = "?1"

    # The public site has no inline executable code. The authenticated admin
    # keeps its legacy inline allowance until its templates are refactored.
    if not h.get("Content-Security-Policy"):
        admin_inline = request.path.startswith("/admin") or request.path.startswith("/login")
        script_src = "'self' 'unsafe-inline'" if admin_inline else "'self'"
        style_src = "'self' 'unsafe-inline'" if admin_inline else "'self'"
        h["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src {style_src}; "
            "font-src 'self'; "
            "img-src 'self' data:; "
            "media-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "manifest-src 'self'"
        )
    return response
