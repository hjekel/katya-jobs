"""SQLite database for storing job listings and application tracking."""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from app.config import DATABASE_PATH
from app.scorer import classify_category, extract_city, detect_posting_type


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

        # Migration: add category, city, posting_type columns
        try:
            conn.execute("SELECT category FROM jobs LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE jobs ADD COLUMN category TEXT DEFAULT ''")
            conn.execute("ALTER TABLE jobs ADD COLUMN city TEXT DEFAULT ''")
            conn.execute("ALTER TABLE jobs ADD COLUMN posting_type TEXT DEFAULT 'direct'")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posting_type ON jobs(posting_type)")
            # Backfill existing jobs
            rows = conn.execute("SELECT id, title, snippet, location, company, source FROM jobs").fetchall()
            for row in rows:
                cat = classify_category(row["title"] or "", row["snippet"] or "")
                city = extract_city(row["location"] or "")
                ptype = detect_posting_type(row["company"] or "", row["source"] or "")
                conn.execute(
                    "UPDATE jobs SET category = ?, city = ?, posting_type = ? WHERE id = ?",
                    (cat, city, ptype, row["id"]),
                )

        # Ensure indexes exist even if columns already existed
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posting_type ON jobs(posting_type)")

        # Feedback table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improve_text TEXT,
                job_boards_text TEXT,
                suggestions_text TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Custom keywords table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
        """)

        # Custom job boards table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_job_boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT,
                created_at TEXT NOT NULL
            )
        """)


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
    category: str = "",
    city: str = "",
    posting_type: str = "direct",
) -> bool:
    """Insert a job if it doesn't exist. Returns True if newly inserted."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                """INSERT INTO jobs
                   (external_id, title, company, location, snippet, url, source,
                    score, salary_min, salary_max, salary_raw, date_posted, date_scraped,
                    category, city, posting_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (external_id, title, company, location, snippet, url, source,
                 score, salary_min, salary_max, salary_raw, date_posted, now,
                 category, city, posting_type),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def _add_dutch_exclusion(conditions: list, params: list):
    """Add SQL conditions to exclude jobs with Dutch-language indicators."""
    dutch_terms = [
        "Nederlands", "Dutch required", "Nederlandse taal",
        "NL spreken", "beheersing van de Nederlandse taal",
        "Dutch language", "vloeiend Nederlands", "moedertaal Nederlands",
    ]
    dutch_or_parts = []
    for term in dutch_terms:
        dutch_or_parts.append("(COALESCE(title,'') || ' ' || COALESCE(snippet,'') LIKE ?)")
        params.append(f"%{term}%")
    conditions.append(f"NOT ({' OR '.join(dutch_or_parts)})")


def get_jobs(
    source: Optional[str] = None,
    search: Optional[str] = None,
    only_new: bool = False,
    min_salary: Optional[int] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    posting_type: Optional[str] = None,
    company: Optional[str] = None,
    sort: str = "newest",
    limit: int = 200,
    offset: int = 0,
    exclude_dutch: bool = False,
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
        conditions.append("(salary_max >= ? OR salary_min IS NULL)")
        params.append(min_salary)
    if category:
        conditions.append("category = ?")
        params.append(category)
    if city:
        conditions.append("city = ?")
        params.append(city)
    if posting_type:
        conditions.append("posting_type = ?")
        params.append(posting_type)
    if company:
        conditions.append("company = ?")
        params.append(company)
    if exclude_dutch:
        _add_dutch_exclusion(conditions, params)

    where = " AND ".join(conditions)

    if sort == "newest":
        order = "date_scraped DESC, date_posted DESC"
    elif sort == "score":
        order = "score DESC, date_scraped DESC"
    elif sort == "oldest":
        order = "date_scraped ASC, date_posted ASC"
    else:
        order = "date_scraped DESC"

    query = f"SELECT * FROM jobs WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_job_count(
    source: Optional[str] = None,
    only_new: bool = False,
    min_salary: Optional[int] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    posting_type: Optional[str] = None,
    company: Optional[str] = None,
    exclude_dutch: bool = False,
) -> int:
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
    if search:
        conditions.append("(title LIKE ? OR company LIKE ? OR snippet LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])
    if category:
        conditions.append("category = ?")
        params.append(category)
    if city:
        conditions.append("city = ?")
        params.append(city)
    if posting_type:
        conditions.append("posting_type = ?")
        params.append(posting_type)
    if company:
        conditions.append("company = ?")
        params.append(company)
    if exclude_dutch:
        _add_dutch_exclusion(conditions, params)
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


ALL_SOURCES = {
    "linkedin": "LinkedIn",
    "indeed": "Indeed NL",
    "iamexpat": "IamExpat",
    "undutchables": "Undutchables",
    "adams": "Adams Recruitment",
    "welcometonl": "Welcome to NL",
}


def get_filter_counts() -> dict:
    """Get counts for all filter panels (category, city, company, posting_type, source)."""
    with get_db() as conn:
        categories = conn.execute(
            "SELECT category, COUNT(*) as c FROM jobs WHERE is_hidden = 0 AND category != '' GROUP BY category ORDER BY c DESC"
        ).fetchall()
        cities = conn.execute(
            "SELECT city, COUNT(*) as c FROM jobs WHERE is_hidden = 0 AND city != '' GROUP BY city ORDER BY c DESC"
        ).fetchall()
        companies = conn.execute(
            "SELECT company, COUNT(*) as c FROM jobs WHERE is_hidden = 0 AND company IS NOT NULL AND company != '' GROUP BY company ORDER BY c DESC"
        ).fetchall()
        posting_types = conn.execute(
            "SELECT posting_type, COUNT(*) as c FROM jobs WHERE is_hidden = 0 GROUP BY posting_type ORDER BY c DESC"
        ).fetchall()
        sources = conn.execute(
            "SELECT source, COUNT(*) as c FROM jobs WHERE is_hidden = 0 GROUP BY source ORDER BY c DESC"
        ).fetchall()
        # Always include all known sources, even with 0 count
        source_counts = {key: 0 for key in ALL_SOURCES}
        for row in sources:
            source_counts[row["source"]] = row["c"]
        return {
            "categories": {row["category"]: row["c"] for row in categories},
            "cities": {row["city"]: row["c"] for row in cities},
            "companies": {row["company"]: row["c"] for row in companies},
            "posting_types": {row["posting_type"]: row["c"] for row in posting_types},
            "sources": source_counts,
        }


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


# --------------------------------------------------------------------------
# Feedback
# --------------------------------------------------------------------------

def save_feedback(improve: str = "", job_boards: str = "", suggestions: str = "") -> int:
    """Save a feedback entry. Returns the new feedback ID."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (improve_text, job_boards_text, suggestions_text, created_at) VALUES (?, ?, ?, ?)",
            (improve, job_boards, suggestions, now),
        )
        return cur.lastrowid


def get_all_feedback() -> list[dict]:
    """Get all feedback entries, newest first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM feedback ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


# --------------------------------------------------------------------------
# Custom keywords
# --------------------------------------------------------------------------

def add_custom_keyword(keyword: str) -> bool:
    """Add a custom search keyword. Returns True if newly added."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO custom_keywords (keyword, created_at) VALUES (?, ?)",
                (keyword.strip(), now),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def get_custom_keywords() -> list[dict]:
    """Get all custom keywords."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM custom_keywords ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_custom_keyword(keyword_id: int):
    """Delete a custom keyword by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM custom_keywords WHERE id = ?", (keyword_id,))


# --------------------------------------------------------------------------
# Custom job boards
# --------------------------------------------------------------------------

def add_custom_job_board(name: str, url: str = "") -> bool:
    """Add a custom job board. Returns True if newly added."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO custom_job_boards (name, url, created_at) VALUES (?, ?, ?)",
                (name.strip(), url.strip(), now),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def get_custom_job_boards() -> list[dict]:
    """Get all custom job boards."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM custom_job_boards ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_custom_job_board(board_id: int):
    """Delete a custom job board by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM custom_job_boards WHERE id = ?", (board_id,))
