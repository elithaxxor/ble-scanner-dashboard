import asyncio
import logging
import typer
from core.scanner import EVENT_BUS, run_scanner
from plugins import load_plugins
from mqtt_client import setup as mqtt_setup
from core.utils import setup_logging

app = typer.Typer(help="BLE Scanner Suite CLI")

setup_logging()
logger = logging.getLogger(__name__)


@app.command()
def scan(interval: int = 5):
    """Run BLE scanner."""
    load_plugins()
    mqtt_setup()
    try:
        asyncio.run(run_scanner(interval))
    except KeyboardInterrupt:
        logger.info("Scanner stopped by user")


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
