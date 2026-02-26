"""Timing utilities (stub)."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timer() -> Iterator[callable]:
    """Context manager yielding a callable that returns elapsed seconds."""

    start = time.perf_counter()

    def elapsed() -> float:
        return time.perf_counter() - start

    try:
        yield elapsed
    finally:
        pass

