"""
In-memory directed graph built from OpenStreetMap road network data.

This module does NOT load data itself. The graph is populated by load_osm.py,
which downloads real road networks via osmnx (Overpass API) and converts them
into this structure.

Data flow:
    OSM (Overpass API)  →  osmnx downloads road network
        →  load_osm.py converts to Graph(nodes, edges)
            →  pickled to /data/graph_cache/ for reuse
                →  loaded into memory at FastAPI startup (main.py)

Nodes: OSM node IDs with lat/lon coordinates.
Edges: directed, weighted by length_m and max_speed_kmh.
"""

from __future__ import annotations

import math
from collections import defaultdict

from backend.models import NodeData, EdgeData, NodeMap, AdjacencyMap, NodeList, NearestNodeAlgorithm

class Graph:
    """
    Directed weighted graph with geographic nodes.

    Storage:
        _nodes: {node_id: NodeData}
        _edges: defaultdict {u: {v: EdgeData}}
        _node_list: [(lat, lon, node_id), ...] for nearest-neighbor lookup

    Supports two edge weight functions:
        - edge_weight_distance: weight = length in meters (for shortest distance)
        - edge_weight_time: weight = travel time in seconds (for fastest route)
    """

    def __init__(self) -> None:
        self._nodes: NodeMap = {}
        self._edges: AdjacencyMap = defaultdict(dict)
        self._node_list: NodeList = []

    def add_node(self, nid: int, lat: float, lon: float, **attrs) -> None:
        self._nodes[nid] = NodeData(lat=lat, lon=lon, **attrs)
        self._node_list.append((lat, lon, nid))

    def add_edge(self, u: int, v: int, length_m: float, max_speed_kmh: float | None = None, **attrs) -> None:
        """u & v are node ids. length_m is in meters. max_speed_kmh is in km/h."""
        if u == v:
            return
        self._edges[u][v] = EdgeData(length_m=length_m, max_speed_kmh=max_speed_kmh, **attrs)

    def node(self, nid: int) -> NodeData | None:
        return self._nodes.get(nid)

    def neighbors(self, nid: int) -> dict[int, EdgeData]:
        return self._edges.get(nid, {})

    def nodes(self) -> dict[int, NodeData]:
        return self._nodes

    def num_nodes(self) -> int:
        return len(self._nodes)

    def num_edges(self) -> int:
        return sum(len(adj) for adj in self._edges.values())

    def get_nearest_node(
        self,
        lat: float,
        lon: float,
        algorithm: NearestNodeAlgorithm = NearestNodeAlgorithm.LINEAR,
    ) -> int | None:
        """Return the node id closest to (lat, lon) using the specified algorithm."""
        if not self._node_list:
            return None

        if algorithm == NearestNodeAlgorithm.LINEAR:
            return self._nearest_linear(lat, lon)
        elif algorithm == NearestNodeAlgorithm.KDTREE:
            raise NotImplementedError("KD-tree nearest neighbor not yet implemented")

    def _nearest_linear(self, lat: float, lon: float) -> int:
        """O(n) brute-force scan. Fine for small graphs."""
        _, _, nid = min(self._node_list, key=lambda n: (lat - n[0]) ** 2 + (lon - n[1]) ** 2)
        return nid

    def edge_weight_distance(self, u: int, v: int) -> float:
        """Edge weight = length in meters. Used for shortest-distance routing."""
        edge = self._edges.get(u, {}).get(v)
        if edge is None:
            return math.inf
        return edge.length_m

    def edge_weight_time(self, u: int, v: int) -> float:
        """Edge weight = travel time in seconds (length / speed). Used for fastest-route."""
        edge = self._edges.get(u, {}).get(v)
        if edge is None:
            return math.inf
        speed_kmh = edge.max_speed_kmh or 50.0
        if speed_kmh <= 0:
            speed_kmh = 50.0
        speed_ms = speed_kmh * 1000 / 3600
        return edge.length_m / speed_ms if speed_ms > 0 else math.inf