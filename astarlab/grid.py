"""Grid world used by the path-finding algorithms.

A grid is a rectangle of cells addressed as (row, col).  Cells can be
free, a wall (impassable) or mud (passable but costs MUD_COST to enter).
"""
from __future__ import annotations

import math
from typing import Iterable, Iterator, Optional, Set, Tuple

Node = Tuple[int, int]  # (row, col)

SQRT2 = math.sqrt(2)
MUD_COST = 5.0

ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAGONAL = ((-1, -1), (-1, 1), (1, -1), (1, 1))


class Grid:
    def __init__(self, rows: int, cols: int) -> None:
        if rows < 2 or cols < 2:
            raise ValueError("grid must be at least 2 x 2")
        self.rows = rows
        self.cols = cols
        self.walls: Set[Node] = set()
        self.mud: Set[Node] = set()
        self.start: Node = (0, 0)
        self.goal: Node = (rows - 1, cols - 1)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def in_bounds(self, node: Node) -> bool:
        r, c = node
        return 0 <= r < self.rows and 0 <= c < self.cols

    def passable(self, node: Node) -> bool:
        return self.in_bounds(node) and node not in self.walls

    def cost(self, node: Node) -> float:
        """Cost of entering `node` (before any diagonal multiplier)."""
        return MUD_COST if node in self.mud else 1.0

    def neighbors(self, node: Node, diagonal: bool = False) -> Iterator[Tuple[Node, float]]:
        """Yield (neighbour, move_cost) pairs.

        Diagonal moves cost sqrt(2) times the cost of the target cell and are
        not allowed to "cut corners" past a wall.
        """
        r, c = node
        for dr, dc in ORTHOGONAL:
            nb = (r + dr, c + dc)
            if self.passable(nb):
                yield nb, self.cost(nb)
        if diagonal:
            for dr, dc in DIAGONAL:
                nb = (r + dr, c + dc)
                if not self.passable(nb):
                    continue
                if not (self.passable((r + dr, c)) and self.passable((r, c + dc))):
                    continue
                yield nb, self.cost(nb) * SQRT2

    # ------------------------------------------------------------------
    # Editing helpers (return True when something changed)
    # ------------------------------------------------------------------
    def _is_endpoint(self, node: Node) -> bool:
        return node == self.start or node == self.goal

    def add_wall(self, node: Node) -> bool:
        if not self.in_bounds(node) or self._is_endpoint(node) or node in self.walls:
            return False
        self.walls.add(node)
        self.mud.discard(node)
        return True

    def add_mud(self, node: Node) -> bool:
        if (not self.in_bounds(node) or self._is_endpoint(node)
                or node in self.walls or node in self.mud):
            return False
        self.mud.add(node)
        return True

    def erase(self, node: Node) -> bool:
        if not self.in_bounds(node):
            return False
        changed = node in self.walls or node in self.mud
        self.walls.discard(node)
        self.mud.discard(node)
        return changed

    def move_start(self, node: Node) -> bool:
        if not self.in_bounds(node) or node == self.goal or node == self.start:
            return False
        self.erase(node)
        self.start = node
        return True

    def move_goal(self, node: Node) -> bool:
        if not self.in_bounds(node) or node == self.start or node == self.goal:
            return False
        self.erase(node)
        self.goal = node
        return True

    def clear_terrain(self) -> None:
        self.walls.clear()
        self.mud.clear()

    # ------------------------------------------------------------------
    # Text format:  # wall   ~ mud   S start   G goal   . free
    # (when rendering a result:  * path   o expanded)
    # ------------------------------------------------------------------
    def to_text(self, path: Optional[Iterable[Node]] = None,
                expanded: Optional[Iterable[Node]] = None) -> str:
        path_set = set(path or [])
        seen = set(expanded or [])
        lines = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                n = (r, c)
                if n == self.start:
                    ch = "S"
                elif n == self.goal:
                    ch = "G"
                elif n in self.walls:
                    ch = "#"
                elif n in path_set:
                    ch = "*"
                elif n in self.mud:
                    ch = "~"
                elif n in seen:
                    ch = "o"
                else:
                    ch = "."
                row.append(ch)
            lines.append("".join(row))
        return "\n".join(lines)

    @classmethod
    def from_text(cls, text: str) -> "Grid":
        lines = [ln.rstrip("\r\n") for ln in text.splitlines() if ln.strip() != ""]
        if not lines:
            raise ValueError("map file is empty")
        width = max(len(ln) for ln in lines)
        grid = cls(len(lines), width)
        start = goal = None
        for r, line in enumerate(lines):
            line = line.ljust(width, "#")
            for c, ch in enumerate(line):
                if ch == "#":
                    grid.walls.add((r, c))
                elif ch == "~":
                    grid.mud.add((r, c))
                elif ch == "S":
                    if start is not None:
                        raise ValueError("map has more than one start 'S'")
                    start = (r, c)
                elif ch == "G":
                    if goal is not None:
                        raise ValueError("map has more than one goal 'G'")
                    goal = (r, c)
        if start is None or goal is None:
            raise ValueError("map needs one 'S' (start) and one 'G' (goal)")
        grid.start, grid.goal = start, goal
        return grid
