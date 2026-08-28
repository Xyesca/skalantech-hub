# PostgreSQL + Alembic-Migrationen (Issue #5)

**Stand:** 2026-08-28 · **Status:** VORBEREITET (P2) — SQLite bleibt kurzfristig produktiv
**Owner laut Issue:** NOVA + SENTINEL · **Task:** t_a0ccc931 (NEXUS)

## Kurzfassung

- Schema-Änderungen laufen ab jetzt über **versionierte Alembic-Migrationen**
  (Flask-Migrate, `migrations/`) — das ad-hoc `ALTER TABLE` beim Start
  (`_migrate_db()`) ist **entfernt**.
- **PostgreSQL ist vorbereitet, aber noch NICHT produktiv.** Der
  Compose-Service `postgres` existiert, bindet ausschließlich an
  `127.0.0.1:5432` und startet nur explizit (`--profile postgres`).
- Datenmigration SQLite → PostgreSQL ist getestet (`scripts/test_pg_migration.sh`,
  komplett grün inkl. Restore-Test und UNIQUE-Atomarität).
- Umstellung erst, wenn Backup, Restore, Migration und Rollback durch
  SENTINEL abgenommen sind (siehe „Go-Live-Checkliste“ unten).

## 1. Was geändert wurde

| Datei | Änderung |
|---|---|
| `requirements.txt` | + `flask-migrate`, `alembic`, `psycopg2-binary` |
| `migrations/` | Alembic-Umgebung + Baseline-Revision `6df6ce6bdd8b` (komplettes Schema: 9 Tabellen, Indexe, `uq_bookings_start_at_utc`) |
| `app/extensions.py` | `migrate = Migrate()` zentral registriert |
| `app/__init__.py` | `_migrate_db()` + `db.create_all()` **entfernt**; `_init_db()`: frisch → `upgrade()`, Alt-Bestand ohne `alembic_version` → `stamp()`, verwaltet → `upgrade()`; `SKIP_DB_BOOTSTRAP=1` für CLI-Werkzeuge |
| `app/config.py` | `SQLALCHEMY_DATABASE_URI` unterstützt bereits `DATABASE_URL` (PG-URL) |
| `docker-compose.yml` | + Service `postgres` (postgres:16-alpine, **nur** `127.0.0.1`, Profil `postgres`, Volume `postgres-data`) |
| `.env.example` | + `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` |
| `scripts/migrate_sqlite_to_postgres.py` | Datenmigration SQLite → PG (Schema via `flask db upgrade`, IDs/FKs erhalten, Sequenzen gefixt, Row-Count-Verifikation, Schutz gegen Doppel-Migration) |
| `scripts/test_pg_migration.sh` | Integrationstest: ephemerer PG-Container, Migration einer **Kopie** der Live-SQLite, App-Smoke, `pg_dump`/`pg_restore`-Restore-Test, UNIQUE-Doppelbuchungs-Test |

## 2. Bootstrap-Logik beim Start (`app/__init__.py::_init_db`)

```text
keine Tabellen            → flask db upgrade      (frisch: Baseline erzeugt alles)
Tabellen, kein alembic_version → stamp head        (Legacy-SQLite: Schema == Baseline,
                                                     wird als Baseline übernommen)
alembic_version vorhanden  → flask db upgrade      (ausstehende Migrationen anwenden)
```

Konsequenz: **Es gibt keinen automatischen `ALTER TABLE` mehr.** Schemaänderungen
werden als neue Revision in `migrations/versions/` angelegt und beim nächsten
Start von der App angewendet. Für die Migration-Authoring-Phase gilt:

```bash
export SKIP_DB_BOOTSTRAP=1   # App nicht beim Import bootstrapen
flask db migrate -m "beschreibung"   # neue Revision generieren (autogenerate)
flask db upgrade                      # anwenden
```

## 3. PostgreSQL-Service (nur intern)

Der Service ist **nicht Teil des Default-Stacks** — `docker compose up -d`
startet weiterhin nur `redis` + `skalantech` (SQLite bleibt produktiv).

```bash
# Explizit starten (Staging/Preview/Migration):
docker compose --profile postgres up -d postgres

# Sicherstellen: lauscht NUR auf 127.0.0.1
ss -ltnp | grep 5432        # → 127.0.0.1:5432, KEIN 0.0.0.0
```

- Bind: `listen_addresses=127.0.0.1`, `network_mode: host`
  (wie redis — einziger Client ist der `skalantech`-Container über Host-localhost).
- Kein öffentlicher Port, keine Tailscale-Exposition (Perimeter-Regel, vgl.
  `docs/PERIMETER_HARDENING_AUDIT.md`).
- Credentials: `POSTGRES_USER/PASSWORD/DB` aus `.env` (werden nicht committet;
  `.env.example` enthält Platzhalter).

## 4. Migrationsplan mit Backup & Rollback

