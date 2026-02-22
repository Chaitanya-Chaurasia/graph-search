"""FastAPI app: creation, middleware, lifespan, router registration."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.state import AppState
from backend.api import map_router, routes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load graph and pathfinder once at startup."""
    app.state.app_state = AppState()
    yield

app = FastAPI(title="Shortest Path on Graph", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(map_router)
app.include_router(routes_router)
