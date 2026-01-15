#!/usr/bin/env bash
set -euo pipefail

# Convenience wrapper: plot baseline (vanilla + ELIC->MVSplat) vs E2E.
#
# Usage:
#   bash scripts/plot_baseline_vs_e2e.sh \
#     --baseline outputs/v1_baseline/results/fair_rd.csv \
#     --e2e outputs/v1_e2e/results/fair_rd.csv \
#     --outdir outputs/plots/baseline_vs_e2e

baseline="outputs/v1_baseline/results/fair_rd.csv"
e2e="outputs/v1_e2e/results/fair_rd.csv"
outdir="outputs/plots/baseline_vs_e2e"
figsize=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --baseline) baseline="$2"; shift 2 ;;
    --e2e) e2e="$2"; shift 2 ;;
    --outdir) outdir="$2"; shift 2 ;;
    --figsize) figsize=("$2" "$3"); shift 3 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

bash scripts/plot_fair_rd.sh \
  --input "$baseline" "$e2e" \
  --outdir "$outdir" \
  --all-metrics \
  --title "RE10K fixed-index (2ctx→3tgt)" \
  --note "bpp = avg over 2 context bitstreams" \
  ${figsize:+--figsize "${figsize[0]}" "${figsize[1]}"}
