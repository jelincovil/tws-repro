from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import gudhi as gd
from .wavelet_projection import project_2d
from .cfp_estimation import exact_opnorm


def gaussian_bump_field(shape=(48,48), centers=((16,16,1.0,5.0),(31,28,-0.8,7.0))):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    z = np.zeros(shape, dtype=float)
    for cy, cx, amp, sig in centers:
        z += amp*np.exp(-((yy-cy)**2 + (xx-cx)**2)/(2*sig**2))
    return z


def cubical_diagrams(field: np.ndarray, max_dim: int = 1):
    cc = gd.CubicalComplex(top_dimensional_cells=np.asarray(field, dtype=float))
    cc.persistence(homology_coeff_field=2, min_persistence=0)
    return [np.asarray(cc.persistence_intervals_in_dimension(k), dtype=float) for k in range(max_dim+1)]


def clean_dgm(dgm):
    if dgm.size == 0:
        return np.empty((0,2))
    dgm = dgm[np.isfinite(dgm).all(axis=1)]
    dgm = dgm[dgm[:,1] > dgm[:,0]]
    return dgm


def landscape_l2_window(dgm1, dgm2, n_landscape=0, U=(-1.0,1.0), grid_size=512):
    dgm1, dgm2 = clean_dgm(dgm1), clean_dgm(dgm2)
    xs = np.linspace(U[0], U[1], grid_size)
    def vals(dgm):
        if len(dgm) == 0:
            return np.zeros_like(xs)
        # Tent functions, sampled on the window grid. (persim is not used:
        # constructing PersLandscapeExact here used to be dead code.)
        tent_vals=[]
        for b,d in dgm:
            tent_vals.append(np.maximum(0.0, np.minimum(xs-b, d-xs)))
        arr=np.sort(np.vstack(tent_vals), axis=0)[::-1]
        return arr[n_landscape] if arr.shape[0] > n_landscape else np.zeros_like(xs)
    diff = vals(dgm1) - vals(dgm2)
    return float(np.sqrt(np.trapezoid(diff*diff, xs)))


def run_thm_a_trials(n_trials=20, seed=20260715, shape=(48,48), j_values=(0,1,2,3), boundary="periodization", U=(-1.0,1.0), cfp=None):
    rng=np.random.default_rng(seed)
    base=gaussian_bump_field(shape)
    diam_U = float(U[1] - U[0])
    rows=[]
    for trial in range(n_trials):
        sigma=float(rng.uniform(0.005,0.05))
        noise=rng.normal(0,sigma,size=shape)
        z1=base
        z2=base+noise
        delta_linf=float(np.max(np.abs(z1-z2)))
        for j in j_values:
            cfp_j = float(cfp) if cfp is not None else exact_opnorm(j, d=2)
            p1=project_2d(z1,j,boundary=boundary)
            p2=project_2d(z2,j,boundary=boundary)
            dg1=cubical_diagrams(p1, max_dim=1)
            dg2=cubical_diagrams(p2, max_dim=1)
            for k in [0,1]:
                lhs=landscape_l2_window(dg1[k], dg2[k], n_landscape=0, U=U)
                rhs=cfp_j*delta_linf*np.sqrt(diam_U)
                pdelta_linf=float(np.max(np.abs(p1-p2)))
                rho_op=pdelta_linf/(cfp_j*delta_linf) if cfp_j*delta_linf>0 else np.nan
                rho_top=lhs/(pdelta_linf*np.sqrt(diam_U)) if pdelta_linf>0 else np.nan
                support_len=6*(2**(j+1)-1)+1
                constant_type=("exact_periodized_kernel" if support_len<=shape[0]
                               else "nonperiodized_kernel_bound")
                rows.append({"trial":trial,"grid_shape":f"{shape[0]}x{shape[1]}","j":j,"k":k,"boundary":boundary,"noise_sigma":sigma,"delta_linf":delta_linf,"lhs_l2":lhs,"rhs_thm_a":rhs,"tightness_ratio":lhs/rhs if rhs>0 else np.nan,"holds": bool(lhs <= rhs + 1e-12),"cfp":cfp_j,"C_fp_used":cfp_j,"constant_type":constant_type,"pdelta_linf":pdelta_linf,"rho_op":rho_op,"rho_top":rho_top})
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser(description="Run an end-to-end Thm A validation on controlled generated fields. Use only if synthetic trials are acceptable for the paper.")
    ap.add_argument("--out", default="results/csv/thm_a_trials.csv")
    # The CLI default is the CANONICAL 160, not the 20 of run_thm_a_trials.
    # --out defaults to the canonical CSV, so a bare `python -m
    # tws_validation.persistence_bounds` overwrites the file behind main.tex
    # 5.1. With a default of 20 that produced 160 rows instead of 1280, i.e. it
    # silently reinstated the artefact this package was audited for. The
    # function default stays 20 for cheap programmatic use, which never writes
    # to results/. Keep in sync with the other four layers that carry this
    # number: run_all.THM_A_N_TRIALS, Makefile THM_A_TRIALS,
    # tools/run_full_validation.sh N_TRIALS, and the provenance block in
    # ../README.md.
    ap.add_argument("--n-trials", type=int, default=160)
    args=ap.parse_args()
    df=run_thm_a_trials(n_trials=args.n_trials)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out,index=False)
    print(df.groupby(['j','k'])['tightness_ratio'].describe().to_string())
    if not df['holds'].all():
        raise SystemExit("At least one Thm A trial violated the bound; inspect output before using in manuscript.")

if __name__ == "__main__":
    main()
