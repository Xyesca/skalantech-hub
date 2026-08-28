#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# Skalantech Hub — PostgreSQL-Migrations- & Restore-Test (Issue #5)
#
# Fährt einen EPHEMERALEN postgres:16-alpine Container hoch (NUR 127.0.0.1,
# Port 55432 — kollidiert nicht mit Produktion/DebtPilot), migriert eine
# KOPIE der Live-SQLite nach PostgreSQL, verifiziert Row-Counts, macht dann
# einen pg_dump/pg_restore-Restore-Test in eine zweite DB und räumt alles
# wieder auf. Kein Bestand wird angefasst.
#
# Voraussetzungen: docker, .venv mit flask-migrate + psycopg2-binary
#                  (requirements.txt), laufende/erreichbare SQLite-Quelle.
#
# Aufruf:
#   ./scripts/test_pg_migration.sh [pfad/zur/sqlite.db]
#   (Default: instance/app.db — KOPIE wird verwendet, Quelle bleibt unangetastet)
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

SRC_DB="${1:-$REPO_DIR/instance/app.db}"
PG_PORT=55432
PG_USER=skalantech
PG_PASS="skalantech-test-$(date +%s)"
PG_DB=skalantech
CT_NAME="skalantech-pg-test-$$"
TMP_DIR="$(mktemp -d /tmp/skalantech-pg-test-XXXXXX)"

