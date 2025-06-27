def test_build_graph():
    records = [
        {"mac_address": "AA", "last_seen": "2024-01-01T00:00:00"},
        {"mac_address": "BB", "last_seen": "2024-01-01T00:00:10"},
        {"mac_address": "CC", "last_seen": "2024-01-01T00:02:00"},
    ]
    from core.graph import build_relationship_graph

    graph = build_relationship_graph(records, window=60)
    assert graph == {"AA": {"BB"}, "BB": {"AA"}}
