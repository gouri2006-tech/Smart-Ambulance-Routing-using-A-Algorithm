# Path Finding on a Grid Using the A\* Algorithm

**Name:** [Your name] &nbsp;|&nbsp; **Register No.:** [Your register number]
**Course:** [Course name and code] &nbsp;|&nbsp; **Class / Section:** [Section]
**Department:** Computer Science Engineering &nbsp;|&nbsp; **Guide:** [Faculty name]

---

## 1. Abstract

This project implements the A\* search algorithm to find least-cost paths between two cells on a 2-D grid
containing walls and costly terrain ("mud"). A graphical visualiser animates the search so that the open list,
closed list and final path can be observed. A\* is compared against Dijkstra's algorithm and Greedy Best-First
Search on 100 generated maps. Results show that A\* returns an optimal path in every case while expanding roughly
5x fewer nodes than Dijkstra on random obstacle maps and about half as many on mazes.

## 2. Problem Statement

Given a grid, a start cell and a goal cell, find the cheapest sequence of moves from start to goal, avoiding walls,
where entering a mud cell costs 5 and entering a normal cell costs 1. Report the path, its cost, and how much
work the search did.

## 3. Background

### 3.1 Graph model
Each free cell is a vertex; each allowed move to a neighbouring cell is an edge with a positive weight. 4-way movement
connects horizontal and vertical neighbours (cost 1). 8-way movement also allows diagonals with cost sqrt(2); a diagonal
move is forbidden if it would cut the corner of a wall.

### 3.2 A\* search
A\* assigns every node `n` the value

```
f(n) = g(n) + h(n)
```

- `g(n)`: cheapest known cost from the start to `n`
- `h(n)`: heuristic estimate of the cheapest cost from `n` to the goal
- `f(n)`: estimated cost of the cheapest path through `n`

A\* repeatedly removes the node with the smallest `f` from the open list. When the goal is removed, the path is
rebuilt by following parent pointers.

**Pseudocode**

```
open  <- priority queue containing start   (priority = f)
g[start] <- 0
while open is not empty:
    n <- node in open with smallest f
    if n is closed: continue
    add n to closed
    if n == goal: return path via parent[]
    for each neighbour m of n with move cost c:
        if m is closed: continue
        if g[n] + c < g[m]:
            g[m] <- g[n] + c ; parent[m] <- n
            push m into open with f = g[m] + h(m)
return "no path"
```

### 3.3 Admissible and consistent heuristics
A heuristic is **admissible** if `h(n)` never exceeds the true cost from `n` to the goal. It is **consistent** if
`h(n) <= c(n, m) + h(m)` for every edge. With a consistent heuristic every node is expanded at most once and the first
path to the goal is optimal.

| Heuristic | Formula | Admissible for |
|---|---|---|
| Manhattan | `\|dx\| + \|dy\|` | 4-way movement only |
| Euclidean | `sqrt(dx^2 + dy^2)` | 4-way and 8-way |
| Chebyshev | `max(\|dx\|, \|dy\|)` | 4-way and 8-way |
| Octile | `(dx + dy) + (sqrt(2) - 2) * min(dx, dy)` | 4-way and 8-way (exact on an empty 8-way grid) |

All heuristics stay admissible when mud is present, because mud only makes moves more expensive than 1.

### 3.4 Related algorithms
- **Dijkstra**: `f(n) = g(n)`, i.e. A\* with `h = 0`. Optimal but explores in every direction.
- **Greedy Best-First**: `f(n) = h(n)`. Very fast but ignores the cost already paid, so it is not optimal.

### 3.5 Complexity
With a binary heap, each of the V cells enters and leaves the open list a bounded number of times, giving
**O(V log V)** time and **O(V)** space on a grid. In general graphs the worst case is O(b^d). The quality of `h` decides how
much of the grid is actually visited.

## 4. Design and Implementation

The project is written in Python 3 using only the standard library.

| Module | Responsibility |
|---|---|
| `grid.py` | `Grid` class: walls, mud, neighbour generation (with corner-cutting rule), text map import/export |
| `algorithms.py` | `search()` implementing A\*, Dijkstra and Greedy in one loop; heuristics; `compare_algorithms()` |
| `maze.py` | Random obstacle generator and recursive-backtracker maze generator (iterative DFS) |
| `gui.py` | Tkinter visualiser; replays the recorded search events as an animation |
| `cli.py` / `main.py` | Terminal interface and entry point |
| `tests/test_astar.py` | 18 unit tests |

