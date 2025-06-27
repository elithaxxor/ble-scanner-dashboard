from sqlmodel import Session, select, create_engine
from datetime import datetime, timedelta

import config
from core import db as core_db
from core.db import init_db, purge_old_entries


def test_purge_old_entries(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    monkeypatch.setattr(core_db, "DB_PATH", str(db))
    core_db._engine = create_engine(f"sqlite:///{db}")
    init_db()
    from core.models import Device
    engine = core_db.get_engine()
    old = datetime.now() - timedelta(days=31)
    with Session(engine) as session:
        session.add(Device(mac="AA", vendor="V", first_seen=old, last_seen=old, rssi_history="[]"))
        session.commit()
    purge_old_entries()
    with Session(engine) as session:
        rows = session.exec(select(Device)).all()
    assert rows == []
