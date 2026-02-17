"""In-memory graph: nodes (id, lat, lon) and edges (from, to, length_m, max_speed_kmh)."""
from __future__ import annotations

import math
from typing import Any


class Graph:
    """Directed graph with geographic nodes and weighted edges."""

    def __init__(self) -> None:
        self._nodes: dict[int, dict[str, Any]] = {}  # id -> {lat, lon, ...}
        self._edges: dict[int, dict[int, dict[str, Any]]] = {}  # u -> { v -> {length_m, max_speed_kmh} }
        self._node_list: list[tuple[float, float, int]] = []  # (lat, lon, id) for nearest-neighbor

    def add_node(self, nid: int, lat: float, lon: float, **attrs: Any) -> None:
        self._nodes[nid] = {"lat": lat, "lon": lon, **attrs}
        self._node_list.append((lat, lon, nid))

    def add_edge(self, u: int, v: int, length_m: float, max_speed_kmh: float | None = None, **attrs: Any) -> None:
        if u not in self._edges:
            self._edges[u] = {}
        self._edges[u][v] = {"length_m": length_m, "max_speed_kmh": max_speed_kmh, **attrs}

    def node(self, nid: int) -> dict[str, Any] | None:
        return self._nodes.get(nid)

    def neighbors(self, nid: int) -> dict[int, dict[str, Any]]:
        """Out-neighbors and edge data."""
        return self._edges.get(nid, {})

    def nodes(self) -> dict[int, dict[str, Any]]:
        return self._nodes

    def num_nodes(self) -> int:
        return len(self._nodes)

    def num_edges(self) -> int:
        return sum(len(adj) for adj in self._edges.values())

    def get_nearest_node(self, lat: float, lon: float) -> int | None:
        """Return node id closest to (lat, lon). Naive linear scan (fine for Phase 1)."""
        if not self._node_list:
            return None
        best_id = None
        best_d2 = math.inf
        for nlat, nlon, nid in self._node_list:
            d2 = (lat - nlat) ** 2 + (lon - nlon) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best_id = nid
        return best_id

    def edge_weight_distance(self, u: int, v: int) -> float:
        """Weight for shortest path by distance (length in meters)."""
        adj = self._edges.get(u, {})
        if v not in adj:
            return math.inf
        return adj[v].get("length_m", math.inf)

    def edge_weight_time(self, u: int, v: int) -> float:
        """Weight for shortest path by time (seconds)."""
        adj = self._edges.get(u, {})
        if v not in adj:
            return math.inf
        length_m = adj[v].get("length_m", 0)
        speed_kmh = adj[v].get("max_speed_kmh") or 50.0
        if speed_kmh <= 0:
            speed_kmh = 50.0
        speed_ms = speed_kmh * 1000 / 3600
        return length_m / speed_ms if speed_ms > 0 else math.inf
