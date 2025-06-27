"""Radio backend plugin architecture."""

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

import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Dict, Optional, Set, Type

__all__ = [
    "RawPacket",
    "RadioBackend",
    "BlueZBackend",
    "UbertoothBackend",
    "NrfBackend",
    "BtlejackBackend",
    "get_backend",
]


@dataclass
class RawPacket:
    """Minimal raw packet representation."""

    timestamp: datetime
    phy: str
    channel: Optional[int]
    rssi: Optional[int]
    address: Optional[str] = None
    access_addr: Optional[str] = None
    handle: Optional[int] = None
    pdu_type: Optional[str] = None
    payload: bytes = b""


class RadioBackend(ABC):
    """Abstract base class for radio backends."""

    name: str
    capabilities: Set[str] = set()

    @abstractmethod
    async def scan(self) -> AsyncIterator[RawPacket]:
        """Yield raw packets from the radio."""


def get_backend(name: str) -> Optional[Type[RadioBackend]]:
    """Return backend class by name."""

    modules: Dict[str, str] = {
        "bluez": "ble_scanner.plugins.bluez",
        "ubertooth": "ble_scanner.plugins.ubertooth",
        "nrf": "ble_scanner.plugins.nrf",
        "btlejack": "ble_scanner.plugins.btlejack",
    }
    module_name = modules.get(name.lower())
    if module_name is None:
        return None
    module = importlib.import_module(module_name)
    return getattr(module, "Backend")


from .bluez import Backend as BlueZBackend
from .ubertooth import Backend as UbertoothBackend
from .nrf import Backend as NrfBackend
from .btlejack import Backend as BtlejackBackend
