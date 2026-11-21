
import sqlite3
from pathlib import Path
import json
from datetime import datetime, timezone


# ==========================================
# CAREERRADAR AI - DATABASE ENGINE
# Created by Priyanshi Mishra
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "jobs.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(
        DB_PATH,
        timeout=30
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS jobs (

                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                job_type TEXT,
                date TEXT,
                description TEXT,
                skills TEXT,
                salary TEXT,
                url TEXT UNIQUE,
                source TEXT,
                remote INTEGER DEFAULT 0,
                categories TEXT DEFAULT '[]',
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_jobs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                status TEXT DEFAULT 'Saved',
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE

            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS app_metadata (

                key TEXT PRIMARY KEY,
                value TEXT

            )
        """)

        # Safely upgrade older databases
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(jobs)"
            ).fetchall()
        }

        if "categories" not in columns:

            connection.execute("""
                ALTER TABLE jobs
                ADD COLUMN categories TEXT DEFAULT '[]'
            """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_date
            ON jobs(date)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company
            ON jobs(company)
        """)


# ==========================================
# METADATA MANAGEMENT
# ==========================================

def set_metadata(key, value):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO app_metadata (key, value)
            VALUES (?, ?)

            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value

        """, (key, str(value)))


def get_metadata(key, default=None):

    with get_connection() as connection:

        row = connection.execute("""
            SELECT value
            FROM app_metadata
            WHERE key = ?
        """, (key,)).fetchone()

        return row["value"] if row else default


# ==========================================
# SAVE / UPDATE JOBS
# ==========================================

def save_jobs(jobs):

    initialize_database()

    inserted = 0
    updated = 0

    with get_connection() as connection:

        for job in jobs:

            job_id = job.get("id")
            job_url = job.get("url")

            if not job_id or not job_url:
                continue

            categories = job.get("categories", [])

            if not isinstance(categories, list):
                categories = []

            existing = connection.execute("""
                SELECT id
                FROM jobs
                WHERE id = ? OR url = ?
            """, (job_id, job_url)).fetchone()

            connection.execute("""
                INSERT INTO jobs (

                    id,
                    title,
                    company,
                    location,
                    job_type,
                    date,
                    description,
                    skills,
                    salary,
                    url,
                    source,
                    remote,
                    categories,
                    fetched_at

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)

                ON CONFLICT(id)
                DO UPDATE SET

                    title = excluded.title,
                    company = excluded.company,
                    location = excluded.location,
                    job_type = excluded.job_type,
                    date = excluded.date,
                    description = excluded.description,
                    skills = excluded.skills,
                    salary = excluded.salary,
                    url = excluded.url,
                    source = excluded.source,
                    remote = excluded.remote,
                    categories = excluded.categories,
                    fetched_at = CURRENT_TIMESTAMP

            """, (

                job_id,
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("job_type", ""),
                job.get("date", ""),
                job.get("description", ""),
                job.get("skills", ""),
                job.get("salary", ""),
                job_url,
                job.get("source", ""),
                int(bool(job.get("remote", False))),
                json.dumps(categories)

            ))

            if existing:
                updated += 1
            else:
                inserted += 1

    set_metadata("last_updated", datetime.now(
        timezone.utc
    ).isoformat())

    set_metadata("last_fetch_count", len(jobs))

    set_metadata("last_new_jobs", inserted)

    return inserted, updated


# ==========================================
# GET ALL JOBS
# ==========================================

def get_all_jobs():

    initialize_database()

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM jobs
            ORDER BY date DESC, fetched_at DESC
        """).fetchall()

        result = []

        for row in rows:

            job = dict(row)

            try:
                job["categories"] = json.loads(
                    job["categories"] or "[]"
                )
            except (ValueError, TypeError):
                job["categories"] = []

            result.append(job)

        return result


# ==========================================
# SEARCH JOBS
# ==========================================

def search_jobs(keyword=""):

    initialize_database()

    with get_connection() as connection:

        search = f"%{keyword.strip()}%"

        rows = connection.execute("""
            SELECT *
            FROM jobs

            WHERE title LIKE ?
               OR company LIKE ?
               OR skills LIKE ?
               OR description LIKE ?
               OR location LIKE ?
               OR categories LIKE ?

            ORDER BY date DESC

        """, (
            search,
            search,
            search,
            search,
            search,
            search
        )).fetchall()

        return [dict(row) for row in rows]


# ==========================================
# FILTER BY CATEGORY
# ==========================================

def get_jobs_by_category(category):

    initialize_database()

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM jobs
            WHERE categories LIKE ?
            ORDER BY date DESC
        """, (f'%"{category}"%',)).fetchall()

        return [dict(row) for row in rows]


# ==========================================
# SAVE A JOB
# ==========================================

def save_job(job_id):

    initialize_database()

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT OR IGNORE INTO saved_jobs (job_id)

            SELECT id
            FROM jobs
            WHERE id = ?

        """, (job_id,))

        return cursor.rowcount > 0


# ==========================================
# REMOVE SAVED JOB
# ==========================================

def remove_saved_job(job_id):

    initialize_database()

    with get_connection() as connection:

        cursor = connection.execute("""
            DELETE FROM saved_jobs
            WHERE job_id = ?
        """, (job_id,))

        return cursor.rowcount > 0


# ==========================================
# UPDATE APPLICATION STATUS
# ==========================================

def update_application_status(job_id, status):

    initialize_database()

    allowed_statuses = [

        "Saved",
        "Applied",
        "Interview",
        "Rejected",
        "Selected"

    ]

    if status not in allowed_statuses:

        raise ValueError(
            "Invalid application status"
        )

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE saved_jobs

            SET status = ?

            WHERE job_id = ?

        """, (status, job_id))

        return cursor.rowcount > 0


# ==========================================
# GET SAVED JOBS
# ==========================================

def get_saved_jobs():

    initialize_database()

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT

                jobs.*,
                saved_jobs.status,
                saved_jobs.saved_at

            FROM saved_jobs

            JOIN jobs
            ON jobs.id = saved_jobs.job_id

            ORDER BY saved_jobs.saved_at DESC

        """).fetchall()

        return [dict(row) for row in rows]


# ==========================================
# DATABASE STATISTICS
# ==========================================

def get_database_stats():

    initialize_database()

    with get_connection() as connection:

        total = connection.execute("""
            SELECT COUNT(*) FROM jobs
        """).fetchone()[0]

        saved = connection.execute("""
            SELECT COUNT(*) FROM saved_jobs
        """).fetchone()[0]

        remote = connection.execute("""
            SELECT COUNT(*)
            FROM jobs
            WHERE remote = 1
        """).fetchone()[0]

        sources = connection.execute("""
            SELECT COUNT(DISTINCT source)
            FROM jobs
        """).fetchone()[0]

        return {

            "total_jobs": total,
            "saved_jobs": saved,
            "remote_jobs": remote,
            "sources": sources,
            "last_updated": get_metadata("last_updated"),
            "last_new_jobs": int(
                get_metadata("last_new_jobs", 0)
            )

        }


# ==========================================
# DATABASE TEST
# ==========================================

if __name__ == "__main__":

    initialize_database()

    print("\nCAREERRADAR AI DATABASE")
    print("=" * 40)

    print("Database:", DB_PATH)

    stats = get_database_stats()

    print("Total jobs:", stats["total_jobs"])
    print("Saved jobs:", stats["saved_jobs"])
    print("Remote jobs:", stats["remote_jobs"])
    print("Sources:", stats["sources"])
    print("Last updated:", stats["last_updated"])

    print("=" * 40)
    print("Database initialized successfully!")
