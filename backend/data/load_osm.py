"""Build our Graph from OpenStreetMap via osmnx."""
from ..core.graph import Graph
from ..config import OSM_PLACE, DEFAULT_SPEED_KMH

try:
    import osmnx as ox
except ImportError:
    ox = None


def load_graph_from_osm(place: str | None = None, use_cache: bool = True) -> Graph:
    """
    Download OSM graph for a place (e.g. city name) and convert to our Graph.
    Uses osmnx; first run may take a minute.
    """
    if ox is None:
        raise ImportError("Install osmnx: pip install osmnx")
    place = place or OSM_PLACE

    from ..config import GRAPH_CACHE
    import hashlib
    cache_key = hashlib.md5(place.encode()).hexdigest()[:12]
    cache_path = GRAPH_CACHE / f"graph_{cache_key}.gpickle"
    if use_cache and cache_path.exists():
        import pickle
        with open(cache_path, "rb") as f:
            G = pickle.load(f)
        return G

    # graph_from_place auto-adds edge lengths (meters)
    G_ox = ox.graph_from_place(place, network_type="drive")
    # add_edge_speeds imputes speed_kph from maxspeed tags + highway-type fallbacks
    G_ox = ox.routing.add_edge_speeds(G_ox, fallback=DEFAULT_SPEED_KMH)

    graph = Graph()
    for n, data in G_ox.nodes(data=True):
        lat = data.get("y", data.get("lat", 0))
        lon = data.get("x", data.get("lon", 0))
        graph.add_node(int(n), lat=lat, lon=lon)

    for u, v, data in G_ox.edges(data=True):
        length_m = float(data.get("length", 0) or 0)
        if length_m <= 0:
            continue
        speed_kmh = data.get("speed_kph", DEFAULT_SPEED_KMH)
        graph.add_edge(int(u), int(v), length_m=length_m, max_speed_kmh=speed_kmh)

    if use_cache:
        import pickle
        with open(cache_path, "wb") as f:
            pickle.dump(graph, f)

    return graph
