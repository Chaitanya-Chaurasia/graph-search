#!/usr/bin/env python3
"""
Demo: load OSM graph (cached after first run) and compute a shortest route.
Run from repo root:  PYTHONPATH=. python run_demo.py
"""
from backend.data import load_graph_from_osm
from backend.core import shortest_path

def main():
    print("Loading graph from OSM (first time may take ~30s)...")
    graph = load_graph_from_osm(use_cache=True)
    print(f"Nodes: {graph.num_nodes()}, Edges: {graph.num_edges()}")

    # Example: two points in the loaded area (Piedmont, CA by default)
    # OSM bbox for Piedmont is roughly 37.82, -122.24 to 37.84, -122.22
    origin_lat, origin_lon = 37.825, -122.23
    dest_lat, dest_lon = 37.835, -122.22

    path, distance_m = shortest_path(graph, origin_lat, origin_lon, dest_lat, dest_lon, by_time=False)
    print(f"Shortest path: {len(path)} points, distance = {distance_m:.1f} m")
    if path:
        print(f"  First point: {path[0]}")
        print(f"  Last point:  {path[-1]}")

if __name__ == "__main__":
    main()
