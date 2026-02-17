# Maps Clone — Shortest Routes + ETA

A maps-like system with **partitioned graph search** for large maps and **ETA calculation** (Uber-style). Plan: Python core + FastAPI backend, then Next.js frontend to visualize the map and routes.

## Plan

See **[PROJECT_PLAN.md](./PROJECT_PLAN.md)** for:

- Part 1: Shortest routes using **partitions** (grid-based) for scalability
- Part 2: **ETA** from edge speeds and optional time/traffic
- Python backend (FastAPI) and Next.js frontend layout
- Phased implementation checklist

## Quick start

```bash
# From repo root
pip install -r requirements.txt
export PYTHONPATH=.

# Run unit tests (no OSM)
pytest tests/ -v

# Demo: load OSM graph and compute one route (first run downloads ~30s)
python run_demo.py

# Start API server (loads graph on first request)
uvicorn backend.main:app --reload
# Then: GET http://127.0.0.1:8000/health
#       GET http://127.0.0.1:8000/map/nodes
#       POST http://127.0.0.1:8000/routes/shortest with JSON body:
#         {"origin": {"lat": 37.825, "lon": -122.23}, "destination": {"lat": 37.835, "lon": -122.22}}
```

## Repo structure (target)

```
backend/     # Python: core graph, partitions, shortest path, ETA, FastAPI
data/        # Graph + partition data, OSM extracts
frontend/    # Next.js + map (Leaflet/Mapbox)
```