### Backup (vor JEDER Umstellung)

```bash
# 1) SQLite-Bestand sichern (Quelle):
cp instance/app.db "backups/app.db.$(date +%Y%m%d-%H%M%S)"

# 2) PostgreSQL-Bestand sichern (nach Migration, für Rollback):
docker exec skalantech-postgres pg_dump -U skalantech -d skalantech \
  > "backups/skalantech.$(date +%Y%m%d-%H%M%S).sql"
```

Restore-Test für den PG-Dump ist automatisierbar:

```bash
./scripts/test_pg_migration.sh   # inkl. pg_dump → pg_restore → Count-Vergleich
```

### Datenmigration SQLite → PostgreSQL

```bash
# 1) PG starten
docker compose --profile postgres up -d postgres

# 2) Schema anlegen (Alembic — KEIN create_all)
DATABASE_URL="postgresql+psycopg2://skalantech:${POSTGRES_PASSWORD}@127.0.0.1:5432/skalantech" \
  SKIP_DB_BOOTSTRAP=1 flask db upgrade

# 3) Daten kopieren (liest die SQLite-Quelle NUR, Ziel muss leer sein)
python scripts/migrate_sqlite_to_postgres.py \
  --source "sqlite:////abs/pfad/instance/app.db" \
  --target "postgresql+psycopg2://skalantech:${POSTGRES_PASSWORD}@127.0.0.1:5432/skalantech"
```

Das Script verweigert den Start, wenn das Ziel bereits Daten enthält
(Doppel-Migrationsschutz) und bricht bei Row-Count-Abweichung ab (exit 1).

### Rollback

| Ebene | Weg |
|---|---|
| App-Code | `git revert` des Deploy-Commits + `docker compose up -d --build skalantech` |
| Schema (PG) | `flask db downgrade -1` (bzw. `-<n>`); für die Baseline existiert `downgrade()` (droppt Tabellen) |
| Daten | SQLite-Bestand aus Schritt 4.1 zurückkopieren + `DATABASE_URL` leer lassen (Default SQLite) — SQLite bleibt Source of Truth bis zur Freigabe |
| Ganz zurück | `docker compose stop postgres` + `DATABASE_URL=` → App läuft wieder rein auf SQLite |

### Staging/Preview

```bash
# Lokale Preview mit PostgreSQL (ohne Produktion anzufassen):
docker compose --profile postgres up -d postgres
DATABASE_URL="postgresql+psycopg2://skalantech:${POSTGRES_PASSWORD}@127.0.0.1:5432/skalantech" \
  FLASK_ENV=development python run.py
# → http://127.0.0.1:5000, DB = PostgreSQL
```

Für Tests: `scripts/test_pg_migration.sh` fährt einen **ephemeren** PG-Container
auf Port 55432 hoch, migriert eine Kopie der Live-SQLite, macht App-Smoke +
Restore-Test und räumt danach vollständig auf (kein Bestand wird angefasst).

## 5. Go-Live-Checkliste (erst nach Freigabe)

- [ ] `backups/` mit SQLite-Kopie + pg_dump vorhanden, Restore-Test grün
- [ ] SENTINEL-Abnahme: `scripts/test_pg_migration.sh` gegen Staging-PG
- [ ] `.env` auf VPS: `DATABASE_URL=postgresql+psycopg2://...` gesetzt
- [ ] `docker compose --profile postgres up -d postgres` (intern verifiziert)
- [ ] `flask db upgrade` + `migrate_sqlite_to_postgres.py` ausgeführt,
      Row-Counts protokolliert
- [ ] Rollback-Pfad schriftlich bestätigt (Abschnitt 4.3)
- [ ] Doku in GitHub committet (README + dieses Dokument)

## 6. Offene Punkte / bekannte Grenzen

- **Zeitzonen:** SQLite speichert aware-Datetimes als naive UTC (Offset wird
  verworfen). Die App schreibt ausschließlich UTC (`datetime.now(timezone.utc)`)
  — auf PostgreSQL (`TIMESTAMP WITHOUT TIME ZONE`) bleibt das Verhalten
  identisch (naive UTC-Spalten). Kein Breaking Change, aber bewusst dokumentiert.
- **n8n-Terminbuchung:** `POST /api/crm/bookings/reserve` nutzt
  `IntegrityError` auf dem UNIQUE-Constraint `start_at_utc` — auf PostgreSQL
  identisch verifiziert (siehe Testschritt 5 im Script).
- **Alembic-Baseline vs. Live-Schema:** Die Live-SQLite wurde per
  `create_all` + historischem ALTER gepflegt und entspricht der Baseline
  (per Test verifiziert: `stamp()` adoptiert ohne Datensatzverlust).
- **Wartung:** Neue Spalten/Indexe künftig IMMER als Alembic-Revision
  (`flask db migrate`), niemals als ad-hoc `ALTER TABLE` im Code.
