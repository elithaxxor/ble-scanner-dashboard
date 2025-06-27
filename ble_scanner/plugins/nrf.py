
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import AsyncIterator

"""Nordic nRF Sniffer radio backend."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime
from typing import AsyncIterator, Iterable, Optional


from . import RadioBackend, RawPacket


class Backend(RadioBackend):
    """nRF Sniffer implementation of :class:`RadioBackend`."""

    name = "nrf"
    capabilities = {"advertising"}


    def __init__(self, command: str = "nrf-sniffer") -> None:
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

    def __init__(self, command: Iterable[str] | None = None) -> None:
        self.command = list(command) if command else ["nrf_sniffer"]

    def _parse_line(self, line: str) -> tuple[Optional[str], Optional[int]]:
        match = re.search(r"([0-9A-Fa-f:]{11,17}).*?(-?\d+)", line)
        if match:
            return match.group(1), int(match.group(2))
        return None, None

    async def scan(self) -> AsyncIterator[RawPacket]:
        proc = await asyncio.create_subprocess_exec(
            *self.command,
            stdout=asyncio.subprocess.PIPE,
        )
        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                address, rssi = self._parse_line(line.decode(errors="ignore"))

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

                    address=address,
                    payload=line.rstrip(b"\n"),
                )
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

