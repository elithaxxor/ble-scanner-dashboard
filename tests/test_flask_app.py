import asyncio
import sqlite3

import pytest

pytest.importorskip("flask")

import config
from core.db import init_db
from flask_app import STOP_EVENT, app


def setup_db(path):
    conn = sqlite3.connect(path)
    conn.execute(
        "INSERT INTO devices (mac, vendor, first_seen, last_seen, rssi_history) VALUES ('AA', 'Vendor', '2020-01-01', '2020-01-01', '[]')"
    )
    conn.commit()
    conn.close()


def test_flask_endpoints(tmp_path, monkeypatch):
    pytest.importorskip("flask")
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    init_db()
    setup_db(db)
    app.testing = True
    STOP_EVENT = asyncio.Event()
    with app.test_client() as client:
        r = client.get("/")
        assert r.status_code == 200
        r = client.get("/history?page=1")
        assert r.status_code == 200
        r = client.get("/shutdown")
        assert r.status_code == 302
