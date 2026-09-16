#!/usr/bin/env python3
"""Frozen invocation: Theorem A on 40 Kermany chest radiographs.

Paso 0: empirical_error_L2 is the pointwise L2(U) landscape distance
(landscape_l2_window), i.e. the LHS of Theorem A, not |‖λ‖₂−‖λ'‖₂|.

From experiments/:
    PYTHONPATH=src python medical_validation/run_medical_experiment.py
    PYTHONPATH=src python medical_validation/run_medical_experiment.py --from-csv
    PYTHONPATH=src python medical_validation/check_caption.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import convolve

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PROJ = EXP.parent
SRC = EXP / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tws_validation.cfp_estimation import db2_undecimated_kernel_1d
from tws_validation.persistence_bounds import cubical_diagrams, landscape_l2_window

SEED = 20260715
N_SAMPLES = 20
EPSILONS = (0.01, 0.02, 0.03, 0.04, 0.05)
U = (0.4, 0.8)
IMG_SIZE = (256, 256)
LANDSCAPE_GRID = 200
SYN_RHO_MED = 5.63e-3
SYN_RHO_MAX = 0.151
SYN_ROP_MED = 0.091
SYN_ROP_MAX = 0.448
SYN_RTOP_MED = 0.084
SYN_RTOP_MAX = 0.535

CHEST = PROJ / "chest_xray"
CSV_PATH = HERE / "results" / "medical_bounds.csv"
CSV_V1 = HERE / "results" / "medical_bounds_v1.csv"
SUMMARY_PATH = HERE / "results" / "medical_summary.json"
INVOCATION_PATH = HERE / "invocation.json"
MANIFEST = HERE / "medical_subset_manifest.json"
FIG_PDF = HERE / "figures" / "theorem_A_medical_illustration.pdf"
FIG_PNG = HERE / "figures" / "theorem_A_medical_illustration.png"
CAPTION_TEX = HERE / "figures" / "medical_caption.tex"
TABLE_TEX = HERE / "tables" / "medical_rho_by_epsilon.tex"
CSV_FLOAT = "%.16e"


def exact_kernel_2d() -> np.ndarray:
    k1 = db2_undecimated_kernel_1d(1)
    expected = np.array([-1.0, 0.0, 9.0, 16.0, 9.0, 0.0, -1.0]) / 32.0
    if k1.shape != expected.shape or not np.allclose(k1, expected, atol=1e-12):
        raise RuntimeError(f"Prop. 3.4 kernel mismatch: {k1}")
    return np.outer(k1, k1)


K2D = exact_kernel_2d()
C_FP = float(np.abs(K2D).sum())
DIAM_U = float(U[1] - U[0])


def apply_A1(z: np.ndarray) -> np.ndarray:
    return convolve(np.asarray(z, dtype=float), K2D, mode="wrap")


def load_gray(path: Path) -> np.ndarray:
    import cv2
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(path)
    img = cv2.resize(img, IMG_SIZE, interpolation=cv2.INTER_AREA)
    z = img.astype(np.float64) / 255.0
    return 1.0 - z


def select_names(rng: np.random.Generator) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    for label in ("NORMAL", "PNEUMONIA"):
        src = CHEST / "test" / label
        pool = sorted(src.glob("*.jpeg"))
        if len(pool) < N_SAMPLES:
            raise RuntimeError(f"{src} has {len(pool)} files, need {N_SAMPLES}")
        idx = rng.choice(len(pool), size=N_SAMPLES, replace=False)
        names[label] = sorted(pool[int(i)].name for i in idx)
    return names


def pair_lhs(clean: np.ndarray, noisy: np.ndarray) -> float:
    d1 = cubical_diagrams(clean, max_dim=0)[0]
    d2 = cubical_diagrams(noisy, max_dim=0)[0]
    return landscape_l2_window(d1, d2, n_landscape=0, U=U, grid_size=LANDSCAPE_GRID)


def run() -> pd.DataFrame:
    if abs(C_FP - (9.0 / 8.0) ** 2) > 1e-12:
        raise RuntimeError(f"||k||_1^2 = {C_FP}, expected (9/8)^2")
    rng = np.random.default_rng(SEED)
    names = select_names(rng)
    MANIFEST.write_text(json.dumps({
        "seed": SEED,
        "normal_files": names["NORMAL"],
        "pneumonia_files": names["PNEUMONIA"],
    }, indent=2) + "\n")
    rows = []
    for label in ("NORMAL", "PNEUMONIA"):
        for fname in names[label]:
            z = load_gray(CHEST / "test" / label / fname)
            pz = apply_A1(z)
            for eps in EPSILONS:
                noise = rng.uniform(-eps, eps, size=IMG_SIZE)
                z2 = np.clip(z + noise, 0.0, 1.0)
                delta = float(np.max(np.abs(z2 - z)))
                pz2 = apply_A1(z2)
                lhs = pair_lhs(pz, pz2)
                a1_delta = float(np.max(np.abs(pz2 - pz)))
                rhs = C_FP * delta * np.sqrt(DIAM_U)
                rho = lhs / rhs if rhs > 0 else float("nan")
                rho_op = a1_delta / (C_FP * delta) if delta > 0 else float("nan")
                rho_top = lhs / (a1_delta * np.sqrt(DIAM_U)) if a1_delta > 0 else float("nan")
                rows.append({
                    "class": label,
                    "image_id": fname,
                    "epsilon": eps,
                    "delta_linf": delta,
                    "empirical_error_L2": lhs,
                    "theoretical_bound": rhs,
                    "rho": rho,
                    "rho_op": rho_op,
                    "rho_top": rho_top,
                    "holds": bool(lhs <= rhs + 1e-12),
                    "cfp": C_FP,
                    "diam_U": DIAM_U,
                })
    df = pd.DataFrame(rows)
    df = df.sort_values(["class", "image_id", "epsilon"]).reset_index(drop=True)
    return df


def _stats(s: pd.Series) -> dict:
    return {
        "median": float(s.median()),
        "p90": float(s.quantile(0.90)),
        "max": float(s.max()),
    }


def write_summary(df: pd.DataFrame) -> dict:
    summary = {
        "n": int(len(df)),
        "n_holds": int(df["holds"].sum()),
        "frac_holds": float(df["holds"].mean()),
        "empirical_error_L2_max": float(df["empirical_error_L2"].max()),
        "bound_at_eps_0_05": float(C_FP * 0.05 * np.sqrt(DIAM_U)),
        "cfp": C_FP,
        "diam_U": DIAM_U,
        "synthetic": {
            "rho_median": SYN_RHO_MED,
            "rho_max": SYN_RHO_MAX,
            "rho_op_median": SYN_ROP_MED,
            "rho_op_max": SYN_ROP_MAX,
            "rho_top_median": SYN_RTOP_MED,
            "rho_top_max": SYN_RTOP_MAX,
        },
    }
    for key in ("rho", "rho_op", "rho_top"):
        block = {"global": _stats(df[key])}
        for cls in ("NORMAL", "PNEUMONIA"):
            block[cls] = _stats(df.loc[df["class"] == cls, key])
        summary[key] = block
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def write_invocation() -> None:
    inv = {
        "seed": SEED,
        "n_per_class": N_SAMPLES,
        "source": "chest_xray/test/{NORMAL,PNEUMONIA}",
        "selection": "np.random.Generator(SEED).choice, no replacement, then sorted names",
        "resize": "256x256 cv2.INTER_AREA",
        "grayscale": True,
        "normalize": "[0,1]",
        "invert": "Z <- 1-Z before A1",
        "operator": "periodized convolution, Prop. 3.4 kernel A_1, mode=wrap",
        "pywt": False,
        "U": list(U),
        "landscape_grid": LANDSCAPE_GRID,
        "integration": "np.trapezoid",
        "lhs": "pointwise L2(U) of first-landscape difference (not reverse-triangle of norms)",
        "homology": "H0 only, GUDHI CubicalComplex top-dimensional cells, finite bars",
        "epsilons": list(EPSILONS),
        "noise": "Uniform(-eps,eps), clip to [0,1], RHS uses measured ||Delta||_inf",
        "cfp": C_FP,
        "boundary": "wrap/periodization",
        "complex": "gudhi.CubicalComplex(top_dimensional_cells=...)",
        "n_points": LANDSCAPE_GRID,
    }
    INVOCATION_PATH.write_text(json.dumps(inv, indent=2) + "\n")


def fmt_sci(x: float) -> str:
    return f"{x:.2e}".replace("e-0", "e-").replace("e+0", "e+")


def fmt_tex_sci(x: float) -> str:
    s = f"{x:.2e}".split("e")
    mant, exp = s[0], int(s[1])
    return f"{mant}\\times 10^{{{exp}}}"


def write_table(df: pd.DataFrame) -> None:
    TABLE_TEX.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Medical Theorem~A checks: median $[\mathrm{max}]$ of $\rho$ by class and $\varepsilon$.}",
        r"\label{tab:medical-rho}",
        r"\begin{tabular}{@{}l" + "c" * len(EPSILONS) + r"@{}}",
        r"\toprule",
        r"class / $\varepsilon$ & " + " & ".join(f"{e:.2f}" for e in EPSILONS) + r" \\",
        r"\midrule",
    ]
    for cls in ("NORMAL", "PNEUMONIA"):
        cells = []
        for e in EPSILONS:
            s = df.loc[(df["class"] == cls) & (np.isclose(df["epsilon"], e)), "rho"]
            cells.append(f"{s.median():.3f} $[{s.max():.3f}]$")
        lines.append(cls + " & " + " & ".join(cells) + r" \\")
    gcells = []
    for e in EPSILONS:
        s = df.loc[np.isclose(df["epsilon"], e), "rho"]
        gcells.append(f"{s.median():.3f} $[{s.max():.3f}]$")
    lines += [
        r"\midrule",
        "all & " + " & ".join(gcells) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    TABLE_TEX.write_text("\n".join(lines))


def write_caption(summary: dict) -> None:
    rg, rn, rp = summary["rho"]["global"], summary["rho"]["NORMAL"], summary["rho"]["PNEUMONIA"]
    rop, rtop = summary["rho_op"]["global"], summary["rho_top"]["global"]
    syn = summary["synthetic"]
    n = summary["n"]
    holds = summary["n_holds"]
    text = f"""% Auto-generated from results/medical_summary.json. Do not edit numbers by hand.
