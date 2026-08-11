"""One-shot copy of the legacy SQLite rows into the DATABASE_URL database.

    uv run python migrate_to_supabase.py [--source posts.db]

Idempotent: rows whose id already exists in the target are skipped.
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import db  # noqa: E402  — must import after load_dotenv so DATABASE_URL is set
from models import Post  # noqa: E402


def _parse_dt(value) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _parse_reasons(value) -> list[str]:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(Path(__file__).parent / "posts.db"))
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        print(f"No source database at {source}")
        return 1
    if db.DATABASE_URL.startswith("sqlite"):
        print("DATABASE_URL is unset or points at SQLite — nothing to migrate to.")
        return 1

    conn = sqlite3.connect(source)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM posts ORDER BY id").fetchall()
    conn.close()
    print(f"Read {len(rows)} rows from {source}")

    db.init_db()
    inserted = skipped = 0
    with db.SessionLocal() as session:
        existing = {pid for (pid,) in session.query(Post.id).all()}
        for row in rows:
            if row["id"] in existing:
                skipped += 1
                continue
            session.add(Post(
                id=row["id"],
                topic=row["topic"],
                language=row["language"],
                text=row["text"],
                image_url=row["image_url"],
                image_prompt=row["image_prompt"],
                viral_score=row["viral_score"],
                viral_reasons=_parse_reasons(row["viral_reasons"]),
                status=row["status"],
                created_at=_parse_dt(row["created_at"]),
                updated_at=_parse_dt(row["updated_at"]),
            ))
            inserted += 1
        session.commit()

    # Explicit ids do not advance Postgres' identity sequence; realign it so the
    # next INSERT does not collide.
    if inserted:
        with db.engine.begin() as pg:
            from sqlalchemy import text as sql
            pg.execute(sql(
                "SELECT setval(pg_get_serial_sequence('posts', 'id'), "
                "COALESCE((SELECT MAX(id) FROM posts), 1))"
            ))

    print(f"Inserted {inserted}, skipped {skipped} (already present).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
