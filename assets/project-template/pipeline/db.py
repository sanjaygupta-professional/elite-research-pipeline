"""SQLite state tracking for pipeline items and artifact downloads."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT DEFAULT '',
    published_at TEXT,
    description TEXT DEFAULT '',
    thumbnail_url TEXT,
    raw_metadata TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'new',
    error_message TEXT,
    notebook_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(source_type, source_id)
);

CREATE TABLE IF NOT EXISTS artifact_downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    artifact_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    downloaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intel_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    signals TEXT NOT NULL DEFAULT '[]',
    possibilities TEXT NOT NULL DEFAULT '[]',
    implications TEXT NOT NULL DEFAULT '[]',
    advisory TEXT NOT NULL DEFAULT '[]',
    themes TEXT NOT NULL DEFAULT '[]',
    raw_response TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(item_id)
);

CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_source ON items(source_type, source_id);
"""


@dataclass
class ItemRow:
    id: int
    source_type: str
    source_id: str
    url: str
    title: str
    author: str
    published_at: str | None
    description: str
    thumbnail_url: str | None
    raw_metadata: dict
    status: str
    error_message: str | None
    notebook_id: str | None
    created_at: str
    updated_at: str


class PipelineDB:
    def __init__(self, db_path: str = "pipeline.db"):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _row_to_item(self, row: sqlite3.Row) -> ItemRow:
        return ItemRow(
            id=row["id"],
            source_type=row["source_type"],
            source_id=row["source_id"],
            url=row["url"],
            title=row["title"],
            author=row["author"],
            published_at=row["published_at"],
            description=row["description"],
            thumbnail_url=row["thumbnail_url"],
            raw_metadata=json.loads(row["raw_metadata"]),
            status=row["status"],
            error_message=row["error_message"],
            notebook_id=row["notebook_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def item_exists(self, source_type: str, source_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM items WHERE source_type = ? AND source_id = ?",
            (source_type, source_id),
        ).fetchone()
        return row is not None

    def insert_item(
        self,
        source_type: str,
        source_id: str,
        url: str,
        title: str,
        author: str = "",
        published_at: str | None = None,
        description: str = "",
        thumbnail_url: str | None = None,
        raw_metadata: dict | None = None,
    ) -> int:
        """Insert a new item. Returns the row ID. Skips if already exists."""
        if self.item_exists(source_type, source_id):
            return -1

        now = self._now()
        cursor = self.conn.execute(
            """INSERT INTO items
            (source_type, source_id, url, title, author, published_at,
             description, thumbnail_url, raw_metadata, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)""",
            (
                source_type, source_id, url, title, author, published_at,
                description, thumbnail_url, json.dumps(raw_metadata or {}),
                now, now,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_pending_items(self, limit: int = 5) -> list[ItemRow]:
        """Get items with status 'new' or 'failed', oldest first."""
        rows = self.conn.execute(
            "SELECT * FROM items WHERE status IN ('new', 'failed') ORDER BY created_at ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_item(r) for r in rows]

    def update_status(
        self,
        item_id: int,
        status: str,
        error_message: str | None = None,
        notebook_id: str | None = None,
    ) -> None:
        fields = ["status = ?", "updated_at = ?"]
        params: list = [status, self._now()]

        if error_message is not None:
            fields.append("error_message = ?")
            params.append(error_message)
        if notebook_id is not None:
            fields.append("notebook_id = ?")
            params.append(notebook_id)

        params.append(item_id)
        self.conn.execute(
            f"UPDATE items SET {', '.join(fields)} WHERE id = ?",
            params,
        )
        self.conn.commit()

    def record_download(self, item_id: int, artifact_type: str, file_path: str) -> None:
        self.conn.execute(
            "INSERT INTO artifact_downloads (item_id, artifact_type, file_path, downloaded_at) VALUES (?, ?, ?, ?)",
            (item_id, artifact_type, file_path, self._now()),
        )
        self.conn.commit()

    def get_downloads(self, item_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT artifact_type, file_path, downloaded_at FROM artifact_downloads WHERE item_id = ?",
            (item_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all_items(self) -> list[ItemRow]:
        rows = self.conn.execute("SELECT * FROM items ORDER BY created_at DESC").fetchall()
        return [self._row_to_item(r) for r in rows]

    def get_stats(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT status, COUNT(*) as cnt FROM items GROUP BY status"
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}

    def save_intel_card(self, item_id: int, card: dict) -> int:
        """Save an intel card for an item. Returns card ID."""
        cur = self.conn.execute(
            """INSERT INTO intel_cards
               (item_id, signals, possibilities, implications, advisory, themes, raw_response)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(item_id) DO UPDATE SET
                   signals=excluded.signals,
                   possibilities=excluded.possibilities,
                   implications=excluded.implications,
                   advisory=excluded.advisory,
                   themes=excluded.themes,
                   raw_response=excluded.raw_response""",
            (
                item_id,
                json.dumps(card.get("signals", [])),
                json.dumps(card.get("possibilities", [])),
                json.dumps(card.get("implications", [])),
                json.dumps(card.get("advisory", [])),
                json.dumps(card.get("themes", [])),
                card.get("raw_response", ""),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_intel_cards(self, limit: int = 50, theme: str | None = None) -> list[dict]:
        """Get intel cards, optionally filtered by theme."""
        if theme:
            escaped = theme.replace("%", "\\%").replace("_", "\\_")
            rows = self.conn.execute(
                """SELECT ic.*, i.title, i.url FROM intel_cards ic
                   JOIN items i ON ic.item_id = i.id
                   WHERE ic.themes LIKE ? ESCAPE '\\'
                   ORDER BY ic.created_at DESC LIMIT ?""",
                (f"%{escaped}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """SELECT ic.*, i.title, i.url FROM intel_cards ic
                   JOIN items i ON ic.item_id = i.id
                   ORDER BY ic.created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            for key in ("signals", "possibilities", "implications", "advisory", "themes"):
                if isinstance(d[key], str):
                    d[key] = json.loads(d[key])
            result.append(d)
        return result

    def get_recent_themes(self, days: int = 30) -> dict[str, int]:
        """Get theme frequency counts from recent intel cards."""
        rows = self.conn.execute(
            """SELECT themes FROM intel_cards
               WHERE created_at > datetime('now', ?)""",
            (f"-{days} days",),
        ).fetchall()
        counts: dict[str, int] = {}
        for (themes_json,) in rows:
            for theme in json.loads(themes_json):
                counts[theme] = counts.get(theme, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))
