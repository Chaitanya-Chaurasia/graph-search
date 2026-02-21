"""Routing endpoints: shortest path."""
from fastapi import APIRouter, Depends, HTTPException
from backend.core import PathFinder
from backend.dependencies import get_pathfinder
from backend.models import ShortestRequest, ShortestResponse, LatLon

router = APIRouter(prefix="/routes", tags=["routes"])

@router.post("/shortest", response_model=ShortestResponse)
def route_shortest(
    req: ShortestRequest,
    pathfinder: PathFinder = Depends(get_pathfinder),
):
    """Shortest path by distance. Returns path (lat, lon) and distance_m."""
    path_points, distance_m = pathfinder.shortest_path(
        req.origin.lat, req.origin.lon,
        req.destination.lat, req.destination.lon,
        by_time=False,
    )
    if not path_points:
        raise HTTPException(status_code=404, detail="No route found")
    path = [LatLon(lat=p[0], lon=p[1]) for p in path_points]
    return ShortestResponse(path=path, distance_m=round(distance_m, 2))
