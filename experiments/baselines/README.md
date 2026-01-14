# Baselines (conference-grade)

This folder contains **baseline evaluation entrypoints** for the thesis:

1) **Vanilla MVSplat** (no compression).
2) **Vanilla ELIC → MVSplat** (compress only the 2 context views, decode to RGB, then run MVSplat).

All baselines use the same **fixed evaluation protocol**:
- split: `dataset/re10k/test`
- index: `assets/indices/re10k/evaluation_index_re10k.json` (2 context → 3 target)

## Where results are written
By default:
- CSV: `outputs/baselines/re10k_fixed/fair_rd.csv`
- plots: `outputs/baselines/re10k_fixed/plots/`

## Baseline artifacts (ELIC reconstructions)
This repo supports evaluating from **precomputed** compressed context reconstructions that follow the
repo-native layout:

```text
<compressed_root>/lambda_<λ>/
  manifest.csv
  recon/<scene>/<frame>.png
```

If your precomputed artifacts live elsewhere, pass `--compressed-base` to `eval_baselines.py` below.

## Run baseline evaluation

```bash
python experiments/baselines/eval_baselines.py \
  --tag-prefix v1_lambda_ \
  --compressed-base outputs/baseline_ELIC_crop256/compressed \
  --out-csv outputs/baselines/re10k_fixed/fair_rd.csv \
  --device cuda
```

## Plot baseline vs E2E

```bash
bash scripts/plot_fair_rd.sh \
  --input outputs/baselines/re10k_fixed/fair_rd.csv outputs/v1_e2e/results/fair_rd.csv \
  --outdir outputs/baselines/re10k_fixed/plots \
  --title "RE10K fixed-index (2ctx→3tgt)" \
  --note "bpp = avg over 2 context bitstreams"
```

