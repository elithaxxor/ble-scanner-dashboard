import csv
from pathlib import Path
from typing import Dict, Optional

from vendor_prefixes import VENDOR_PREFIXES

VENDOR_CACHE: Dict[str, str] = {}


def load_vendor_data(path: Path = Path("vendors.csv")) -> None:
    """Load vendor prefixes from bundled file and optional CSV."""
    VENDOR_CACHE.update({k.upper(): v for k, v in VENDOR_PREFIXES.items()})
    if not path.exists():
        return
    with path.open() as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                prefix, vendor = row[0].strip().upper(), row[1].strip()
                VENDOR_CACHE[prefix] = vendor


def lookup_vendor(mac: str) -> Optional[str]:
    """Return vendor name for a MAC address if known."""
    prefix = mac.upper().replace(":", "")[:6]
    return VENDOR_CACHE.get(prefix)
