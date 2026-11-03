"""Command-line front end (works without any GUI)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .algorithms import ALGORITHMS, compare_algorithms, search
from .grid import Grid
from .maze import recursive_backtracker


def run_cli(map_path: Optional[str] = None,
            algorithm: str = "astar",
            heuristic: str = "manhattan",
            diagonal: bool = False,
            seed: int = 7,
            rows: int = 21,
            cols: int = 41,
            compare: bool = False) -> int:
    if map_path:
        grid = Grid.from_text(Path(map_path).read_text(encoding="utf-8"))
    else:
        grid = Grid(rows, cols)
        recursive_backtracker(grid, seed=seed, loops=0.08)

    result = search(grid, algorithm, heuristic, diagonal)
    expanded = [n for kind, n in result.events if kind == "closed"]

    print(grid.to_text(path=result.path, expanded=expanded))
    print()
    print("Legend:  S start   G goal   # wall   ~ mud (cost 5)   * path   o expanded")
    print()
    if result.found:
        print(f"{ALGORITHMS[algorithm]} ({result.heuristic}, "
              f"{'8-way' if diagonal else '4-way'} moves)")
        print(f"  path cost       : {result.cost:.2f}")
        print(f"  path length     : {result.path_length} steps")
        print(f"  nodes expanded  : {result.expanded}")
        print(f"  nodes generated : {result.generated}")
        print(f"  time            : {result.elapsed_ms:.3f} ms")
    else:
        print(f"No path found (expanded {result.expanded} nodes).")
    if result.warning:
        print(f"  note: {result.warning}")

    if compare:
        print()
        print_comparison(grid, diagonal)
    return 0 if result.found else 1


def print_comparison(grid: Grid, diagonal: bool) -> None:
    header = f"{'Algorithm':<20}{'Heuristic':<12}{'Cost':>9}{'Expanded':>10}{'Generated':>11}{'ms':>9}  Optimal"
    print(header)
    print("-" * len(header))
    for res, optimal in compare_algorithms(grid, diagonal):
        cost = f"{res.cost:.2f}" if res.found else "none"
        opt = "-" if optimal is None else ("yes" if optimal else "NO")
        print(f"{res.label:<20}{res.heuristic:<12}{cost:>9}{res.expanded:>10}"
              f"{res.generated:>11}{res.elapsed_ms:>9.3f}  {opt}")
