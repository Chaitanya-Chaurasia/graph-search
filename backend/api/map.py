from fastapi import APIRouter, Depends
from backend.core import Graph
from backend.dependencies import get_graph
from backend.models import MapNodesResponse

router = APIRouter(prefix="/map", tags=["map"])

@router.get("/nodes", response_model=MapNodesResponse)
def map_nodes(
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lon: float | None = None,
    max_lon: float | None = None,
    graph: Graph = Depends(get_graph),
):
    """Return nodes, optionally filtered by bounding box."""
    nodes = []
    for nid, data in graph.nodes().items():
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
