#!/usr/bin/env python3
"""Render the frozen medical Theorem A figure from CSV/JSON only. No rerun."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "results" / "medical_bounds.csv"
SUMMARY_PATH = HERE / "results" / "medical_summary.json"
INVOCATION_PATH = HERE / "invocation.json"
FIG_PDF = HERE / "figures" / "theorem_A_medical_illustration.pdf"
FIG_PNG = HERE / "figures" / "theorem_A_medical_illustration.png"
CAPTION_TEX = HERE / "figures" / "medical_caption.tex"
SEED = 20260715

EPSILONS = (0.01, 0.02, 0.03, 0.04, 0.05)


def load() -> tuple[pd.DataFrame, dict, dict]:
    df = pd.read_csv(CSV_PATH)
    summary = json.loads(SUMMARY_PATH.read_text())
    inv = json.loads(INVOCATION_PATH.read_text())
    return df, summary, inv


def fmt_tex_sci(x: float) -> str:
    mant, exp = f"{x:.2e}".split("e")
    return f"{mant}\\times 10^{{{int(exp)}}}"


def caption_text(summary: dict, inv: dict, max_row: pd.Series) -> str:
    """LaTeX caption source. Pure: renders the text, writes nothing.

    Split out of ``write_caption`` so read-only callers (``check_caption.py``)
    can compare against the committed caption instead of silently rewriting
    it before comparing.
    """
    return f"""% Auto-generated from medical_summary.json + invocation.json. Do not edit numbers by hand.
