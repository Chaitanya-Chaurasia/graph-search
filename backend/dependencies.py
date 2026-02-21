"""FastAPI dependency providers. Callables to be used for dependency injections"""
from fastapi import Request
from backend.state import AppState
from backend.core import Graph, PathFinder


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state

def get_graph(request: Request) -> Graph:
    return request.app.state.app_state.graph

def get_pathfinder(request: Request) -> PathFinder:
    return request.app.state.app_state.pathfinder
