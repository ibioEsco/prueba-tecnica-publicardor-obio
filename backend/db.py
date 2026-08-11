import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "posts.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'en',
                text TEXT NOT NULL,
                image_url TEXT,
                image_prompt TEXT,
                viral_score INTEGER NOT NULL,
                viral_reasons TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


def save_post(topic: str, language: str, text: str, image_url: str,
              image_prompt: str, viral_score: int, viral_reasons: list[str]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO posts (topic, language, text, image_url, image_prompt,
               viral_score, viral_reasons, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)""",
            (topic, language, text, image_url, image_prompt,
             viral_score, json.dumps(viral_reasons), now, now)
        )
        conn.commit()
        return cur.lastrowid


def update_post_status(post_id: int, status: str, text: str = None):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        if text:
            conn.execute(
                "UPDATE posts SET status=?, text=?, updated_at=? WHERE id=?",
                (status, text, now, post_id)
            )
        else:
            conn.execute(
                "UPDATE posts SET status=?, updated_at=? WHERE id=?",
                (status, now, post_id)
            )
        conn.commit()


def get_all_posts() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM posts ORDER BY created_at DESC"
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["viral_reasons"] = json.loads(d["viral_reasons"])
        result.append(d)
    return result


def get_post(post_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["viral_reasons"] = json.loads(d["viral_reasons"])
    return d
