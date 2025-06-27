import json
import csv
import shutil
from pathlib import Path
from typing import Optional

from core.db import get_devices
from config import DB_PATH


def export_data(fmt: str, dest: Path, limit: Optional[int] = None) -> Path:
    """Export device records to JSON, CSV or SQLite."""
    fmt = fmt.lower()
    data = get_devices(limit)
    if fmt == "json":
        dest.write_text(json.dumps(data, indent=2))
    elif fmt == "csv":
        headers = [
            "mac_address",
            "device_name",
            "first_seen",
            "last_seen",
            "frequency_count",
            "rssi",
            "manufacturer",
            "rssi_history",
        ]
        with dest.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    elif fmt == "sqlite":
        shutil.copy(Path(DB_PATH), dest)
    else:
        raise ValueError(f"Unsupported format {fmt}")
    return dest
