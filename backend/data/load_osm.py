"""Build our Graph from OpenStreetMap via osmnx."""
from ..core.graph import Graph
from ..config import OSM_PLACE, DEFAULT_SPEED_KMH

try:
    import osmnx as ox
except ImportError:
    ox = None


def _parse_speed_kmh(maxspeed_value) -> float:
    """Parse OSM maxspeed tag to a single float in km/h."""
    if maxspeed_value is None or (isinstance(maxspeed_value, float) and maxspeed_value != maxspeed_value):
        return DEFAULT_SPEED_KMH
    if isinstance(maxspeed_value, (int, float)):
        return float(maxspeed_value)
    s = str(maxspeed_value).strip()
    if not s:
        return DEFAULT_SPEED_KMH
    # "50", "50 mph", "30 mph"
    parts = s.lower().split()
    try:
        val = float(parts[0])
    except ValueError:
        return DEFAULT_SPEED_KMH
    if len(parts) > 1 and "mph" in parts[1]:
        val *= 1.60934
    return val


def load_graph_from_osm(place: str | None = None, use_cache: bool = True) -> Graph:
    """
    Download OSM graph for a place (e.g. city name) and convert to our Graph.
    Uses osmnx; first run may take a minute.
    """
    if ox is None:
        raise ImportError("Install osmnx: pip install osmnx")
    place = place or OSM_PLACE

    # Optional: cache by place name to avoid re-downloading
    from ..config import GRAPH_CACHE
    import hashlib
    cache_key = hashlib.md5(place.encode()).hexdigest()[:12]
    cache_path = GRAPH_CACHE / f"graph_{cache_key}.gpickle"
    if use_cache and cache_path.exists():
        import pickle
        with open(cache_path, "rb") as f:
            G = pickle.load(f)
        return G

    G_ox = ox.graph_from_place(place, network_type="drive")
    G_ox = ox.add_edge_speeds(G_ox)
    G_ox = ox.add_edge_lengths(G_ox)

    graph = Graph()
    for n, data in G_ox.nodes(data=True):
        lat = data.get("y", data.get("lat", 0))
        lon = data.get("x", data.get("lon", 0))
        graph.add_node(int(n), lat=lat, lon=lon)

    for u, v, data in G_ox.edges(data=True):
        length_m = float(data.get("length", 0) or 0)
        if length_m <= 0:
            continue
        maxspeed = data.get("maxspeed", DEFAULT_SPEED_KMH)
        speed_kmh = _parse_speed_kmh(maxspeed)
        graph.add_edge(int(u), int(v), length_m=length_m, max_speed_kmh=speed_kmh)

    if use_cache:
        import pickle
        with open(cache_path, "wb") as f:
            pickle.dump(graph, f)

    return graph
