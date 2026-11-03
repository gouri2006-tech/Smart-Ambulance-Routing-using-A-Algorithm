import math
import unittest

from astarlab import Grid, random_walls, recursive_backtracker, search
from astarlab.algorithms import compare_algorithms


def assert_valid_path(case, grid, result, diagonal=False):
    path = result.path
    case.assertEqual(path[0], grid.start)
    case.assertEqual(path[-1], grid.goal)
    for a, b in zip(path, path[1:]):
        dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
        case.assertTrue(grid.passable(b))
        if diagonal:
            case.assertTrue(max(dr, dc) == 1)
        else:
            case.assertEqual(dr + dc, 1)


def random_grid(seed, size=20, density=0.25):
    g = Grid(size, size)
    random_walls(g, density, seed)
    return g


class TestBasics(unittest.TestCase):
    def test_empty_grid_cost_equals_manhattan_distance(self):
        g = Grid(10, 10)
        r = search(g, "astar", "manhattan")
        self.assertTrue(r.found)
        self.assertEqual(r.cost, 18)
        assert_valid_path(self, g, r)

    def test_no_path(self):
        g = Grid(5, 5)
        for row in range(5):
            g.walls.add((row, 2))
        r = search(g, "astar")
        self.assertFalse(r.found)
        self.assertEqual(r.path, [])

    def test_start_equals_goal(self):
        g = Grid(5, 5)
        g.goal = g.start
        r = search(g, "astar")
        self.assertTrue(r.found)
        self.assertEqual(r.cost, 0)
        self.assertEqual(r.path, [g.start])

    def test_blocked_endpoints(self):
        g = Grid(5, 5)
        g.walls.add(g.goal)
        self.assertFalse(search(g, "astar").found)

    def test_invalid_names(self):
        g = Grid(4, 4)
        with self.assertRaises(ValueError):
            search(g, "bogus")
        with self.assertRaises(ValueError):
            search(g, "astar", "bogus")


class TestOptimality(unittest.TestCase):
    def test_astar_matches_dijkstra_four_way(self):
        for heuristic in ("manhattan", "euclidean", "octile", "chebyshev"):
            for seed in range(40):
                g = random_grid(seed)
                a = search(g, "astar", heuristic)
                d = search(g, "dijkstra")
                self.assertEqual(a.found, d.found)
                if d.found:
                    self.assertAlmostEqual(a.cost, d.cost, places=9, msg=f"{heuristic} seed {seed}")
                    assert_valid_path(self, g, a)

    def test_astar_matches_dijkstra_eight_way(self):
        for heuristic in ("octile", "euclidean", "chebyshev"):
            for seed in range(40):
                g = random_grid(seed)
                a = search(g, "astar", heuristic, diagonal=True)
                d = search(g, "dijkstra", diagonal=True)
                self.assertEqual(a.found, d.found)
                if d.found:
                    self.assertAlmostEqual(a.cost, d.cost, places=9, msg=f"{heuristic} seed {seed}")
                    assert_valid_path(self, g, a, diagonal=True)

    def test_astar_matches_dijkstra_with_mud(self):
        for seed in range(30):
            g = random_grid(seed, density=0.15)
            for r in range(20):
                for c in range(20):
                    if (r * 7 + c * 3 + seed) % 5 == 0 and (r, c) not in g.walls \
                            and (r, c) not in (g.start, g.goal):
                        g.mud.add((r, c))
            a = search(g, "astar", "manhattan")
            d = search(g, "dijkstra")
            self.assertEqual(a.found, d.found)
            if d.found:
                self.assertAlmostEqual(a.cost, d.cost, places=9)

    def test_astar_expands_fewer_nodes_than_dijkstra(self):
        astar_total = dijkstra_total = 0
        for seed in range(30):
            g = random_grid(seed, size=30, density=0.2)
            a = search(g, "astar", "manhattan")
            d = search(g, "dijkstra")
            astar_total += a.expanded
            dijkstra_total += d.expanded
        self.assertLess(astar_total, dijkstra_total)

    def test_greedy_returns_valid_but_maybe_longer_path(self):
        for seed in range(30):
            g = random_grid(seed)
            gr = search(g, "greedy", "manhattan")
            a = search(g, "astar", "manhattan")
            self.assertEqual(gr.found, a.found)
            if a.found:
                assert_valid_path(self, g, gr)
                self.assertGreaterEqual(gr.cost, a.cost - 1e-9)


class TestMovementRules(unittest.TestCase):
    def test_no_corner_cutting(self):
        g = Grid(3, 3)
        g.start, g.goal = (0, 0), (1, 1)
        g.walls |= {(0, 1), (1, 0)}
        self.assertFalse(search(g, "astar", "octile", diagonal=True).found)

    def test_diagonal_is_shorter_on_open_grid(self):
        g = Grid(10, 10)
        four = search(g, "astar", "octile", diagonal=False)
        eight = search(g, "astar", "octile", diagonal=True)
        self.assertAlmostEqual(eight.cost, 9 * math.sqrt(2))
        self.assertLess(eight.cost, four.cost)

    def test_mud_is_avoided_when_detour_is_cheaper(self):
        g = Grid(5, 5)
        g.start, g.goal = (2, 0), (2, 4)
        g.mud |= {(2, 1), (2, 2), (2, 3)}
        r = search(g, "astar", "manhattan")
        self.assertEqual(r.cost, 6)
        self.assertFalse(any(n in g.mud for n in r.path))

    def test_manhattan_with_diagonal_gives_warning(self):
        g = Grid(6, 6)
        self.assertTrue(search(g, "astar", "manhattan", diagonal=True).warning)
        self.assertEqual(search(g, "astar", "octile", diagonal=True).warning, "")


class TestMazeAndText(unittest.TestCase):
    def test_mazes_are_solvable(self):
        for seed in range(10):
            for loops in (0.0, 0.1):
                g = Grid(21, 31)
                recursive_backtracker(g, seed, loops)
                self.assertTrue(search(g, "astar").found, f"seed {seed}")

    def test_text_round_trip(self):
        g = random_grid(3)
        g.mud |= {(1, 1), (2, 2)} - {g.start, g.goal} - g.walls
        g2 = Grid.from_text(g.to_text())
        self.assertEqual((g.rows, g.cols), (g2.rows, g2.cols))
        self.assertEqual(g.walls, g2.walls)
        self.assertEqual(g.mud, g2.mud)
        self.assertEqual((g.start, g.goal), (g2.start, g2.goal))

    def test_bad_map_text(self):
        with self.assertRaises(ValueError):
            Grid.from_text("...\n...")          # no S / G
        with self.assertRaises(ValueError):
            Grid.from_text("S.S\n..G")          # two starts

    def test_compare_marks_dijkstra_optimal(self):
        g = random_grid(5)
        rows = compare_algorithms(g, diagonal=True)
        dijkstra = [opt for res, opt in rows if res.algorithm == "dijkstra"][0]
        self.assertIn(dijkstra, (True, None))


if __name__ == "__main__":
    unittest.main()
