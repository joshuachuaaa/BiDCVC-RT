# BiDCVC-RT  
**Anchor-Free Bidirectional Stereo Extension of DCVC-RT**

![status](https://img.shields.io/badge/status-research%20prototype-blue)

BiDCVC-RT is a research prototype extending DCVC-RT to a two-stream stereo setting using symmetric cross-view entropy priors.

The design preserves DCVC-RT’s real-time efficiency principles (single-scale latent representation, masked multi-pass entropy coding, implicit temporal modeling) while removing traditional left→right anchor dependencies. Both views are treated symmetrically.

The current focus is architecture prototyping and system-level evaluation (rate–distortion and latency). End-to-end evaluation with novel-view synthesis (via MVSplat) is planned.

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
├─ configs/
│  ├─ default.yaml
│  └─ ablations/
├─ src/
│  ├─ bidcvc_rt/
│  └─ third_party/DCVC/
├─ tools/
│  ├─ demo_stereo_codec.py
│  ├─ plot_rd.py
│  └─ profile_latency.py
├─ scripts/
│  ├─ build.sh
│  └─ download_samples.sh
├─ docs/
│  └─ assets/
├─ LICENSE
└─ README.md
```

---

## Quickstart

### Requirements

- Linux recommended
- Python 3.10+
- NVIDIA GPU with CUDA (strongly recommended)
- A working DCVC checkout

### Install

```bash
git clone https://github.com/<your-username>/bidcvc-rt.git
cd bidcvc-rt

git submodule update --init --recursive

conda create -n bidcvc-rt python=3.10 -y
conda activate bidcvc-rt

pip install -r requirements.txt

bash scripts/build.sh
```

---

## Minimal Demo

```bash
python -m tools.demo_stereo_codec \
  --left data/sample/left.mp4 \
  --right data/sample/right.mp4 \
  --out runs/demo_01 \
  --fps 30 --width 640 --height 360 \
  --seed_frac 0.30
```

Expected outputs:

- `stream.bin`
- `decoded_left.mp4`
- `decoded_right.mp4`
- `metrics.json`
- `latency.csv`

---

## Current Status

- [x] Two-stream encode/decode pipeline  
- [x] Seed-based cross-view entropy conditioning  
- [ ] Rate-distortion benchmarking  
- [ ] Latency instrumentation  
- [ ] MVSplat integration  
- [ ] Rendered-view evaluation  

---

## Roadmap

Planned experiments:

- RD curves (bitrate vs PSNR / LPIPS)
- Latency breakdown (network vs entropy coding vs mux)
- Packet-loss robustness (seed protection strategies)
- Rendered-view evaluation using MVSplat
- Temporal stability metrics (tLPIPS)

---

## License

Intended to be released under MIT for compatibility with DCVC.

---

## References

- DCVC-RT (CVPR 2025)
- BiSIC (ECCV 2024)
- Checkerboard Context Model (CVPR 2021)
- LLSS (CVPR 2024)
- SASIC (CVPR 2022)
- MVSplat (ECCV 2024)

---

## Disclaimer

This repository is an active research prototype.  
Performance claims are not final and experimental results are in progress.