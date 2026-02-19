"""PathFinder: shortest path routing on a Graph (Dijkstra)."""

from __future__ import annotations

import math
import heapq
from typing import TYPE_CHECKING, Callable

from backend.config import NEAREST_NODE_ALGORITHM

if TYPE_CHECKING:
    from .graph import Graph


class PathFinder:
    """Snap (lat,lon) to nearest nodes and run shortest-path algorithms."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def shortest_path(
        self,
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
        graph = self._graph
        start = graph.get_nearest_node(origin_lat, origin_lon, algorithm=NEAREST_NODE_ALGORITHM)
        goal = graph.get_nearest_node(dest_lat, dest_lon, algorithm=NEAREST_NODE_ALGORITHM)

        if start is None or goal is None:
            return [], math.inf
        
        # callabale variable
        weight_fn = graph.edge_weight_time if by_time else graph.edge_weight_distance

        path_ids, cost = self._dijkstra(start, goal, weight_fn)

        # pass copy of graph instead of self._graph
        path_points = self._get_path_from_nodes(graph, path_ids)

        return path_points, cost

    def _dijkstra(
        self,
        start: int,
        goal: int,
        weight_fn: Callable[[int, int], float],
    ) -> tuple[list[int], float]:
        """
        Dijkstra from start to goal. weight_fn(u, v) returns edge weight.
        Returns (path node ids, total cost) or ([], inf) if no path.
        """
        graph = self._graph

        # maintain a dictionary to store shortest distance of a node "u" to node "goal". 
        # using a dictionary instead of array because array could take up huge memory.  
        dist: dict[int, float] = {start: 0.0}
        # apart from the distance, we also want to reconstruct the path. 
        # we use a dictionary to store this mapping prev[node_a] = node_b, prev[node_b] = node_f and so on .....
        prev: dict[int, int] = {}
        # maintain a heap to get nearest neighbour in O(1). if heap is empty, all neighbours have been explored.
        heap: list[tuple[float, int]] = [(0.0, start)]

        while heap: 
            distance, node = heapq.heappop(heap)
            # we found our target
            if node == goal:
                break
            # for node u, if we already found a smaller distance in the previous computation, skip this iteration
            if distance > dist.get(node, math.inf):
                continue
            # explore all neighbors
            for neighbor, _ in graph.neighbors(node).items():
                weight = weight_fn(node, neighbor)
                # data missing (highly unlikely and this is data bug)
                if weight == math.inf:
                    continue
                # relax neighbors when a new shortest distance has been found
                new_distance = weight + distance
                if new_distance < dist.get(neighbor, math.inf):
                    dist[neighbor] = new_distance
                    prev[neighbor] = node
                    heapq.heappush(heap, (new_distance, neighbor))

        if goal not in prev and start != goal:
            return [], math.inf
        path = []
        # make a copy of goal for backtracking
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        path.reverse()
        return path, dist.get(goal, math.inf)

    def _get_path_from_nodes(self, graph: Graph, path: list[int]) -> list:
        """Create a path from a list of nodes which _dijkstra() returns"""
        path_points = []
        for nid in path:
            node = graph.node(nid)
            if node:
                path_points.append((node.lat, node.lon))
        return path_points
