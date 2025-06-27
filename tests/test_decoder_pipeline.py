from datetime import datetime
from types import SimpleNamespace
from pathlib import Path

import pytest

from ble_scanner.decoder import decode_pcap, SignalType, DecodedEvent


class DummyPacket(SimpleNamespace):
    pass


def make_packet(signal: str) -> DummyPacket:
    return DummyPacket(
        sniff_time=datetime(2021, 1, 1),
        btle=SimpleNamespace(
            advertising_header_type=signal,
            adv_address="AA:BB:CC:DD:EE:FF",
            rssi="-40",
        ),
    )


class DummyCapture(list):
    def close(self):
        pass


def fake_capture(file, *_, **__):
    name = Path(file).name
    mapping = {
        "adv_ind.pcap": "ADV_IND",
        "scan_req.pcap": "SCAN_REQ",
        "scan_rsp.pcap": "SCAN_RSP",
        "connect_req.pcap": "CONNECT_REQ",
        "adv_nonconn_ind.pcap": "ADV_NONCONN_IND",
    }
    signal = mapping.get(name, "ADV_IND")
    return DummyCapture([make_packet(signal)])


@pytest.mark.parametrize(
    "pcap,stype",
    [
        ("adv_ind.pcap", SignalType.ADV_IND),
        ("scan_req.pcap", SignalType.SCAN_REQ),
        ("scan_rsp.pcap", SignalType.SCAN_RSP),
        ("connect_req.pcap", SignalType.CONNECT_REQ),
        ("adv_nonconn_ind.pcap", SignalType.ADV_NONCONN_IND),
    ],
)
def test_decode_pcap(monkeypatch, pcap, stype):
    from ble_scanner import decoder as dec

    monkeypatch.setattr(dec.pipeline, "pyshark", SimpleNamespace(FileCapture=fake_capture))
    file = Path(__file__).parent / "data" / pcap
    events = list(dec.decode_pcap(str(file)))
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, DecodedEvent)
    assert event.signal == stype
    assert event.address == "AA:BB:CC:DD:EE:FF"
    assert event.rssi == -40

