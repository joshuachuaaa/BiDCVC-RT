"""Minimal `python -m pytest` runner.

Discovers `tests/test_*.py` and executes top-level functions named `test_*`.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
from pathlib import Path
from types import ModuleType


def _bootstrap_path(repo_root: Path) -> None:
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _discover(repo_root: Path) -> list[Path]:
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return []
    return sorted(tests_dir.rglob("test_*.py"))


def _import_file(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_module_tests(mod: ModuleType) -> int:
    failures = 0
    for name in dir(mod):
        if not name.startswith("test_"):
            continue
        fn = getattr(mod, name)
        if not callable(fn):
            continue
        try:
            fn()
        except Exception:  # noqa: BLE001
            failures += 1
            print(f"FAILED: {mod.__name__}.{name}", file=sys.stderr)
            traceback.print_exc()
    return failures


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--version", action="store_true", help="Print version and exit.")
    _ = p.parse_args(argv)
    if _.version:
        print("pytest-stub 0.0.0")
        return 0

    repo_root = Path.cwd()
    _bootstrap_path(repo_root)

    test_files = _discover(repo_root)
    if not test_files:
        print("No tests found.")
        return 5

    failures = 0
    for i, path in enumerate(test_files):
        mod = _import_file(path, module_name=f"_pytest_stub_test_{i}")
        failures += _run_module_tests(mod)

    if failures:
        print(f"{failures} test(s) failed.", file=sys.stderr)
        return 1
    print(f"{len(test_files)} file(s) collected, all tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

