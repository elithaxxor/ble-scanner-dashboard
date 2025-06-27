from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List


def build_relationship_graph(records: Iterable[dict], window: int = 60) -> Dict[str, set]:
    """Return adjacency map of devices seen within `window` seconds."""
    events = [(r["mac_address"], datetime.fromisoformat(r["last_seen"])) for r in records]
    events.sort(key=lambda x: x[1])
    graph: Dict[str, set] = defaultdict(set)
    for i, (mac_a, time_a) in enumerate(events):
        for mac_b, time_b in events[i + 1 :]:
            if (time_b - time_a).total_seconds() > window:
                break
            if mac_a != mac_b:
                graph[mac_a].add(mac_b)
                graph[mac_b].add(mac_a)
    return graph
