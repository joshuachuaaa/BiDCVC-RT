#!/usr/bin/env python3
"""Plot fair rate–distortion curves from CSV metrics.

Expected CSV columns (minimum):
  - tag
  - bpp
  - psnr
  - ssim
  - lpips

This intentionally stays lightweight (no pandas dependency).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def _read_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows.extend(list(reader))
    return rows


def _as_float(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


def _group_key(tag: str) -> str:
    # Heuristic grouping: v1_lambda_0.032 -> v1, v2_* -> v2, etc.
    if "_lambda_" in tag:
        return tag.split("_lambda_", 1)[0]
    return tag


def _format_lambda(value: float) -> str:
    return ("%.3f" % float(value)).rstrip("0").rstrip(".")


def _extract_lambda(tag: str) -> float | None:
    m = re.search(r"(?:^|[/_])lambda_([0-9]*\.?[0-9]+(?:e[+-]?[0-9]+)?)", tag)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _extract_lambda_from_row(row: dict[str, str]) -> float | None:
    # Prefer parsing from the tag, but fall back to paths if tags are not descriptive.
    for key in ("tag", "compressed_root", "run_dir", "mvsplat_ckpt", "elic_ckpt", "ckpt"):
        text = str(row.get(key, "")).strip()
        if not text:
            continue
        lmbda = _extract_lambda(text)
        if lmbda is not None:
            return lmbda
    return None


def _extract_rd_lambda(text: str) -> float | None:
    m = re.search(r"(?:^|[/_])rd_([0-9]*\.?[0-9]+(?:e[+-]?[0-9]+)?)", text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _extract_rd_lambda_from_row(row: dict[str, str]) -> float | None:
    for key in ("tag", "compressed_root", "run_dir", "mvsplat_ckpt", "elic_ckpt", "ckpt"):
        text = str(row.get(key, "")).strip()
        if not text:
            continue
        rd = _extract_rd_lambda(text)
        if rd is not None:
            return rd
    return None


def _pretty_group_label(group: str) -> str:
    if group == "v1":
        return "Baseline (ELIC → MVSplat)"
    if "e2e" in group:
        # e.g., v1_e2e_noscale -> "E2E fine-tuned (noscale)"
        suffix = group
        if suffix.startswith("v1_e2e"):
            suffix = suffix.removeprefix("v1_e2e").lstrip("_")
        if suffix in ("", "v1_e2e"):
            return "E2E fine-tuned"
        return f"E2E fine-tuned ({suffix.replace('_', ' ')})"
    return group.replace("_", " ")


def _stable_index(key: str, n: int) -> int:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % max(1, int(n))


def _plot_metric(
    *,
    rows: list[dict[str, str]],
    metric: str,
    out_path: Path,
    note: str | None,
    title: str | None,
    label_points: bool,
    figsize: tuple[float, float],
) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe

    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "lines.linewidth": 2.2,
            "lines.markersize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        tag = r.get("tag", "")
        bpp = _as_float(r.get("bpp", "nan"))
        y = _as_float(r.get(metric, "nan"))
        if not tag or bpp != bpp or y != y:  # NaN checks
            continue
        groups[_group_key(tag)].append({"bpp": bpp, "y": y, "tag": tag, "row": r})

    if not groups:
        raise SystemExit(f"No valid rows to plot for metric={metric}.")

    fig, ax = plt.subplots(figsize=figsize)
    baseline_key = "vanilla"
    baseline_pts = groups.get(baseline_key, [])
    non_baseline_pts = [pt for group, pts in groups.items() if group != baseline_key for pt in pts]
    zoom_xs = [float(pt["bpp"]) for pt in non_baseline_pts]
    zoom_xlim: tuple[float, float] | None = None
    if baseline_pts and zoom_xs:
        x_min = min(zoom_xs)
        x_max = max(zoom_xs)
        if x_max > x_min:
            pad = (x_max - x_min) * 0.05
        else:
            pad = x_min * 0.05 if x_min > 0 else 0.05
        zoom_xlim = (x_min - pad, x_max + pad)

    palette = list(plt.get_cmap("tab10").colors)
    group_keys_sorted = sorted(groups.keys())
    label_note = (
        "Point labels: baseline shows ELIC λ; E2E shows (ELIC λ, λ_rd)." if label_points else None
    )
    if note and label_note:
        note = f"{note}\\n{label_note}"
    elif label_note:
        note = label_note

    def annotate_point(
        *,
        x: float,
        y: float,
        text: str,
        color: Any,
        base_offset: tuple[int, int],
    ) -> None:
        # Simple collision-avoidance heuristic: try a sequence of offsets and pick the first
        # that doesn't overlap existing label boxes.
        #
        # We avoid new dependencies (e.g., adjustText) but still get "paper-ready" readability.
        offset_candidates = [
            base_offset,
            (base_offset[0], base_offset[1] + 16),
            (base_offset[0], base_offset[1] - 16),
            (base_offset[0] * 2, base_offset[1]),
            (base_offset[0] * 2, base_offset[1] + 16),
            (base_offset[0] * 2, base_offset[1] - 16),
            (-base_offset[0], base_offset[1]),
            (-base_offset[0], base_offset[1] + 16),
            (-base_offset[0], base_offset[1] - 16),
            (-base_offset[0] * 2, base_offset[1]),
            (-base_offset[0] * 2, base_offset[1] + 16),
            (-base_offset[0] * 2, base_offset[1] - 16),
        ]

        renderer = None
        used_bboxes = getattr(annotate_point, "_used_bboxes", None)
        if used_bboxes is None:
            used_bboxes = []
            setattr(annotate_point, "_used_bboxes", used_bboxes)

        for dx, dy in offset_candidates:
            ha = "left" if dx >= 0 else "right"
            va = "bottom" if dy >= 0 else "top"
            txt = ax.annotate(
                text,
                xy=(x, y),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=9,
                ha=ha,
                va=va,
                color=color,
            )
            txt.set_path_effects([pe.withStroke(linewidth=3, foreground="white")])
            try:
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                bbox = txt.get_window_extent(renderer=renderer)
                if any(bbox.overlaps(b) for b in used_bboxes):
                    txt.remove()
                    continue
                used_bboxes.append(bbox)
                return
            except Exception:
                # If we can't compute extents (rare backend issues), keep the first label.
                return

    for group in group_keys_sorted:
        pts = sorted(groups[group], key=lambda d: float(d["bpp"]))
        xs = [float(p["bpp"]) for p in pts]
        ys = [float(p["y"]) for p in pts]
        if group == baseline_key and baseline_pts and zoom_xs:
            continue
        color_idx = _stable_index(group, len(palette))
        color = palette[color_idx]
        # Marker convention (paper-friendly):
        #   - Baseline (ELIC → MVSplat): solid circles.
        #   - Other evals / methods: triangles and squares.
        if group == "v1":
            marker = "o"
            marker_face = color
        elif "e2e" in group:
            marker = "s"
            marker_face = "white"
        else:
            marker = "^"
            marker_face = "white"
        ax.plot(
            xs,
            ys,
            marker=marker,
            linestyle="-",
            color=color,
            markerfacecolor=marker_face,
            markeredgecolor=color,
            markeredgewidth=1.6,
            label=_pretty_group_label(group),
        )
        if label_points:
            offset_cycle = [(10, 12), (10, -16), (-10, 12), (-10, -16)]
            for pi, (x, y, p) in enumerate(zip(xs, ys, pts)):
                row_payload = p.get("row", {})
                lmbda = _extract_lambda_from_row(row_payload) if isinstance(row_payload, dict) else None
                if lmbda is None:
                    continue
                label = f"λ={_format_lambda(lmbda)}"
                if "e2e" in group:
                    rd = _extract_rd_lambda_from_row(row_payload) if isinstance(row_payload, dict) else None
                    if rd is None:
                        rd = lmbda
                    label = f"λ={_format_lambda(lmbda)}\nλ_rd={_format_lambda(rd)}"
                base_offset = offset_cycle[(color_idx + pi) % len(offset_cycle)]
                annotate_point(x=x, y=y, text=label, color=color, base_offset=base_offset)

    if baseline_pts and zoom_xs:
        baseline_y = sum(float(p["y"]) for p in baseline_pts) / float(len(baseline_pts))
        if zoom_xlim is None:
            x_min, x_max = min(zoom_xs), max(zoom_xs)
        else:
            x_min, x_max = zoom_xlim
        ax.plot(
            [x_min, x_max],
            [baseline_y, baseline_y],
            linestyle=":",
            linewidth=2.2,
            color="0.25",
            label="Uncompressed context (24 bpp)",
        )
        txt = ax.annotate(
            "uncompressed (24 bpp)",
            xy=(x_max, baseline_y),
            xytext=(8, 0),
            textcoords="offset points",
            fontsize=9,
            ha="left",
            va="center",
            color="0.25",
        )
        txt.set_path_effects([pe.withStroke(linewidth=3, foreground="white")])

    ax.set_xlabel("Rate (bpp)")
    ylabel = {
        "psnr": "PSNR (dB) ↑",
        "ssim": "SSIM ↑",
        "lpips": "LPIPS ↓",
    }.get(metric, metric)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title)
    ax.grid(True, linestyle="--", linewidth=0.8, alpha=0.25)
    ax.set_axisbelow(True)
    ax.margins(x=0.06, y=0.12)
    if zoom_xlim is not None:
        ax.set_xlim(*zoom_xlim)
    ax.legend(loc="best", frameon=False, title="Method")
    if note:
        fig.text(0.01, 0.01, note, ha="left", va="bottom", fontsize=9)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Plot fair RD curves from CSV metrics")
    parser.add_argument(
        "--input",
        type=Path,
        nargs="+",
        default=[repo_root / "outputs" / "v1_baseline" / "results" / "fair_rd.csv"],
        help="One or more CSV files to read (rows are concatenated).",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=repo_root / "outputs" / "v1_baseline" / "results" / "plots",
        help="Output directory for plots.",
    )
    parser.add_argument(
        "--all-metrics",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Plot PSNR + SSIM + LPIPS (otherwise PSNR only).",
    )
    parser.add_argument("--note", type=str, default=None, help="Optional note to place on plots.")
    parser.add_argument("--title", type=str, default=None, help="Optional plot title.")
    parser.add_argument(
        "--figsize",
        type=float,
        nargs=2,
        default=(8.6, 5.8),
        metavar=("W", "H"),
        help="Figure size in inches (width height).",
    )
    parser.add_argument(
        "--label-points",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Annotate each RD point with its λ (parsed from the row tag).",
    )
    args = parser.parse_args()

    rows = _read_rows(args.input)
    metrics = ["psnr", "ssim", "lpips"] if args.all_metrics else ["psnr"]

    for metric in metrics:
        stem = f"fair_rd_{metric}"
        _plot_metric(
            rows=rows,
            metric=metric,
            out_path=args.outdir / f"{stem}.pdf",
            note=args.note,
            title=args.title,
            label_points=bool(args.label_points),
            figsize=(float(args.figsize[0]), float(args.figsize[1])),
        )
        _plot_metric(
            rows=rows,
            metric=metric,
            out_path=args.outdir / f"{stem}.png",
            note=args.note,
            title=args.title,
            label_points=bool(args.label_points),
            figsize=(float(args.figsize[0]), float(args.figsize[1])),
        )
        print("Wrote:", args.outdir / f"{stem}.pdf")
        print("Wrote:", args.outdir / f"{stem}.png")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
