"""Replay HID notifications to a BLE device."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Iterable
from pathlib import Path

from bleak import BleakClient

logger = logging.getLogger(__name__)


async def _replay_sequence(client: BleakClient, char_uuid: str, packets: Iterable[bytes]) -> None:
    """Write each packet to the characteristic with a short delay."""
    for pkt in packets:
        logger.debug("Writing %s", pkt.hex())
        await client.write_gatt_char(char_uuid, pkt)
        await asyncio.sleep(0.05)


async def replay(address: str, char_uuid: str, packet_file: Path) -> None:
    """Connect to *address* and replay HID packets from *packet_file*."""
    logger.info("Connecting to %s", address)
    async with BleakClient(address) as client:
        data = json.loads(packet_file.read_text())
        packets = [bytes.fromhex(p) for p in data]
        await _replay_sequence(client, char_uuid, packets)
    logger.info("Replay complete")

