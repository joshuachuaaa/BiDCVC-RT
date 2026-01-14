# V1 baseline (ELIC → RGB → MVSplat)

This folder is kept as a **legacy alias** for historical reasons.
The canonical V1 baseline entrypoints are now:

- Compressor: `experiments/v1_compressor/compress.py`
- Renderer eval: `experiments/v1_renderer/eval_fair_mvsplat.py`

The `experiments/v1_baseline/*.py` scripts remain as thin wrappers that forward to the new locations.

This experiment implements the **bitstream baseline**:

1. Select 2 context frames per scene from a **fixed evaluation index** (`assets/indices/re10k/evaluation_index_re10k.json`).
2. Compress each context frame independently with **ELIC** at a given λ (true bitstream size).
3. Decode back to RGB and run **vanilla MVSplat** to render the target views.

The intended use is to produce a **rate–distortion curve** (bpp vs PSNR/SSIM/LPIPS).

## 1) Compress required context frames

```bash
python experiments/v1_compressor/compress.py \
  --index-path assets/indices/re10k/evaluation_index_re10k.json \
  --dataset-root dataset/re10k \
  --lambdas 0.004 0.008 0.016 0.032 0.15 0.45 \
  --skip-existing
```

If you already have precomputed ELIC outputs under `outputs/baseline_ELIC/compressed/` (legacy layout),
you *can* point eval to them via `--compressed-root outputs/baseline_ELIC/compressed/lambda_<λ>`, but be careful:

- Those legacy artifacts are typically **full-resolution** (e.g., 640×360) ELIC encodes.
- MVSplat’s RE10K pipeline **always** applies `rescale_and_crop(..., shape=[256,256])` (see
  `third_party/mvsplat/src/dataset/shims/crop_shim.py:51`), so `eval_fair_mvsplat.py` will resize+crop the
  decoded PNGs before feeding them to the renderer.
- However, the **bitrate accounting** from legacy `metrics.csv` / `.bin` reflects the *full-resolution* encoding,
  and is therefore **not comparable** to E2E runs that compress the *cropped* 256×256 inputs.

For conference-grade RD plots, regenerate the baseline bitstreams with `compress.py` so the transmitted inputs
match the actual MVSplat inputs (crop-then-compress).

Outputs (per λ):

```text
outputs/v1_baseline/compressed/lambda_<λ>/
  manifest.csv              # per-image bpp + bookkeeping
  recon/<scene>/<frame>.png # decoded RGB used as MVSplat context input
```

## 2) Evaluate MVSplat fairly

Vanilla MVSplat (no compression):

```bash
python experiments/v1_renderer/eval_fair_mvsplat.py \
  --tag vanilla \
  --mvsplat-ckpt checkpoints/vanilla/MVSplat/re10k.ckpt \
  --output outputs/v1_baseline/results/fair_rd.csv
```

Compressed V1 (one row per λ; append to same CSV):

```bash
out=outputs/v1_baseline/results/fair_rd.csv
rm -f "$out"
for l in 0.004 0.008 0.016 0.032 0.15 0.45; do
  python experiments/v1_renderer/eval_fair_mvsplat.py \
    --tag "v1_lambda_${l}" \
    --mvsplat-ckpt checkpoints/vanilla/MVSplat/re10k.ckpt \
    --compressed-root "outputs/v1_baseline/compressed/lambda_${l}" \
    --output "$out" --append
done
```

## 3) Plot

```bash
bash scripts/plot_fair_rd.sh --input outputs/v1_baseline/results/fair_rd.csv
```
