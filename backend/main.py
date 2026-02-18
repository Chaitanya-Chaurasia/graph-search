"""FastAPI app: map nodes and shortest route."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import ShortestRequest, ShortestResponse, LatLon, MapNodesResponse
from backend.data import load_graph_from_osm
from backend.core import shortest_path

# Global graph (loaded once at startup)
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = load_graph_from_osm(use_cache=True)
    return _graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload graph on startup."""
    get_graph()
    yield
    # shutdown: nothing to do


app = FastAPI(title="Maps Clone API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "nodes": get_graph().num_nodes()}


@app.get("/map/nodes", response_model=MapNodesResponse)
def map_nodes(min_lat: float | None = None, max_lat: float | None = None, min_lon: float | None = None, max_lon: float | None = None):
    """Return nodes, optionally filtered by bbox."""
    g = get_graph()
    nodes = []
    for nid, data in g.nodes().items():
        lat, lon = data.lat, data.lon
        if min_lat is not None and lat < min_lat:
            continue
        if max_lat is not None and lat > max_lat:
            continue
        if min_lon is not None and lon < min_lon:
            continue
        if max_lon is not None and lon > max_lon:
            continue
        nodes.append({"id": nid, "lat": lat, "lon": lon})
    return MapNodesResponse(nodes=nodes)


@app.post("/routes/shortest", response_model=ShortestResponse)
def route_shortest(req: ShortestRequest):
    """Shortest path by distance. Returns path (lat,lon) and distance_m."""
    g = get_graph()
    path_points, distance_m = shortest_path(
        g,
        req.origin.lat, req.origin.lon,
        req.destination.lat, req.destination.lon,
        by_time=False,
    )
    if not path_points:
        raise HTTPException(status_code=404, detail="No route found")
    path = [LatLon(lat=p[0], lon=p[1]) for p in path_points]
    return ShortestResponse(path=path, distance_m=round(distance_m, 2))
