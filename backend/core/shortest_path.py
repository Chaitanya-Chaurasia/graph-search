"""Shortest path by distance (Dijkstra). Snap (lat,lon) to nearest node."""
from __future__ import annotations

import math
import heapq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph import Graph


def _dijkstra(
    graph: Graph,
    start: int,
    goal: int,
    weight_fn,
) -> tuple[list[int], float]:
    """
    Dijkstra from start to goal. weight_fn(u, v) returns edge weight.
    Returns (path node ids, total cost) or ([], inf) if no path.
    """
    dist: dict[int, float] = {start: 0.0}
    prev: dict[int, int] = {}
    heap: list[tuple[float, int]] = [(0.0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if u == goal:
            break
        if d > dist.get(u, math.inf):
            continue
        for v, _ in graph.neighbors(u).items():
            w = weight_fn(u, v)
            if w == math.inf:
                continue
            alt = d + w
            if alt < dist.get(v, math.inf):
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))

    if goal not in prev and start != goal:
        return [], math.inf
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path, dist.get(goal, math.inf)


def shortest_path(
    graph: Graph,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    by_time: bool = False,
) -> tuple[list[tuple[float, float]], float]:
    """
    Shortest path between two (lat, lon) points.
    Snaps to nearest nodes, runs Dijkstra.
    Returns (path as list of (lat, lon), total cost).
    Cost is distance_m if by_time=False, else duration_sec.
    """
    start = graph.get_nearest_node(origin_lat, origin_lon)
    goal = graph.get_nearest_node(dest_lat, dest_lon)
    if start is None or goal is None:
        return [], math.inf
    weight_fn = graph.edge_weight_time if by_time else graph.edge_weight_distance
    path_ids, cost = _dijkstra(graph, start, goal, weight_fn)
    path_points = []
    for nid in path_ids:
        n = graph.node(nid)
        if n:
            path_points.append((n["lat"], n["lon"]))
    return path_points, cost
