"""Evaluate latency (stub CLI)."""

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
        prog="eval_latency.py",
        description="Run latency evaluation (TODO).",
    )
    p.add_argument("--config", type=Path, required=True, help="Eval config YAML.")
    p.add_argument(
        "--output-dir", type=Path, default=Path("runs/latency"), help="Output directory."
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _bootstrap_src_path()

    from bidcvc.api.codec import run_latency_eval

    try:
        run_latency_eval(config_path=args.config, output_dir=args.output_dir)
    except NotImplementedError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
