"""Stereo Access Unit (AU) encode/decode.

AU(t) = [L.A][R.A][L.B][R.B]
where Stage A = (z + pass0 y) and Stage B = (pass1 y).

Wire format (v1):
  magic[4] + version[u8] + nal_type[u8] + sps_id[u8] + qp[u8]
  + len(L.A)[u32] + bytes
  + len(R.A)[u32] + bytes
  + len(L.B)[u32] + bytes
  + len(R.B)[u32] + bytes
"""

from __future__ import annotations

from dataclasses import dataclass

from bidcvc.api.errors import BitstreamError
from bidcvc.bitstream.constants import (
    AU_VERSION,
    MAGIC_AU,
    NAL_TYPE_STEREO_AU,
)
from bidcvc.bitstream.framing import pack_u32, pack_u8, unpack_u32, unpack_u8
from bidcvc.bitstream.io import ByteReader


@dataclass(frozen=True)
class StereoAU:
    """Stereo Access Unit payload."""

    sps_id: int
    qp: int
    la: bytes
    ra: bytes
    lb: bytes
    rb: bytes
    version: int = AU_VERSION
    nal_type: int = NAL_TYPE_STEREO_AU


def encode_au(au: StereoAU) -> bytes:
    if au.version != AU_VERSION:
        raise BitstreamError(f"unsupported AU version: {au.version}")
    if au.nal_type != NAL_TYPE_STEREO_AU:
        raise BitstreamError(f"unsupported nal_type for StereoAU: {au.nal_type}")
    if not (0 <= au.sps_id <= 0xFF):
        raise BitstreamError(f"sps_id out of range: {au.sps_id}")
    if not (0 <= au.qp <= 0xFF):
        raise BitstreamError(f"qp out of range: {au.qp}")

    parts = [
        MAGIC_AU,
        pack_u8(au.version),
        pack_u8(au.nal_type),
        pack_u8(au.sps_id),
        pack_u8(au.qp),
    ]
    for seg in (au.la, au.ra, au.lb, au.rb):
        if not isinstance(seg, (bytes, bytearray, memoryview)):
            raise BitstreamError(f"segment must be bytes-like, got {type(seg).__name__}")
        seg_b = bytes(seg)
        parts.append(pack_u32(len(seg_b)))
        parts.append(seg_b)
    return b"".join(parts)


def decode_au(data: bytes) -> StereoAU:
    r = ByteReader(data)
    magic = r.read_exact(4)
    if magic != MAGIC_AU:
        raise BitstreamError(f"bad AU magic: {magic!r}")
    version = unpack_u8(r.read_exact(1))
    if version != AU_VERSION:
        raise BitstreamError(f"unsupported AU version: {version}")
    nal_type = unpack_u8(r.read_exact(1))
    if nal_type != NAL_TYPE_STEREO_AU:
        raise BitstreamError(f"unexpected nal_type for StereoAU: {nal_type}")
    sps_id = unpack_u8(r.read_exact(1))
    qp = unpack_u8(r.read_exact(1))

    segs: list[bytes] = []
    for seg_name in ("L.A", "R.A", "L.B", "R.B"):
        seg_len = unpack_u32(r.read_exact(4))
        if seg_len > r.remaining():
            raise BitstreamError(
                f"truncated AU while reading {seg_name}: need {seg_len} bytes, have {r.remaining()}"
            )
        segs.append(r.read_exact(seg_len))

    if r.remaining() != 0:
        raise BitstreamError(f"trailing bytes after AU: {r.remaining()}")

    la, ra, lb, rb = segs
    return StereoAU(
        sps_id=sps_id,
        qp=qp,
        la=la,
        ra=ra,
        lb=lb,
        rb=rb,
        version=version,
        nal_type=nal_type,
    )

