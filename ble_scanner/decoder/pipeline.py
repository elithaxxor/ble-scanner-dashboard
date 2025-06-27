"""Pcap decoding utilities using pyshark."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generator, Optional

try:
    import pyshark
except Exception as exc:  # pragma: no cover - optional dependency
    pyshark = None  # type: ignore


class SignalType(Enum):
    """Enumeration of common BLE signal types."""

    ADV_IND = "ADV_IND"
    ADV_DIRECT_IND = "ADV_DIRECT_IND"
    ADV_NONCONN_IND = "ADV_NONCONN_IND"
    SCAN_REQ = "SCAN_REQ"
    SCAN_RSP = "SCAN_RSP"
    CONNECT_REQ = "CONNECT_REQ"


@dataclass
class DecodedEvent:
    """Decoded BLE event extracted from a pcap packet."""

    timestamp: datetime
    source: Optional[str]
    destination: Optional[str]
    signal_type: SignalType
    rssi: Optional[int] = None


_PDU_MAP = {
    "ADV_IND": SignalType.ADV_IND,
    "ADV_DIRECT_IND": SignalType.ADV_DIRECT_IND,
    "ADV_NONCONN_IND": SignalType.ADV_NONCONN_IND,
    "SCAN_REQ": SignalType.SCAN_REQ,
    "SCAN_RSP": SignalType.SCAN_RSP,
    "CONNECT_REQ": SignalType.CONNECT_REQ,
}


def parse_pcap(path: str) -> Generator[DecodedEvent, None, None]:
    """Yield :class:`DecodedEvent` objects from a pcap file."""

    if pyshark is None:
        raise RuntimeError("pyshark is required to parse pcap files")

    capture = pyshark.FileCapture(path, display_filter="btle")
    for packet in capture:
        btle = getattr(packet, "btle", None)
        if btle is None:
            continue
        pdu_val = (
            getattr(btle, "advertising_header_pdu_type", None)
            or getattr(btle, "pdu_type", None)
        )
        if pdu_val is None:
            continue
        pdu_str = str(pdu_val).upper()
        signal = None
        for key, val in _PDU_MAP.items():
            if key in pdu_str:
                signal = val
                break
        if signal is None:
            continue
        ts = datetime.fromtimestamp(float(packet.sniff_timestamp))
        src = getattr(btle, "adva_address", None) or getattr(btle, "src_addr", None)
        dst = getattr(btle, "inita_address", None) or getattr(btle, "dst_addr", None)
        rssi = getattr(packet, "rssi", None)
        try:
            rssi = int(str(rssi)) if rssi is not None else None
        except ValueError:
            rssi = None
        yield DecodedEvent(ts, src, dst, signal, rssi)
