"""Sign-pattern pair that attains the Lipschitz constant of Theorem A.

A steep two-basin field has a unique dominant finite H0 bar generated at a
strict local minimum x0. The perturbation is minus the sign pattern of the
undecimated approximation kernel row at x0. Then ||P Δ||_∞ = ||P|| ||Δ||_∞
and, for small ε, only the birth of that bar moves. On the rising flank the
first-landscape difference equals that shift, so the tightness ratio against
the exact operator norm is 1.

No GUDHI: sublevel H0 is union-find with 8-connectivity, finite bars only.
The operator is the implemented db2 map ``project_2d`` (periodization, j=0).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .cfp_estimation import db2_undecimated_kernel_1d, exact_opnorm
from .wavelet_projection import project_2d


def two_basin_field(n: int = 48, x1=(12, 12), x0=(34, 34),
                    slope: float = 3.0, offset: float = 20.0) -> np.ndarray:
    X, Y = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    cone1 = slope * np.hypot(X - x1[0], Y - x1[1])
    cone0 = offset + slope * np.hypot(X - x0[0], Y - x0[1])
    return np.minimum(cone1, cone0)


def kernel_row_at(n: int, center: tuple[int, int], j: int = 0) -> np.ndarray:
    """Periodized impulse response of A_{j+1} centred at ``center``."""
    k1 = db2_undecimated_kernel_1d(j + 1)
    K = np.outer(k1, k1)
    row = np.zeros((n, n), dtype=float)
    c = K.shape[0] // 2
    i0, j0 = center
    for a in range(K.shape[0]):
        for b in range(K.shape[1]):
            row[(i0 + a - c) % n, (j0 + b - c) % n] += K[a, b]
    return row


def h0_finite_bars(field: np.ndarray) -> list[tuple[float, float]]:
    """Sublevel H0 on the pixel grid, 8-connectivity, elder rule; finite bars."""
    n = field.shape[0]
    flat = np.asarray(field, dtype=float).ravel()
    order = np.argsort(flat, kind="stable")
    parent = np.full(flat.size, -1, dtype=int)
    birth = {}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    bars: list[tuple[float, float]] = []
    for idx in order:
        parent[idx] = idx
        birth[idx] = flat[idx]
        i, j = divmod(int(idx), n)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ii, jj = i + di, j + dj
                if 0 <= ii < n and 0 <= jj < n:
                    q = ii * n + jj
                    if parent[q] >= 0:
                        r1, r2 = find(int(idx)), find(q)
                        if r1 != r2:
                            if birth[r1] < birth[r2]:
                                r1, r2 = r2, r1
                            if flat[idx] > birth[r1]:
                                bars.append((float(birth[r1]), float(flat[idx])))
                            parent[r1] = r2
    return bars


def landscape1(bars: list[tuple[float, float]], t: np.ndarray) -> np.ndarray:
    v = np.zeros_like(t, dtype=float)
    for b, d in bars:
        v = np.maximum(v, np.clip(np.minimum(t - b, d - t), 0.0, None))
    return v


def longest_bar(bars: list[tuple[float, float]]) -> tuple[float, float]:
    return max(bars, key=lambda bd: bd[1] - bd[0])


def run_sign_pattern(n: int = 48, j: int = 0, eps: float = 0.05,
                     x0=(34, 34), x1=(12, 12),
                     boundary: str = "periodization") -> dict:
    z1 = two_basin_field(n=n, x1=x1, x0=x0)
    pz1 = project_2d(z1, j, boundary=boundary)
    row = kernel_row_at(n, x0, j=j)
    delta = -eps * np.sign(row)
    pdelta = project_2d(delta, j, boundary=boundary)
    cfp = exact_opnorm(j, d=2)
    delta_linf = float(np.max(np.abs(delta)))
    op_sat = float(np.max(np.abs(pdelta)) / (cfp * delta_linf))

    bars1 = h0_finite_bars(pz1)
    bars2 = h0_finite_bars(pz1 + pdelta)
    b, d = longest_bar(bars1)
    shift = cfp * delta_linf
    u0, u1 = b, 0.5 * (b + d) - 0.5 * shift
    if not (u1 > u0):
        raise RuntimeError("U is empty: death too close to birth for this ε")
    t = np.linspace(u0, u1, 200001)
    diff = np.abs(landscape1(bars1, t) - landscape1(bars2, t))
    lhs = float(np.sqrt(np.trapezoid(diff * diff, t)))
    diam = float(u1 - u0)
    rhs = cfp * delta_linf * np.sqrt(diam)
    b2, d2 = longest_bar(bars2)
    return {
        "j": j, "n": n, "eps": eps, "boundary": boundary,
        "cfp": cfp, "delta_linf": delta_linf, "op_saturation": op_sat,
        "bar1_birth": b, "bar1_death": d,
        "bar2_birth": b2, "bar2_death": d2,
        "n_bars_1": len(bars1), "n_bars_2": len(bars2),
        "U0": u0, "U1": u1, "diam_U": diam,
        "lhs_l2": lhs, "rhs_op": rhs,
        "rho_op": lhs / rhs if rhs > 0 else float("nan"),
        "birth_shift": b - b2, "expected_shift": shift,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Sign-pattern pair attaining the Theorem A constant.")
    ap.add_argument("--out", default="results/csv/sign_pattern_extremal.csv")
    args = ap.parse_args()
    rec = run_sign_pattern()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([rec]).to_csv(args.out, index=False)
    print(pd.Series(rec).to_string())
    print(f"rho_op = {rec['rho_op']:.16f}   op_saturation = {rec['op_saturation']:.16f}")


if __name__ == "__main__":
    main()
