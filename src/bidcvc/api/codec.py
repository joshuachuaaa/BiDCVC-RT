"""High-level codec API.

This module is the intended entrypoint for scripts and experiments. The neural
codec itself is TODO; for now we provide:
- Bitstream SPS and StereoAU encode/decode wrappers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bidcvc.api.errors import BitstreamError

if TYPE_CHECKING:  # pragma: no cover
    from bidcvc.bitstream.au import StereoAU
    from bidcvc.bitstream.sps import StereoSPS


def sps_serialize(sps: "StereoSPS") -> bytes:
    """Serialize a StereoSPS to bytes."""

    from bidcvc.bitstream.sps import encode_sps

    return encode_sps(sps)


def sps_parse(data: bytes) -> "StereoSPS":
    """Parse a StereoSPS from bytes."""

    from bidcvc.bitstream.sps import decode_sps

    return decode_sps(data)


def au_serialize(au: "StereoAU") -> bytes:
    """Serialize a StereoAU to bytes."""

    from bidcvc.bitstream.au import encode_au

    return encode_au(au)


def au_parse(data: bytes) -> "StereoAU":
    """Parse a StereoAU from bytes."""

    from bidcvc.bitstream.au import decode_au

    return decode_au(data)


def encode_stereo_frame(*_args, **_kwargs) -> bytes:
    """Encode one stereo frame to a StereoAU bitstream.

    TODO: Wire actual BiDCVC-RT model code. This stub exists so CLIs can be
    implemented now.
    """

    raise NotImplementedError(
        "BiDCVC-RT model wiring is TODO. Bitstream encode/decode is available, "
        "but neural encoding is not implemented yet."
    )


def decode_stereo_au(*_args, **_kwargs):
    """Decode one StereoAU bitstream into reconstructed frames.

    TODO: Wire actual BiDCVC-RT model code.
    """

    raise NotImplementedError(
        "BiDCVC-RT model wiring is TODO. Bitstream parse is available, "
        "but neural decoding is not implemented yet."
    )


def list_ablations() -> list[str]:
    """List available ablation switches (placeholder).

    TODO: Expose a stable ablation surface for experiments.
    """

    return []


def run_rd_eval(*_args, **_kwargs) -> None:
    """Run rate-distortion evaluation (placeholder)."""

    raise NotImplementedError("RD evaluation wiring is TODO.")


def run_latency_eval(*_args, **_kwargs) -> None:
    """Run latency evaluation (placeholder)."""

    raise NotImplementedError("Latency evaluation wiring is TODO.")
