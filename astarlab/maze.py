"""Terrain generators: random obstacles and a perfect-maze carver."""
from __future__ import annotations

import random
from typing import Optional

from .grid import Grid


def random_walls(grid: Grid, density: float = 0.25, seed: Optional[int] = None) -> None:
    """Fill the grid with random walls (start and goal are kept free)."""
    rng = random.Random(seed)
    grid.clear_terrain()
    for r in range(grid.rows):
        for c in range(grid.cols):
            node = (r, c)
            if node in (grid.start, grid.goal):
                continue
            if rng.random() < density:
                grid.walls.add(node)


def recursive_backtracker(grid: Grid, seed: Optional[int] = None, loops: float = 0.05) -> None:
    """Carve a maze with an iterative depth-first search.

    The start is moved to the top-left cell and the goal to the bottom-right
    cell.  `loops` is the chance of knocking down an extra wall so that the
    maze has more than one route (a "perfect" maze has exactly one, which
    makes every algorithm look the same).
    """
    if grid.rows < 5 or grid.cols < 5:
        raise ValueError("grid must be at least 5 x 5 to carve a maze")
    rng = random.Random(seed)
    rows, cols = grid.rows, grid.cols
    grid.mud.clear()
    walls = {(r, c) for r in range(rows) for c in range(cols)}
    grid.walls = walls

    first = (1, 1)
    walls.discard(first)
    stack = [first]
    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            nr, nc = r + dr, c + dc
            if 1 <= nr <= rows - 2 and 1 <= nc <= cols - 2 and (nr, nc) in walls:
                options.append((nr, nc, dr, dc))
        if options:
            nr, nc, dr, dc = rng.choice(options)
            walls.discard((r + dr // 2, c + dc // 2))
            walls.discard((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    if loops > 0:
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if (r, c) not in walls:
                    continue
                horizontal = ((r, c - 1) not in walls and (r, c + 1) not in walls
                              and (r - 1, c) in walls and (r + 1, c) in walls)
                vertical = ((r - 1, c) not in walls and (r + 1, c) not in walls
                            and (r, c - 1) in walls and (r, c + 1) in walls)
                if (horizontal or vertical) and rng.random() < loops:
                    walls.discard((r, c))

    last_r = rows - 2 if (rows - 2) % 2 == 1 else rows - 3
    last_c = cols - 2 if (cols - 2) % 2 == 1 else cols - 3
    grid.start = (1, 1)
    grid.goal = (last_r, last_c)
