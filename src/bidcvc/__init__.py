"""BiDCVC-RT: codec-only stereo video compression research scaffold.

This package is intentionally lightweight at import time:
- No torch imports at module import time for optional components.
- Bitstream code remains torch-free and dependency-light.
"""

from __future__ import annotations

__all__ = ["api", "bitstream"]

__version__ = "0.0.0"

