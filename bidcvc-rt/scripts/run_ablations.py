"""Run ablation sweeps (stub CLI)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_ablations.py",
        description="Run ablation sweeps for BiDCVC-RT (TODO).",
    )
    p.add_argument("--config", type=Path, required=True, help="Training/eval config YAML.")
    p.add_argument("--output-dir", type=Path, default=Path("runs/ablations"))
    return p


def main(argv: list[str] | None = None) -> int:
    _ = build_parser().parse_args(argv)
    _bootstrap_src_path()

    from bidcvc.api.codec import list_ablations

    # NOTE: This script intentionally does not run any models yet.
    print("Known ablations:")
    for name in list_ablations():
        print(f"- {name}")
    print("TODO: wire actual ablation runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
