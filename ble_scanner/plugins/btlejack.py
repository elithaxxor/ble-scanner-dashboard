from __future__ import annotations

import asyncio
from datetime import datetime
from typing import AsyncIterator

from . import RadioBackend, RawPacket


class Backend(RadioBackend):
    """BtleJack implementation of :class:`RadioBackend`."""

    name = "btlejack"
    capabilities = {"advertising"}

    def __init__(self, command: str = "btlejack") -> None:
        self.command = command

    async def scan(self) -> AsyncIterator[RawPacket]:
        proc = await asyncio.create_subprocess_exec(
            self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        assert proc.stdout is not None
        try:
            async for raw in proc.stdout:
                line = raw.decode().strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                addr, rssi = parts[0], int(parts[-1])
                yield RawPacket(
                    timestamp=datetime.now(),
                    phy="LE1M",
                    channel=None,
                    rssi=rssi,
                    address=addr,
                    payload=b"",
                )
                await asyncio.sleep(0)
        finally:
            proc.kill()
            await proc.wait()
