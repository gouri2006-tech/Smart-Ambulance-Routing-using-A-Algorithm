"""Benchmark A*, Dijkstra and Greedy on random obstacle grids and mazes.

    python benchmark.py

Prints a Markdown table that can be pasted into the report.
"""
import statistics

from astarlab import Grid, random_walls, recursive_backtracker, search

SETUPS = [
    ("A* (Manhattan)", "astar", "manhattan"),
    ("A* (Euclidean)", "astar", "euclidean"),
    ("Dijkstra", "dijkstra", "manhattan"),
    ("Greedy (Manhattan)", "greedy", "manhattan"),
]


def make_random(seed):
    g = Grid(40, 40)
    random_walls(g, 0.25, seed)
    return g


def make_maze(seed):
    g = Grid(41, 41)
    recursive_backtracker(g, seed, loops=0.10)
    return g


def run(name, factory, runs=50):
    grids = [factory(s) for s in range(runs)]
    reference = [search(g, "dijkstra") for g in grids]
    solvable = [i for i, r in enumerate(reference) if r.found]
    print(f"\n### {name}  ({len(solvable)} of {runs} grids solvable)\n")
    print("| Algorithm | Avg path cost | Avg nodes expanded | Avg time (ms) | Optimal paths |")
    print("|---|---|---|---|---|")
    for label, algo, heur in SETUPS:
        costs, expanded, times, optimal = [], [], [], 0
        for i in solvable:
            r = search(grids[i], algo, heur)
            costs.append(r.cost)
            expanded.append(r.expanded)
            times.append(r.elapsed_ms)
            optimal += abs(r.cost - reference[i].cost) < 1e-9
        print(f"| {label} | {statistics.mean(costs):.1f} | {statistics.mean(expanded):.0f} | "
              f"{statistics.mean(times):.2f} | {100 * optimal / len(solvable):.0f}% |")


if __name__ == "__main__":
    run("Random obstacle grids, 40 x 40, 25% walls", make_random)
    run("Mazes, 41 x 41, with loops", make_maze)
