"""A tiny subset of `pytest`.

This is **not** the upstream pytest project.

It exists only so this repository can run a minimal test suite in restricted
environments where external dependencies cannot be fetched.

Supported API:
- `pytest.raises(ExpectedException)`
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeVar


E = TypeVar("E", bound=BaseException)


@dataclass
class _ExcInfo(Generic[E]):
    type: Type[E]
    value: E


class _Raises(Generic[E]):
    def __init__(self, expected: Type[E]) -> None:
        self._expected = expected
        self.excinfo: Optional[_ExcInfo[E]] = None

    def __enter__(self) -> "_Raises[E]":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc is None:
            raise AssertionError(f"DID NOT RAISE {self._expected.__name__}")
        if not isinstance(exc, self._expected):
            return False
        self.excinfo = _ExcInfo(type=exc.__class__, value=exc)
        return True


def raises(expected_exception: Type[E]) -> _Raises[E]:
    return _Raises(expected_exception)

