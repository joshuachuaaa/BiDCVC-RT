# BiDCVC-RT
**Anchor-Free Bidirectional Stereo Extension of DCVC-RT**

![status](https://img.shields.io/badge/status-research%20prototype-blue)

BiDCVC-RT is a research prototype extending DCVC-RT to a two-stream stereo setting using symmetric cross-view entropy priors.

The design preserves DCVC-RT’s real-time efficiency principles (single-scale latent representation, masked multi-pass entropy coding, implicit temporal modeling) while removing traditional left→right anchor dependencies. Both views are treated symmetrically.

This repository is intentionally **codec-only**: it focuses on compression, bitstream contracts, baselines, and system-level evaluation (rate–distortion and latency). Downstream rendering, telepresence, and networking stacks are out of scope.

---

## Motivation

Most neural video codecs operate on a single stream. In stereo capture, this leaves significant cross-view redundancy unused.

Existing stereo approaches often rely on an anchor view (e.g., left→right dependency), which can:

- Reduce parallelism
- Increase latency
- Introduce asymmetry between views

BiDCVC-RT explores a different direction:

- No permanent anchor view
- Symmetric bidirectional cross-view conditioning
- Real-time-oriented entropy modeling

The goal is to retain DCVC-RT’s throughput characteristics while improving stereo redundancy exploitation.

---

## Design Overview

At each timestep *t*, both views are processed in two entropy passes:

### Stage A - Seed Encoding

A subset of latent elements (seed fraction) from both left and right views is encoded first using masked entropy coding.

These seed latents are exchanged symmetrically between views.

### Stage B - Conditional Completion

Remaining latent elements are encoded conditioned on:

- Temporal context from timestep (t-1)
- Cross-view seed latents from Stage A

This produces symmetric cross-view priors without enforcing a strict left→right order.

---

## Bitstream contract

Stereo Access Unit (AU) at time `t` is defined as:

`AU(t) = [L.A][R.A][L.B][R.B]`

- Stage A = `(z + pass0 y)`
- Stage B = `(pass1 y)`

The wire format is versioned and strict (roundtrip + robust parser errors). See `docs/bitstream_format.md`.

---

## Default Experimental Setup (Initial Baseline)

- 30 FPS
- 640×360 resolution
- Seed fraction: 25-40%
- Single-scale latent representation (1/8 spatial scale)

These values are starting baselines and will be refined as experiments mature.

---

## Repository Structure

```
.
├─ configs/                  # YAML placeholders (codec/eval/training)
├─ docs/                     # architecture + bitstream docs
├─ experiments/              # stub runners/plotters
├─ scripts/                  # thin CLIs (import only from bidcvc.api)
├─ src/bidcvc/               # library code (src-layout)
├─ tests/                    # pytest unit tests (bitstream-focused)
└─ third_party/DCVC/          # placeholder for DCVC-RT git submodule
```

---

## Quickstart

### Requirements

- Python 3.10+
- A working DCVC-RT checkout (optional for now; required for baseline integration)

### Install

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

### CLI sanity

```bash
python scripts/encode_stereo.py --help
python scripts/decode_stereo.py --help
```

---

## Current Status

- [x] Versioned bitstream contract (Stereo SPS + StereoAU)
- [x] Torch-free bitstream tests
- [x] Thin CLI wiring stubs
- [ ] DCVC-RT baseline adapter (requires `third_party/DCVC` submodule)
- [ ] BiDCVC-RT model implementation + training + evaluation

---

## Optional downstream evaluation (separate repo)

Rendered-view / novel-view evaluation may be explored in a separate downstream repository (e.g., using MVSplat), but it is not a goal of this repository and no such code will live here.

---

## DCVC-RT dependency

Vanilla DCVC-RT is intentionally **not** vendored here. Add it under `third_party/DCVC/` as a git submodule (see `third_party/DCVC/README.md`), and implement glue under `src/bidcvc/models/dcvc_adapter/`.

---

## License

MIT (see `LICENSE`).

---

## References

- DCVC-RT (CVPR 2025)
- BiSIC (ECCV 2024)
- Checkerboard Context Model (CVPR 2021)
- LLSS (CVPR 2024)
- SASIC (CVPR 2022)

---

## Disclaimer

This repository is an active research scaffold. Performance claims are not final and experimental results are in progress.
