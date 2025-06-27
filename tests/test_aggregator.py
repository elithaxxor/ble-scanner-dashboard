from unittest.mock import patch
from core import aggregator


def test_aggregate_deduplication():
    with patch("core.aggregator.fetch_results") as mock_fetch:
        mock_fetch.side_effect = [
            [{"mac_address": "AA", "last_seen": "1"}],
            [{"mac_address": "AA", "last_seen": "2"}],
        ]
        res = aggregator.aggregate(["url1", "url2"])
        assert res[0]["last_seen"] == "2"
