"""Tkinter GUI: an interactive A* path-finding visualiser."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .algorithms import ALGORITHMS, compare_algorithms, search
from .grid import Grid
from .maze import random_walls, recursive_backtracker

CELL = 22

COLORS = {
    "empty": "#ffffff",
    "wall": "#2b2d42",
    "mud": "#a67c52",
    "open": "#b7e4c7",
    "closed": "#90caf9",
    "path": "#ffd166",
    "start": "#2e7d32",
    "goal": "#d62828",
    "line": "#d9d9d9",
}

ALGO_LABELS = {"A*": "astar", "Dijkstra": "dijkstra", "Greedy Best-First": "greedy"}
HEUR_LABELS = {"Manhattan": "manhattan", "Euclidean": "euclidean",
               "Chebyshev": "chebyshev", "Octile": "octile"}
TOOLS = [("Wall", "wall"), ("Erase", "erase"), ("Mud (cost 5)", "mud"),
         ("Move Start", "start"), ("Move Goal", "goal")]


class App:
    def __init__(self, root, rows: int = 25, cols: int = 35) -> None:
        self.root = root
        root.title("A* Path-Finding Visualiser")

        self.tool = tk.StringVar(value="wall")
        self.algo_var = tk.StringVar(value="A*")
        self.heur_var = tk.StringVar(value="Manhattan")
        self.diag_var = tk.BooleanVar(value=False)
        self.speed_var = tk.IntVar(value=60)
        self.status_var = tk.StringVar(
            value="Draw walls with the mouse, then press Run. Left-click and drag to paint.")

        self.animating = False
        self.after_id = None
        self.result = None
        self.events = []
        self.event_index = 0
        self.path_queue = []
        self.open_cells = set()
        self.closed_cells = set()
        self.path_cells = set()
        self.rects = {}
        self.cell = CELL

        self.grid = Grid(rows, cols)
        self._default_endpoints()

        self._build_controls()
        self.canvas = tk.Canvas(root, highlightthickness=0, bg=COLORS["line"])
        self.canvas.pack(padx=8, pady=4)
        self.canvas.bind("<Button-1>", self._on_paint)
        self.canvas.bind("<B1-Motion>", self._on_paint)
        tk.Label(root, textvariable=self.status_var, anchor="w", justify="left",
                 wraplength=760).pack(fill="x", padx=8, pady=(0, 8))
        self._build_canvas()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _default_endpoints(self) -> None:
        self.grid.start = (self.grid.rows // 2, 2)
        self.grid.goal = (self.grid.rows // 2, self.grid.cols - 3)

    def _build_controls(self) -> None:
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=8, pady=(8, 0))

        ttk.Label(bar, text="Algorithm:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.algo_var, values=list(ALGO_LABELS),
                     state="readonly", width=17).pack(side="left", padx=(2, 10))
        ttk.Label(bar, text="Heuristic:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.heur_var, values=list(HEUR_LABELS),
                     state="readonly", width=10).pack(side="left", padx=(2, 10))
        ttk.Checkbutton(bar, text="Diagonal moves", variable=self.diag_var).pack(side="left", padx=(0, 10))
        ttk.Label(bar, text="Speed:").pack(side="left")
        ttk.Scale(bar, from_=1, to=100, variable=self.speed_var, length=120).pack(side="left", padx=2)

        tools = ttk.Frame(self.root)
        tools.pack(fill="x", padx=8, pady=(6, 0))
        ttk.Label(tools, text="Brush:").pack(side="left")
        for label, value in TOOLS:
            ttk.Radiobutton(tools, text=label, value=value, variable=self.tool).pack(side="left", padx=4)

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=8, pady=(6, 0))
        for text, command in [("Run", self.run), ("Stop", self.stop),
                              ("Clear Path", self.clear_search), ("Clear All", self.clear_all),
                              ("Random Walls", self.random_walls), ("Maze", self.maze),
                              ("Compare All", self.compare), ("Save Map", self.save_map),
                              ("Load Map", self.load_map)]:
            ttk.Button(buttons, text=text, command=command).pack(side="left", padx=2)

        legend = ttk.Frame(self.root)
        legend.pack(fill="x", padx=8, pady=(6, 0))
        for name, color in [("start", COLORS["start"]), ("goal", COLORS["goal"]),
                            ("wall", COLORS["wall"]), ("mud", COLORS["mud"]),
                            ("open list", COLORS["open"]), ("closed list", COLORS["closed"]),
                            ("final path", COLORS["path"])]:
            tk.Label(legend, text=" " * 2, bg=color, relief="solid", borderwidth=1).pack(side="left")
            ttk.Label(legend, text=name).pack(side="left", padx=(2, 10))

    def _build_canvas(self) -> None:
        g = self.grid
        self.cell = max(6, min(CELL, 900 // g.cols, 650 // g.rows))
        self.canvas.delete("all")
        self.canvas.config(width=g.cols * self.cell, height=g.rows * self.cell)
        self.rects = {}
        for r in range(g.rows):
            for c in range(g.cols):
                x0, y0 = c * self.cell, r * self.cell
                self.rects[(r, c)] = self.canvas.create_rectangle(
                    x0, y0, x0 + self.cell, y0 + self.cell,
                    fill=self._color((r, c)), outline=COLORS["line"])

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def _color(self, node) -> str:
        g = self.grid
        if node == g.start:
            return COLORS["start"]
        if node == g.goal:
            return COLORS["goal"]
        if node in self.path_cells:
            return COLORS["path"]
        if node in g.walls:
            return COLORS["wall"]
        if node in g.mud:
            return COLORS["mud"] if node not in self.closed_cells else COLORS["closed"]
        if node in self.closed_cells:
            return COLORS["closed"]
        if node in self.open_cells:
            return COLORS["open"]
        return COLORS["empty"]

    def _paint(self, node) -> None:
        item = self.rects.get(node)
        if item is not None:
            self.canvas.itemconfig(item, fill=self._color(node))

    def _repaint_all(self) -> None:
        for node in self.rects:
            self._paint(node)

    def _on_paint(self, event) -> None:
        if self.animating:
            return
        node = (event.y // self.cell, event.x // self.cell)
        if not self.grid.in_bounds(node):
            return
        g = self.grid
        tool = self.tool.get()
        touched = [node]
        if tool == "wall":
            changed = g.add_wall(node)
        elif tool == "erase":
            changed = g.erase(node)
        elif tool == "mud":
            changed = g.add_mud(node)
        elif tool == "start":
            touched.append(g.start)
            changed = g.move_start(node)
        else:
            touched.append(g.goal)
            changed = g.move_goal(node)
        if not changed:
            return
        if self.open_cells or self.closed_cells or self.path_cells:
            self.clear_search()      # old result no longer matches the map
        for n in touched:
            self._paint(n)

    # ------------------------------------------------------------------
    # Running the search (animated replay of the recorded events)
    # ------------------------------------------------------------------
    def run(self) -> None:
        if self.animating:
            return
        self.clear_search()
        algo = ALGO_LABELS[self.algo_var.get()]
        heur = HEUR_LABELS[self.heur_var.get()]
        self.result = search(self.grid, algo, heur, self.diag_var.get())
        self.events = self.result.events
        self.event_index = 0
        self.animating = True
        self.status_var.set("Searching ...")
        self._tick()

    def _tick(self) -> None:
        if not self.animating:
            return
        speed = int(self.speed_var.get())
        batch = 1 + (speed * speed) // 250
        for _ in range(batch):
            if self.event_index >= len(self.events):
                self._start_path_animation()
                return
            kind, node = self.events[self.event_index]
            self.event_index += 1
            if kind == "open":
                self.open_cells.add(node)
            else:
                self.open_cells.discard(node)
                self.closed_cells.add(node)
            self._paint(node)
        self.after_id = self.root.after(15, self._tick)

    def _start_path_animation(self) -> None:
        if self.result.found:
            self.path_queue = list(self.result.path)
            self._tick_path()
        else:
            self._finish()

    def _tick_path(self) -> None:
        if not self.animating:
            return
        if not self.path_queue:
            self._finish()
            return
        node = self.path_queue.pop(0)
        self.path_cells.add(node)
        self._paint(node)
        delay = max(5, 40 - int(self.speed_var.get()) // 3)
        self.after_id = self.root.after(delay, self._tick_path)

    def _finish(self) -> None:
        self.animating = False
        self.after_id = None
        res = self.result
        if res.found:
            text = (f"{res.label} ({res.heuristic}) | cost {res.cost:.2f} | "
                    f"{res.path_length} steps | expanded {res.expanded} | "
                    f"generated {res.generated} | {res.elapsed_ms:.2f} ms")
        else:
            text = f"{res.label}: no path found (expanded {res.expanded} nodes)."
        if res.warning:
            text += "\nNote: " + res.warning
        self.status_var.set(text)

    def stop(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.animating = False

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------
    def clear_search(self) -> None:
        self.stop()
        touched = self.open_cells | self.closed_cells | self.path_cells
        self.open_cells = set()
        self.closed_cells = set()
        self.path_cells = set()
        for node in touched:
            self._paint(node)

    def clear_all(self) -> None:
        self.clear_search()
        self.grid.clear_terrain()
        self._default_endpoints()
        self._repaint_all()
        self.status_var.set("Cleared.")

    def random_walls(self) -> None:
        self.clear_search()
        random_walls(self.grid, 0.25)
        self._repaint_all()
        self.status_var.set("Random walls placed (25% density). Some maps have no path - that is fine.")

    def maze(self) -> None:
        self.clear_search()
        try:
            recursive_backtracker(self.grid, loops=0.08)
        except ValueError as exc:
            messagebox.showerror("Maze", str(exc))
            return
        self._repaint_all()
        self.status_var.set("Maze generated. Start and goal moved to opposite corners.")

    def compare(self) -> None:
        diagonal = self.diag_var.get()
        rows = compare_algorithms(self.grid, diagonal)
        win = tk.Toplevel(self.root)
        win.title("Algorithm comparison")
        cols = ("Algorithm", "Heuristic", "Path cost", "Expanded", "Generated", "Time (ms)", "Optimal?")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=len(rows))
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=115, anchor="center")
        for res, optimal in rows:
            tree.insert("", "end", values=(
                res.label, res.heuristic,
                f"{res.cost:.2f}" if res.found else "no path",
                res.expanded, res.generated, f"{res.elapsed_ms:.3f}",
                "-" if optimal is None else ("yes" if optimal else "NO")))
        tree.pack(padx=10, pady=10)
        note = "Dijkstra is the reference for optimality. Fewer expanded nodes = a more efficient search."
        if diagonal:
            note += "\nWith diagonal moves on, Manhattan is not admissible and may be sub-optimal."
        ttk.Label(win, text=note, justify="left").pack(padx=10, pady=(0, 10))

    def save_map(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text map", "*.txt")])
        if path:
            Path(path).write_text(self.grid.to_text(), encoding="utf-8")
            self.status_var.set(f"Saved map to {path}")

    def load_map(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Text map", "*.txt")])
        if not path:
            return
        try:
            grid = Grid.from_text(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            messagebox.showerror("Load map", str(exc))
            return
        self.clear_search()
        self.grid = grid
        self._build_canvas()
        self.status_var.set(f"Loaded {grid.rows} x {grid.cols} map from {path}")


def launch() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()
