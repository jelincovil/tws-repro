from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import pywt
from .wavelet_projection import project_2d


def scaling_function_norms(wavelet: str = "db2", level: int = 12) -> dict[str, float]:
    w = pywt.Wavelet(wavelet)
    phi, psi, x = w.wavefun(level=level)
    dx = float(x[1] - x[0])
    return {"phi_linf": float(np.max(np.abs(phi))), "phi_l1": float(np.sum(np.abs(phi))*dx), "support_grid_min": float(x[0]), "support_grid_max": float(x[-1])}


def db2_lowpass() -> np.ndarray:
    s3 = np.sqrt(3.0)
    return np.array([1 + s3, 3 + s3, 3 - s3, 1 - s3]) / (4.0 * np.sqrt(2.0))


def _dilate(kernel: np.ndarray, m: int) -> np.ndarray:
    out = np.zeros((len(kernel) - 1) * m + 1, dtype=float)
    out[::m] = kernel
    return out


def db2_undecimated_kernel_1d(level: int) -> np.ndarray:
    """À-trous db2 approximation kernel at MRA level ``level`` ≥ 1 (half autocorrelation cascade)."""
    if level < 1:
        raise ValueError("level must be ≥ 1 (A_{j+1} has level j+1)")
    h = db2_lowpass()
    a = np.correlate(h, h, mode="full") / 2.0
    k = a.copy()
    for L in range(2, level + 1):
        k = np.convolve(k, _dilate(a, 2 ** (L - 1)))
    return k


def undecimated_kernel_1d(wavelet: str, level: int) -> np.ndarray:
    """À-trous approximation kernel at MRA level ``level`` ≥ 1 (half autocorrelation cascade)."""
    if level < 1:
        raise ValueError("level must be ≥ 1")
    if wavelet == "db2":
        return db2_undecimated_kernel_1d(level)
    h = np.asarray(pywt.Wavelet(wavelet).dec_lo, dtype=float)
    a = np.correlate(h, h, mode="full") / 2.0
    k = a.copy()
    for L in range(2, level + 1):
        k = np.convolve(k, _dilate(a, 2 ** (L - 1)))
    return k


def exact_opnorm(j: int, d: int = 2, wavelet: str = "db2") -> float:
    """Exact ``||A_{j+1}||_{∞→∞}`` on ``Z^d``: ``||k_{j+1}||_1^d`` for a separable filter."""
    k = undecimated_kernel_1d(wavelet, j + 1)
    return float(np.abs(k).sum() ** d)


def cfp_kernel_bound(d: int = 2, K: int = 7, wavelet: str = "db2", level: int = 12) -> float:
    """Deprecated crude kernel estimate; not used in Theorem A or tightness."""
    vals = scaling_function_norms(wavelet, level)
    # For orthonormal db2, primal and dual scaling functions coincide.
    return float(((2*K + 1) ** d) * vals["phi_linf"] * vals["phi_l1"])


def test_inputs(shape=(64,64), n_random=64, seed=20260715):
    rng = np.random.default_rng(seed)
    for i in range(n_random):
        yield "random_sign", np.where(rng.random(shape) < 0.5, -1.0, 1.0)
    for coord in [(0,0), (shape[0]//2, shape[1]//2), (shape[0]//3, shape[1]//4), (shape[0]-1, shape[1]-1)]:
        x = np.zeros(shape); x[coord] = 1.0
        yield "delta", x
    yy, xx = np.mgrid[0:shape[0],0:shape[1]]
    for sx, sy in [(5,5),(8,12),(15,8)]:
        z = np.sin(xx/sx) + np.cos(yy/sy)
        z = z / np.max(np.abs(z))
        yield "deterministic_texture", z


def estimate_cfp(shape=(128,128), j_values=range(0,7), boundaries=("periodization","symmetric","zero"), wavelet="db2", n_random=64, seed=20260715):
    rows=[]
    inputs=list(test_inputs(shape, n_random=n_random, seed=seed))
    for j in j_values:
        for b in boundaries:
            ratios=[]
            kinds=[]
            for kind, x in inputs:
                y=project_2d(x, j, wavelet=wavelet, boundary=b)
                denom=np.max(np.abs(x))
                ratios.append(float(np.max(np.abs(y))/denom if denom else np.nan))
                kinds.append(kind)
            ratios_np=np.asarray(ratios)
            rows.append({"grid_shape":f"{shape[0]}x{shape[1]}","j":j,"boundary":b,"constant_type":"sampled_max_ratio","n_inputs":len(ratios),"max_ratio":float(np.nanmax(ratios_np)),"q95_ratio":float(np.nanquantile(ratios_np,0.95)),"median_ratio":float(np.nanmedian(ratios_np)),"kernel_bound_K7":cfp_kernel_bound(d=2,K=7,wavelet=wavelet)})
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default="results/csv/cfp_estimates.csv")
    # CANONICAL 64 -> n_inputs = 71. --out defaults to the canonical CSV, so a
    # bare `python -m tws_validation.cfp_estimation` rewrites the file behind
    # main.tex 5.1 and must reproduce it. Keep in sync with the other four
    # layers: run_all.CFP_N_RANDOM, Makefile CFP_N_RANDOM,
    # tools/run_full_validation.sh N_RANDOM, and ../README.md.
    ap.add_argument("--n-random", type=int, default=64)
    args=ap.parse_args()
    df=estimate_cfp(n_random=args.n_random)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
