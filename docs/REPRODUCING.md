# Reproducing results

This repo contains:
- **V1 baseline** (ELIC-compressed context frames → MVSplat).
- **V1 E2E** (end-to-end fine-tuning of ELIC + MVSplat with an RD objective).

- V1 baseline: `experiments/v1_compressor/` + `experiments/v1_renderer/`
- V1 E2E: `experiments/v1_e2e/`

## Fair R–D plot (V1 baseline)

Prereqs:
- Dataset at `dataset/re10k/...`
- Checkpoints under `checkpoints/` (see `docs/INSTALL.md`)

### 1) Compress only the required V1 context frames

```bash
python experiments/v1_compressor/compress.py \
  --index-path assets/indices/re10k/evaluation_index_re10k.json \
  --lambdas 0.004 0.008 0.016 0.032 0.15 0.45 \
  --output-root outputs/v1_baseline/compressed \
  --skip_existing
```

If you're on a CPU-only machine, add `--device cpu` (expect it to be slow).

If you already have precomputed ELIC outputs in the legacy layout under `outputs/baseline_ELIC/compressed/`,
you *can* point `--compressed-root` at `outputs/baseline_ELIC/compressed/lambda_<λ>` during eval, but note that
those bitrates are typically computed on the **full-resolution** inputs and are not comparable to E2E runs that
compress the **cropped** 256×256 inputs. For conference-grade RD curves, regenerate bitstreams via `compress.py`.

### 2) Run fair evaluation (vanilla + V1)

Vanilla MVSplat (no compression):

```bash
python experiments/v1_renderer/eval_fair_mvsplat.py \
  --tag vanilla \
  --output outputs/v1_baseline/results/fair_rd.csv
```

If you're on a CPU-only machine, add `--device cpu` (expect it to be slow).

V1 for multiple lambdas (append rows to one CSV):

```bash
out=outputs/v1_baseline/results/fair_rd.csv
rm -f "$out"
for l in 0.004 0.008 0.016 0.032 0.15 0.45; do
  python experiments/v1_renderer/eval_fair_mvsplat.py \
    --compressed-root "outputs/v1_baseline/compressed/lambda_${l}" \
    --tag "v1_lambda_${l}" \
    --output "$out" --append
done
```

### 3) Plot

```bash
bash scripts/plot_fair_rd.sh \
  --input outputs/v1_baseline/results/fair_rd.csv \
  --note "V1 BPP: bitstream (avg over 2 context views)"
```

Outputs:
- `outputs/v1_baseline/results/plots/fair_rd_psnr.pdf` (+ `.png`)
- one plot per metric when using `--all-metrics`

---

## V1 E2E (one RD point)
Train:
```bash
python experiments/v1_e2e/train_e2e.py \
  --tag e2e \
  --lambda 0.032 \
  --rd-lambda 0.032 \
  --nvs-mse-scale 65025 \
  --device cuda \
  --max-steps 18000 \
  --batch-size 15 \
  --num-workers 8 \
  --progress rich
```

Plot training curves:
```bash
python experiments/v1_e2e/plot_curves.py \
  --run-dir checkpoints/v1_e2e/e2e_lambda_0.032_rd_1 \
  --train-mode step --smooth-window 200 \
  --out outputs/v1_e2e/results.png
```
