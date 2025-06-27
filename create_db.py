"""Bootstrap database using Alembic migrations."""

from alembic.config import Config
from alembic import command


def main() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    main()
