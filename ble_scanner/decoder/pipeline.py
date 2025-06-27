from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from enum import Enum
from typing import Generator, Optional

try:
    import pyshark  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyshark = None

__all__ = ["SignalType", "DecodedEvent", "decode_pcap"]


class SignalType(str, Enum):
    """Enumeration of BLE signal types from the dissector."""

    ADV_IND = "ADV_IND"
    ADV_NONCONN_IND = "ADV_NONCONN_IND"
    ADV_DIRECT_IND = "ADV_DIRECT_IND"
    SCAN_REQ = "SCAN_REQ"
    SCAN_RSP = "SCAN_RSP"
    CONNECT_REQ = "CONNECT_REQ"
    UNKNOWN = "UNKNOWN"


@dataclass
class DecodedEvent:
    """High level representation of a decoded BLE packet."""

    timestamp: _dt.datetime
    address: Optional[str]
    signal: SignalType
    rssi: Optional[int]


_TYPE_MAP = {
    "ADV_IND": SignalType.ADV_IND,
    "ADV_NONCONN_IND": SignalType.ADV_NONCONN_IND,
    "ADV_DIRECT_IND": SignalType.ADV_DIRECT_IND,
    "SCAN_REQ": SignalType.SCAN_REQ,
    "SCAN_RSP": SignalType.SCAN_RSP,
    "CONNECT_REQ": SignalType.CONNECT_REQ,
}


def _map_type(raw_type: str) -> SignalType:
    return _TYPE_MAP.get(raw_type.upper(), SignalType.UNKNOWN)


def decode_pcap(path: str) -> Generator[DecodedEvent, None, None]:
    """Yield :class:`DecodedEvent` items parsed from a pcap file."""

    if pyshark is None:  # pragma: no cover - environment without pyshark
        raise ImportError("pyshark is required to parse pcaps")

    capture = pyshark.FileCapture(path, keep_packets=False)
    for packet in capture:
        btle = getattr(packet, "btle", None)
        if btle is None:
            continue
        raw_type = getattr(btle, "advertising_header_type", None)
        addr = getattr(btle, "adv_address", None)
        rssi = getattr(btle, "rssi", None)
        if isinstance(rssi, str):
            try:
                rssi = int(rssi)
            except ValueError:
                rssi = None
        event = DecodedEvent(
            timestamp=getattr(packet, "sniff_time", _dt.datetime.utcnow()),
            address=str(addr) if addr is not None else None,
            signal=_map_type(str(raw_type)) if raw_type is not None else SignalType.UNKNOWN,
            rssi=rssi,
        )
        yield event
    capture.close()
