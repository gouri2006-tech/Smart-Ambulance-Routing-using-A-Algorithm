"""astarlab - a small A* path-finding library with a visualiser."""
from .algorithms import (ALGORITHMS, HEURISTICS, SearchResult,
                         compare_algorithms, search)
from .grid import Grid
from .maze import random_walls, recursive_backtracker

__all__ = [
    "ALGORITHMS", "HEURISTICS", "SearchResult", "Grid",
    "compare_algorithms", "search", "random_walls", "recursive_backtracker",
]
