#!/usr/bin/env python3
"""Every numeric token in medical_caption.tex must come from JSON/CSV."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from render_final_figure import fmt_tex_sci, load, write_caption  # noqa: E402


def main() -> None:
    df, summary, inv = load()
    imax = df["rho"].idxmax()
    max_row = df.loc[imax]
    expected = write_caption(summary, inv, max_row)
    on_disk = (HERE / "figures" / "medical_caption.tex").read_text()
    if on_disk != expected:
        raise SystemExit("caption on disk != regenerated from JSON")

    must = [
        str(summary["n"]),
        str(summary["n_holds"]),
        fmt_tex_sci(summary["rho"]["global"]["median"]),
        f"{summary['rho']['global']['max']:.3f}",
        f"{summary['rho']['NORMAL']['max']:.3f}",
        f"{summary['rho']['PNEUMONIA']['max']:.3f}",
        f"{summary['rho_op']['global']['median']:.3f}",
        f"{summary['rho_top']['global']['median']:.3f}",
        f"{summary['synthetic']['rho_max']:.3f}",
        f"{summary['synthetic']['rho_op_median']:.3f}",
        f"{summary['synthetic']['rho_top_median']:.3f}",
        fmt_tex_sci(summary["synthetic"]["rho_median"]),
        f"{summary['bound_at_eps_0_05']:.3f}",
        str(inv["seed"]),
        "256",
        str(max_row["image_id"]).replace("_", r"\_"),
        f"{float(max_row['epsilon']):.2f}",
        "n=20",
    ]
    missing = [m for m in must if m not in on_disk]
    if missing:
        raise SystemExit(f"caption missing: {missing}")
    if re.search(r"TO-BE-FILLED|FIXME|XXX", on_disk):
        raise SystemExit("placeholders")
    print("check_caption: OK")


if __name__ == "__main__":
    main()
