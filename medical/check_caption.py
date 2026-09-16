#!/usr/bin/env python3
"""Every number in medical_caption.tex must agree with the frozen JSON/CSV.

Read-only. The previous version called ``write_caption``, which rewrote the
caption before reading it back, so the comparison was a tautology and a plain
"check" silently mutated a tracked artefact. It now renders the caption with
the pure ``caption_text`` and compares that against the file on disk.

The caption is deliberately condensed: it keeps the two counts (number of
radiographs, number of comparisons) and defers the per-class statistics to
``sec:medical`` and ``tab:medical-rho`` in the manuscript, where they carry
their own assertions. The counts kept here are checked against the data rather
than trusted from the template.
"""
from __future__ import annotations

import re
from pathlib import Path

from render_final_figure import caption_text, load

HERE = Path(__file__).resolve().parent

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

    # Numbers the condensed caption still states inline, each derived from the
    # frozen data (not from the template, which hardcodes them).
    must = [
        str(summary["n"]),                    # 200 comparisons
        str(df["image_id"].nunique()),         # 40 radiographs
    ]
    missing = [m for m in must if m not in on_disk]
    if missing:
        raise SystemExit(f"caption missing: {missing}")

    # Guards the wording fixed in the revision pass: the panel-(a) quantity is
    # the weighted discrete error, not a continuous L2(U) integral.
    if "weighted discrete" not in on_disk:
        raise SystemExit("caption lost the 'weighted discrete' wording")
    if "discretized" in on_disk:
        raise SystemExit("caption still says 'discretized'")

    if re.search(r"TO-BE-FILLED|FIXME|XXX", on_disk):
        raise SystemExit("placeholders")

    print("check_caption: OK")


if __name__ == "__main__":
    main()
