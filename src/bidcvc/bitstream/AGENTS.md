# Bitstream package rules (strict)

- Must NOT import torch.
- Prefer standard library only (struct, io, dataclasses, enum).
- Implement:
  - SPS encode/decode (versioned)
  - StereoAU encode/decode with explicit lengths for [L.A][R.A][L.B][R.B]
  - Robust validation and clear BitstreamError messages
- Write pytest unit tests that:
  - roundtrip serialize->parse->serialize equals original bytes
  - truncated/corrupt inputs raise BitstreamError