\\caption{{Theorem~A on {n} chest-radiograph comparisons (20 NORMAL $+$ 20 PNEUMONIA,
seed 20260715, $U=[0.4,0.8]$, $H_0$).
Left: empirical $L^2(U)$ landscape distance versus measured $\\lVert\\Delta\\rVert_\\infty$,
with the exact certificate $(9/8)^2\\,\\lVert\\Delta\\rVert_\\infty\\sqrt{{\\mathrm{{diam}}(U)}}$.
Right: tightness $\\rho$. All {holds}/{n} rows satisfy $\\rho\\le 1$
(frac.\\,holds $={summary['frac_holds']:.1f}$).
Global median $\\rho={fmt_tex_sci(rg['median'])}$, max ${rg['max']:.3f}$
(NORMAL median ${fmt_tex_sci(rn['median'])}$, max ${rn['max']:.3f}$;
PNEUMONIA median ${fmt_tex_sci(rp['median'])}$, max ${rp['max']:.3f}$).
The synthetic suite of \\S5.1 had median $\\rho={fmt_tex_sci(syn['rho_median'])}$ and max ${syn['rho_max']:.3f}$:
real radiographs stress the envelope more, without saturating it.
Factoring $\\rho=\\rho_{{\\mathrm{{op}}}}\\rho_{{\\mathrm{{top}}}}$ (eq.~(11)) gives
median $\\rho_{{\\mathrm{{op}}}}={rop['median']:.3f}$ and
$\\rho_{{\\mathrm{{top}}}}={rtop['median']:.3f}$.
No class-wise significance is claimed ($n=20$).}}
"""
    CAPTION_TEX.parent.mkdir(parents=True, exist_ok=True)
    CAPTION_TEX.write_text(text)


def plot(df: pd.DataFrame, summary: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.linewidth": 0.7,
        "legend.frameon": False,
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
    })
    rng = np.random.default_rng(SEED)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.5, 4.8))

    styles = {
        "NORMAL": dict(marker="o", facecolors="none", edgecolors="0.2",
                       linewidths=0.8, s=28, label="NORMAL"),
        "PNEUMONIA": dict(marker="^", c="0.45", edgecolors="0.1",
                          linewidths=0.4, s=28, label="PNEUMONIA"),
    }
    for label, kw in styles.items():
        sub = df[df["class"] == label]
        jitter = rng.uniform(-0.0008, 0.0008, size=len(sub))
        ax.scatter(sub["delta_linf"].to_numpy() + jitter,
                   sub["empirical_error_L2"].to_numpy(),
                   alpha=0.6, zorder=3, **kw)
    xmax = float(df["delta_linf"].max())
    xs = np.linspace(0.0, xmax * 1.05, 300)
    ax.plot(xs, C_FP * xs * np.sqrt(DIAM_U), color="0.05", ls="--", lw=1.4,
            zorder=2, label=r"certificate $(9/8)^2\,x\,\sqrt{0.4}$")
    y_emp = float(df["empirical_error_L2"].max())
    ax.set_ylim(0.0, 1.15 * y_emp)
    ax.set_xlim(0.0, xmax * 1.08)
    ax.set_xlabel(r"measured $\|\Delta\|_\infty$")
    ax.set_ylabel(r"$\|\lambda_1|_U(A_1Z_1)-\lambda_1|_U(A_1Z_2)\|_{L^2(U)}$")
    b05 = summary["bound_at_eps_0_05"]
    ax.text(0.04, 0.96,
            rf"bound at $\varepsilon=0.05$: ${b05:.3f}$",
            transform=ax.transAxes, va="top", ha="left", fontsize=8)
    ax.legend(loc="upper left", fontsize=8, handlelength=2.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    eps = list(EPSILONS)
    x = np.arange(len(eps), dtype=float)
    width = 0.34
    box_kw = dict(widths=0.28, showfliers=False, medianprops=dict(color="0.1", lw=1.2),
                  whiskerprops=dict(color="0.3"), capprops=dict(color="0.3"),
                  boxprops=dict(color="0.3"))
    for cls, offset, mkr, face in (
        ("NORMAL", -width / 2, "o", "none"),
        ("PNEUMONIA", width / 2, "^", "0.45"),
    ):
        data = [df.loc[(df["class"] == cls) & np.isclose(df["epsilon"], e), "rho"].to_numpy()
                for e in eps]
        bp = bx.boxplot(data, positions=x + offset, **box_kw)
        for i, ys in enumerate(data):
            js = rng.uniform(-0.07, 0.07, size=len(ys))
            bx.scatter(np.full(len(ys), x[i] + offset) + js, ys,
                       marker=mkr, facecolors=face, edgecolors="0.15",
                       linewidths=0.5, s=14, alpha=0.6, zorder=3)
    bx.axhline(1.0, color="0.1", ls="--", lw=1.1, zorder=1)
    bx.axhline(SYN_RHO_MAX, color="0.25", ls=":", lw=1.2, zorder=1)
    bx.axhline(SYN_RHO_MED, color="0.45", ls=":", lw=0.9, zorder=1)
    bx.set_ylim(0.0, 1.05)
    bx.set_xticks(x)
    bx.set_xticklabels([f"{e:.2f}" for e in eps])
    bx.set_xlabel(r"nominal $\varepsilon$")
    bx.set_ylabel(r"tightness $\rho$")
    bx.text(0.99, 1.0, r"saturation (prop.~3.3)", transform=bx.get_yaxis_transform(),
            ha="right", va="bottom", fontsize=7, color="0.15")
    bx.text(0.99, SYN_RHO_MAX, r"max synthetic, fig.~2", transform=bx.get_yaxis_transform(),
            ha="right", va="bottom", fontsize=7, color="0.25")
    bx.text(0.99, SYN_RHO_MED + 0.015, r"median synthetic", transform=bx.get_yaxis_transform(),
            ha="right", va="bottom", fontsize=7, color="0.4")
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
               markeredgecolor="0.2", markersize=7, label="NORMAL"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="0.45",
               markeredgecolor="0.1", markersize=7, label="PNEUMONIA"),
    ]
    bx.legend(handles=handles, loc="upper left", fontsize=8)
    bx.spines["top"].set_visible(False)
    bx.spines["right"].set_visible(False)

    fig.tight_layout(w_pad=2.0)
    FIG_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PDF, dpi=300, bbox_inches="tight")
    fig.savefig(FIG_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_csv(df: pd.DataFrame) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False, float_format=CSV_FLOAT, lineterminator="\n")


def main() -> None:
    write_invocation()
    if "--from-csv" in sys.argv:
        df = pd.read_csv(CSV_PATH)
    else:
        df = run()
        write_csv(df)
    bad = df.loc[df["rho"] > 1 + 1e-12]
    if len(bad):
        print(bad.to_string())
        raise SystemExit("STOP: rho > 1; not adjusting axes or dropping rows.")
    if not bool(df["holds"].all()):
        raise SystemExit("STOP: holds is not True on every row.")
    summary = write_summary(df)
    write_table(df)
    write_caption(summary)
    plot(df, summary)
    print(f"rows={summary['n']} holds={summary['n_holds']}/{summary['n']} "
          f"max rho={summary['rho']['global']['max']:.4f} "
          f"median rho={summary['rho']['global']['median']:.4e}")
    print(f"wrote {CSV_PATH.relative_to(PROJ)}")
    print(f"wrote {FIG_PDF.relative_to(PROJ)}")


if __name__ == "__main__":
    main()
