"""Vendor lookup utilities."""

import json
from pathlib import Path
from typing import Dict, Optional

from vendor_prefixes import VENDOR_PREFIXES

VENDOR_CACHE: Dict[str, str] = {}


def load_vendor_data(path: Path = Path("vendor_prefixes.json")) -> None:
    """Load vendor prefixes from bundled file and optional JSON."""
    VENDOR_CACHE.update({k.upper(): v for k, v in VENDOR_PREFIXES.items()})
    if not path.exists():
        return
    with path.open() as f:
        data = json.load(f)
        for prefix, vendor in data.items():
            VENDOR_CACHE[prefix.upper()] = vendor


def lookup_vendor(mac: str) -> str:
    """Return vendor name for a MAC address if known."""
    prefix = mac.upper().replace(":", "")[:6]
    return VENDOR_CACHE.get(prefix, "Unknown")
