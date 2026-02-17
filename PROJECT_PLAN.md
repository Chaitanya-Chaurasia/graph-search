# Maps Clone + Shortest Routes (Partitioned) + ETA — Project Plan

A phased plan for building a maps-like system with **partitioned graph search** for large maps, **ETA calculation** (Uber-style), and a **Python backend + Next.js frontend** webapp for visualization.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NEXT.JS FRONTEND                                 │
│  Map UI • Route visualization • ETA display • Search / waypoints         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ REST / WebSocket (optional)
┌─────────────────────────────────────────────────────────────────────────┐
│                         PYTHON BACKEND (FastAPI)                          │
│  /routes/shortest  •  /routes/eta  •  /map/partitions  •  /map/nodes     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE ENGINE (Python)                              │
│  Partitioned graph • Dijkstra/A* • Contraction hierarchies (optional)   │
│  ETA service (speed, traffic, time-of-day)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                        │
│  Graph (nodes, edges) • Partitions (spatial index) • OSM / custom data  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Maps Clone + Shortest Routes with Partitions

### 1.1 Data model

- **Nodes**: `id`, `lat`, `lon`, optional `partition_id`.
- **Edges**: `from_node`, `to_node`, `length_m`, `road_type`, optional `max_speed_kmh`.
- **Graph**: Directed (or bidirectional) weighted graph; weight = distance or travel time.

### 1.2 Why partitions?

- On large maps (millions of nodes), one global Dijkstra/A* is too slow.
- **Partitioning** splits the graph into regions (e.g. grid cells or custom boundaries).
- Route query: find which partitions the origin and destination lie in; run search **within and across** those partitions (and maybe a small “border” set) instead of the whole graph.

### 1.3 Partition strategies (pick one to start)

| Strategy | Idea | Pros | Cons |
|----------|------|------|------|
| **Grid** | Divide map into lat/lon grid cells; assign nodes to cells. | Simple, fast lookup. | Boundaries are arbitrary; many border edges. |
| **Spatial hashing** | Same as grid but with consistent cell size in meters (e.g. 1km). | Easy to reason about distance. | Same as grid. |
| **Recursive bisection** | Split graph by latitude/longitude alternately. | Good balance. | More implementation work. |
| **Contraction hierarchies (CH)** | Preprocess: contract “unimportant” nodes; query uses a small subgraph. | Very fast queries on large graphs. | Complex; better as Phase 2. |

**Recommendation:** Start with a **grid** (e.g. 0.01° or ~1 km cells). Each node belongs to one cell; edges can cross cells. For a route, only load nodes/edges in **origin cell**, **destination cell**, and optionally **cells along a coarse path** (e.g. straight line or bbox).

### 1.4 Shortest path pipeline

1. **Input**: origin `(lat, lon)`, destination `(lat, lon)`.
2. **Snap to graph**: Find nearest node (or create a short “virtual” edge to nearest) for origin and destination.
3. **Partition scope**: Determine partition(s) to load (e.g. origin cell + destination cell + cells in a corridor).
4. **Build subgraph**: Load only nodes/edges in that scope from disk or cache.
5. **Run shortest path**: Dijkstra or A* (with Euclidean heuristic) on the subgraph.
6. **Output**: List of `(lat, lon)` or node IDs + total distance (and later, time).

### 1.5 Tech choices (Part 1)

- **Language**: Python 3.10+.
- **Graph**: In-memory with `networkx` for prototyping, or a simple **dict-of-dicts** / adjacency list for full control.
- **Data**: Start with a small OSM extract (e.g. one city) — use **osmnx** or **pyrosm** to build nodes/edges from OSM.
- **Partitions**: Grid index: `(lat_idx, lon_idx)` → list of node IDs; store on disk (e.g. pickle, or SQLite/JSON) and load only needed cells.

---

## Part 2: ETA (Uber-Style)

### 2.1 What ETA needs

- **Distance** (already from Part 1).
- **Speed** per edge (or segment): from speed limit, road type, or live/cached traffic.
- **Travel time** = `distance / speed` per edge; sum along path.

### 2.2 Speed model (simple → advanced)

1. **Static**: Each edge has `max_speed_kmh` (from OSM); `time = length_m / (speed_kmh * 1000/3600)`.
2. **Time-of-day**: Different speeds by hour (e.g. rush hour factors); store or compute a multiplier per edge per time slice.
3. **Traffic (optional)**: External traffic API or historical curves; multiply base time by a factor.

### 2.3 ETA pipeline

1. Get **shortest path** (in distance or in time) from Part 1.
2. If “shortest by time”: use **weight = length_m / speed_m_per_s** so Dijkstra minimizes time.
3. For each edge on path: `time_sec = length_m / speed_m_per_sec` (speed from model above).
4. **ETA** = `departure_time + sum(edge_times)`; return also **duration_sec** and optionally per-segment breakdown.

### 2.4 Optional: time-dependent weights

- Precompute or look up “speed at time T” for each edge; then pathfinding uses **time-dependent Dijkstra** (expand by arrival time at each node). Start simple (static speed), add this later if needed.

---

## Part 3: Python Backend (API)

### 3.1 Framework

