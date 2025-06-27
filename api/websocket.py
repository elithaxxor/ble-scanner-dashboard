import asyncio
import logging
from fastapi import WebSocket
from core.scanner import EVENT_BUS

logger = logging.getLogger(__name__)


async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            event = await EVENT_BUS.get()
            await ws.send_json(event)
    except asyncio.CancelledError:
        pass
    finally:
        await ws.close()
