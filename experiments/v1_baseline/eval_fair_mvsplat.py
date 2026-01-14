#!/usr/bin/env python3
"""Deprecated entrypoint (kept for backward compatibility).

Use `experiments/v1_renderer/eval_fair_mvsplat.py` instead.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    script = Path(__file__).resolve().parents[1] / "v1_renderer" / "eval_fair_mvsplat.py"
    runpy.run_path(str(script), run_name="__main__")

