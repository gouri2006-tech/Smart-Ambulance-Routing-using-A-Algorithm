# A* Path-Finding Visualiser

**Name:** [Your name] &nbsp;|&nbsp; **Register No.:** [Your register number] &nbsp;|&nbsp; **Course / Section:** [Course, section]

An interactive project that finds the shortest path on a grid using the **A\* (A-star) algorithm**,
and compares it with **Dijkstra's algorithm** and **Greedy Best-First Search**.
Written in pure Python (standard library only) - nothing to install.

## Features

- Animated A\* search: see the **open list** (green), **closed list** (blue) and the **final path** (yellow)
- Draw walls and **mud** (cost 5) with the mouse; move the start and goal
- Four heuristics: Manhattan, Euclidean, Chebyshev, Octile
- 4-way or 8-way (diagonal) movement, with no corner-cutting through walls
- Random obstacles and a random maze generator
- **Compare All** button: A\* vs Dijkstra vs Greedy on the same map (cost, nodes expanded, time, optimal or not)
- Save / load maps as plain text files
- Terminal mode that works even without a GUI
- 18 unit tests that check A\* against Dijkstra on hundreds of random grids

## How to run it in VS Code

1. Unzip `astar_project.zip`.
2. In VS Code: **File > Open Folder...** and choose the `astar_project` folder.
3. Install the **Python** extension if VS Code asks (Python 3.8+ required).
4. Open `main.py` and press **F5** (choose *Run A\* Visualiser (GUI)*), or run in the terminal:

```
python main.py
```

If `python` is not recognised on Windows use `py main.py`. On Linux, if you get a tkinter error:
`sudo apt install python3-tk`.

### Other commands

| Command | What it does |
|---|---|
| `python main.py --cli --compare` | Terminal demo on a random maze + comparison table |
| `python main.py --cli --map examples/map_mud.txt --compare` | Run on a saved map |
| `python main.py --cli --diagonal --heuristic octile` | 8-way movement |
| `python -m unittest discover -v` | Run all unit tests |
| `python benchmark.py` | Benchmark on 100 random grids and mazes |

The **Run** panel in VS Code's Run and Debug view (F5 menu) also has ready-made entries for all of these.

## Using the GUI

1. Pick a **brush** (Wall, Erase, Mud, Move Start, Move Goal) and click or drag on the grid.
2. Choose an **algorithm** and **heuristic**, tick **Diagonal moves** if you want, and press **Run**.
3. Press **Compare All** to see a table of all algorithms on your map.
4. Try `Load Map` with the files in `examples/`.

Things to try for your demo / viva:

- `examples/map_mud.txt` - A\* walks around the mud river (cost 30); Greedy wades through it (cost 40).
- `examples/map_maze.txt` - Greedy finds a path of 108 steps; A\* and Dijkstra find the optimal 78, but A\* expands fewer nodes.
- Tick **Diagonal moves** with the **Manhattan** heuristic: a warning appears because Manhattan is not admissible for 8-way movement.

## Project structure

```
astar_project/
|-- main.py               entry point (GUI or --cli)
|-- benchmark.py          experiments used in REPORT.md
|-- astarlab/
|   |-- grid.py           Grid class: walls, mud, neighbours, text format
|   |-- algorithms.py     A*, Dijkstra, Greedy + heuristics (the core of the project)
|   |-- maze.py           random walls and maze generator
|   |-- gui.py            Tkinter visualiser
|   `-- cli.py            terminal front end
|-- tests/test_astar.py   unit tests
|-- examples/             sample maps
|-- REPORT.md             project report (theory, design, results)
`-- .vscode/              run / test configuration
```

## The algorithm in one paragraph

A\* keeps an **open list** (a priority queue of nodes still to explore) and a **closed set**.
Every node gets a score `f(n) = g(n) + h(n)`, where `g(n)` is the cost already paid to reach it and
`h(n)` is a heuristic *estimate* of the cost still to go. A\* always expands the open node with the
lowest `f`. If `h` never over-estimates (it is *admissible*), the first time the goal is expanded the
path found is guaranteed to be the cheapest. Dijkstra is the special case `h = 0` (explores in all
directions); Greedy Best-First uses only `h` (fast, but not optimal).

## Viva questions and answers

Q1. What is A\* and how does it differ from Dijkstra?
A\* is a best-first graph search that uses `f(n) = g(n) + h(n)`. Dijkstra uses only `g(n)`, so it explores uniformly in every direction. A\* uses the heuristic to bias the search toward the goal, so it expands fewer nodes while still returning an optimal path.

Q2. What does "admissible heuristic" mean and why does it matter?
A heuristic is admissible if it never over-estimates the true remaining cost. A\* is only guaranteed to return the shortest path when `h` is admissible (and with a closed set, consistent). In this project Manhattan is admissible for 4-way moves, but not for 8-way moves, which is why the program shows a warning in that case and why Octile/Euclidean are used for diagonals.

Q3. What data structures does your implementation use?
A binary heap (`heapq`) for the open list, giving O(log n) insert and extract-min; a dictionary `g` for the best-known cost to each node; a dictionary `parent` to rebuild the path; and a set for the closed list. A counter is used as a tie-breaker so the heap never has to compare nodes.

Q4. What is the time and space complexity?
In the worst case A\* is O(b^d) with branching factor b and solution depth d; on a grid with V cells it is O(V log V) with a heap, and O(V) space. A good heuristic shrinks the part of the grid that is actually explored (see the benchmark in REPORT.md: about 5x fewer nodes than Dijkstra on random grids).

Q5. Why is Greedy Best-First faster but not optimal?
It ranks nodes by `h(n)` alone and ignores the cost already paid, so it rushes toward the goal and can commit to an expensive route (mud, or a long way round). In the benchmark its paths were optimal in only 0-2% of the test maps.

Q6. How did you test the project?
Unit tests check that A\* returns the same cost as Dijkstra on 40 random grids for each heuristic (4-way and 8-way, with and without mud), that no path is reported when the goal is walled off, that diagonal moves cannot cut corners, that mazes are always solvable, and that A\* expands fewer nodes than Dijkstra overall.

## Possible extensions

Add Jump Point Search, bidirectional A\*, Weighted A\* (`f = g + w*h`), a 3-D grid, or load a real map image.
