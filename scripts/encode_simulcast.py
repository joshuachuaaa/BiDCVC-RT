"""Encode left/right independently (simulcast baseline) - stub CLI."""

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
        prog="encode_simulcast.py",
        description="Encode left/right independently as a simulcast baseline (TODO).",
    )
    p.add_argument("--left", type=Path, required=True, help="Path to left-view input.")
    p.add_argument("--right", type=Path, required=True, help="Path to right-view input.")
    p.add_argument("--output-dir", type=Path, required=True, help="Directory for outputs.")
    p.add_argument("--qp", type=int, default=22, help="Quantization parameter (opaque, 0-255).")
    return p


def main(argv: list[str] | None = None) -> int:
    _ = build_parser().parse_args(argv)
    _bootstrap_src_path()

    from bidcvc.api.baseline import get_dcvc_rt_baseline

    try:
        _ = get_dcvc_rt_baseline()
    except NotImplementedError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

