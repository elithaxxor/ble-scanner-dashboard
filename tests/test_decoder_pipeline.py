import types
import sys
from pathlib import Path

import pytest

# Create a dummy pyshark module before importing pipeline
fake_pyshark = types.SimpleNamespace()
sys.modules['pyshark'] = fake_pyshark

from ble_scanner.decoder import pipeline


class DummyLayer:
    def __init__(self, pdu: str, src: str, dst: str) -> None:
        self.advertising_header_pdu_type = pdu
        self.adva_address = src
        self.inita_address = dst


class DummyPacket:
    def __init__(self, ts: float, pdu: str, src: str, dst: str, rssi: int) -> None:
        self.sniff_timestamp = str(ts)
        self.rssi = rssi
        self.btle = DummyLayer(pdu, src, dst)


@pytest.mark.parametrize(
    "pdu,expected",
    [
        ("ADV_IND", pipeline.SignalType.ADV_IND),
        ("ADV_DIRECT_IND", pipeline.SignalType.ADV_DIRECT_IND),
        ("ADV_NONCONN_IND", pipeline.SignalType.ADV_NONCONN_IND),
        ("SCAN_REQ", pipeline.SignalType.SCAN_REQ),
        ("CONNECT_REQ", pipeline.SignalType.CONNECT_REQ),
    ],
)
def test_parse_pcap(monkeypatch, tmp_path: Path, pdu: str, expected: pipeline.SignalType) -> None:
    pcap = tmp_path / f"{pdu.lower()}.pcap"
    pcap.write_bytes(b"\x00")

    packets = [DummyPacket(0.0, pdu, "AA:BB", "CC:DD", -40)]

    def fake_capture(path: str, display_filter: str = "btle"):
        assert Path(path) == pcap
        return packets

    fake_pyshark.FileCapture = fake_capture
    monkeypatch.setattr(pipeline, "pyshark", fake_pyshark)

    events = list(pipeline.parse_pcap(str(pcap)))
    assert len(events) == 1
    event = events[0]
    assert event.signal_type == expected
    assert event.source == "AA:BB"
    assert event.destination == "CC:DD"
    assert event.rssi == -40
