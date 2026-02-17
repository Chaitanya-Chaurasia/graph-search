"""App configuration."""
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
GRAPH_CACHE = DATA_DIR / "graph_cache"

# OSM / graph
OSM_PLACE = "Piedmont, California, USA"  # small area for fast load; change to your city
DEFAULT_SPEED_KMH = 50.0  # fallback when OSM has no maxspeed

# Grid (for Phase 2 partitions)
GRID_CELL_DEG = 0.01  # ~1 km

# Ensure dirs exist
DATA_DIR.mkdir(exist_ok=True)
GRAPH_CACHE.mkdir(exist_ok=True)
