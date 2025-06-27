import asyncio
import logging

import uvicorn

from api.app import app
from core.scanner import run_scanner
from plugins import load_plugins
from mqtt_client import setup as mqtt_setup
from core.utils import setup_logging
import config

setup_logging()
logger = logging.getLogger(__name__)


async def main() -> None:
    load_plugins()
    mqtt_setup()
    scanner_task = asyncio.create_task(run_scanner(config.SCAN_INTERVAL))
    server_task = asyncio.to_thread(
        uvicorn.run,
        app,
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        log_level="info",
    )
    await asyncio.gather(scanner_task, server_task)


if __name__ == "__main__":
    asyncio.run(main())
