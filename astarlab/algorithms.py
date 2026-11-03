"""Path-finding algorithms: A*, Dijkstra and Greedy Best-First Search.

All three share one implementation of the "best-first" loop; they only
differ in how a node's priority is computed:

    A*                f(n) = g(n) + h(n)
    Dijkstra          f(n) = g(n)            (A* with h = 0)
    Greedy best-first f(n) = h(n)

g(n) is the cheapest known cost from the start to n and h(n) is the
heuristic estimate of the remaining cost from n to the goal.
"""
from __future__ import annotations

import heapq
import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .grid import Grid, Node, SQRT2

Heuristic = Callable[[Node, Node], float]


# ----------------------------------------------------------------------
# Heuristics
# ----------------------------------------------------------------------
def manhattan(a: Node, b: Node) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a: Node, b: Node) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def chebyshev(a: Node, b: Node) -> float:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def octile(a: Node, b: Node) -> float:
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dx + dy) + (SQRT2 - 2) * min(dx, dy)


def zero(a: Node, b: Node) -> float:
    return 0.0


HEURISTICS: Dict[str, Heuristic] = {
    "manhattan": manhattan,
    "euclidean": euclidean,
    "chebyshev": chebyshev,
    "octile": octile,
}

ALGORITHMS: Dict[str, str] = {
    "astar": "A*",
    "dijkstra": "Dijkstra",
    "greedy": "Greedy Best-First",
}


# ----------------------------------------------------------------------
# Result object
# ----------------------------------------------------------------------
@dataclass
class SearchResult:
    algorithm: str
    heuristic: str
    diagonal: bool
    found: bool
    path: List[Node] = field(default_factory=list)
    cost: float = math.inf
    expanded: int = 0      # nodes moved to the closed set
    generated: int = 0     # nodes pushed onto the open list
    elapsed_ms: float = 0.0
    events: List[Tuple[str, Node]] = field(default_factory=list)  # ("open"|"closed", node)
    warning: str = ""

    @property
    def path_length(self) -> int:
        """Number of steps (moves) in the path."""
        return max(len(self.path) - 1, 0)

    @property
    def label(self) -> str:
        return ALGORITHMS[self.algorithm]


# ----------------------------------------------------------------------
# The search itself
# ----------------------------------------------------------------------
def search(grid: Grid,
           algorithm: str = "astar",
           heuristic: str = "manhattan",
           diagonal: bool = False,
           start: Optional[Node] = None,
           goal: Optional[Node] = None) -> SearchResult:
    if algorithm not in ALGORITHMS:
        raise ValueError(f"unknown algorithm {algorithm!r}; choose from {list(ALGORITHMS)}")
    if heuristic not in HEURISTICS:
        raise ValueError(f"unknown heuristic {heuristic!r}; choose from {list(HEURISTICS)}")

    start = grid.start if start is None else start
    goal = grid.goal if goal is None else goal
    h = zero if algorithm == "dijkstra" else HEURISTICS[heuristic]
    used = "none" if algorithm == "dijkstra" else heuristic

    result = SearchResult(algorithm, used, diagonal, found=False)
    if algorithm == "astar" and diagonal and heuristic == "manhattan":
        result.warning = ("Manhattan distance over-estimates when diagonal moves are allowed, "
                          "so the path may not be optimal. Use Octile or Euclidean instead.")

    if not grid.passable(start) or not grid.passable(goal):
        return result

    def priority(g_val: float, h_val: float) -> float:
        if algorithm == "astar":
            return g_val + h_val
        if algorithm == "dijkstra":
            return g_val
        return h_val  # greedy

    t0 = time.perf_counter()
    counter = itertools.count()          # tie-breaker so heap never compares nodes
    g: Dict[Node, float] = {start: 0.0}
    parent: Dict[Node, Optional[Node]] = {start: None}
    closed = set()

    h0 = h(start, goal)
    open_heap: List[Tuple[float, float, int, Node]] = [(priority(0.0, h0), h0, next(counter), start)]
    result.generated = 1
    result.events.append(("open", start))

    while open_heap:
        _, _, _, current = heapq.heappop(open_heap)
        if current in closed:            # stale duplicate entry
            continue
        closed.add(current)
        result.expanded += 1
        result.events.append(("closed", current))

        if current == goal:
            path = []
            node: Optional[Node] = current
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            result.found = True
            result.path = path
            result.cost = g[goal]
            break

        for nb, step_cost in grid.neighbors(current, diagonal):
            if nb in closed:
                continue
            tentative = g[current] + step_cost
            if tentative < g.get(nb, math.inf):
                g[nb] = tentative
                parent[nb] = current
                h_val = h(nb, goal)
                # on equal f prefer the node closer to the goal (smaller h)
                heapq.heappush(open_heap, (priority(tentative, h_val), h_val, next(counter), nb))
                result.generated += 1
                result.events.append(("open", nb))

    result.elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return result


# ----------------------------------------------------------------------
# Convenience: compare several algorithms on the same grid
# ----------------------------------------------------------------------
COMPARE_SETUPS = [
    ("astar", "manhattan"),
    ("astar", "euclidean"),
    ("astar", "octile"),
    ("dijkstra", "manhattan"),
    ("greedy", "manhattan"),
]


def compare_algorithms(grid: Grid, diagonal: bool = False) -> List[Tuple[SearchResult, Optional[bool]]]:
    """Run every setup in COMPARE_SETUPS.

    Returns (result, is_optimal) pairs.  Dijkstra is the ground truth for
    optimality; is_optimal is None when no path exists.
    """
    results = [search(grid, a, hname, diagonal) for a, hname in COMPARE_SETUPS]
    reference = next(r for r in results if r.algorithm == "dijkstra")
    out: List[Tuple[SearchResult, Optional[bool]]] = []
    for r in results:
        if not reference.found:
            out.append((r, None))
        else:
            out.append((r, r.found and abs(r.cost - reference.cost) < 1e-9))
    return out
