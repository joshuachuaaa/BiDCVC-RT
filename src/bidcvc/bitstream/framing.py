"""Primitive framing helpers (struct packing / unpacking)."""

from __future__ import annotations

import struct

from bidcvc.api.errors import BitstreamError


def pack_u8(v: int) -> bytes:
    if not (0 <= v <= 0xFF):
        raise BitstreamError(f"u8 out of range: {v}")
    return struct.pack(">B", v)


def pack_u16(v: int) -> bytes:
    if not (0 <= v <= 0xFFFF):
        raise BitstreamError(f"u16 out of range: {v}")
    return struct.pack(">H", v)


def pack_u32(v: int) -> bytes:
    if not (0 <= v <= 0xFFFFFFFF):
        raise BitstreamError(f"u32 out of range: {v}")
    return struct.pack(">I", v)


def unpack_u8(b: bytes) -> int:
    if len(b) != 1:
        raise BitstreamError(f"expected 1 byte for u8, got {len(b)}")
    return struct.unpack(">B", b)[0]


def unpack_u16(b: bytes) -> int:
    if len(b) != 2:
        raise BitstreamError(f"expected 2 bytes for u16, got {len(b)}")
    return struct.unpack(">H", b)[0]


def unpack_u32(b: bytes) -> int:
    if len(b) != 4:
        raise BitstreamError(f"expected 4 bytes for u32, got {len(b)}")
    return struct.unpack(">I", b)[0]

