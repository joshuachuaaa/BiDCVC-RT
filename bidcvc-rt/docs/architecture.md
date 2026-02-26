# Architecture (stub)

## Scope

This repository is **codec-only** and focused on BiDCVC-RT (bidirectional stereo extension of DCVC-RT) and codec baselines.

## Modules

- `bidcvc.api`: Stable API surface for scripts/experiments.
- `bidcvc.bitstream`: Torch-free bitstream contract (SPS + StereoAU).
- `bidcvc.models`: Model implementations and adapters (TODO).
  - `bidcvc.models.dcvc_adapter`: Adapter layer for vanilla DCVC-RT in `third_party/DCVC`.
  - `bidcvc.models.stereo`: BiDCVC-RT stereo extensions (TODO).

## Bitstream contract

Stereo Access Unit (AU) at time `t` is defined as:

`AU(t) = [L.A][R.A][L.B][R.B]`

- Stage A = `(z + pass0 y)`
- Stage B = `(pass1 y)`

See `docs/bitstream_format.md` for wire format details.

## TODO

- Implement neural codec model + training/eval pipelines.
- Integrate vanilla DCVC-RT via `third_party/DCVC` + adapters.

