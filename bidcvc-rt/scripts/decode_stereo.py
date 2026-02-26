"""Decode a BiDCVC-RT StereoAU bitstream (stub CLI)."""

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
        prog="decode_stereo.py",
        description="Decode BiDCVC-RT StereoAU bitstreams (model TODO).",
    )
    p.add_argument("--input", type=Path, required=True, help="Input .bin path.")
    p.add_argument(
        "--inspect",
        action="store_true",
        help="Parse bitstream and print header + segment sizes.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _bootstrap_src_path()

    from bidcvc.api.codec import au_parse
    from bidcvc.api.errors import BitstreamError

    data = args.input.read_bytes()
    try:
        au = au_parse(data)
    except BitstreamError as e:
        print(f"BitstreamError: {e}", file=sys.stderr)
        return 2

    if args.inspect:
        print(f"sps_id={au.sps_id} qp={au.qp} version={au.version} nal_type={au.nal_type}")
        print(f"L.A={len(au.la)} bytes")
        print(f"R.A={len(au.ra)} bytes")
        print(f"L.B={len(au.lb)} bytes")
        print(f"R.B={len(au.rb)} bytes")
        return 0

    from bidcvc.api.codec import decode_stereo_au

    try:
        _ = decode_stereo_au(au)
    except NotImplementedError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

