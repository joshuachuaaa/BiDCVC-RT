"""Small byte IO helpers (standard library only)."""

from __future__ import annotations

from dataclasses import dataclass

from bidcvc.api.errors import BitstreamError


@dataclass
class ByteReader:
    data: bytes
    offset: int = 0

    def remaining(self) -> int:
        return len(self.data) - self.offset

    def read_exact(self, n: int) -> bytes:
        if n < 0:
            raise BitstreamError(f"invalid read length: {n}")
        end = self.offset + n
        if end > len(self.data):
            raise BitstreamError(
                f"truncated input: need {n} bytes, have {self.remaining()}"
            )
        out = self.data[self.offset : end]
        self.offset = end
        return out

