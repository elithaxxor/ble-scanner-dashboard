
from __future__ import annotations

from typing import Any, Optional, Callable
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session as _Session
from sqlalchemy import create_engine, select, delete, ForeignKey

class SQLModel(DeclarativeBase):
    def dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Session(_Session):
    def exec(self, statement):
        result = self.execute(statement)
        try:
            return result.scalars()
        except Exception:
            return result


def Field(
    default: Any = None,
    *,
    primary_key: bool = False,
    foreign_key: Optional[str] = None,
    default_factory: Optional[Callable[[], Any]] = None,
):
    if default_factory is not None:
        default = default_factory()
    args = []
    if foreign_key is not None:
        args.append(ForeignKey(foreign_key))
    return mapped_column(*args, default=default, primary_key=primary_key)

__all__ = ["SQLModel", "Session", "Field", "create_engine", "select", "delete"]
