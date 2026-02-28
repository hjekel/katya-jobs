"""SQLite database for storing job listings and application tracking."""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from app.config import DATABASE_PATH


def get_db_path() -> str:
    return os.environ.get("DATABASE_PATH", DATABASE_PATH)


@contextmanager
def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                snippet TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                salary_min INTEGER,
                salary_max INTEGER,
                salary_raw TEXT,
                date_posted TEXT,
                date_scraped TEXT NOT NULL,
                is_new INTEGER DEFAULT 1,
                is_hidden INTEGER DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_new ON jobs(is_new)")

        # Application tracker table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL REFERENCES jobs(id),
                status TEXT NOT NULL DEFAULT 'interested',
                date_saved TEXT NOT NULL,
                date_applied TEXT,
                notes TEXT DEFAULT '',
                reminder_date TEXT,
                UNIQUE(job_id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_app_status ON applications(status)")

        # Migration: add salary columns if upgrading from old schema
        try:
            conn.execute("SELECT salary_min FROM jobs LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE jobs ADD COLUMN salary_min INTEGER")
            conn.execute("ALTER TABLE jobs ADD COLUMN salary_max INTEGER")
            conn.execute("ALTER TABLE jobs ADD COLUMN salary_raw TEXT")


def upsert_job(
    external_id: str,
    title: str,
    company: Optional[str],
    location: Optional[str],
    snippet: Optional[str],
    url: str,
    source: str,
    score: int,
    date_posted: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    salary_raw: Optional[str] = None,
) -> bool:
    """Insert a job if it doesn't exist. Returns True if newly inserted."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                """INSERT INTO jobs
                   (external_id, title, company, location, snippet, url, source,
                    score, salary_min, salary_max, salary_raw, date_posted, date_scraped)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (external_id, title, company, location, snippet, url, source,
                 score, salary_min, salary_max, salary_raw, date_posted, now),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def get_jobs(
    source: Optional[str] = None,
    search: Optional[str] = None,
    only_new: bool = False,
    min_salary: Optional[int] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict]:
    conditions = ["is_hidden = 0"]
    params: list = []

    if source:
        conditions.append("source = ?")
        params.append(source)
    if only_new:
        conditions.append("is_new = 1")
    if search:
        conditions.append("(title LIKE ? OR company LIKE ? OR snippet LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])
    if min_salary is not None:
        # Show jobs with salary >= min OR jobs with no salary listed
        conditions.append("(salary_max >= ? OR salary_min IS NULL)")
        params.append(min_salary)

    where = " AND ".join(conditions)
    query = f"SELECT * FROM jobs WHERE {where} ORDER BY score DESC, date_scraped DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_job_count(source: Optional[str] = None, only_new: bool = False, min_salary: Optional[int] = None) -> int:
    conditions = ["is_hidden = 0"]
    params: list = []
    if source:
        conditions.append("source = ?")
        params.append(source)
    if only_new:
        conditions.append("is_new = 1")
    if min_salary is not None:
        conditions.append("(salary_max >= ? OR salary_min IS NULL)")
        params.append(min_salary)
    where = " AND ".join(conditions)
    with get_db() as conn:
        row = conn.execute(f"SELECT COUNT(*) as cnt FROM jobs WHERE {where}", params).fetchone()
        return row["cnt"]


def get_job_by_id(job_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def mark_all_seen():
    with get_db() as conn:
        conn.execute("UPDATE jobs SET is_new = 0 WHERE is_new = 1")


def hide_job(job_id: int):
    with get_db() as conn:
        conn.execute("UPDATE jobs SET is_hidden = 1 WHERE id = ?", (job_id,))


def get_stats() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM jobs WHERE is_hidden = 0").fetchone()["c"]
        new = conn.execute("SELECT COUNT(*) as c FROM jobs WHERE is_new = 1 AND is_hidden = 0").fetchone()["c"]
        sources = conn.execute(
            "SELECT source, COUNT(*) as c FROM jobs WHERE is_hidden = 0 GROUP BY source"
        ).fetchall()
        return {
            "total": total,
            "new": new,
            "by_source": {row["source"]: row["c"] for row in sources},
        }


# --------------------------------------------------------------------------
# Application tracker
# --------------------------------------------------------------------------

def save_application(job_id: int) -> bool:
    """Save a job to the application tracker. Returns True if newly saved."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO applications (job_id, status, date_saved) VALUES (?, 'interested', ?)",
                (job_id, now),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def update_application(job_id: int, status: Optional[str] = None,
                       notes: Optional[str] = None, reminder_date: Optional[str] = None,
                       date_applied: Optional[str] = None):
    with get_db() as conn:
        if status:
            conn.execute("UPDATE applications SET status = ? WHERE job_id = ?", (status, job_id))
        if notes is not None:
            conn.execute("UPDATE applications SET notes = ? WHERE job_id = ?", (notes, job_id))
        if reminder_date is not None:
            conn.execute("UPDATE applications SET reminder_date = ? WHERE job_id = ?", (reminder_date, job_id))
        if date_applied is not None:
            conn.execute("UPDATE applications SET date_applied = ? WHERE job_id = ?", (date_applied, job_id))


def remove_application(job_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))


def get_applications() -> list[dict]:
    """Get all saved applications with job details."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT a.*, j.title, j.company, j.location, j.url, j.source,
                   j.score, j.snippet, j.salary_min, j.salary_max, j.salary_raw
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            ORDER BY
                CASE a.status
                    WHEN 'offer' THEN 1
                    WHEN 'interview' THEN 2
                    WHEN 'applied' THEN 3
                    WHEN 'interested' THEN 4
                    WHEN 'rejected' THEN 5
                END,
                a.date_saved DESC
        """).fetchall()
        return [dict(row) for row in rows]
