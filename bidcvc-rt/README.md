# BiDCVC-RT

BiDCVC-RT is a **codec-only** research scaffold for bidirectional stereo video compression, built as a stereo extension around DCVC-RT baselines.

## Status

This repository currently provides:
- A strict, versioned **bitstream contract** (Stereo SPS + Stereo Access Unit).
- Thin CLI entrypoints under `scripts/` (model wiring is TODO).

The actual neural codec logic (DCVC-RT integration, stereo priors, entropy models) is stubbed and intentionally incomplete.

## Quickstart

From `bidcvc-rt/`:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python scripts/encode_stereo.py --help
python scripts/decode_stereo.py --help
```

## Layout

- `src/bidcvc/api/`: stable API surface for scripts and experiments.
- `src/bidcvc/bitstream/`: torch-free bitstream codec contract.
- `third_party/DCVC/`: placeholder for adding vanilla DCVC-RT as a git submodule.
