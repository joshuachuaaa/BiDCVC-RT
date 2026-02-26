"""Stereo SPS (Sequence Parameter Set) encode/decode.

This is a minimal, versioned contract for stream-level parameters.
"""

from __future__ import annotations

from dataclasses import dataclass

from bidcvc.api.errors import BitstreamError
from bidcvc.bitstream.constants import MAGIC_SPS, SPS_VERSION
from bidcvc.bitstream.framing import pack_u16, pack_u8, unpack_u16, unpack_u8
from bidcvc.bitstream.io import ByteReader


@dataclass(frozen=True)
class StereoSPS:
    """Minimal stereo SPS."""

    sps_id: int
    width: int
    height: int
    version: int = SPS_VERSION


def encode_sps(sps: StereoSPS) -> bytes:
    """Encode SPS to bytes."""

    if sps.version != SPS_VERSION:
        raise BitstreamError(f"unsupported SPS version: {sps.version}")
    if not (0 <= sps.sps_id <= 0xFF):
        raise BitstreamError(f"sps_id out of range: {sps.sps_id}")
    if not (1 <= sps.width <= 0xFFFF):
        raise BitstreamError(f"width out of range: {sps.width}")
    if not (1 <= sps.height <= 0xFFFF):
        raise BitstreamError(f"height out of range: {sps.height}")

    return b"".join(
        [
            MAGIC_SPS,
            pack_u8(sps.version),
            pack_u8(sps.sps_id),
            pack_u16(sps.width),
            pack_u16(sps.height),
        ]
    )


def decode_sps(data: bytes) -> StereoSPS:
    """Decode SPS from bytes."""

    r = ByteReader(data)
    magic = r.read_exact(4)
    if magic != MAGIC_SPS:
        raise BitstreamError(f"bad SPS magic: {magic!r}")
    version = unpack_u8(r.read_exact(1))
    if version != SPS_VERSION:
        raise BitstreamError(f"unsupported SPS version: {version}")
    sps_id = unpack_u8(r.read_exact(1))
    width = unpack_u16(r.read_exact(2))
    height = unpack_u16(r.read_exact(2))
    if r.remaining() != 0:
        raise BitstreamError(f"trailing bytes after SPS: {r.remaining()}")
    return StereoSPS(sps_id=sps_id, width=width, height=height, version=version)

