"""Extremal pair for Theorem A tightness (review item B2).

A single Gaussian bump and an amplitude shift move one birth--death pair.
U is a short interval centred on that tent. The ratio is against the
exact j=0 operator norm (9/8)^2, not the kernel bound.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .persistence_bounds import (
    clean_dgm,
    cubical_diagrams,
    gaussian_bump_field,
    landscape_l2_window,
)
from .wavelet_projection import project_2d

OP_NORM_J0 = (9.0 / 8.0) ** 2


def longest_finite_bar(dgm: np.ndarray):
    dgm = clean_dgm(dgm)
    if len(dgm) == 0:
        return None
    persist = dgm[:, 1] - dgm[:, 0]
    return dgm[int(np.argmax(persist))]


def run_extremal(shape=(48, 48), j: int = 0, amp=1.0, d_amp=0.25,
                 sig=6.0, boundary="periodization") -> pd.DataFrame:
    z1 = gaussian_bump_field(shape=shape, centers=((shape[0] // 2, shape[1] // 2, amp, sig),))
    z2 = gaussian_bump_field(shape=shape, centers=((shape[0] // 2, shape[1] // 2, amp + d_amp, sig),))
    p1 = project_2d(z1, j, boundary=boundary)
    p2 = project_2d(z2, j, boundary=boundary)
    delta = float(np.max(np.abs(z1 - z2)))
    rows = []
    for k in (0, 1):
        d1 = cubical_diagrams(p1, max_dim=1)[k]
        d2 = cubical_diagrams(p2, max_dim=1)[k]
        bar = longest_finite_bar(d1)
        if bar is None:
            continue
        mid = 0.5 * (bar[0] + bar[1])
        half = 0.5 * (bar[1] - bar[0])
        for frac in (0.25, 0.5, 1.0, 1.5):
            w = max(frac * half, 1e-3)
            U = (mid - w, mid + w)
            lhs = landscape_l2_window(d1, d2, n_landscape=0, U=U)
            rhs_op = OP_NORM_J0 * delta * np.sqrt(U[1] - U[0])
            rows.append({
                "j": j, "k": k, "U0": U[0], "U1": U[1],
                "diam_U": U[1] - U[0],
                "delta_linf": delta,
                "lhs_l2": lhs,
                "rhs_op": rhs_op,
                "rho_op": lhs / rhs_op if rhs_op > 0 else np.nan,
                "bar_birth": bar[0], "bar_death": bar[1],
            })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/csv/extremal_tightness.csv")
    args = ap.parse_args()
    df = run_extremal()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    best = df.loc[df["rho_op"].idxmax()]
    print(df.to_string(index=False))
    print(f"max rho_op = {best['rho_op']:.4f}  (k={int(best['k'])}, diam_U={best['diam_U']:.4f})")


if __name__ == "__main__":
    main()
