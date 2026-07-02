import os
import sqlite3
from typing import List

DB_PATH = os.getenv("MEMORY_DB_PATH", "memory.db")
MAX_MEMORY_MESSAGES = 6

def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    return con

def get_memory(session_id: str) -> List[dict]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT role, content FROM memory
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, MAX_MEMORY_MESSAGES),
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def add_to_memory(session_id: str, message: dict) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO memory (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, message["role"], message["content"]),
        )