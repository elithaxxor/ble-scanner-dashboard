import asyncio
import json
from pathlib import Path

from active import hid_replay


class DummyClient:
    def __init__(self, address: str) -> None:
        self.address = address
        self.writes: list[tuple[str, bytes]] = []

    async def __aenter__(self) -> "DummyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        pass

    async def write_gatt_char(self, uuid: str, data: bytes) -> None:
        self.writes.append((uuid, data))


def test_replay(tmp_path: Path, monkeypatch) -> None:
    packets = ["01ff", "02aa"]
    pfile = tmp_path / "pkts.json"
    pfile.write_text(json.dumps(packets))

    dummy = DummyClient("AA:BB")

    monkeypatch.setattr(hid_replay, "BleakClient", lambda addr: dummy)

    asyncio.run(hid_replay.replay("AA:BB", "1234", pfile))

    assert dummy.writes == [
        ("1234", bytes.fromhex("01ff")),
        ("1234", bytes.fromhex("02aa")),
    ]
