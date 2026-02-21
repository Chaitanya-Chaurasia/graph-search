"""Runtime application state, initialized once during FastAPI lifespan."""
from backend.core import Graph, PathFinder
from backend.data import load_graph_from_osm

class AppState:
    """Holds the graph and pathfinder, loaded once at startup."""

    def __init__(self) -> None:
        self.graph: Graph = load_graph_from_osm(use_cache=True)
        self.pathfinder: PathFinder = PathFinder(self.graph)
