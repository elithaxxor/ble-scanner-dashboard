import asyncio
from types import SimpleNamespace

import config
from core import scanner
from core.db import get_devices, init_db


class DummyDevice(SimpleNamespace):
    pass


async def fake_discover():
    return [
        DummyDevice(address="AA:BB:CC:DD:EE:FF", name="Test", rssi=-30, metadata={})
    ]


def test_scan_once(tmp_path, monkeypatch):
    db = tmp_path / "db.sqlite"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    monkeypatch.setattr(scanner, "DB_PATH", str(db), raising=False)
    from core import db as core_db

    monkeypatch.setattr(core_db, "DB_PATH", str(db))
    init_db()
    monkeypatch.setattr(
        scanner, "BleakScanner", SimpleNamespace(discover=fake_discover)
    )

    async def fake_vendor(mac: str) -> str:
        return "Vendor"

    monkeypatch.setattr(scanner, "vendor_for_mac", fake_vendor)
    asyncio.run(scanner.scan_once())
    rows = get_devices(1)
    assert rows[0]["mac"] == "AA:BB:CC:DD:EE:FF"
