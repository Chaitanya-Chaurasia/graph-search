from collections import defaultdict
from enum import Enum
from typing import TypeAlias
from pydantic import BaseModel, ConfigDict, Field

# Graph data models

class NearestNodeAlgorithm(str, Enum):
    """Algorithm used by Graph.get_nearest_node()."""
    LINEAR = "linear"       # O(n) brute-force scan with euclidean distance
    KDTREE = "kdtree"       # scipy KD-tree (TODO)

class NodeData(BaseModel):
    """ 
    Geographic node with lat/lon. Extra OSM attributes allowed. 
    TODO: Add traffic scores (static, then dynamic as attrs)
    TODO: Tolls, croad quality.
    """
    lat: float
    lon: float
    model_config = ConfigDict(extra="allow")

class EdgeData(BaseModel):
    """Directed edge with distance and optional speed limit."""
    length_m: float
    max_speed_kmh: float | None = None
    model_config = ConfigDict(extra="allow")

# Graph-level type aliases for data structure

NodeMap: TypeAlias = dict[int, NodeData]
AdjacencyMap: TypeAlias = defaultdict[int, dict[int, EdgeData]]
NodeList: TypeAlias = list[tuple[float, float, int]]

# API request / response schemas

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
