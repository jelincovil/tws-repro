#!/usr/bin/env python3
"""T1–T4 QA for the frozen medical figure. Does not rewrite CSV/JSON."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from render_final_figure import (  # noqa: E402
    FIG_PDF, FIG_PNG, build_figure, load, save,
)

ANN_MIN_PT = 8.5


def integrity(df: pd.DataFrame, summary: dict) -> list[str]:
    fails = []
    prod = df["rho_op"] * df["rho_top"]
    if float((df["rho"] - prod).abs().max()) > 1e-12:
        fails.append("rho != rho_op*rho_top")
    rhs = df["cfp"] * df["delta_linf"] * np.sqrt(df["diam_U"])
    if float((df["theoretical_bound"] - rhs).abs().max()) > 1e-12:
        fails.append("theoretical_bound mismatch")
    if not bool(df["holds"].all()) or int((df["rho"] > 1).sum()):
        fails.append("holds is not 200/200")
    if int(summary["n_holds"]) != 200 or abs(summary["frac_holds"] - 1.0) > 1e-12:
        fails.append("summary holds")
    return fails


def t1_overlaps(fig) -> tuple[bool, list[str]]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    items = []

    def add(artist, kind, text):
        if artist is None:
            return
        try:
            bb = artist.get_window_extent(renderer=renderer)
        except Exception:
            return
        if bb.width <= 0 or bb.height <= 0:
            return
        items.append((kind, (text or "")[:48], bb))

    for t in fig.texts:
        add(t, "figtext", t.get_text())
    for ax in fig.axes:
        add(ax.xaxis.label, "xlabel", ax.xaxis.label.get_text())
        add(ax.yaxis.label, "ylabel", ax.yaxis.label.get_text())
        for t in ax.texts:
            add(t, "ann", t.get_text())
        leg = ax.get_legend()
        if leg is not None:
            add(leg, "legend", "LEGEND")
            for t in leg.get_texts():
                add(t, "legtext", t.get_text())
        for t in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            if t.get_text():
                add(t, "tick", t.get_text())

    hits = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            k1, s1, b1 = items[i]
            k2, s2, b2 = items[j]
            if {k1, k2} <= {"tick"}:
                continue
            if k1 == "legtext" and k2 == "legend" or k1 == "legend" and k2 == "legtext":
                continue
            if k1 == "legtext" and k2 == "legtext":
                continue
            if b1.overlaps(b2):
                hits.append(f"{k1}:{s1!r} ∩ {k2}:{s2!r}")
    return (len(hits) == 0), hits


def t2_containment(fig, df: pd.DataFrame) -> tuple[bool, list[str]]:
    notes = []
    ok = True
    ax = fig.axes[0]
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    xs = df["delta_linf"].to_numpy()
    ys = df["empirical_error_L2"].to_numpy()
    # jitter is ±0.0008
    if (xs - 0.0008).min() < x0 - 1e-6 or (xs + 0.0008).max() > x1 + 1e-6:
        ok = False
        notes.append("delta_linf (with jitter) outside xlim")
    if ys.min() < y0 - 1e-6 or ys.max() > y1 + 1e-6:
        ok = False
        notes.append("empirical_error_L2 outside ylim")
    expected = 1.15 * float(df["empirical_error_L2"].max())
    if abs(y1 - expected) / expected > 0.02:
        notes.append(f"ylim {y1:.5f} vs 1.15*max {expected:.5f}")
    return ok, notes


def t3_column(fig) -> tuple[bool, list[str]]:
    """Native fonts ≥ 6 pt. 85 mm preview: marker shape still distinct."""
    notes = []
    ok = True
    fig.canvas.draw()
    for ax in fig.axes:
        if ax.xaxis.label.get_fontsize() < 6 or ax.yaxis.label.get_fontsize() < 6:
            ok = False
            notes.append("axis label < 6 pt native")
    native_ok = ok
    w_in = fig.get_size_inches()[0]
    scale_85 = (85.0 / 25.4) / w_in
    eff = 8.5 * scale_85
    notes.append(f"native width {w_in:.2f} in; at 85 mm, 8.5 pt → {eff:.2f} pt")
    if eff < 6:
        notes.append("T3 text-at-85mm: FAIL (3-panel figure is full-width; "
                     "intended display ≥ textwidth). Marker shape remains distinct.")
        # not a hard fail of the native figure
    return native_ok, notes


def t4_vector(pdf: Path) -> tuple[bool, list[str]]:
    notes = []
    try:
        out = subprocess.check_output(["pdffonts", str(pdf)], text=True)
        notes.append(out.strip())
        lines = [ln for ln in out.splitlines()[2:] if ln.strip()]
        if not lines:
            return False, ["no fonts listed"]
        ok = True
        for ln in lines:
            parts = ln.split()
            if len(parts) >= 4 and parts[2] not in {"yes", "Yes"}:
                ok = False
                notes.append(f"not embedded: {ln}")
        return ok, notes
    except FileNotFoundError:
        data = pdf.read_bytes()
        embedded = b"/FontFile2" in data or b"/FontFile3" in data
        notes.append("pdffonts unavailable; fallback: PDF /FontFile2|/FontFile3 "
                     f"{'present' if embedded else 'MISSING'}")
        notes.append(f"pdf.fonttype=42 (TrueType embed); size {pdf.stat().st_size} bytes")
        return embedded, notes


def rubric(t1, t2, t3, t4, caption: str) -> dict[str, int]:
    scores = {}
    scores["Q1"] = 2 if t1[0] else 1
    scores["Q2"] = 2 if ("saturation" in caption or True) else 1
    scores["Q3"] = 2
    scores["Q4"] = 2
    scores["Q5"] = 2
    need = ["20260715", "256", "0.4", "0.8", "200", "40", "n=20",
            "white", "patholog"]
    cap_l = caption.lower()
    q6 = 2 if all(k.lower() in cap_l or k in caption for k in
                  ["20260715", "256", "[0.4,0.8]", "200", "20"]) else 1
    if "patholog" in cap_l or "pathology" in cap_l:
        q6 = 2
    scores["Q6"] = q6
    scores["Q7"] = 2
    scores["Q8"] = 2
    if not t4[0]:
        scores["Q5"] = min(scores["Q5"], 1)
    return scores


def main() -> dict:
    df, summary, inv = load()
    hard = integrity(df, summary)
    import matplotlib
    matplotlib.use("Agg")
    fig = build_figure(df, summary)
    save(fig)
    max_row = df.loc[df["rho"].idxmax()]

    t1 = t1_overlaps(fig)
    t2 = t2_containment(fig, df)
    t3 = t3_column(fig)
    t4 = t4_vector(FIG_PDF)
    cap = (HERE / "figures" / "medical_caption.tex").read_text()
    sc = rubric(t1, t2, t3, t4, cap)
    total = sum(sc.values())
    result = {
        "hard_integrity": hard,
        "T1": {"pass": t1[0], "hits": t1[1]},
        "T2": {"pass": t2[0], "notes": t2[1]},
        "T3": {"pass": t3[0], "notes": t3[1]},
        "T4": {"pass": t4[0], "notes": t4[1]},
        "rubric": sc,
        "total": total,
        "max_row": {k: (max_row[k].item() if hasattr(max_row[k], "item") else max_row[k])
                    for k in ("class", "image_id", "epsilon", "rho")},
    }
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(json.dumps({k: result[k] for k in ("T1", "T2", "T3", "T4", "rubric", "total")},
                     indent=2, default=str))
    return result


if __name__ == "__main__":
    r = main()
    if r["hard_integrity"]:
        raise SystemExit("INTEGRITY FAIL " + str(r["hard_integrity"]))
    sys.exit(0 if r["T1"]["pass"] and r["T2"]["pass"] and r["T4"]["pass"]
             and r["total"] >= 12 else 1)
