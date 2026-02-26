from __future__ import annotations

import pytest

from bidcvc.api.errors import BitstreamError
from bidcvc.bitstream.sps import StereoSPS, decode_sps, encode_sps


def test_sps_roundtrip_bytes() -> None:
    sps = StereoSPS(sps_id=7, width=640, height=480)
    b = encode_sps(sps)
    parsed = decode_sps(b)
    assert parsed == sps
    assert encode_sps(parsed) == b


def test_sps_truncated_raises() -> None:
    b = encode_sps(StereoSPS(sps_id=1, width=16, height=16))
    for cut in range(len(b)):
        with pytest.raises(BitstreamError):
            decode_sps(b[:cut])


def test_sps_bad_magic_raises() -> None:
    b = encode_sps(StereoSPS(sps_id=1, width=16, height=16))
    with pytest.raises(BitstreamError):
        decode_sps(b"XXXX" + b[4:])

