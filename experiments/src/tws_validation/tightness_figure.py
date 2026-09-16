"""Regenerate figures/thm_a_tightness.png from the Module B CSV.

Until now this figure shipped as a committed PNG with no generating script (the
repository README said so explicitly), which made the only empirical figure of
the manuscript non-reproducible and silently stale whenever Module B was re-run.
This module closes that hole: the figure is now a pure function of
`results/csv/thm_a_trials.csv`.

The plotted quantity is the tightness ratio recorded by
`persistence_bounds.run_thm_a_trials`, i.e.

    LHS / RHS = ||landscape difference||_{L2(U)}
                / ( C_fp(j) * ||Z1 - Z2||_inf * sqrt(diam U) )

with C_fp(j) the exact per-scale operator norm of the Proposition
(||A_{j+1}||_{∞→∞} for db2), not a kernel estimate.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot_tightness(df: pd.DataFrame, out: str, bins: int = 25) -> dict:
    r = df["tightness_ratio"].to_numpy(dtype=float)
    r = r[np.isfinite(r) & (r > 0)]
    if r.size == 0:
        raise ValueError("no finite positive tightness ratios in the input CSV")
    median = float(np.median(r))
    stats = {"n": int(r.size), "median": median, "max": float(r.max()),
             "min": float(r.min()), "n_violations": int((r > 1.0).sum())}

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.linewidth": 0.6,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "legend.frameon": False,
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
    })
    edges = np.logspace(np.log10(r.min()), np.log10(r.max()), bins + 1)
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    ax.hist(r, bins=edges, color="0.55", edgecolor="0.15", linewidth=0.4)
    ax.set_xscale("log")
    ax.set_xlim(edges[0] / 3.0, 3.0)
    ax.axvline(1.0, color="0.15", linestyle="--", linewidth=1.1, label=r"threshold $1$")
    ax.axvline(median, color="0.15", linestyle=":", linewidth=1.1,
               label=rf"median ${median:.2e}$")
    ax.set_xlabel("tightness ratio (log scale)")
    ax.set_ylabel("count")
    ax.legend(loc="lower right", handlelength=2.0, fontsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Regenerate thm_a_tightness.png from the Module B CSV.")
    ap.add_argument("--trials", default="results/csv/thm_a_trials.csv")
    ap.add_argument("--out", default="results/figures/thm_a_tightness.png")
    ap.add_argument("--also-copy-to", default=None,
                    help="optional second path to write the same figure")
    ap.add_argument("--bins", type=int, default=25)
    args = ap.parse_args()

    df = pd.read_csv(args.trials)
    stats = plot_tightness(df, args.out, bins=args.bins)
    print(f"wrote {args.out}")
    print(f"  comparisons : {stats['n']}")
    print(f"  median      : {stats['median']:.6e}")
    print(f"  max         : {stats['max']:.6e}")
    print(f"  violations  : {stats['n_violations']}")
    if args.also_copy_to:
        plot_tightness(df, args.also_copy_to, bins=args.bins)
        print(f"wrote {args.also_copy_to}")


if __name__ == "__main__":
    main()
