import sqlite3
import threading
from pathlib import Path

DB_PATH = Path("data/crawler.db")


class Storage:
    def __init__(self):
        self._local = threading.local()
        self._ensure_db()
        self._init_schema()

    def _ensure_db(self):
        DB_PATH.parent.mkdir(exist_ok=True)

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self):
        conn = self._get_conn()

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS crawl_jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin_url TEXT,
                max_depth INTEGER,
                status TEXT DEFAULT 'active'
            );

            CREATE TABLE IF NOT EXISTS frontier (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                url TEXT,
                depth INTEGER,
                status TEXT DEFAULT 'pending',
                UNIQUE(job_id, url)
            );

            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                title TEXT,
                body TEXT
            );

            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                page_url TEXT,
                origin_url TEXT,
                depth INTEGER,
                UNIQUE(job_id, page_url)
            );

            CREATE TABLE IF NOT EXISTS inverted_index (
                term TEXT,
                page_url TEXT,
                freq INTEGER
            );
            """
        )

        conn.commit()

    def create_job(self, origin, depth):
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT INTO crawl_jobs (origin_url, max_depth) VALUES (?, ?)",
            (origin, depth),
        )
        conn.commit()
        return cur.lastrowid

    def complete_job(self, job_id):
        conn = self._get_conn()
        conn.execute(
            "UPDATE crawl_jobs SET status='completed' WHERE job_id=?",
            (job_id,),
        )
        conn.commit()

    def add_frontier(self, job_id, url, depth):
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT OR IGNORE INTO frontier (job_id, url, depth) VALUES (?, ?, ?)",
            (job_id, url, depth),
        )
        conn.commit()
        return cur.rowcount > 0

    def mark_in_progress(self, fid):
        conn = self._get_conn()
        conn.execute("UPDATE frontier SET status='in_progress' WHERE id=?", (fid,))
        conn.commit()

    def mark_done(self, fid):
        conn = self._get_conn()
        conn.execute("UPDATE frontier SET status='done' WHERE id=?", (fid,))
        conn.commit()

    def mark_failed(self, fid):
        conn = self._get_conn()
        conn.execute("UPDATE frontier SET status='failed' WHERE id=?", (fid,))
        conn.commit()

    def get_pending(self, job_id):
        conn = self._get_conn()
        return conn.execute(
            "SELECT * FROM frontier WHERE job_id=? AND status='pending'",
            (job_id,),
        ).fetchall()

    def save_page(self, url, title, body):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO pages (url, title, body) VALUES (?, ?, ?)",
            (url, title, body),
        )
        conn.commit()

    def add_discovery(self, job_id, page_url, origin_url, depth):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO discoveries VALUES (NULL, ?, ?, ?, ?)",
            (job_id, page_url, origin_url, depth),
        )
        conn.commit()

    def save_terms(self, url, terms):
        conn = self._get_conn()
        conn.execute("DELETE FROM inverted_index WHERE page_url=?", (url,))
        conn.executemany(
            "INSERT INTO inverted_index VALUES (?, ?, ?)",
            [(t, url, f) for t, f in terms],
        )
        conn.commit()

    def search(self, terms):
        if not terms:
            return []

        conn = self._get_conn()
        q = ",".join("?" * len(terms))

        return conn.execute(
            f"""
            SELECT ii.page_url, d.origin_url, d.depth, SUM(ii.freq) as score
            FROM inverted_index ii
            JOIN discoveries d ON ii.page_url = d.page_url
            WHERE ii.term IN ({q})
            GROUP BY ii.page_url, d.origin_url, d.depth
            ORDER BY score DESC
            """,
            terms,
        ).fetchall()

    def status(self):
        conn = self._get_conn()

        return {
            "active_jobs": conn.execute(
                "SELECT COUNT(*) FROM crawl_jobs WHERE status='active'"
            ).fetchone()[0],
            "pages": conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
            "pending": conn.execute(
                "SELECT COUNT(*) FROM frontier WHERE status='pending'"
            ).fetchone()[0],
            "in_progress": conn.execute(
                "SELECT COUNT(*) FROM frontier WHERE status='in_progress'"
            ).fetchone()[0],
            "done": conn.execute(
                "SELECT COUNT(*) FROM frontier WHERE status='done'"
            ).fetchone()[0],
            "failed": conn.execute(
                "SELECT COUNT(*) FROM frontier WHERE status='failed'"
            ).fetchone()[0],
        }