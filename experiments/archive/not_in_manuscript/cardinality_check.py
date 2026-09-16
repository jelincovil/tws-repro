from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def count_indices(d: int, r: int, diam: float, K: float = 7.0) -> int:
    """Count integer lattice centers intersecting an expanded d-cube window.

    Model: centers at spacing 2^-r; support radius K*2^-r; window side length diam.
    Count = ceil((diam + 2K 2^-r)/2^-r)^d = ceil(diam*2^r + 2K)^d.
    The asymptotic slope of log2(count) versus r is d, not 2.
    """
    return int(np.ceil(diam*(2**r) + 2*K) ** d)


def make_table(ds=(2,3,4), rs=range(1,17), diam_values=(0.25,0.5,1.0), K=7.0):
    rows=[]
    for d in ds:
        for diam in diam_values:
            for r in rs:
                c=count_indices(d,r,diam,K)
                old=count_indices(2,r,diam,K)
                rows.append({"d":d,"diam":diam,"r":r,"count":c,"log2_count":float(np.log2(float(c))),"old_exponent2_proxy":old,"undercount_factor_vs_old":float(c/old)})
    return pd.DataFrame(rows)


def fit_exponents(df, r_min=10):
    rows=[]
    for (d,diam), g in df.groupby(['d','diam']):
        h=g[g['r'] >= r_min]
        slope, intercept=np.polyfit(h['r'], h['log2_count'], 1)
        rows.append({"d":d,"diam":diam,"fit_r_min":r_min,"fitted_exponent_vs_r":float(slope),"abs_error_vs_d":float(abs(slope-d)),"n_points":len(h)})
    return pd.DataFrame(rows)


def plot(df, out="results/figures/cardinality_exponent.png"):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10})
    fig, ax = plt.subplots(figsize=(6.2,4.0))
    for d, g in df[df['diam']==1.0].groupby('d'):
        ax.plot(g['r'], g['count'], marker='o', linewidth=1.7, markersize=3.5, label=f'd={d}')
    ax.set_yscale('log')
    ax.set_xlabel('scale r')
    ax.set_ylabel(r'Cardinality $|W_r^V|$')
    ax.set_title('Localized index-cardinality growth')
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out, dpi=220)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--results", default="results/csv/cardinality_counts.csv")
    ap.add_argument("--fits", default="results/csv/cardinality_fits.csv")
    ap.add_argument("--figure", default="results/figures/cardinality_exponent.png")
    args=ap.parse_args()
    df=make_table(); fits=fit_exponents(df)
    Path(args.results).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.results,index=False); fits.to_csv(args.fits,index=False); plot(df,args.figure)
    print(fits.to_string(index=False))

if __name__ == "__main__":
    main()
