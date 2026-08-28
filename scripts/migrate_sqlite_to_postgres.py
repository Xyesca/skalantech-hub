#!/usr/bin/env python3
"""Skalantech Hub — SQLite → PostgreSQL Datenmigration (Issue #5).

Kopiert ALLE Daten aus einer bestehenden SQLite-Datenbank in eine
PostgreSQL-Datenbank, ohne IDs zu verlieren (FK-Integrität bleibt).

Ablauf:
  1. Schema: `flask db upgrade` gegen das PG-Ziel (Alembic-Baseline) —
     KEIN create_all, KEINE ad-hoc ALTER TABLE.
  2. Daten: Tabellen in FK-sicherer Reihenfolge kopieren, explizite IDs
     (lead_notes.lead_id, bookings.lead_id bleiben gültig).
  3. Sequenzen: PG-Serials auf max(id)+1 setzen (neue Einträge kollidieren
     nicht mit migrierten IDs).
  4. Verifikation: Row-Counts Quelle vs. Ziel je Tabelle; Abbruch bei
     Abweichung.

Aufruf:
    python scripts/migrate_sqlite_to_postgres.py \
        --source sqlite:////path/to/instance/app.db \
        --target postgresql+psycopg2://user:pass@127.0.0.1:5432/skalantech

    # oder über Env:
    SOURCE_DATABASE_URL=... TARGET_DATABASE_URL=... python scripts/migrate_sqlite_to_postgres.py

Sicherheit:
  - Das Ziel-Schema wird NUR über Migrationen erzeugt (kein DROP, kein
    create_all). Bestehende Ziel-Tabellen bleiben unangetastet, wenn die
    Migration sie bereits angelegt hat.
  - Die Quelle wird NUR gelesen (Read-only).
  - Abbruch (exit 1), wenn das Ziel bereits Daten enthält — bewusste
    Doppel-Migration verhindern.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

from sqlalchemy import MetaData, Table, create_engine, func, inspect, select, text

# Tabellen in FK-sicherer Reihenfolge (Eltern vor Kindern).
TABLE_ORDER = [
    "admin",
    "settings",
    "links",
    "projects",
    "contact_messages",
    "leads",
    "lead_notes",
    "bookings",
    "analytics_events",
]

# Tabellen, deren PK-Spalte eine Serial-Sequenz in PG hat.
SEQUENCE_TABLES = TABLE_ORDER


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default=os.environ.get("SOURCE_DATABASE_URL"))
    p.add_argument("--target", default=os.environ.get("TARGET_DATABASE_URL"))
    p.add_argument("--skip-schema", action="store_true",
                   help="Schema nicht migrieren (bereits via flask db upgrade erzeugt)")
    return p.parse_args()


def _ensure_empty_target(engine) -> None:
    """Weigere dich, in ein Ziel mit Daten zu schreiben (Idempotenz-Schutz)."""
    insp = inspect(engine)
    for table in TABLE_ORDER:
        if not insp.has_table(table):
            continue
        with engine.connect() as conn:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
        if count:
            sys.exit(
                f"FEHLER: Ziel-Tabelle '{table}' enthält bereits {count} Zeilen. "
                "Migration nur gegen eine leere Ziel-DB ausführen."
            )


def _copy_table(src_conn, tgt_conn, src_table: Table, tgt_table: Table) -> int:
    """Kopiere alle Zeilen einer Tabelle mit expliziten IDs."""
    rows = src_conn.execute(select(src_table)).mappings().all()
    if not rows:
        return 0
    columns = [c.name for c in tgt_table.columns]
    insert = tgt_table.insert()
    tgt_conn.execute(insert, [{c: row[c] for c in columns} for row in rows])
    return len(rows)


def _fix_sequences(engine, metadata: MetaData) -> None:
    """PG-Serials auf max(id)+1 setzen, damit neue IDs nicht kollidieren."""
    for table_name in SEQUENCE_TABLES:
        table = metadata.tables.get(table_name)
        if table is None:
            continue
        pk = [c for c in table.primary_key.columns]
        if len(pk) != 1:
            continue
        pk_col = pk[0].name
        with engine.begin() as conn:
            current = conn.execute(text(f'SELECT COALESCE(MAX("{pk_col}"), 0) FROM "{table_name}"')).scalar()
            sequence = f'"{table_name}_{pk_col}_seq"'
            conn.execute(text(f"SELECT setval('{sequence}', {current + 1}, false)"))


def main() -> int:
    args = parse_args()
    if not args.source or not args.target:
        print("FEHLER: --source und --target sind erforderlich.", file=sys.stderr)
        return 2

    src = create_engine(args.source)
    tgt = create_engine(args.target)

    # ── 1. Schema via Alembic (Flask-Migrate) ────────────────────────────
    if not args.skip_schema:
        # Flask-App braucht TARGET_DATABASE_URL als aktive DB.
        os.environ["DATABASE_URL"] = args.target
        os.environ["SKIP_DB_BOOTSTRAP"] = "1"  # App beim Import nicht bootstrapen
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        from app import create_app
        from app.extensions import migrate  # noqa: F401  (registriert Alembic)

        app = create_app("production")
        with app.app_context():
            from flask_migrate import upgrade

            # Verzeichnis kommt aus migrate.init_app() (absolut, siehe app/__init__.py)
            upgrade()
        print("Schema: flask db upgrade gegen Ziel angewendet.")

    # ── 2. Daten kopieren ─────────────────────────────────────────────────
    _ensure_empty_target(tgt)
    meta = MetaData()
    meta.reflect(bind=src)
    tgt_meta = MetaData()
    tgt_meta.reflect(bind=tgt)

    totals = {}
    with src.connect() as src_conn, tgt.begin() as tgt_conn:
        for table_name in TABLE_ORDER:
            if table_name not in meta.tables:
                print(f"  übersprungen (nicht in Quelle): {table_name}")
                continue
            if table_name not in tgt_meta.tables:
                sys.exit(f"FEHLER: Ziel-Tabelle '{table_name}' fehlt — Schema-Migration nicht angewendet?")
            n = _copy_table(src_conn, tgt_conn, meta.tables[table_name], tgt_meta.tables[table_name])
            totals[table_name] = n
            print(f"  kopiert {n:>5} → {table_name}")

    _fix_sequences(tgt, tgt_meta)

    # ── 3. Verifikation ───────────────────────────────────────────────────
    errors = []
    with src.connect() as src_conn, tgt.connect() as tgt_conn:
        for table_name, expected in totals.items():
            actual = tgt_conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
            status = "OK" if actual == expected else "FEHLER"
            if actual != expected:
                errors.append(f"{table_name}: Quelle={expected} Ziel={actual}")
            print(f"  verify {status:>6} {table_name}: {actual} (Quelle {expected})")

    if errors:
        print("\nMIGRATION FEHLGESCHLAGEN:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nMIGRATION OK — Daten vollständig nach PostgreSQL kopiert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
