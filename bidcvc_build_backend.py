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

_CACHED_PROJECT: dict[str, Any] | None = None

def _root() -> Path:
    return Path(__file__).resolve().parent


def _project() -> dict[str, Any]:
    global _CACHED_PROJECT
    if _CACHED_PROJECT is None:
        _CACHED_PROJECT = _parse_pyproject_project((_root() / "pyproject.toml").read_text(encoding="utf-8"))
    return _CACHED_PROJECT


def _parse_pyproject_project(text: str) -> dict[str, Any]:
    """Parse the `[project]` table from `pyproject.toml` without external deps.

    We intentionally support only a tiny TOML subset required by this scaffold:
    - `[project]` string keys: name/version/description/requires-python
    - `[project]` arrays of strings: dependencies
    - `[project.optional-dependencies]` arrays of strings

    This keeps the build backend stdlib-only on Python 3.10.
    """

    project: dict[str, Any] = {}
    optional_deps: dict[str, list[str]] = {}

    section: str | None = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        # NOTE: This is a minimal parser; we strip comments naively.
        line = raw.split("#", 1)[0].strip()
        i += 1
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]").strip()
            continue

        if "=" not in line or section is None:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value.startswith("[") and not value.endswith("]"):
            # Multi-line array.
            chunks = [value]
            while i < len(lines):
                nxt = lines[i].split("#", 1)[0].strip()
                i += 1
                if not nxt:
                    continue
                chunks.append(nxt)
                if "]" in nxt:
                    break
            value = " ".join(chunks)

        if section == "project":
            if key not in {"name", "version", "description", "requires-python", "dependencies"}:
                continue
            project[key] = _parse_toml_value(value)
        elif section == "project.optional-dependencies":
            parsed = _parse_toml_value(value)
            if not isinstance(parsed, list):
                raise ValueError(f"expected array for optional-dependency {key}, got: {value!r}")
            optional_deps[key] = [str(x) for x in parsed]

    if optional_deps:
        project["optional-dependencies"] = optional_deps
    return project


def _parse_toml_value(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return _parse_toml_array(value)
    if value.startswith('"') and value.endswith('"'):
        return _parse_toml_string(value)
    if value.startswith("'") and value.endswith("'"):
        return _parse_toml_string(value)
    # Fallback: keep raw string.
    return value


def _parse_toml_string(token: str) -> str:
    # Minimal string unquoting; good enough for this scaffold's pyproject.
    quote = token[0]
    if not token.endswith(quote):
        raise ValueError(f"unterminated string: {token!r}")
    inner = token[1:-1]
    if quote == '"':
        inner = inner.replace('\\"', '"').replace("\\\\", "\\")
    else:
        inner = inner.replace("\\'", "'").replace("\\\\", "\\")
    return inner


def _parse_toml_array(token: str) -> list[Any]:
    token = token.strip()
    if token == "[]":
        return []
    if not (token.startswith("[") and token.endswith("]")):
        raise ValueError(f"invalid array token: {token!r}")
    body = token[1:-1]

    items: list[str] = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch in " \t\r\n,":
            i += 1
            continue
        if ch not in ("'", '"'):
            raise ValueError(f"unexpected array token at {i}: {body[i:i+20]!r}")
        quote = ch
        i += 1
        start = i
        out = []
        while i < len(body):
            c = body[i]
            if c == "\\" and i + 1 < len(body):
                out.append(body[start:i])
                out.append(body[i : i + 2])
                i += 2
                start = i
                continue
            if c == quote:
                out.append(body[start:i])
                i += 1
                break
            i += 1
        else:
            raise ValueError("unterminated string in array")
        raw_str = "".join(out)
        items.append(_parse_toml_string(quote + raw_str + quote))
    return items


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
            req_s = str(req).strip()
            marker: str | None = None
            if ";" in req_s:
                base, marker = req_s.split(";", 1)
                req_s = base.strip()
                marker = marker.strip()

            if " @ file:" in req_s:
                name_part, url_part = req_s.split(" @ file:", 1)
                abs_path = (_root() / url_part.strip()).resolve()
                req_s = f"{name_part.strip()} @ {abs_path.as_uri()}"

            extra_marker = f"extra == '{extra}'"
            combined_marker = f"({marker}) and ({extra_marker})" if marker else extra_marker
            lines.append(f"Requires-Dist: {req_s} ; {combined_marker}")

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
