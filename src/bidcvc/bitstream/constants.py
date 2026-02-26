"""Bitstream constants for BiDCVC-RT.

The bitstream is a first-class, versioned contract.
"""

from __future__ import annotations

MAGIC_SPS = b"BSPS"
MAGIC_AU = b"BAU0"

SPS_VERSION = 1
AU_VERSION = 1

NAL_TYPE_STEREO_AU = 1

U8_MAX = 0xFF
U16_MAX = 0xFFFF
U32_MAX = 0xFFFFFFFF

