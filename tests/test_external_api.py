from unittest.mock import patch
import asyncio
import external_api
from core import scanner


def test_vendor_for_mac_cache():
    scanner.VENDOR_CACHE.clear()
    scanner.VENDOR_CACHE["AA11BB"] = "TestVendor"
    assert asyncio.run(scanner.vendor_for_mac("AA:11:BB:00:00:00")) == "TestVendor"


@patch("external_api.requests.get")
def test_shodan_lookup(mock_get):
    mock_get.return_value.json.return_value = {"matches": []}
    mock_get.return_value.raise_for_status.return_value = None
    external_api.SHODAN_API_KEY = "dummy"
    res = external_api.shodan_lookup("test")
    assert "matches" in res


@patch("external_api.requests.get")
def test_censys_lookup(mock_get):
    mock_get.return_value.json.return_value = {"result": []}
    mock_get.return_value.raise_for_status.return_value = None
    external_api.CENSYS_API_ID = "id"
    external_api.CENSYS_API_SECRET = "secret"
    res = external_api.censys_lookup("1.2.3.4")
    assert "result" in res
