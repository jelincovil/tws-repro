#!/usr/bin/env python3
"""Recompute global statistics from the frozen CSV and write global_results.json.

Does not touch radiographs. Does not re-run GUDHI.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from render_final_figure import _assert_frozen, load

HERE = Path(__file__).resolve().parent
GLOBAL_PATH = HERE / "results" / "global_results.json"
TABLE_PATH = HERE / "tables" / "medical_rho_by_epsilon.tex"
EPSILONS = (0.01, 0.02, 0.03, 0.04, 0.05)
FROZEN_MD5 = {
    "results/medical_bounds.csv": "6be3272f5570ea123fba7de6cb036fcc",
    "results/medical_summary.json": "738bf317b5fda722ec8c50e269998337",
}


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stats(series: pd.Series) -> dict[str, float]:
    s = series.astype(float)
    return {
        "median": float(s.median()),
        "p90": float(s.quantile(0.9)),
        "max": float(s.max()),
    }


def _close(a: float, b: float, tol: float = 1e-12) -> None:
    if abs(float(a) - float(b)) > tol:
        raise SystemExit(f"mismatch: {a} vs {b}")


def rho_by_epsilon(df: pd.DataFrame) -> dict:
    out: dict = {}
    for label in ("NORMAL", "PNEUMONIA", "all"):
        block = {}
        for e in EPSILONS:
            if label == "all":
                sub = df.loc[np.isclose(df["epsilon"], e), "rho"]
            else:
                sub = df.loc[
                    (df["class"] == label) & np.isclose(df["epsilon"], e), "rho"
                ]
            block[f"{e:.2f}"] = {
                "median": float(sub.median()),
                "max": float(sub.max()),
                "n": int(len(sub)),
            }
        out[label] = block
    return out


def write_table(by_eps: dict) -> str:
    def med(block: dict, e: float) -> str:
        return f"{block[f'{e:.2f}']['median']:.3f}"

    def mx(block: dict, e: float) -> str:
        return f"{block[f'{e:.2f}']['max']:.3f}"

    k = len(EPSILONS)
    colspec = "@{}l" + "".join([r"S[table-format=1.3]"] * (2 * k)) + "@{}"
    header_eps = " & ".join(
        r"\multicolumn{2}{c}{" + f"${e:.2f}$" + "}" for e in EPSILONS
    )
    cmidrules = " ".join(
        rf"\cmidrule(lr){{{2 + 2 * i}-{3 + 2 * i}}}" for i in range(k)
    )
    header_stat = " & ".join([r"{median} & {max}"] * k)

    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\setlength{\tabcolsep}{4pt}",
        (
            r"\caption{Medical illustration of Theorem~A: median and maximum of the"
            "\n"
            r"weighted discrete ratio $\rho_w$ of \cref{eq:tightness} by class and"
            "\n"
            r"$\varepsilon$ (all entries to three decimals).}"
        ),
        r"\label{tab:medical-rho}",
        rf"\begin{{tabular}}{{{colspec}}}",
        r"\toprule",
        r"class / $\varepsilon$ & " + header_eps + r" \\",
        cmidrules,
        r" & " + header_stat + r" \\",
        r"\midrule",
    ]
    for label in ("NORMAL", "PNEUMONIA"):
        cells = " & ".join(
            f"{med(by_eps[label], e)} & {mx(by_eps[label], e)}" for e in EPSILONS
        )
        lines.append(f"{label} & {cells} \\\\")
    lines.append(r"\midrule")
    cells = " & ".join(
        f"{med(by_eps['all'], e)} & {mx(by_eps['all'], e)}" for e in EPSILONS
    )
    lines.append(f"all & {cells} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    text = "\n".join(lines)
    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.write_text(text)
    return text


def file_record(rel: str) -> dict:
    path = HERE / rel
    return {
        "path": rel,
        "bytes": path.stat().st_size,
        "md5": _md5(path),
        "sha256": _sha256(path),
    }


def main() -> None:
    df, summary, inv = load()
    _assert_frozen(summary, df)

    for rel, expected in FROZEN_MD5.items():
        got = _md5(HERE / rel)
        if got != expected:
            raise SystemExit(f"md5 mismatch {rel}: {got} != {expected}")

    n = int(len(df))
    n_holds = int(df["holds"].astype(bool).sum())
    _close(n, summary["n"])
    _close(n_holds, summary["n_holds"])
    _close(float(df["empirical_error_L2"].max()), summary["empirical_error_L2_max"])
    _close(float(df["cfp"].iloc[0]), summary["cfp"], tol=1e-12)
    _close(float(df["diam_U"].iloc[0]), summary["diam_U"])

    recomputed = {
        "rho": {
            "global": _stats(df["rho"]),
            "NORMAL": _stats(df.loc[df["class"] == "NORMAL", "rho"]),
            "PNEUMONIA": _stats(df.loc[df["class"] == "PNEUMONIA", "rho"]),
        },
        "rho_op": {
            "global": _stats(df["rho_op"]),
            "NORMAL": _stats(df.loc[df["class"] == "NORMAL", "rho_op"]),
            "PNEUMONIA": _stats(df.loc[df["class"] == "PNEUMONIA", "rho_op"]),
        },
        "rho_top": {
            "global": _stats(df["rho_top"]),
            "NORMAL": _stats(df.loc[df["class"] == "NORMAL", "rho_top"]),
            "PNEUMONIA": _stats(df.loc[df["class"] == "PNEUMONIA", "rho_top"]),
        },
    }
    for key in ("rho", "rho_op", "rho_top"):
        for group in ("global", "NORMAL", "PNEUMONIA"):
            for stat in ("median", "p90", "max"):
                _close(recomputed[key][group][stat], summary[key][group][stat])

    imax = df["rho"].idxmax()
    max_row = df.loc[imax]
    by_eps = rho_by_epsilon(df)
    write_table(by_eps)

    n_images = int(df["image_id"].nunique())
    n_normal = int(df.loc[df["class"] == "NORMAL", "image_id"].nunique())
    n_pneu = int(df.loc[df["class"] == "PNEUMONIA", "image_id"].nunique())

    global_results = {
        "title": "Theorem A medical illustration — frozen global results",
        "not_a_clinical_validation": True,
        "no_classwise_significance_claimed": True,
        "lhs_metric": (
            "pointwise L2(U) of the first-landscape difference "
            "(not |‖λ‖₂ − ‖λ′‖₂|)"
        ),
        "n_comparisons": n,
        "n_holds": n_holds,
        "frac_holds": float(n_holds / n),
        "n_images": n_images,
        "n_per_class": {"NORMAL": n_normal, "PNEUMONIA": n_pneu},
        "seed": int(inv["seed"]),
        "U": list(inv["U"]),
        "diam_U": float(summary["diam_U"]),
        "cfp": float(summary["cfp"]),
        "cfp_exact": "(9/8)^2",
        "empirical_error_L2_max": float(summary["empirical_error_L2_max"]),
        "bound_at_eps_0_05": float(summary["bound_at_eps_0_05"]),
        "rho": summary["rho"],
        "rho_op": summary["rho_op"],
        "rho_top": summary["rho_top"],
        "synthetic": summary["synthetic"],
        "max_rho": {
            "image_id": str(max_row["image_id"]),
            "class": str(max_row["class"]),
            "epsilon": float(max_row["epsilon"]),
            "delta_linf": float(max_row["delta_linf"]),
            "empirical_error_L2": float(max_row["empirical_error_L2"]),
            "theoretical_bound": float(max_row["theoretical_bound"]),
            "rho": float(max_row["rho"]),
            "rho_op": float(max_row["rho_op"]),
            "rho_top": float(max_row["rho_top"]),
        },
        "rho_by_epsilon": by_eps,
        "invocation": inv,
        "files": {
            "medical_bounds.csv": file_record("results/medical_bounds.csv"),
            "medical_summary.json": file_record("results/medical_summary.json"),
            "invocation.json": file_record("invocation.json"),
            "medical_subset_manifest.json": file_record(
                "medical_subset_manifest.json"
            ),
        },
        "notes": {
            "all_200_rows_hold": n_holds == n,
            "radiographs_stress_envelope_more_than_synthetic": (
                float(max_row["rho"]) > float(summary["synthetic"]["rho_max"])
            ),
            "envelope_not_saturated": float(max_row["rho"]) < 1.0,
            "elevated_rho_op_from_white_noise_not_pathology": True,
        },
    }
    GLOBAL_PATH.write_text(json.dumps(global_results, indent=2) + "\n")
    print("verify_results: OK")
    print(f"  n={n} holds={n_holds}/{n}")
    print(f"  rho median={recomputed['rho']['global']['median']:.6f} "
          f"max={recomputed['rho']['global']['max']:.6f}")
    print(f"  max at {max_row['image_id']} ε={float(max_row['epsilon']):.2f}")
    print(f"  wrote {GLOBAL_PATH}")
    print(f"  wrote {TABLE_PATH}")


if __name__ == "__main__":
    main()
