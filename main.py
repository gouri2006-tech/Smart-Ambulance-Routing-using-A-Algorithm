"""Entry point.

    python main.py                     open the graphical visualiser
    python main.py --cli               run in the terminal (random maze demo)
    python main.py --cli --map examples/map_obstacles.txt --compare
    python main.py --cli --diagonal --heuristic octile --compare
"""
import argparse
import sys

from astarlab.algorithms import ALGORITHMS, HEURISTICS


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="A* path-finding project")
    p.add_argument("--cli", action="store_true", help="use the terminal instead of the GUI")
    p.add_argument("--map", help="text map file (# wall, ~ mud, S start, G goal, . free)")
    p.add_argument("--algorithm", choices=list(ALGORITHMS), default="astar")
    p.add_argument("--heuristic", choices=list(HEURISTICS), default="manhattan")
    p.add_argument("--diagonal", action="store_true", help="allow 8-direction movement")
    p.add_argument("--compare", action="store_true", help="print an algorithm comparison table")
    p.add_argument("--seed", type=int, default=7, help="maze seed for the CLI demo")
    p.add_argument("--rows", type=int, default=21)
    p.add_argument("--cols", type=int, default=41)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    use_cli = args.cli
    if not use_cli:
        try:
            import tkinter  # noqa: F401
        except ImportError:
            print("tkinter is not installed, so the GUI cannot start - running the terminal "
                  "version instead.\n(Linux: sudo apt install python3-tk)\n")
            use_cli = True

    if use_cli:
        from astarlab.cli import run_cli
        return run_cli(args.map, args.algorithm, args.heuristic, args.diagonal,
                       args.seed, args.rows, args.cols, args.compare)

    from astarlab.gui import launch
    launch()
    return 0


if __name__ == "__main__":
    sys.exit(main())
