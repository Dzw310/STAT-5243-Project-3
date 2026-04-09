import sqlite3
from contextlib import contextmanager

from config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id    TEXT PRIMARY KEY,
    "group"    TEXT NOT NULL CHECK("group" IN ('A', 'B')),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    article_id  TEXT PRIMARY KEY,
    headline    TEXT NOT NULL,
    teaser      TEXT NOT NULL,
    full_summary TEXT NOT NULL,
    full_content TEXT NOT NULL,
    author      TEXT NOT NULL,
    date        TEXT NOT NULL,
    category    TEXT NOT NULL,
    image_url   TEXT,
    source_url  TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(user_id),
    event_type      TEXT NOT NULL CHECK(event_type IN (
                        'page_view', 'click', 'scroll', 'article_time', 'session_end'
                    )),
    article_id      TEXT,
    article_position INTEGER,
    value           REAL,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
"""


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def db_session():
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
