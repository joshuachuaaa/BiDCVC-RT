"""Minimal PEP 517/660 build backend (stdlib-only).

Why this exists:
- The execution environment for this scaffold may be offline and lack build
  tooling inside isolated build envs.
- Keeping the backend in-repo avoids external build dependencies while still
  supporting `pip install -e ".[dev]"`.

This backend supports:
- Wheel builds (`build_wheel`)
- Editable installs (`build_editable`) via a `.pth` that points at `src/`.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import os
import zipfile
from pathlib import Path
from typing import Any

try:
    import tomllib  # py>=3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[assignment]


def _root() -> Path:
    return Path(__file__).resolve().parent


def _load_pyproject() -> dict[str, Any]:
    data = (_root() / "pyproject.toml").read_bytes()
    return tomllib.loads(data.decode("utf-8"))


def _project() -> dict[str, Any]:
    return _load_pyproject().get("project", {})


def _dist_name_for_wheel(name: str) -> str:
    # Wheel filenames/dist-info use a normalized name (hyphens become underscores).
    return name.replace("-", "_")


def _metadata_text(for_extra: str | None = None) -> str:
    proj = _project()
    name = str(proj.get("name", "UNKNOWN"))
    version = str(proj.get("version", "0.0.0"))
    summary = str(proj.get("description", ""))
    requires_python = proj.get("requires-python")

    lines: list[str] = [
        "Metadata-Version: 2.1",
        f"Name: {name}",
        f"Version: {version}",
    ]
    if summary:
        lines.append(f"Summary: {summary}")
    if requires_python:
        lines.append(f"Requires-Python: {requires_python}")
    lines.append("License-File: LICENSE")

    for req in proj.get("dependencies", []) or []:
        lines.append(f"Requires-Dist: {req}")

    optional = proj.get("optional-dependencies", {}) or {}
    for extra, reqs in optional.items():
        lines.append(f"Provides-Extra: {extra}")
        for req in reqs or []:
            # Resolve local relative file: URLs relative to the project root so
            # `pip install -e ".[dev]"` works in offline environments.
            req_s = str(req)
            if " @ file:" in req_s:
                name_part, url_part = req_s.split(" @ file:", 1)
                abs_path = (_root() / url_part).resolve()
                req_s = f"{name_part} @ {abs_path.as_uri()}"
            if ";" in req_s:
                base, marker = req_s.split(";", 1)
                marker = marker.strip()
                combined = f"({marker}) and (extra == '{extra}')"
                lines.append(f"Requires-Dist: {base.strip()} ; {combined}")
            else:
                lines.append(f"Requires-Dist: {req_s} ; extra == '{extra}'")

    if for_extra is not None:
        lines.append(f"Provides-Extra: {for_extra}")

    return "\n".join(lines) + "\n"


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: bidcvc_build_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def get_requires_for_build_wheel(config_settings: dict[str, Any] | None = None) -> list[str]:
    return []


def get_requires_for_build_editable(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, Any] | None = None,
) -> str:
    return _prepare_metadata(metadata_directory)


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: dict[str, Any] | None = None,
) -> str:
    return _prepare_metadata(metadata_directory)


def _prepare_metadata(metadata_directory: str) -> str:
    proj = _project()
    name = _dist_name_for_wheel(str(proj.get("name", "UNKNOWN")))
    version = str(proj.get("version", "0.0.0"))
    dist_info = f"{name}-{version}.dist-info"
    out_dir = Path(metadata_directory) / dist_info
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (out_dir / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    return dist_info


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel(wheel_directory=wheel_directory, editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel(wheel_directory=wheel_directory, editable=True)


def _hash_bytes(data: bytes) -> tuple[str, int]:
    digest = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"sha256={b64}", len(data)


def _build_wheel(*, wheel_directory: str, editable: bool) -> str:
    proj = _project()
    dist = _dist_name_for_wheel(str(proj.get("name", "UNKNOWN")))
    version = str(proj.get("version", "0.0.0"))
    wheel_name = f"{dist}-{version}-py3-none-any.whl"

    dist_info = f"{dist}-{version}.dist-info"
    files: dict[str, bytes] = {}

    # Metadata
    files[f"{dist_info}/METADATA"] = _metadata_text().encode("utf-8")
    files[f"{dist_info}/WHEEL"] = _wheel_text().encode("utf-8")

    # Editable wiring via .pth pointing at src/
    if editable:
        src_path = (_root() / "src").resolve()
        files[f"{dist}.pth"] = (src_path.as_posix() + os.linesep).encode("utf-8")
    else:
        src_root = _root() / "src"
        for path in src_root.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(src_root).as_posix()
            files[rel] = path.read_bytes()

    # RECORD (filled last)
    record_path = f"{dist_info}/RECORD"
    record_rows: list[list[str]] = []
    for path, data in files.items():
        h, size = _hash_bytes(data)
        record_rows.append([path, h, str(size)])
    record_rows.append([record_path, "", ""])
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerows(record_rows)
    record_text = buf.getvalue()
    files[record_path] = record_text.encode("utf-8")

    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)
    wheel_path = wheel_dir / wheel_name

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files.keys()):
            zf.writestr(path, files[path])

    return wheel_name
