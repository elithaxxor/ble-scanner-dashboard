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

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ble_scanner.plugins import get_backend
from core.scanner import EVENT_BUS, run_radio_backend


class DummyDevice(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_get_backend():
    backend_cls = get_backend("bluez")
    assert backend_cls is not None


@pytest.mark.asyncio
async def test_bluez_backend_scan(monkeypatch):
    backend_cls = get_backend("bluez")
    assert backend_cls is not None

    async def fake_discover(timeout=5):
        return [DummyDevice(address="AA:BB", rssi=-10)]

    with patch("ble_scanner.plugins.bluez.BleakScanner.discover", fake_discover):
        backend = backend_cls(timeout=0)
        gen = backend.scan()
        packet = await gen.__anext__()
        assert packet.address == "AA:BB"
        await gen.aclose()


@pytest.mark.asyncio
async def test_run_radio_backend(monkeypatch):
    backend_cls = get_backend("bluez")
    assert backend_cls is not None

    async def fake_discover(timeout=5):
        return [DummyDevice(address="CC:DD", rssi=-20)]

    with patch("ble_scanner.plugins.bluez.BleakScanner.discover", fake_discover):
        backend = backend_cls(timeout=0)
        stop = asyncio.Event()

        async def runner():
            with patch("core.scanner.update_device", return_value=None):
                task = asyncio.create_task(run_radio_backend(backend, stop_event=stop))
                event = await asyncio.wait_for(EVENT_BUS.get(), timeout=0.2)
                stop.set()
                await task
                return event

        event = await runner()
        assert event["address"] == "CC:DD"