cleanup() {
  docker rm -f "$CT_NAME" >/dev/null 2>&1 || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "== 0. Vorbereitung =="
[ -f "$SRC_DB" ] || { echo "FEHLER: SQLite-Quelle nicht gefunden: $SRC_DB"; exit 1; }
cp "$SRC_DB" "$TMP_DIR/source-copy.db"   # KOPIE — Original wird nie angefasst
echo "Quelle (Kopie): $TMP_DIR/source-copy.db"

echo "== 1. Ephemeraler PostgreSQL-Container (127.0.0.1:$PG_PORT) =="
docker run -d --name "$CT_NAME" \
  -e POSTGRES_USER="$PG_USER" \
  -e POSTGRES_PASSWORD="$PG_PASS" \
  -e POSTGRES_DB="$PG_DB" \
  -p "127.0.0.1:$PG_PORT:5432" \
  postgres:16-alpine >/dev/null

for i in $(seq 1 30); do
  if docker exec "$CT_NAME" pg_isready -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker exec "$CT_NAME" pg_isready -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1 \
  || { echo "FEHLER: PostgreSQL wurde nicht bereit."; exit 1; }
echo "PostgreSQL bereit."

TARGET_URL="postgresql+psycopg2://$PG_USER:$PG_PASS@127.0.0.1:$PG_PORT/$PG_DB"
SOURCE_URL="sqlite:///$TMP_DIR/source-copy.db"

echo "== 2. Datenmigration SQLite → PostgreSQL =="
SOURCE_DATABASE_URL="$SOURCE_URL" TARGET_DATABASE_URL="$TARGET_URL" \
  .venv/bin/python scripts/migrate_sqlite_to_postgres.py

echo "== 3. App-Smoke gegen PostgreSQL (create_app + upgrade/stamp) =="
# App mit DATABASE_URL=PG starten: _init_db() sieht alembic_version → upgrade (no-op),
# _ensure_admin findet Admin (migriert) → kein Doppel-Seed.
DATABASE_URL="$TARGET_URL" SECRET_KEY=test ADMIN_USERNAME=admin ADMIN_PASSWORD=test \
  SESSION_COOKIE_SECURE=false RATELIMIT_STORAGE_URI=memory:// \
  .venv/bin/python - <<'PY'
import os, sys
sys.path.insert(0, os.getcwd())
from app import create_app
app = create_app("production")
with app.app_context():
    from app.models import Admin, Booking, Lead, AnalyticsEvent
    print(f"  Admin={Admin.query.count()} Leads={Lead.query.count()} "
          f"Bookings={Booking.query.count()} Events={AnalyticsEvent.query.count()}")
    assert Admin.query.count() == 1, "Admin-Seed darf nicht duplizieren"
print("  App-Smoke OK")
PY

echo "== 4. Restore-Test (pg_dump → pg_restore in zweite DB) =="
# Backup der migrierten DB
docker exec "$CT_NAME" pg_dump -U "$PG_USER" -d "$PG_DB" > "$TMP_DIR/backup.sql"
echo "  pg_dump: $(wc -l < "$TMP_DIR/backup.sql") Zeilen"

# Zweite DB anlegen + Restore
docker exec "$CT_NAME" psql -U "$PG_USER" -d postgres -c "CREATE DATABASE ${PG_DB}_restore;" >/dev/null
docker exec -i "$CT_NAME" psql -U "$PG_USER" -d "${PG_DB}_restore" < "$TMP_DIR/backup.sql" >/dev/null
echo "  pg_restore: OK"

# Row-Counts Backup vs Restore
docker exec "$CT_NAME" psql -U "$PG_USER" -d "$PG_DB" -t -A -c \
  "SELECT 'bookings', COUNT(*) FROM bookings UNION ALL SELECT 'leads', COUNT(*) FROM leads UNION ALL SELECT 'analytics_events', COUNT(*) FROM analytics_events UNION ALL SELECT 'contact_messages', COUNT(*) FROM contact_messages;" \
  > "$TMP_DIR/counts_orig.txt"
docker exec "$CT_NAME" psql -U "$PG_USER" -d "${PG_DB}_restore" -t -A -c \
  "SELECT 'bookings', COUNT(*) FROM bookings UNION ALL SELECT 'leads', COUNT(*) FROM leads UNION ALL SELECT 'analytics_events', COUNT(*) FROM analytics_events UNION ALL SELECT 'contact_messages', COUNT(*) FROM contact_messages;" \
  > "$TMP_DIR/counts_restore.txt"

echo "  Original:  $(tr '\n' ' ' < "$TMP_DIR/counts_orig.txt")"
echo "  Restored:  $(tr '\n' ' ' < "$TMP_DIR/counts_restore.txt")"
if ! diff -q "$TMP_DIR/counts_orig.txt" "$TMP_DIR/counts_restore.txt" >/dev/null; then
  echo "FEHLER: Restore-Counts weichen ab."; exit 1
fi
echo "  Restore-Counts identisch."

echo "== 5. Slot-Reserve-Atomarität auf PostgreSQL (UNIQUE-Constraint) =="
# Parallele Doppelbuchung: genau 1 muss gewinnen (Bookings.UNIQUE start_at_utc)
docker exec "$CT_NAME" psql -U "$PG_USER" -d "$PG_DB" -c \
  "INSERT INTO bookings (booking_id, start_at_utc, end_at_utc, name, email, topic, status)
   VALUES ('restore-test-1', '2030-01-15 09:00:00', '2030-01-15 09:30:00', 'Test', 't@t.de', 'Potenzial-Check', 'confirmed');" >/dev/null
if docker exec "$CT_NAME" psql -U "$PG_USER" -d "$PG_DB" -c \
  "INSERT INTO bookings (booking_id, start_at_utc, end_at_utc, name, email, topic, status)
   VALUES ('restore-test-2', '2030-01-15 09:00:00', '2030-01-15 09:30:00', 'Test2', 't2@t.de', 'Potenzial-Check', 'confirmed');" >/dev/null 2>&1; then
  echo "FEHLER: Doppelbuchung wurde NICHT abgewiesen (UNIQUE fehlt auf PG)."; exit 1
fi
echo "  Doppelbuchung korrekt abgewiesen (UNIQUE uq_bookings_start_at_utc aktiv)."

echo ""
echo "✅ POSTGRES-MIGRATIONS- & RESTORE-TEST KOMPLETT GRÜN"
