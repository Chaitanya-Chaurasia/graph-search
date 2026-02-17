"""Unit tests for shortest path on a small hand-built graph."""
import sys
from pathlib import Path

# Run from repo root: PYTHONPATH includes repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.graph import Graph
from backend.core.shortest_path import shortest_path


def test_simple_chain():
    """Linear chain 1 -> 2 -> 3. Shortest path from (lat,lon) of 1 to 3."""
    g = Graph()
    g.add_node(1, 0.0, 0.0)
    g.add_node(2, 0.01, 0.0)
    g.add_node(3, 0.02, 0.0)
    g.add_edge(1, 2, length_m=100.0)
    g.add_edge(2, 3, length_m=100.0)

    path, dist = shortest_path(g, 0.0, 0.0, 0.02, 0.0, by_time=False)
    assert len(path) == 3
    assert dist == 200.0


def test_same_point():
    """Origin and destination snap to same node."""
    g = Graph()
    g.add_node(1, 0.0, 0.0)
    path, dist = shortest_path(g, 0.0, 0.0, 0.0, 0.0, by_time=False)
    assert len(path) == 1
    assert dist == 0.0


def test_no_path():
    """Two components: no path."""
    g = Graph()
    g.add_node(1, 0.0, 0.0)
    g.add_node(2, 1.0, 1.0)
    # no edges
    path, dist = shortest_path(g, 0.0, 0.0, 1.0, 1.0, by_time=False)
    assert len(path) == 0
    assert dist == float("inf")


def test_two_routes_picks_shortest():
    """ 1 --100m--> 2 --100m--> 3
        1 --50m--> 4 --50m--> 3
        Shortest 1->3 is 100m via 4.
    """
    g = Graph()
    g.add_node(1, 0.0, 0.0)
    g.add_node(2, 0.01, 0.0)
    g.add_node(3, 0.02, 0.0)
    g.add_node(4, 0.01, 0.01)
    g.add_edge(1, 2, length_m=100.0)
    g.add_edge(2, 3, length_m=100.0)
    g.add_edge(1, 4, length_m=50.0)
    g.add_edge(4, 3, length_m=50.0)

    path, dist = shortest_path(g, 0.0, 0.0, 0.02, 0.0, by_time=False)
    assert dist == 100.0
    assert len(path) == 3  # 1, 4, 3
