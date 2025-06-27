import asyncio
from sqlmodel import Session, create_engine
from datetime import datetime

import pytest

pytest.importorskip("flask")

import config
from core import db as core_db
from core.db import init_db
import flask_app
from flask_app import app


def setup_db(engine):
    from core.models import Device

    with Session(engine) as session:
        session.add(
            Device(
                mac="AA",
                vendor="Vendor",
                first_seen=datetime(2020, 1, 1),
                last_seen=datetime(2020, 1, 1),
                rssi_history="[]",
            )
        )
        session.commit()


def test_flask_endpoints(tmp_path, monkeypatch):
    pytest.importorskip("flask")
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    monkeypatch.setattr(core_db, "DB_PATH", str(db))
    core_db._engine = create_engine(f"sqlite:///{db}")
    init_db()
    setup_db(core_db._engine)
    app.testing = True
    flask_app.STOP_EVENT = asyncio.Event()
    with app.test_client() as client:
        r = client.get("/")
        assert r.status_code == 200
        r = client.get("/history?page=1")
        assert r.status_code == 200
        r = client.get("/shutdown")
        assert r.status_code == 302
