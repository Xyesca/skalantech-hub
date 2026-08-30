# ═══════════════════════════════════════════════════════════════════════
# Skalantech Hub — Multi-stage Dockerfile
# ═══════════════════════════════════════════════════════════════════════

# ── Stage 1: Install dependencies ─────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ─────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# Non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Ensure directories exist with correct permissions
RUN mkdir -p instance/uploads && chown -R appuser:appuser /app

USER appuser
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Production WSGI server (4 workers)
# --timeout 300 > Flask-Demo-Proxy-Timeout (280s): Worker darf lokale
# Inferenz (Ollama lfm25, 50–240s) nicht vor der Antwort killen.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--timeout", "300", "run:app"]
