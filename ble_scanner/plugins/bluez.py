"""BlueZ radio backend using Bleak."""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import AsyncIterator

from bleak import BleakScanner

from . import RadioBackend, RawPacket


class Backend(RadioBackend):
    """BlueZ implementation of :class:`RadioBackend`."""

    name = "bluez"
    capabilities = {"advertising"}

    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout

    async def scan(self) -> AsyncIterator[RawPacket]:
        while True:
            devices = await BleakScanner.discover(timeout=self.timeout)
            now = datetime.now()
            for dev in devices:
                yield RawPacket(
                    timestamp=now,
                    phy="LE1M",
                    channel=None,
                    rssi=dev.rssi,
                    address=dev.address,
                    payload=b"",
                )
            await asyncio.sleep(0)
