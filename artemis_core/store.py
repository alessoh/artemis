"""Saved lab runs, kept in the Neon Postgres database.

The table lives in its own schema, ``artemis``, so it never collides with the
tables Omnigent manages in the same database. Every function opens a short
connection, which suits Vercel's request-scoped functions.

The database address is read from the first of DATABASE_URL_UNPOOLED,
DATABASE_URL or POSTGRES_URL that is set (Vercel's Neon integration provides
these). When none is set, :func:`available` returns False and the website
still works, showing only the results published as static pages.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

URL_VARIABLES = ("DATABASE_URL_UNPOOLED", "DATABASE_URL", "POSTGRES_URL")
STATUSES = ("starting", "running", "complete", "failed", "stopped")

SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS artemis;
CREATE TABLE IF NOT EXISTS artemis.runs (
    id            TEXT PRIMARY KEY,
    kind          TEXT NOT NULL,
    title         TEXT NOT NULL,
    question      TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL,
    detail        TEXT NOT NULL DEFAULT '',
    report_md     TEXT,
    messages      JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS runs_status_idx ON artemis.runs (status);
CREATE INDEX IF NOT EXISTS runs_created_idx ON artemis.runs (created_at DESC);
"""

_schema_ready = False


class StoreUnavailable(RuntimeError):
    """Raised when no database address is configured."""


def database_url() -> str:
    """The configured Postgres address, or '' when none is set."""
    for name in URL_VARIABLES:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def available() -> bool:
    """True when a database address is configured."""
    return bool(database_url())


@contextmanager
def connect() -> Iterator[Any]:
    """Open a connection, create the schema once per process, commit on success."""
    global _schema_ready
    url = database_url()
    if not url:
        raise StoreUnavailable("No database address is configured (DATABASE_URL).")
    import psycopg  # imported lazily so pages and tests work without it

    with psycopg.connect(url, connect_timeout=10, autocommit=False) as conn:
        if not _schema_ready:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()
            _schema_ready = True
        yield conn
        conn.commit()


def _row(cur: Any, row: tuple | None) -> dict[str, Any] | None:
    if row is None:
        return None
    names = [d.name for d in cur.description]
    out = dict(zip(names, row))
    for key in ("created_at", "updated_at", "completed_at"):
        if isinstance(out.get(key), datetime):
            out[key] = out[key].astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def create_run(run_id: str, kind: str, title: str, question: str) -> None:
    """Record a newly started run."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO artemis.runs (id, kind, title, question, status) VALUES (%s, %s, %s, %s, 'starting') "
            "ON CONFLICT (id) DO NOTHING",
            (run_id, kind, title, question),
        )


def set_status(run_id: str, status: str, detail: str = "") -> None:
    """Update a run's status and a short human-readable detail."""
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE artemis.runs SET status = %s, detail = %s, updated_at = now() WHERE id = %s",
            (status, detail[:500], run_id),
        )


def complete_run(run_id: str, title: str, report_md: str, messages: list[str]) -> None:
    """Save a finished run's report and the lead's messages."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE artemis.runs SET status = 'complete', title = %s, report_md = %s, messages = %s::jsonb, "
            "detail = '', updated_at = now(), completed_at = now() WHERE id = %s",
            (title, report_md, json.dumps(messages), run_id),
        )


def save_messages(run_id: str, messages: list[str]) -> None:
    """Keep the lead's messages so far (used for runs that end without a report)."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE artemis.runs SET messages = %s::jsonb, updated_at = now() WHERE id = %s",
            (json.dumps(messages), run_id),
        )


def get_run(run_id: str) -> dict[str, Any] | None:
    """One run with its report and messages, or None."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM artemis.runs WHERE id = %s", (run_id,))
        return _row(cur, cur.fetchone())


def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    """Recent runs, newest first, without their long text fields."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, kind, title, question, status, detail, created_at, updated_at, completed_at "
            "FROM artemis.runs ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return [_row(cur, r) for r in cur.fetchall()]


def active_runs() -> list[dict[str, Any]]:
    """Runs still starting or running."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, kind, title, status, created_at, updated_at FROM artemis.runs "
            "WHERE status IN ('starting', 'running') ORDER BY created_at"
        )
        return [_row(cur, r) for r in cur.fetchall()]
