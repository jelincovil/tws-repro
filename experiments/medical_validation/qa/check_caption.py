#!/usr/bin/env python3
"""Every numeric token in medical_caption.tex must come from JSON/CSV.

Read-only. This used to call ``write_caption``, which rewrote the caption
before reading it back, so the comparison was a tautology and a plain "check"
silently mutated a tracked artefact. It now renders with the pure
``caption_text`` and compares that against the file on disk.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from render_final_figure import caption_text, fmt_tex_sci, load  # noqa: E402

CAPTION_TEX = HERE / "figures" / "medical_caption.tex"


def main() -> None:
    df, summary, inv = load()
    max_row = df.loc[df["rho"].idxmax()]

    expected = caption_text(summary, inv, max_row)
    on_disk = CAPTION_TEX.read_text()
    if on_disk != expected:
        raise SystemExit(
            "caption on disk != regenerated from JSON; re-run render_final_figure.py"
        )

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