% Condensed: invocation details and per-class statistics live in
% \\cref{{sec:medical}} and \\cref{{tab:medical-rho}}.
\\caption{{Numerical illustration on $40$ chest-radiograph arrays with
$200$ artificially perturbed comparisons. Panel (a) compares the
weighted discrete landscape error with the deterministic
upper-bound expression; panel (b) shows the computed tightness ratios;
panel (c) shows their empirical factorization. These floating-point
implementation results are not clinical, statistical, or probabilistic
robustness guarantees.}}
"""


def write_caption(summary: dict, inv: dict, max_row: pd.Series) -> str:
    text = caption_text(summary, inv, max_row)
    CAPTION_TEX.parent.mkdir(parents=True, exist_ok=True)
    CAPTION_TEX.write_text(text)
    return text


def _assert_frozen(summary: dict, df: pd.DataFrame) -> None:
    checks = [
        (summary["empirical_error_L2_max"], 0.012252732864477821),
        (summary["bound_at_eps_0_05"], 0.040022576636506026),
        (summary["rho"]["global"]["max"], 0.38221852267456186),
        (summary["rho_op"]["global"]["median"], 0.7014742006762027),
        (summary["rho_top"]["global"]["median"], 0.21227797021672196),
        (summary["synthetic"]["rho_max"], 0.151),
        (summary["synthetic"]["rho_op_median"], 0.091),
        (summary["synthetic"]["rho_top_median"], 0.084),
    ]
    for a, b in checks:
        if abs(float(a) - b) > 1e-9:
            raise SystemExit(f"JSON mismatch: {a} vs {b}")
    row = df[(df["image_id"] == "person33_virus_72.jpeg") & np.isclose(df["epsilon"], 0.02)]
    if len(row) != 1 or abs(float(row["rho"].iloc[0]) - 0.38221852267456186) > 1e-9:
        raise SystemExit("max-rho row mismatch")


def find_text_overlaps(fig) -> list[tuple[str, str]]:
    import itertools
    import matplotlib
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = [a for a in fig.findobj(matplotlib.text.Text)
             if a.get_text() and a.get_visible() and a.get_text().strip()]
    packed = []
    for t in texts:
        bb = t.get_window_extent(renderer=renderer)
        # Ghost top/right tick labels keep a 1×1 px box at the origin.
        if bb.width < 2 or bb.height < 2:
            continue
        packed.append((t, bb))
    overlaps = []
    for (t1, b1), (t2, b2) in itertools.combinations(packed, 2):
        s1, s2 = t1.get_text(), t2.get_text()
        if not b1.overlaps(b2):
            continue
        # Legitimate: two ticks, or two entries inside the same legend.
        p1, p2 = t1.get_transform(), t2.get_transform()
        same_legend = (getattr(t1, "_legend_handle", None) or
                       str(type(t1.axes.get_legend() if t1.axes else None)))
        is_tick = lambda t: t.get_text() in {x.get_text() for ax in fig.axes
                     for x in list(ax.get_xticklabels()) + list(ax.get_yticklabels())}
        if is_tick(t1) and is_tick(t2):
            continue
        if t1.axes is not None and t1.axes.get_legend() is not None:
            leg_texts = set(t1.axes.get_legend().get_texts())
            if t1 in leg_texts and t2 in leg_texts:
                continue
        if t2.axes is not None and t2.axes.get_legend() is not None:
            leg_texts = set(t2.axes.get_legend().get_texts())
            if t1 in leg_texts and t2 in leg_texts:
                continue
        if s1 in ("0.00", "0.0") and s2 in ("0.00", "0.0"):
            continue
        overlaps.append((s1[:40], s2[:40]))
    return overlaps


def build_figure(df: pd.DataFrame, summary: dict, layout: dict | None = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    L = layout or {}
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "axes.labelsize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    y_emp = float(summary["empirical_error_L2_max"])
    b05 = float(summary["bound_at_eps_0_05"])
    syn_max = float(summary["synthetic"]["rho_max"])
    syn_rop = float(summary["synthetic"]["rho_op_median"])
    syn_rtop = float(summary["synthetic"]["rho_top_median"])
    med_rop = float(summary["rho_op"]["global"]["median"])
    med_rtop = float(summary["rho_top"]["global"]["median"])
    rho_max = float(summary["rho"]["global"]["max"])
    cfp = 1.265625

    rng = np.random.default_rng(SEED)
    fig = plt.figure(figsize=(12.4, 4.6))
    gs = GridSpec(1, 3, width_ratios=[1.2, 1.2, 0.9], wspace=0.34,
                  left=0.08, right=0.99, bottom=0.18, top=0.84)
    ax = fig.add_subplot(gs[0])
    bx = fig.add_subplot(gs[1])
    cx = fig.add_subplot(gs[2])

    # ----- (a) -----
    for label, kw in (
        ("NORMAL", dict(marker="o", facecolors="none", edgecolors="#666666",
                        linewidths=1.2, s=22, label="NORMAL")),
        ("PNEUMONIA", dict(marker="^", c="#444444", edgecolors="#444444",
                           linewidths=0.4, s=22, label="PNEUMONIA")),
    ):
        sub = df[df["class"] == label]
        jitter = rng.uniform(-0.0008, 0.0008, size=len(sub))
        ax.scatter(sub["delta_linf"].to_numpy() + jitter,
                   sub["empirical_error_L2"].to_numpy(),
                   alpha=0.75, zorder=3, **kw)
    xmax = float(df["delta_linf"].max())
    xs = np.linspace(0.0, xmax * 1.06, 400)
    ax.plot(xs, cfp * xs * np.sqrt(0.4), color="black", ls="--", lw=1.5, zorder=2,
            label=r"$(9/8)^2\,\times\,\sqrt{0.4}$")
    ax.set_ylim(0.0, 1.15 * y_emp)
    ax.set_yticks([0.0, 0.004, 0.008, 0.012])
    ax.set_xlim(0.0, xmax * 1.08)
    ax.set_xlabel(r"measured $\|\Delta\|_\infty$")
    ax.set_ylabel(r"Weighted discrete error")
    ax.legend(loc="upper right", bbox_to_anchor=(0.95, 0.95),
              fontsize=9, handlelength=1.8, frameon=False)
    ax.text(0.98, 0.98, rf"bound at $\varepsilon=0.05$: ${b05:.3f}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color="0.2")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    # ----- (b) -----
    eps = list(EPSILONS)
    xpos = np.arange(len(eps), dtype=float)
    width = 0.34
    box_kw = dict(widths=0.28, showfliers=False,
                  medianprops=dict(color="0.15", lw=1.5),
                  whiskerprops=dict(color="0.4", lw=1.0),
                  capprops=dict(color="0.4", lw=1.0),
                  boxprops=dict(color="0.35", lw=1.0))
    pneu_off = width / 2
    for cls, offset, mkr, face, mec in (
        ("NORMAL", -width / 2, "o", "none", "#666666"),
        ("PNEUMONIA", pneu_off, "^", "#444444", "#444444"),
    ):
        data = [df.loc[(df["class"] == cls) & np.isclose(df["epsilon"], e), "rho"].to_numpy()
                for e in eps]
        bx.boxplot(data, positions=xpos + offset, **box_kw)
        for i, ys in enumerate(data):
            js = rng.uniform(-0.25, 0.25, size=len(ys)) * 0.22
            bx.scatter(np.full(len(ys), xpos[i] + offset) + js, ys,
                       marker=mkr, facecolors=face, edgecolors=mec,
                       linewidths=0.6, s=15, alpha=0.6, zorder=3)
    bx.axhline(1.0, color="black", ls="--", lw=1.2, zorder=1)
    bx.axhline(syn_max, color="0.45", ls=":", lw=1.2, zorder=1)
    bx.set_ylim(0.01, 1.5)
    bx.set_yscale("log")
    bx.set_yticks([0.01, 0.03, 0.1, 0.3, 1.0])
    bx.set_yticklabels(["0.01", "0.03", "0.1", "0.3", "1.0"])
    bx.set_xlim(-0.6, 4.6)
    bx.set_xticks(xpos)
    bx.set_xticklabels([f"{e:.2f}" for e in eps])
    bx.set_xlabel(r"nominal $\varepsilon$")
    bx.set_ylabel(r"discrete tightness $\rho_w$")
    bx.text(0.98, 0.985, "saturation (prop. 3.3)", transform=bx.transAxes,
            ha="right", va="top", fontsize=8.5, color="0.2")
    bx.text(0.98, 0.65, "max synthetic (fig. 2)",
            transform=bx.get_yaxis_transform(), ha="right", va="bottom",
            fontsize=8.5, color="0.4")
    bx.annotate("", xy=(4.45, syn_max), xycoords="data",
                xytext=(4.45, 0.63), textcoords="data",
                arrowprops=dict(arrowstyle="->", color="0.45", lw=0.9))
    # epsilon=0.02 -> index 1; PNEUMONIA offset
    xy_max = (1.0 + pneu_off, rho_max)
    xytext_b = L.get("xytext_b", (0.45, 0.65))
    bx.annotate(
        "max $\\rho = 0.382$\nperson33_virus_72\n$\\varepsilon = 0.02$",
        xy=xy_max, xycoords="data",
        xytext=xytext_b, textcoords="axes fraction",
        fontsize=8.5, ha="left", va="bottom", color="0.2",
        arrowprops=dict(arrowstyle="->", color="0.35", lw=0.9),
    )
    # Class legend intentionally omitted here: panel (a) already establishes
    # circles = NORMAL, triangles = PNEUMONIA, and a second legend collided
    # with the "max synthetic (fig. 2)" annotation.
    bx.spines["top"].set_visible(False)
    bx.spines["right"].set_visible(False)
    bx.grid(False)

    # ----- (c) -----
    op_vals = df["rho_op"].to_numpy()
    top_vals = df["rho_top"].to_numpy()
    vp = cx.violinplot([op_vals, top_vals], positions=[1, 2], widths=0.7,
                       showmedians=True, showextrema=False)
    for body in vp["bodies"]:
        body.set_facecolor("#AAAAAA")
        body.set_edgecolor("0.35")
        body.set_alpha(0.5)
        body.set_linewidth(1.0)
    vp["cmedians"].set_color("black")
    vp["cmedians"].set_linewidth(1.5)
    cx.plot([0.72, 1.28], [syn_rop, syn_rop], color="0.45", ls=":", lw=1.0)
    cx.plot([1.72, 2.28], [syn_rtop, syn_rtop], color="0.45", ls=":", lw=1.0)
    cx.text(0.23913043478260873, -0.22, "synthetic med.", transform=cx.transAxes,
            ha="center", va="top", fontsize=8, color="gray")
    cx.text(0.673913043478261, -0.22, "synthetic med.", transform=cx.transAxes,
            ha="center", va="top", fontsize=8, color="gray")
    xytext_op = L.get("xytext_op", (1.35, 0.75))
    xytext_top = L.get("xytext_top", (1.65, 0.35))
    cx.annotate("medical med. 0.701", xy=(1, med_rop),
                xytext=xytext_op, fontsize=8.5, color="0.2",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=0.8))
    cx.annotate("medical med. 0.212", xy=(2, med_rtop),
                xytext=xytext_top, fontsize=8.5, color="0.2",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=0.8))
    cx.set_xticks([1, 2])
    cx.set_xticklabels(["Smoother\nfactor", "Topological\nfactor"])
    cx.set_xlabel("factor")
    cx.set_ylabel("factor value")
    cx.set_ylim(0.0, 1.05)
    cx.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cx.set_xlim(0.45, 2.75)
    cx.spines["top"].set_visible(False)
    cx.spines["right"].set_visible(False)
    cx.grid(False)

    for axis, tag in zip((ax, bx, cx), ("(a)", "(b)", "(c)")):
        axis.text(-0.16, 1.14, tag, transform=axis.transAxes,
                  fontsize=11, fontweight="bold", va="bottom", ha="left",
                  clip_on=False)

    return fig


def save(fig) -> None:
    FIG_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PDF, dpi=300, bbox_inches="tight", pad_inches=0.1)
    fig.savefig(FIG_PNG, dpi=300, bbox_inches="tight", pad_inches=0.1)


def main() -> None:
    import matplotlib.pyplot as plt
    df, summary, inv = load()
    _assert_frozen(summary, df)
    y_emp = float(summary["empirical_error_L2_max"])
    assert y_emp <= 0.0141 + 1e-9
    assert float(df["rho"].max()) <= 1.05

    attempts = [
        {},
        {"xytext_b": (0.52, 0.62), "xytext_op": (1.45, 0.80), "xytext_top": (1.70, 0.40)},
        {"xytext_b": (0.58, 0.70), "xytext_op": (1.50, 0.86), "xytext_top": (1.55, 0.42)},
    ]
    fig = None
    overlaps = None
    for i, layout in enumerate(attempts, 1):
        if fig is not None:
            plt.close(fig)
        fig = build_figure(df, summary, layout)
        overlaps = find_text_overlaps(fig)
        if not overlaps:
            break
        print(f"attempt {i} overlaps: {overlaps}")
    else:
        raise SystemExit(f"FALLO ESTÉTICO: Solapamientos detectados: {overlaps}")

    save(fig)
    data = FIG_PDF.read_bytes()
    if b"/FontFile2" not in data and b"/FontFile3" not in data:
        raise SystemExit("PDF text does not look embedded (no /FontFile2)")
    plt.close(fig)
    print("✅ FIGURA FINAL GENERADA. Cero solapamientos. Estética Q1 aplicada.")
    print(f"wrote {FIG_PDF}")
    print(f"wrote {FIG_PNG}")


if __name__ == "__main__":
    main()
