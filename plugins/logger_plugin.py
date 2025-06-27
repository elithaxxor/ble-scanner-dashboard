import logging

logger = logging.getLogger(__name__)

async def handle(event: dict) -> None:
    logger.info("Plugin event: %s", event)
