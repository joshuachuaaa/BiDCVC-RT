# Bitstream format (v1)

## Goals

- Versioned, deterministic serialization.
- Robust validation with clear errors.
- Torch-free implementation (`bidcvc.bitstream`).

## Stereo SPS

File/packet format (v1):

- `magic` (4 bytes): `b"BSPS"`
- `version` (u8): `1`
- `sps_id` (u8)
- `width` (u16, big-endian)
- `height` (u16, big-endian)

Implemented in `bidcvc.bitstream.sps`.

## Stereo Access Unit (StereoAU)

Access Unit definition:

`AU(t) = [L.A][R.A][L.B][R.B]`

Wire format (v1):

- `magic` (4 bytes): `b"BAU0"`
- `version` (u8): `1`
- `nal_type` (u8): `1` (StereoAU)
- `sps_id` (u8)
- `qp` (u8)
- `L.A_len` (u32, big-endian) + `L.A` bytes
- `R.A_len` (u32, big-endian) + `R.A` bytes
- `L.B_len` (u32, big-endian) + `L.B` bytes
- `R.B_len` (u32, big-endian) + `R.B` bytes

Implemented in `bidcvc.bitstream.au`.

## Validation behavior

- Bad magic/version/nal_type or truncated buffers raise `bidcvc.api.errors.BitstreamError`.
- Parsers are strict: trailing bytes after the structure are rejected.