- **FastAPI**: async, automatic OpenAPI docs, easy JSON.

### 3.2 Suggested endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /map/nodes` | GET | List nodes (optional bbox: `?min_lat=&max_lat=&min_lon=&max_lon=`) for frontend to draw. |
| `GET /map/partitions` | GET | Return partition boundaries (e.g. GeoJSON) for debugging/visualization. |
| `POST /routes/shortest` | POST | Body: `{ "origin": { "lat", "lon" }, "destination": { "lat", "lon" } }` → path (list of points), distance_m. |
| `POST /routes/eta` | POST | Same as above + optional `departure_time` (ISO) → path, distance_m, duration_sec, eta (ISO). |
| `GET /health` | GET | Health check. |

### 3.3 Project layout (Python)

```
graph-search/
├── README.md
├── PROJECT_PLAN.md          # this file
├── requirements.txt
├── pyproject.toml           # optional
│
├── backend/
│   ├── main.py              # FastAPI app, route registration
│   ├── config.py            # settings (data path, grid size, etc.)
│   ├── api/
│   │   ├── routes.py        # /routes/shortest, /routes/eta
│   │   └── map.py           # /map/nodes, /map/partitions
│   ├── core/
│   │   ├── graph.py         # graph representation, load/save
│   │   ├── partition.py     # grid partition, which cells to load
│   │   ├── shortest_path.py # Dijkstra/A* on subgraph
│   │   └── eta.py           # travel time, ETA from path
│   ├── data/
│   │   ├── load_osm.py      # build graph from OSM (osmnx/pyrosm)
│   │   └── build_partitions.py  # assign nodes to grid, persist
│   └── models/
│       └── schemas.py       # Pydantic request/response models
│
├── data/                    # gitignore most of it
│   ├── graph.json or .gpickle
│   ├── partitions.json
│   └── sample.osm.pbf       # small OSM extract
│
└── frontend/                # Next.js (later)
    └── ...
```

---

## Part 4: Next.js Frontend (Later)

### 4.1 Goals

- Show the **map** (e.g. Mapbox GL or Leaflet).
- Draw **nodes** (optional, for debugging) and **partition boundaries**.
- **Search**: click or type origin/destination; call backend `POST /routes/shortest` and `POST /routes/eta`.
- Draw **route polyline** and show **distance + ETA**.

### 4.2 Stack

- **Next.js** (App Router or Pages).
- **Map**: Mapbox GL JS or **Leaflet** with React (e.g. `react-leaflet`).
- **State**: React state or Zustand; no need for Redux initially.
- **API client**: `fetch` to `http://localhost:8000` (or env var).

### 4.3 CORS

- Backend: add CORS middleware allowing the Next.js origin (e.g. `http://localhost:3000`).

---

## Implementation Phases

### Phase 1 — Core graph + shortest path (no partitions)

- [ ] Load a small OSM area into nodes + edges (osmnx/pyrosm).
- [ ] Implement in-memory graph (adjacency list or networkx).
- [ ] Snap (lat, lon) to nearest node.
- [ ] Dijkstra or A* for shortest path (by distance).
- [ ] Unit tests: known graph, assert path and length.

### Phase 2 — Partitions

- [ ] Define grid (cell size from config).
- [ ] Assign each node to a cell; build partition index.
- [ ] For a query, determine “scope” (origin cell + dest cell + corridor).
- [ ] Load only those nodes/edges; run Dijkstra on subgraph.
- [ ] Validate: same result as full-graph search (on small graph).

### Phase 3 — ETA

- [ ] Add `max_speed_kmh` (or default by road type) to edges.
- [ ] Shortest path by **time** (weight = length/speed).
- [ ] ETA = departure_time + sum(edge times); expose in API.

### Phase 4 — Python API

- [ ] FastAPI app with `/routes/shortest`, `/routes/eta`, `/map/nodes`, `/map/partitions`.
- [ ] Pydantic schemas; CORS for frontend.
- [ ] Use core graph + partition + ETA under the hood.

### Phase 5 — Next.js frontend

- [ ] Next.js app; map component (Leaflet/Mapbox).
- [ ] Form or map click for origin/destination.
- [ ] Call backend; draw route and show distance + ETA.

### Phase 6 (optional) — Scale and polish

- [ ] Larger OSM region; persist graph and partitions to disk; load on startup.
- [ ] Contraction hierarchies or better partition strategy if needed.
- [ ] Time-of-day or traffic for ETA.

---

## Quick Start (After You Implement Phase 1)

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload

# Frontend (when ready)
cd frontend && npm i && npm run dev
```

---

## Summary

| Part | Deliverable |
|------|-------------|
| **Part 1** | Maps-like graph + shortest path on **partitioned** large maps (grid-based to start). |
| **Part 2** | ETA using edge speeds and optional time/traffic. |
| **Backend** | Python (FastAPI) exposing routes and map data. |
| **Frontend** | Next.js + map library to visualize nodes, partitions, and routes with ETA. |

Start with a **small OSM graph** and get Dijkstra working end-to-end; then add partitions, then ETA, then API, then the webapp. This plan should give you a clear path from zero to a working maps clone with routes and ETAs.
