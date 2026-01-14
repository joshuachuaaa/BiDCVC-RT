# Outputs directory

This folder is for run artifacts (logs, metrics CSVs, rendered images) and is ignored by git.

## Canonical layout (conference-grade)

Keep *all* non-source artifacts under `outputs/` so the repo stays clean and reproducible:

- Baselines (vanilla MVSplat + vanilla ELIC→MVSplat):
  - `outputs/v1_baseline/results/fair_rd.csv`
  - `outputs/v1_baseline/results/plots/`
- End-to-end (ELIC↔MVSplat):
  - `outputs/v1_e2e/results/fair_rd.csv`
  - `outputs/v1_e2e/results/fast_eval.csv` (cheap selection; bpp is an estimate)
  - `outputs/v1_e2e/*.png` (training/curve plots)

Avoid writing metrics/plots under `experiments/**/results/` or `experiments/**/compressed/`.
