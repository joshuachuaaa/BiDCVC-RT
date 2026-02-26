"""DCVC-RT adapter placeholder.

Do not vendor or modify DCVC under this module. The expected layout is:
  third_party/DCVC/  (git submodule or vendored snapshot)

This file intentionally avoids importing torch at module import time.
"""

from __future__ import annotations

from bidcvc.api.errors import MissingDependencyError


def load_vanilla_dcvc_rt(*_args, **_kwargs):
    """Load vanilla DCVC-RT implementation.

    TODO: Provide a real adapter once third_party/DCVC is present.
    """

    raise MissingDependencyError(
        "DCVC-RT code is missing. Add it under third_party/DCVC as a git submodule "
        "(see third_party/DCVC/README.md), then wire an adapter in "
        "bidcvc.models.dcvc_adapter.vanilla."
    )

