import asyncio
from core.scanner import EVENT_BUS, parse_ibeacon, parse_eddystone


def test_event_bus():
    async def inner():
        await EVENT_BUS.put({"hello": "world"})
        return await asyncio.wait_for(EVENT_BUS.get(), timeout=1)

    result = asyncio.run(inner())
    assert result["hello"] == "world"


def test_parse_ibeacon():
    payload = b"\x02\x15" + b"\x00" * 21
    res = parse_ibeacon(payload)
    assert res["major"] == 0
    assert res["minor"] == 0


def test_parse_eddystone():
    payload = bytes([0x00, 0xC5]) + b"\x01" * 16
    res = parse_eddystone(payload)
    assert res["type"] == "uid"
