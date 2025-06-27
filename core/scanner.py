import asyncio
import json
import logging
import sqlite3
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from mac_vendor_lookup import MacLookup

from bleak import BleakScanner

from config import DB_PATH
from plugins import dispatch_event
from mqtt_client import publish_event
from notifications import send_all_notifications
from core.db import init_db, purge_old_entries
from core.utils import setup_logging
from vendor_lookup import load_vendor_data, lookup_vendor

setup_logging()
logger = logging.getLogger(__name__)

EVENT_BUS: "asyncio.Queue[dict]" = asyncio.Queue()
THREAD_EXECUTOR: ThreadPoolExecutor | None = None
PROCESS_EXECUTOR: ProcessPoolExecutor | None = None

VENDOR_CACHE: Dict[str, str] = {}
MAC_LOOKUP = MacLookup()

MASTER_MAC_PATH = Path("master_mac.csv")


def init_executors(threads: int, processes: int) -> None:
    """Initialise thread and process pools."""
    global THREAD_EXECUTOR, PROCESS_EXECUTOR
    THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=threads)
    PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=processes) if processes > 0 else None


def broadcast_event(event: dict) -> None:
    """Send event to the queue, plugins and MQTT broker."""
    EVENT_BUS.put_nowait(event)
    dispatch_event(event)
    publish_event(event)
    try:
        send_all_notifications(f"New BLE device {event.get('address')}")
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Notification error: %s", exc)


def load_vendor_cache(path: Path = MASTER_MAC_PATH) -> None:
    """Load vendor prefixes from builtin list and optional CSV file."""
    load_vendor_data(path)
    logger.info("Loaded %d vendors", len(VENDOR_CACHE))


async def vendor_for_mac(address: str) -> Optional[str]:
    """Return vendor for a MAC using cache or online lookup."""
    prefix = address.upper().replace(":", "")[:6]
    if prefix in VENDOR_CACHE:
        return VENDOR_CACHE[prefix]
    if PROCESS_EXECUTOR is None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, MAC_LOOKUP.lookup, address)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(PROCESS_EXECUTOR, MAC_LOOKUP.lookup, address)


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


def parse_eddystone(data: bytes) -> Optional[Dict[str, str]]:
    if not data:
        return None
    frame_type = data[0]
    if frame_type == 0x00 and len(data) >= 18:
        return {
            "type": "uid",
            "tx_power": int.from_bytes(data[1:2], "big", signed=True),
            "namespace": data[2:12].hex(),
            "instance": data[12:18].hex(),
        }
    if frame_type == 0x10 and len(data) >= 4:
        url = data[2:].decode(errors="ignore")
        return {
            "type": "url",
            "tx_power": int.from_bytes(data[1:2], "big", signed=True),
            "url": url,
        }
    return None


def _update_device_sync(address: str, name: str, rssi: int, vendor: Optional[str]) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute(
            "SELECT frequency_count, rssi_history FROM devices WHERE mac_address = ?",
            (address,),
        )
        res = cursor.fetchone()
        if res:
            new_count = res[0] + 1
            history = json.loads(res[1] or "[]")
            history.append({"t": now.isoformat(), "rssi": rssi})
            cursor.execute(
                """
                UPDATE devices SET last_seen=?, frequency_count=?, rssi=?, device_name=?, rssi_history=?
                WHERE mac_address=?
                """,
                (now, new_count, rssi, name, json.dumps(history), address),
            )
        else:
            cursor.execute(
                """
                INSERT INTO devices (mac_address, device_name, first_seen, last_seen,
                                    frequency_count, rssi, manufacturer, rssi_history)
                VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (address, name, now, now, rssi, vendor, json.dumps([{"t": now.isoformat(), "rssi": rssi}])),
            )
        conn.commit()
    except Exception as exc:
        logger.error("DB error: %s", exc)
    finally:
        if "conn" in locals():
            conn.close()


async def update_device(address: str, name: str, rssi: int) -> None:
    vendor = await vendor_for_mac(address)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(THREAD_EXECUTOR, _update_device_sync, address, name, rssi, vendor)


async def scan_once() -> None:
    devices = await BleakScanner.discover()
    for dev in devices:
        if dev.address and dev.rssi is not None:
            await update_device(dev.address, dev.name or "Unknown", dev.rssi)
            ibeacon = None
            eddystone = None
            mfg_data = dev.metadata.get("manufacturer_data", {})
            for cid, payload in mfg_data.items():
                if cid == 0x004C:  # Apple iBeacon
                    ibeacon = parse_ibeacon(bytes(payload))
                if cid == 0xFEAA:  # Eddystone
                    eddystone = parse_eddystone(bytes(payload))
            broadcast_event(
                {
                    "address": dev.address,
                    "name": dev.name,
                    "rssi": dev.rssi,
                    "aoa": await direction_finding_stub(dev),
                    "ibeacon": ibeacon,
                    "eddystone": eddystone,
                }
            )


async def _worker(interval: int) -> None:
    while True:
        await scan_once()
        await asyncio.sleep(interval)


async def run_scanner(interval: int = 5, workers: int = 1, threads: int = 1, processes: int = 0) -> None:
    load_vendor_cache()
    init_db()
    purge_old_entries()
    init_executors(threads, processes)
    tasks = [asyncio.create_task(_worker(interval)) for _ in range(workers)]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Scanner stopped")
