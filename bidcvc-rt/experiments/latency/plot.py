"""Plot latency results (stub)."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Plot latency results (TODO).")
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("runs/latency/plot.png"))
    return p


def main(argv: list[str] | None = None) -> int:
    _ = build_parser().parse_args(argv)
    raise NotImplementedError("Plotting is TODO.")


if __name__ == "__main__":
    raise SystemExit(main())

