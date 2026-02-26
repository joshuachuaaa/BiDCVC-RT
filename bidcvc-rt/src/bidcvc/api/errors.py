"""Error types for BiDCVC-RT."""

from __future__ import annotations


class BiDCVCError(Exception):
    """Base class for BiDCVC-RT errors."""


class BitstreamError(BiDCVCError):
    """Raised when bitstream parsing/validation fails."""


class MissingDependencyError(BiDCVCError):
    """Raised when an optional dependency or third_party code is missing."""

