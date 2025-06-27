import asyncio
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from bleak import BleakScanner

from config import DB_PATH, LOG_FILE, LOG_LEVEL
from plugins import dispatch_event
from mqtt_client import publish_event

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

EVENT_BUS: "asyncio.Queue[dict]" = asyncio.Queue()

VENDOR_CACHE: Dict[str, str] = {}

MASTER_MAC_PATH = Path("master_mac.csv")


def broadcast_event(event: dict) -> None:
    """Send event to the queue, plugins and MQTT broker."""
    EVENT_BUS.put_nowait(event)
    dispatch_event(event)
    publish_event(event)


def load_vendor_cache(path: Path = MASTER_MAC_PATH) -> None:
    if not path.exists():
        logger.warning("Vendor map file not found: %s", path)
        return
    with path.open() as f:
        for line in f:
            if "," in line:
                mac, vendor = line.strip().split(",", 1)
                VENDOR_CACHE[mac.upper()] = vendor
    logger.info("Loaded %d vendors", len(VENDOR_CACHE))


async def direction_finding_stub(device) -> Optional[float]:
    """Placeholder for AoA/AoD calculation."""
    return None


def parse_ibeacon(data: bytes) -> Optional[Dict[str, str]]:
    if len(data) < 23:
        return None
    return {
        "uuid": data[2:18].hex(),
        "major": int.from_bytes(data[18:20], "big"),
        "minor": int.from_bytes(data[20:22], "big"),
        "tx_power": int.from_bytes(data[22:23], "big", signed=True),
    }


async def update_device(address: str, name: str, rssi: int) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute(
            "SELECT frequency_count FROM Devices WHERE mac_address = ?",
            (address,),
        )
        res = cursor.fetchone()
        vendor = VENDOR_CACHE.get(address[:8].upper())
        if res:
            new_count = res[0] + 1
            cursor.execute(
                """
                UPDATE Devices SET last_seen=?, frequency_count=?, rssi=?, device_name=?
                WHERE mac_address=?
                """,
                (now, new_count, rssi, name, address),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Devices (mac_address, device_name, first_seen, last_seen,
                                    frequency_count, rssi, manufacturer)
                VALUES (?, ?, ?, ?, 1, ?, ?)
                """,
                (address, name, now, now, rssi, vendor),
            )
        conn.commit()
    except Exception as exc:
        logger.error("DB error: %s", exc)
    finally:
        if "conn" in locals():
            conn.close()


async def scan_once() -> None:
    devices = await BleakScanner.discover()
    for dev in devices:
        if dev.address and dev.rssi is not None:
            await update_device(dev.address, dev.name or "Unknown", dev.rssi)
            broadcast_event(
                {
                    "address": dev.address,
                    "name": dev.name,
                    "rssi": dev.rssi,
                    "aoa": await direction_finding_stub(dev),
                }
            )


async def run_scanner(interval: int = 5) -> None:
    load_vendor_cache()
    while True:
        await scan_once()
        await asyncio.sleep(interval)
