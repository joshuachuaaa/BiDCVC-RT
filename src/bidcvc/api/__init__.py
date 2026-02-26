"""Public API surface for BiDCVC-RT.

Scripts under `scripts/` must import only from `bidcvc.api.*`.
"""

from __future__ import annotations

from bidcvc.api.errors import BiDCVCError, BitstreamError, MissingDependencyError

__all__ = [
    "BiDCVCError",
    "BitstreamError",
    "MissingDependencyError",
]

