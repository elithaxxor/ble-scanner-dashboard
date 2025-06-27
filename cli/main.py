import asyncio
import typer
import logging
from core.scanner import run_scanner, EVENT_BUS

app = typer.Typer(help="BLE Scanner Suite CLI")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def scan(interval: int = 5):
    """Run BLE scanner."""
    asyncio.run(run_scanner(interval))


@app.command()
def listen():
    """Consume events from the bus and print them."""

    async def _listen():
        while True:
            event = await EVENT_BUS.get()
            logger.info("%s", event)

    asyncio.run(_listen())


if __name__ == "__main__":
    app()
