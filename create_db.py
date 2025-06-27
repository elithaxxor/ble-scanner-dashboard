"""Create the application database and run migrations."""

from alembic.config import Config
from alembic import command

from core.db import init_db


def main() -> None:
    init_db()
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    main()

