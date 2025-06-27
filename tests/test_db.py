import sqlite3
from datetime import datetime, timedelta

import config
from core import db as core_db
from core.db import init_db, purge_old_entries


def test_purge_old_entries(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    monkeypatch.setattr(core_db, "DB_PATH", str(db))
    init_db()
    conn = sqlite3.connect(db)
    old = datetime.now() - timedelta(days=31)
    conn.execute(
        "INSERT INTO devices (mac, vendor, first_seen, last_seen, rssi_history) VALUES (?, ?, ?, ?, ?)",
        ("AA", "V", old, old, "[]"),
    )
    conn.commit()
    conn.close()
    purge_old_entries()
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT * FROM devices").fetchall()
    conn.close()
    assert rows == []
