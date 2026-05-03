from __future__ import annotations

import argparse
import sqlite3
from datetime import date as date_class, datetime, timedelta, timezone
from pathlib import Path


def default_ingestion_db_path() -> Path:
    return Path.home() / ".bibletrack" / "ingestion.sqlite3"


def _resolve_db_path(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path is not None else default_ingestion_db_path()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def update_ingestion_state(
    date: str,
    translation: str,
    content_hash: str,
    db_path: str | Path | None = None,
    status: str | None = None,
) -> str:
    """Upsert ingestion state into a compact SQLite store in the user's home directory."""
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    translation_key = translation.strip().lower()

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestion_state (
                date TEXT NOT NULL,
                translation TEXT NOT NULL,
                status TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (date, translation)
            )
            """
        )
        existing = conn.execute(
            "SELECT content_hash FROM ingestion_state WHERE date = ? AND translation = ?",
            (date, translation_key),
        ).fetchone()
        resolved_status = status or "Ingested"
        conn.execute(
            """
            INSERT INTO ingestion_state (date, translation, status, content_hash, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date, translation) DO UPDATE SET
                status = excluded.status,
                content_hash = excluded.content_hash,
                updated_at = excluded.updated_at
            """,
            (date, translation_key, resolved_status, content_hash, now),
        )
        conn.commit()

    return resolved_status


def get_ingestion_status(date: str, db_path: str | Path | None = None) -> str:
    """Return the most recent ingestion status for a date, regardless of translation."""
    path = _resolve_db_path(db_path)
    if not path.exists():
        return "Missing"

    with sqlite3.connect(path) as conn:
        row = conn.execute(
            """
            SELECT status
            FROM ingestion_state
            WHERE date = ?
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (date,),
        ).fetchone()

    return row[0] if row else "Missing"


def _parse_date_key(date_key: str) -> date_class:
    month_str, day_str = date_key.split("-")
    return date_class(2000, int(month_str), int(day_str))


def get_ingestion_range_status(start: str, end: str, db_path: str | Path | None = None) -> str:
    """Return a compact count of ingested dates within an inclusive range."""
    start_date = _parse_date_key(start)
    end_date = _parse_date_key(end)
    if end_date < start_date:
        raise ValueError("end must be on or after start")

    path = _resolve_db_path(db_path)
    expected = 0
    current = start_date
    wanted: set[str] = set()
    while current <= end_date:
        wanted.add(f"{current.month}-{current.day}")
        expected += 1
        current += timedelta(days=1)

    if not path.exists():
        return f"0/{expected}"

    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT DISTINCT date FROM ingestion_state").fetchall()

    present = sum(1 for (stored_date,) in rows if stored_date in wanted)
    return f"{present}/{expected}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage BibleTrack ingestion state")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update", help="Upsert ingestion state")
    update_parser.add_argument("--date", required=True, help="BibleTrack date key, e.g. 4-19")
    update_parser.add_argument("--content-hash", required=True, help="Content hash for the ingested day")
    update_parser.add_argument("--translation", default="nkjv", help="Translation key, defaults to nkjv")
    update_parser.add_argument("--status", default=None, help="Optional explicit status to store")
    update_parser.add_argument("--db", default=None, help="SQLite database path")

    status_parser = subparsers.add_parser("status", help="Query ingestion state")
    status_group = status_parser.add_mutually_exclusive_group(required=True)
    status_group.add_argument("--date", help="BibleTrack date key, e.g. 4-19")
    status_group.add_argument("--start", help="Start date key for an inclusive range, e.g. 4-1")
    status_parser.add_argument("--end", help="End date key for an inclusive range, required with --start")
    status_parser.add_argument("--db", default=None, help="SQLite database path")

    args = parser.parse_args()

    if args.command == "update":
        print(update_ingestion_state(args.date, args.translation, args.content_hash, args.db, args.status))
        return

    if args.start:
        if not args.end:
            raise SystemExit("--end is required with --start")
        print(get_ingestion_range_status(args.start, args.end, args.db))
    else:
        print(get_ingestion_status(args.date, args.db))


if __name__ == "__main__":
    main()
