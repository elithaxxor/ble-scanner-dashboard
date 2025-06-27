import logging
from typing import Iterable, List, Dict
import requests

logger = logging.getLogger(__name__)


def fetch_results(url: str) -> List[Dict[str, str]]:
    """Fetch device results from a remote dashboard."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Failed to fetch %s: %s", url, exc)
    return []


def aggregate(endpoints: Iterable[str]) -> List[Dict[str, str]]:
    """Aggregate device lists from multiple endpoints."""
    merged: Dict[str, Dict[str, str]] = {}
    for ep in endpoints:
        for dev in fetch_results(ep):
            mac = dev.get("mac_address")
            if not mac:
                continue
            curr = merged.get(mac)
            if not curr or curr.get("last_seen", "") < dev.get("last_seen", ""):
                merged[mac] = dev
    return list(merged.values())
