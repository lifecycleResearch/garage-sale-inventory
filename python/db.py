"""SQLite database helper for garage sale inventory."""
import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "inventory.db"
SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    brand TEXT,
    description TEXT,
    category TEXT,
    condition TEXT,
    price REAL,
    suggested_price REAL,
    cost REAL,
    image_path TEXT,
    platforms_json TEXT DEFAULT '[]',
    status TEXT DEFAULT 'draft',
    listed_urls_json TEXT DEFAULT '{}',
    created_at REAL DEFAULT (unixepoch()),
    updated_at REAL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO categories (name) VALUES
('Furniture'), ('Electronics'), ('Clothing'), ('Toys'),
('Books'), ('Tools'), ('Sports'), ('Jewelry'), ('Art'), ('Collectibles'), ('Other');

CREATE TABLE IF NOT EXISTS platform_auths (
    platform TEXT PRIMARY KEY,
    auth_json TEXT DEFAULT '{}',
    connected INTEGER DEFAULT 0,
    updated_at REAL DEFAULT (unixepoch())
);

INSERT OR IGNORE INTO platform_auths (platform) VALUES
('ebay'), ('facebook_marketplace'), ('craigslist'), ('instagram'),
('x'), ('shopify'), ('woocommerce'), ('poshmark'), ('mercari');
"""

_local = threading.local()


def init_db() -> Path:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor():
    with get_conn() as conn:
        yield conn.cursor()


def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def rows_to_dicts(rows):
    return [row_to_dict(r) for r in rows if r is not None]


# ── Items ──────────────────────────────────────────────────────────

def create_item(data: dict) -> dict:
    item_id = f"item_{uuid.uuid4().hex[:12]}"
    data["id"] = item_id
    data.setdefault("platforms_json", "[]")
    data.setdefault("listed_urls_json", "{}")
    cols = ", ".join(data.keys())
    placeholders = ", ".join([f":{k}" for k in data])
    sql = f"INSERT INTO items ({cols}) VALUES ({placeholders})"
    with get_cursor() as cur:
        cur.execute(sql, data)
    return get_item(item_id)


def get_item(item_id: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return row_to_dict(cur.fetchone())


def get_items(status: str | None = None, limit: int = 1000, offset: int = 0) -> list[dict]:
    sql = "SELECT * FROM items WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_cursor() as cur:
        cur.execute(sql, params)
        return rows_to_dicts(cur.fetchall())


def update_item(item_id: str, data: dict) -> dict | None:
    data.pop("id", None)
    if not data:
        return get_item(item_id)
    sets = ", ".join([f"{k} = :{k}" for k in data])
    data["id"] = item_id
    with get_cursor() as cur:
        cur.execute(f"UPDATE items SET {sets} WHERE id = :id", data)
    return get_item(item_id)


def delete_item(item_id: str) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cur.rowcount > 0


def set_item_status(item_id: str, status: str) -> dict | None:
    return update_item(item_id, {"status": status})


# ── Categories ─────────────────────────────────────────────────────

def get_categories() -> list[dict]:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM categories ORDER BY name")
        return rows_to_dicts(cur.fetchall())


# ── Platform Auth ────────────────────────────────────────────────

def get_platforms() -> list[dict]:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM platform_auths ORDER BY platform")
        return rows_to_dicts(cur.fetchall())


def get_platform(platform: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM platform_auths WHERE platform = ?", (platform,))
        return row_to_dict(cur.fetchone())


def set_platform_auth(platform: str, auth: dict, connected: bool = False) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO platform_auths (platform, auth_json, connected, updated_at)
               VALUES (?, ?, ?, unixepoch())
               ON CONFLICT(platform) DO UPDATE SET
                 auth_json = excluded.auth_json,
                 connected = excluded.connected,
                 updated_at = excluded.updated_at""",
            (platform, json.dumps(auth), 1 if connected else 0),
        )
    return get_platform(platform)


# ── Helpers ──────────────────────────────────────────────────────

def dict_to_item(item: dict) -> dict:
    """Deserialize JSON fields for API response."""
    if not item:
        return item
    try:
        item["platforms"] = json.loads(item.get("platforms_json") or "[]")
    except Exception:
        item["platforms"] = []
    try:
        item["listed_urls"] = json.loads(item.get("listed_urls_json") or "{}")
    except Exception:
        item["listed_urls"] = {}
    return item
