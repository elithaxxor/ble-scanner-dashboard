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



class DummyProcess:
    def __init__(self, lines):
        self._lines = [l.encode() for l in lines]
        self.returncode = None

    async def _readline(self):
        if self._lines:
            return self._lines.pop(0)
        return b""

    @property
    def stdout(self):
        return SimpleNamespace(readline=self._readline)

    def kill(self):
        self.returncode = 0

    terminate = kill

    async def wait(self):
        pass

def test_get_backend_imports_module(monkeypatch):
    class DummyBackend:
        pass

    dummy_module = SimpleNamespace(Backend=DummyBackend)

    called = {}

    def fake_import(name):
        called["name"] = name
        return dummy_module

    monkeypatch.setattr(
        "ble_scanner.plugins.importlib.import_module", fake_import
    )

    backend_cls = get_backend("bluez")
    assert backend_cls is DummyBackend
    assert called["name"] == "ble_scanner.plugins.bluez"
    from ble_scanner import plugins as plugins_mod
    plugins_mod._BACKENDS.clear()



@pytest.mark.asyncio
async def test_get_backend():
    for name in ("bluez", "ubertooth", "nrf", "btlejack"):
        backend_cls = get_backend(name)
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
async def test_ubertooth_backend_scan(monkeypatch):
    backend_cls = get_backend("ubertooth")
    assert backend_cls is not None

    proc = DummyProcess(["AA:BB:CC:DD:EE:FF -40"])

    async def fake_exec(*args, **kwargs):
        return proc

    with patch(
        "ble_scanner.plugins.ubertooth.asyncio.create_subprocess_exec",
        fake_exec,
    ):
        backend = backend_cls()
        gen = backend.scan()
        packet = await gen.__anext__()
        assert packet.address == "AA:BB:CC:DD:EE:FF"
        assert packet.rssi == -40
        await gen.aclose()


@pytest.mark.asyncio
async def test_nrf_backend_scan(monkeypatch):
    backend_cls = get_backend("nrf")
    assert backend_cls is not None

    proc = DummyProcess(["11:22:33:44:55:66 -30"])

    async def fake_exec(*args, **kwargs):
        return proc

    with patch(
        "ble_scanner.plugins.nrf.asyncio.create_subprocess_exec",
        fake_exec,
    ):
        backend = backend_cls()
        gen = backend.scan()
        packet = await gen.__anext__()
        assert packet.address == "11:22:33:44:55:66"
        assert packet.rssi == -30
        await gen.aclose()


@pytest.mark.asyncio
async def test_btlejack_backend_scan(monkeypatch):
    backend_cls = get_backend("btlejack")
    assert backend_cls is not None

    proc = DummyProcess(["FF:EE:DD:CC:BB:AA -25"])

    async def fake_exec(*args, **kwargs):
        return proc

    with patch(
        "ble_scanner.plugins.btlejack.asyncio.create_subprocess_exec",
        fake_exec,
    ):
        backend = backend_cls()
        gen = backend.scan()
        packet = await gen.__anext__()
        assert packet.address == "FF:EE:DD:CC:BB:AA"
        assert packet.rssi == -25
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
