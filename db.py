# db.py
import sqlite3
from contextlib import closing

DB_PATH = "items.db"

def get_conn():
    # Single-process bot: this is fine.
    return sqlite3.connect(DB_PATH)

def init_db():
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item)
        )
        """)

def upsert_item(user_id: str, item: str, location: str):
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as cur:
        cur.execute("""
        INSERT INTO items (user_id, item, location)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item)
        DO UPDATE SET location=excluded.location, updated_at=CURRENT_TIMESTAMP
        """, (user_id, item, location))

def get_item(user_id: str, item: str) -> str | None:
    with closing(get_conn()) as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT location FROM items WHERE user_id=? AND item=?", (user_id, item))
        row = cur.fetchone()
        return row[0] if row else None

def delete_item(user_id: str, item: str) -> bool:
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as cur:
        cur.execute("DELETE FROM items WHERE user_id=? AND item=?", (user_id, item))
        return cur.rowcount > 0

def list_items(user_id: str) -> list[tuple[str, str]]:
    with closing(get_conn()) as conn, closing(conn.cursor()) as cur:
        cur.execute("SELECT item, location FROM items WHERE user_id=? ORDER BY item ASC", (user_id,))
        return cur.fetchall()
