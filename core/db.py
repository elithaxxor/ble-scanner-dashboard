"""SQLite helper functions."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from config import DB_PATH


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            vendor TEXT,
            first_seen DATETIME,
            last_seen DATETIME,
            rssi_history TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def purge_old_entries(days: int = 30) -> None:
    """Remove outdated entries and shrink DB if oversized."""

    cutoff = datetime.now() - timedelta(days=days)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices WHERE last_seen < ?", (cutoff,))
    if Path(DB_PATH).stat().st_size > 1 * 1024**3:
        cursor.execute("DELETE FROM devices WHERE last_seen < ?", (cutoff,))
        conn.execute("VACUUM")
    conn.commit()
    conn.close()


def get_devices(limit: int | None = None, offset: int = 0):
    """Return devices as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM devices ORDER BY last_seen DESC"
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
