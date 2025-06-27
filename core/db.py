"""SQLite helper functions using SQLModel ORM."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

from sqlmodel import SQLModel, create_engine, Session, select, delete, text

from config import DB_PATH
from .models import Device

_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def get_engine():
    return _engine


def init_db() -> None:
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(_engine)


def purge_old_entries(days: int = 30) -> None:
    """Remove outdated entries and shrink DB if oversized."""
    cutoff = datetime.now() - timedelta(days=days)
    with Session(_engine) as session:
        session.exec(delete(Device).where(Device.last_seen < cutoff))
        session.commit()
    if Path(DB_PATH).stat().st_size > 1 * 1024**3:
        with _engine.connect() as conn:
            conn.execute(text("VACUUM"))


def get_session() -> Session:
    return Session(_engine)


def get_devices(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
    """Return devices as list of dicts."""
    with Session(_engine) as session:
        stmt = select(Device).order_by(Device.last_seen.desc())
        if limit is not None:
            stmt = stmt.offset(offset).limit(limit)
        rows = session.exec(stmt).all()
        return [d.dict() for d in rows]
