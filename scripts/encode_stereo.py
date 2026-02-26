"""Encode a stereo video into BiDCVC-RT StereoAU bitstreams (stub CLI)."""

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
        prog="encode_stereo.py",
        description="Encode stereo inputs into BiDCVC-RT StereoAU bitstreams (model TODO).",
    )
    p.add_argument("--left", type=Path, required=True, help="Path to left-view input.")
    p.add_argument("--right", type=Path, required=True, help="Path to right-view input.")
    p.add_argument("--output", type=Path, required=True, help="Output .bin path.")
    p.add_argument("--qp", type=int, default=22, help="Quantization parameter (opaque, 0-255).")
    p.add_argument("--sps-id", type=int, default=0, help="SPS id to embed in the AU header.")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse args and exit without encoding.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("OK (dry-run): CLI wiring is present; model encode is TODO.")
        return 0

    _bootstrap_src_path()

    from bidcvc.api.codec import encode_stereo_frame

    try:
        _ = encode_stereo_frame(
            left_path=args.left,
            right_path=args.right,
            output_path=args.output,
            qp=args.qp,
            sps_id=args.sps_id,
        )
    except NotImplementedError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

