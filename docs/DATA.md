# Data (RealEstate10K)

This repo expects a preprocessed RealEstate10K dataset in the same format as MVSplat.

## Expected layout

```text
dataset/re10k/
  train/
    index.json
    *.torch
  test/
    index.json
    *.torch
```

- `index.json` maps scene keys to `.torch` chunk files.
- Each `.torch` file is a list of examples containing JPEG bytes + camera parameters.
- This repo uses **two splits**: `train` and `test`.
- Some helper scripts accept `--stage eval` as an alias for `test` because the canonical index file is named
  `dataset_index_eval.json` (mirroring the “evaluation split” terminology), but the on-disk directory is still `test/`.

## Evaluation index

The fixed evaluation index used for fair comparison across V1/V2/V3 is committed at:

- `assets/indices/re10k/evaluation_index_re10k.json`

You can sanity-check an index file with:

```bash
python scripts/verify_eval_index.py assets/indices/re10k/evaluation_index_re10k.json
```

## Canonical indices

Canonical index files live under `assets/indices/re10k/`:

- `assets/indices/re10k/dataset_index_train.json`
- `assets/indices/re10k/dataset_index_eval.json`
- `assets/indices/re10k/evaluation_index_re10k.json`
