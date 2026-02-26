"""Run latency experiment (stub)."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run latency experiment (TODO).")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("runs/latency"))
    return p


def main(argv: list[str] | None = None) -> int:
    _ = build_parser().parse_args(argv)
    raise NotImplementedError("Latency experiment is TODO.")


if __name__ == "__main__":
    raise SystemExit(main())

