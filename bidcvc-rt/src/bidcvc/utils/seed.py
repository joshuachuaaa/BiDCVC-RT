"""Reproducibility seeding utilities (stub)."""

from __future__ import annotations

import os
import random


def seed_everything(seed: int) -> None:
    """Seed Python RNGs (and optionally torch/numpy in the future)."""

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

