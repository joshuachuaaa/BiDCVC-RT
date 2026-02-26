"""Minimal stdlib-only wheel builder for the local `pytest` stub."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import zipfile
from pathlib import Path
from typing import Any


def _root() -> Path:
    return Path(__file__).resolve().parent


def get_requires_for_build_wheel(config_settings: dict[str, Any] | None = None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, Any] | None = None,
) -> str:
    dist_info = "pytest-0.0.0.dist-info"
    out = Path(metadata_directory) / dist_info
    out.mkdir(parents=True, exist_ok=True)
    (out / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (out / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    return dist_info


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    wheel_name = "pytest-0.0.0-py3-none-any.whl"
    dist_info = "pytest-0.0.0.dist-info"

    files: dict[str, bytes] = {
        f"{dist_info}/METADATA": _metadata_text().encode("utf-8"),
        f"{dist_info}/WHEEL": _wheel_text().encode("utf-8"),
    }

    for path in (_root() / "pytest").rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(_root()).as_posix()
        files[rel] = path.read_bytes()

    record_path = f"{dist_info}/RECORD"
    record_rows: list[list[str]] = []
    for path, data in files.items():
        h, size = _hash_bytes(data)
        record_rows.append([path, h, str(size)])
    record_rows.append([record_path, "", ""])
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerows(record_rows)
    files[record_path] = buf.getvalue().encode("utf-8")

    out_dir = Path(wheel_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    wheel_path = out_dir / wheel_name
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files.keys()):
            zf.writestr(path, files[path])
    return wheel_name


def _metadata_text() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            "Name: pytest",
            "Version: 0.0.0",
            "Summary: Minimal pytest stub used for offline scaffolds.",
            "Requires-Python: >=3.10",
            "",
        ]
    )


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: pytest_build_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _hash_bytes(data: bytes) -> tuple[str, int]:
    digest = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"sha256={b64}", len(data)

