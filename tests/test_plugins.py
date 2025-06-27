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


def test_get_backend_imports_module(monkeypatch):
    class DummyBackend:
        pass

    dummy_module = SimpleNamespace(Backend=DummyBackend)

    called = {}

    def fake_import(name):
        called["name"] = name
        return dummy_module

    monkeypatch.setattr("ble_scanner.plugins.importlib.import_module", fake_import)

    backend_cls = get_backend("bluez")
    assert backend_cls is DummyBackend
    assert called["name"] == "ble_scanner.plugins.bluez"
    from ble_scanner import plugins as plugins_mod

    plugins_mod._BACKENDS.clear()


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


class DummyStream:
    def __init__(self, lines: list[str]):
        self._lines = [line.encode() for line in lines]

    def __aiter__(self):
        self._iter = iter(self._lines)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class DummyProc:
    def __init__(self, lines: list[str]):
        self.stdout = DummyStream(lines)

    def kill(self) -> None:  # pragma: no cover - not triggered
        pass

    async def wait(self) -> None:  # pragma: no cover - not triggered
        pass


@pytest.mark.asyncio
async def test_ubertooth_backend_scan(monkeypatch):
    backend_cls = get_backend("ubertooth")
    assert backend_cls is not None

    async def fake_exec(*args, **kwargs):
        return DummyProc(["AA:BB -30"])

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    backend = backend_cls()
    gen = backend.scan()
    packet = await gen.__anext__()
    assert packet.address == "AA:BB"
    assert packet.rssi == -30
    await gen.aclose()


@pytest.mark.asyncio
async def test_nrf_backend_scan(monkeypatch):
    backend_cls = get_backend("nrf")
    assert backend_cls is not None

    async def fake_exec(*args, **kwargs):
        return DummyProc(["CC:DD -40"])

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    backend = backend_cls()
    gen = backend.scan()
    packet = await gen.__anext__()
    assert packet.address == "CC:DD"
    assert packet.rssi == -40
    await gen.aclose()


@pytest.mark.asyncio
async def test_btlejack_backend_scan(monkeypatch):
    backend_cls = get_backend("btlejack")
    assert backend_cls is not None

    async def fake_exec(*args, **kwargs):
        return DummyProc(["EE:FF -50"])

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    backend = backend_cls()
    gen = backend.scan()
    packet = await gen.__anext__()
    assert packet.address == "EE:FF"
    assert packet.rssi == -50
    await gen.aclose()
