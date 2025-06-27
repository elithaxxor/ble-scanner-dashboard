"""Database helper functions using SQLModel ORM."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, List, Optional

from sqlmodel import SQLModel, Session, create_engine, select, delete

from config import DB_PATH
from .models import Device


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


def purge_old_entries(days: int = 30) -> None:
    """Remove outdated entries and shrink DB if oversized."""

    cutoff = datetime.now() - timedelta(days=days)
    with Session(get_engine()) as session:
        session.exec(delete(Device).where(Device.last_seen < cutoff))
        session.commit()
        if Path(DB_PATH).exists() and Path(DB_PATH).stat().st_size > 1 * 1024**3:
            session.connection().exec_driver_sql("VACUUM")


def get_devices(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
    """Return devices as list of dicts."""
    with Session(get_engine()) as session:
        stmt = select(Device).order_by(Device.last_seen.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        results = session.exec(stmt).all()
        return [d.dict() for d in results]
