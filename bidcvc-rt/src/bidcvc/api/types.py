"""Shared API datatypes.

This module is a placeholder; concrete tensor/array types are intentionally not
locked down yet to keep core packaging lightweight.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class StereoFrame:
    """Raw stereo frame container.

    TODO: Define canonical representation (e.g., numpy arrays or torch tensors).
    """

    left: Any
    right: Any


@dataclass(frozen=True)
class EncodedStereoAU:
    """Opaque encoded access unit bytes with minimal metadata."""

    sps_id: int
    qp: int
    au_bytes: bytes
    pts: Optional[int] = None

