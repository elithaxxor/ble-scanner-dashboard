
import types
import sys

from datetime import datetime
from types import SimpleNamespace

from pathlib import Path

import pytest

]# Create a dummy pyshark module before importing pipeline
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


