import os
import logging
from typing import Any, Dict
import requests

logger = logging.getLogger(__name__)

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
WIGLE_API_NAME = os.getenv("WIGLE_API_NAME", "")
WIGLE_API_TOKEN = os.getenv("WIGLE_API_TOKEN", "")
CENSYS_API_ID = os.getenv("CENSYS_API_ID", "")
CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET", "")


def shodan_lookup(query: str) -> Dict[str, Any]:
    """Query the Shodan API for a host or search string."""
    if not SHODAN_API_KEY:
        logger.warning("Shodan API key not configured")
        return {}
    url = "https://api.shodan.io/shodan/host/search"
    params = {"key": SHODAN_API_KEY, "query": query}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Shodan lookup failed: %s", exc)
        return {}


def wigle_lookup(ssid: str) -> Dict[str, Any]:
    """Search Wigle for a Wi-Fi SSID."""
    if not (WIGLE_API_NAME and WIGLE_API_TOKEN):
        logger.warning("Wigle credentials not configured")
        return {}
    url = "https://api.wigle.net/api/v2/network/search"
    params = {"ssid": ssid}
    try:
        resp = requests.get(
            url,
            params=params,
            auth=(WIGLE_API_NAME, WIGLE_API_TOKEN),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Wigle lookup failed: %s", exc)
        return {}


def censys_lookup(query: str) -> Dict[str, Any]:
    """Query the Censys search API."""
    if not (CENSYS_API_ID and CENSYS_API_SECRET):
        logger.warning("Censys credentials not configured")
        return {}
    url = "https://search.censys.io/api/v2/hosts/search"
    params = {"q": query}
    try:
        resp = requests.get(
            url,
            params=params,
            auth=(CENSYS_API_ID, CENSYS_API_SECRET),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Censys lookup failed: %s", exc)
        return {}
