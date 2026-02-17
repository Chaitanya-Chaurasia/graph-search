"""Pydantic request/response models."""
from pydantic import BaseModel, Field


class LatLon(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class ShortestRequest(BaseModel):
    origin: LatLon
    destination: LatLon


class ShortestResponse(BaseModel):
    path: list[LatLon]
    distance_m: float


class MapNodesResponse(BaseModel):
    nodes: list[dict]  # [{"id", "lat", "lon"}, ...]
