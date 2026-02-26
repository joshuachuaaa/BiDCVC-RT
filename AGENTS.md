# BiDCVC-RT (codec-only) — Agent Instructions

Scope (non-negotiable)
- This repository is ONLY for stereo video compression research/engineering (BiDCVC-RT) and codec baselines.
- DO NOT add MVSplat, 3D rendering, telepresence systems, WebRTC, networking stacks, or any downstream tasks.
- DO NOT add "optional" downstream folders or dependencies. Strict codec-only.

Language / tooling
- Python 3.10.
- Use pytest only for now (no ruff/black/mypy unless explicitly asked).
- Use src-layout packaging (src/bidcvc/...).

Architecture contracts
- Bitstream is a first-class contract. Implement a versioned Stereo Access Unit (AU) format:
  AU(t) = [L.A][R.A][L.B][R.B]
  where Stage A = (z + pass0 y) and Stage B = (pass1 y).
- src/bidcvc/bitstream must be torch-free and as dependency-free as practical.
- scripts/ must import ONLY from src/bidcvc/api (no direct imports from models/*).
- Keep vanilla DCVC-RT code isolated under third_party/DCVC (submodule or vendored snapshot).
  Do not modify third_party/DCVC in this task; use adapters under src/bidcvc/models/dcvc_adapter.

Reproducibility / publishability
- Add docs stubs: docs/architecture.md, docs/bitstream_format.md, docs/reproducibility.md.
- Add CITATION.cff, LICENSE, README.md.
- Add configs/ for codec/eval/training (YAML).
- All generated outputs go under runs/ and must be gitignored.

Acceptance criteria (must pass)
- `python -m pip install -e ".[dev]"` works on Python 3.10.
- `python -m pytest` passes.
- `python scripts/encode_stereo.py --help` works (CLI can be stubbed).
- `python scripts/decode_stereo.py --help` works (CLI can be stubbed).

Implementation guidance
- Prefer small, testable modules.
- Avoid importing torch at import time in modules that should be lightweight.
  Use TYPE_CHECKING or lazy imports if needed.