**Key implementation choices**

- The open list is a `heapq` binary heap of `(f, h, counter, node)`. Ties on `f` are broken in favour of smaller `h`, and a counter
  makes entries unique so nodes are never compared.
- Instead of decrease-key, a node is pushed again when a cheaper route is found; stale entries are skipped when popped (lazy deletion).
- `search()` records every "open" and "closed" event. The GUI replays this list at a user-chosen speed, which keeps the algorithm
  completely independent of the user interface and easy to test.
- The program warns when A\* is run with Manhattan distance and diagonal moves, since the heuristic is then inadmissible.

## 5. Testing

Eighteen unit tests (`python -m unittest discover -v`) cover:

- empty-grid cost equals Manhattan distance; start = goal; unreachable goal; blocked start/goal; invalid arguments
- **optimality**: A\* cost equals Dijkstra cost on 40 random maps for each heuristic, in 4-way mode, 8-way mode and with mud
- A\* expands fewer nodes than Dijkstra in total over 30 maps
- Greedy returns valid but never cheaper paths than A\*
- no corner cutting; diagonal path cost on an empty grid is 9 * sqrt(2); mud is avoided when the detour is cheaper
- generated mazes are always solvable; map text round-trips correctly

All tests pass.

## 6. Experimental Results

`python benchmark.py` generates 50 random obstacle grids (40 x 40, 25% walls) and 50 mazes (41 x 41, with extra openings)
and runs each algorithm with 4-way movement. Only solvable maps are counted. Times are for this machine and will differ on yours.

**Random obstacle grids, 40 x 40, 25% walls (32 of 50 maps solvable)**

| Algorithm | Avg path cost | Avg nodes expanded | Avg time (ms) | Optimal paths |
|---|---|---|---|---|
| A\* (Manhattan) | 78.4 | 220 | 0.79 | 100% |
| A\* (Euclidean) | 78.4 | 942 | 2.86 | 100% |
| Dijkstra | 78.4 | 1183 | 5.46 | 100% |
| Greedy (Manhattan) | 92.2 | 113 | 0.71 | 0% |

**Mazes, 41 x 41, with loops (50 of 50 solvable)**

| Algorithm | Avg path cost | Avg nodes expanded | Avg time (ms) | Optimal paths |
|---|---|---|---|---|
| A\* (Manhattan) | 98.4 | 432 | 2.39 | 100% |
| A\* (Euclidean) | 98.4 | 589 | 3.19 | 100% |
| Dijkstra | 98.4 | 811 | 3.97 | 100% |
| Greedy (Manhattan) | 120.6 | 154 | 0.82 | 2% |

**Observations**

1. Every A\* run returned the same cost as Dijkstra, confirming optimality with admissible heuristics.
2. A\* with Manhattan expanded about 5.4x fewer nodes than Dijkstra on open random maps (220 vs 1183) and about 1.9x fewer on mazes
   (432 vs 811). Mazes help A\* less because walls force the path away from the straight line to the goal, so the heuristic is less informative.
3. Manhattan beat Euclidean for 4-way movement because it is a tighter (larger, still admissible) estimate of the true cost.
4. Greedy expanded the fewest nodes but produced paths 18-23% longer than optimal and was almost never optimal.

## 7. Limitations and Future Work

- The grid is small enough that the heap-based implementation is instantaneous; very large maps could use Jump Point Search or hierarchical A\*.
- Possible extensions: Weighted A\* (`f = g + w * h`) for faster, bounded-suboptimal search; bidirectional A\*; moving obstacles (D\* Lite); 3-D grids.

## 8. Conclusion

A\* combines the optimality of Dijkstra's algorithm with a goal-directed heuristic, giving optimal paths with far less search effort. The
implementation and its visualiser demonstrate how the choice of heuristic affects efficiency and why admissibility is required for correctness.

## 9. References

1. P. E. Hart, N. J. Nilsson and B. Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths," *IEEE Transactions on Systems Science and Cybernetics*, vol. 4, no. 2, pp. 100-107, 1968.
2. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2021 - Chapter 3 (Informed Search).
3. E. W. Dijkstra, "A note on two problems in connexion with graphs," *Numerische Mathematik*, vol. 1, pp. 269-271, 1959.
4. A. Patel, "Amit's A\* Pages" (heuristics for grid maps), Stanford University.
