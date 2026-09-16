"""Module A-bis — sample-size dependence of the empirical C_fp maximum.

The headline empirical ratio reported for C_fp is a *sample maximum* over a
finite pool of test inputs, most of which are random sign patterns. A sample
maximum is non-decreasing in the sample size n, so quoting it without stating
n (and the seed) is not reproducible. This module measures that dependence
explicitly so the manuscript can state it instead of assuming it away.

For each n it re-runs the Module A estimator at a fixed scale j and records the
per-boundary maxima plus the boundary that attains the overall maximum.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .cfp_estimation import estimate_cfp

DEFAULT_N_VALUES = (4, 8, 16, 32, 64, 128, 256)
BOUNDARIES = ("periodization", "symmetric", "zero")


def sample_max_vs_n(n_values=DEFAULT_N_VALUES, shape=(128, 128), j: int = 0,
                    boundaries=BOUNDARIES, wavelet: str = "db2",
                    seed: int = 20260715) -> pd.DataFrame:
    rows = []
    for n in n_values:
        df = estimate_cfp(shape=shape, j_values=[j], boundaries=boundaries,
                          wavelet=wavelet, n_random=n, seed=seed)
        best = df.loc[df["max_ratio"].idxmax()]
        row = {"n_random": n, "n_inputs": int(df["n_inputs"].iloc[0]), "j": j,
               "seed": seed, "shape": f"{shape[0]}x{shape[1]}", "wavelet": wavelet}
        for b in boundaries:
            row[f"max_ratio_{b}"] = float(df.loc[df["boundary"] == b, "max_ratio"].iloc[0])
        row["max_ratio_overall"] = float(best["max_ratio"])
        row["argmax_boundary"] = str(best["boundary"])
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Sample-size dependence of the empirical C_fp maximum "
                    "(evidence that the reported maximum is a sample maximum).")
    ap.add_argument("--out", default="results/csv/cfp_sample_max_vs_n.csv")
    ap.add_argument("--n-values", default=",".join(str(n) for n in DEFAULT_N_VALUES),
                    help="comma-separated list of --n-random values to sweep")
    ap.add_argument("--j", type=int, default=0,
                    help="scale at which the overall maximum is attained (default 0)")
    ap.add_argument("--seed", type=int, default=20260715)
    args = ap.parse_args()

    n_values = tuple(int(tok) for tok in args.n_values.split(",") if tok.strip())
    df = sample_max_vs_n(n_values=n_values, j=args.j, seed=args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    cols = ["n_random", "n_inputs", "max_ratio_overall", "argmax_boundary"]
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
