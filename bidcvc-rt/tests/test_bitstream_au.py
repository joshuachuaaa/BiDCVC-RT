from __future__ import annotations

import struct

import pytest

from bidcvc.api.errors import BitstreamError
from bidcvc.bitstream.au import StereoAU, decode_au, encode_au


def test_au_roundtrip_bytes() -> None:
    au = StereoAU(
        sps_id=3,
        qp=22,
        la=b"\x00\x01",
        ra=b"",
        lb=b"abc",
        rb=b"\xff" * 5,
    )
    b = encode_au(au)
    parsed = decode_au(b)
    assert parsed == au
    assert encode_au(parsed) == b


def test_au_truncated_raises() -> None:
    b = encode_au(
        StereoAU(
            sps_id=0,
            qp=0,
            la=b"a",
            ra=b"b",
            lb=b"c",
            rb=b"d",
        )
    )
    for cut in range(len(b)):
        with pytest.raises(BitstreamError):
            decode_au(b[:cut])


def test_au_bad_magic_raises() -> None:
    b = encode_au(StereoAU(sps_id=1, qp=1, la=b"", ra=b"", lb=b"", rb=b""))
    with pytest.raises(BitstreamError):
        decode_au(b"XXXX" + b[4:])


def test_au_bad_nal_type_raises() -> None:
    b = bytearray(
        encode_au(StereoAU(sps_id=1, qp=1, la=b"", ra=b"", lb=b"", rb=b""))
    )
    b[5] = 0  # nal_type
    with pytest.raises(BitstreamError):
        decode_au(bytes(b))


def test_au_length_overflow_raises() -> None:
    au = StereoAU(sps_id=1, qp=1, la=b"hi", ra=b"", lb=b"", rb=b"")
    b = encode_au(au)
    # Overwrite the first segment length to exceed remaining bytes.
    bad = b[:8] + struct.pack(">I", 9999) + b[12:]
    with pytest.raises(BitstreamError):
        decode_au(bad)

