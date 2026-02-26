# Reproducibility (stub)

## Environment

- Python 3.10
- Minimal dev deps: `pytest`

## Outputs

All generated outputs (bitstreams, metrics, plots, checkpoints) must go under:
- `runs/`
- or `outputs/`

These paths are gitignored.

## Seeding

`bidcvc.utils.seed.seed_everything()` currently seeds Python RNGs only (torch/numpy TODO).

