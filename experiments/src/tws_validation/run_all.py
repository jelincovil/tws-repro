"""Run the companion-note experiments into results/.

CANONICAL INVOCATION. The numbers quoted in the companion note
(arXiv:XXXX.XXXXX, placeholder) come from this driver. The constants
below are the ones documented in the README. They previously disagreed
with both the module CLI defaults and the Makefile, which is why the reported
C_fp value could not be reproduced from the documented commands.

Fixed here:
  Module A  n_random = 64   (was 32 here, while the CLI/Makefile used 64)
  Module B  n_trials = 160  -> 160 * 4 scales * 2 degrees = 1280 comparisons
  seeds     module defaults (20260715); do not override without re-deriving
            every number in the manuscript.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .cfp_estimation import estimate_cfp
from .persistence_bounds import run_thm_a_trials
from .tightness_figure import plot_tightness
from .sign_pattern_extremal import run_sign_pattern

# Canonical experiment constants — keep in sync with README and Makefile.
CFP_SHAPE = (128, 128)
CFP_N_RANDOM = 64
THM_A_N_TRIALS = 160


def main() -> None:
    # This driver takes NO arguments, and silently ignoring them is dangerous:
    # a full run overwrites all five committed CSVs plus the manuscript figure
    # and takes about an hour. Before this guard, `run_all --help` did not print
    # help -- there is no argparse here -- it started the destructive run while
    # the user believed they were asking for usage. Same failure family as the
    # five layers of BLOCKER 1 and the --smoke run that clobbered the paper
    # figure: a command that looks harmless and destroys the canonical artefact.
    # There is no `run_all --smoke`; --smoke belongs to
    # tools/run_full_validation.sh, and `make smoke` is a different recipe again.
    if len(sys.argv) > 1:
        raise SystemExit(
            f"run_all takes no arguments (got: {' '.join(sys.argv[1:])}).\n"
            "\n"
            "It is the CANONICAL driver: it regenerates and OVERWRITES every\n"
            "committed CSV under results/csv/ plus results/figures/"
            "thm_a_tightness.png,\n"
            "and takes roughly an hour. It is deterministic, so the outputs are\n"
            "bit-identical to what is committed -- but run it deliberately.\n"
            "\n"
            "  Full canonical run:\n"
            "    PYTHONPATH=src python -m tws_validation.run_all\n"
            "\n"
            "  Fast smoke check (writes only *_smoke.csv, touches nothing else):\n"
            "    PYTHONPATH=src python -m tws_validation.cfp_estimation \\\n"
            "        --n-random 4 --out results/csv/cfp_estimates_smoke.csv\n"
            "    PYTHONPATH=src python -m tws_validation.persistence_bounds \\\n"
            "        --n-trials 5 --out results/csv/thm_a_trials_smoke.csv\n"
            "\n"
            "  Per-module options: run that module with --help; the modules do\n"
            "  use argparse, this driver does not."
        )

    # experiments/ (parent of src/)
    base = Path(__file__).resolve().parents[1]
    csv_dir = base / "results" / "csv"
    fig_dir = base / "results" / "figures"
    csv_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Module A — C_fp
    cfp = estimate_cfp(shape=CFP_SHAPE, n_random=CFP_N_RANDOM)
    cfp_path = csv_dir / "cfp_estimates.csv"
    cfp.to_csv(cfp_path, index=False)
    print(f"Module A → {cfp_path}  (n_random={CFP_N_RANDOM}, "
          f"n_inputs={int(cfp['n_inputs'].iloc[0])})")

    # Module B — Theorem A. n_trials counts NOISE REALISATIONS; each contributes
    # 4 scales x 2 homological degrees, so the number of landscape comparisons
    # reported in the manuscript is 8 * n_trials.
    thm = run_thm_a_trials(n_trials=THM_A_N_TRIALS)
    thm_path = csv_dir / "thm_a_trials.csv"
    thm.to_csv(thm_path, index=False)
    holds = bool(thm["holds"].all()) if "holds" in thm.columns else False
    print(f"Module B → {thm_path} "
          f"({len(thm)} comparisons from {THM_A_N_TRIALS} trials, all holds={holds})")
    if not holds:
        raise SystemExit(
            "At least one Thm A trial violated the bound; inspect CSV before manuscript use."
        )

    # Figure — tightness histogram, derived from the Module B CSV just written.
    tight_path = fig_dir / "thm_a_tightness.png"
    stats = plot_tightness(thm, str(tight_path))
    paper_fig = base.parent / "paper" / "figures" / "thm_a_tightness.png"
    if paper_fig.parent.is_dir():
        plot_tightness(thm, str(paper_fig))
    print(f"Figure → {tight_path} (median={stats['median']:.3e}, "
          f"max={stats['max']:.3e})")

    # Sign-pattern pair attaining the Theorem A constant (seconds, not hours).
    sharp = run_sign_pattern()
    sharp_path = csv_dir / "sign_pattern_extremal.csv"
    pd.DataFrame([sharp]).to_csv(sharp_path, index=False)
    print(f"Sharpness → {sharp_path}  rho_op={sharp['rho_op']:.16f}")

    print("Wrote operator-norm, Theorem A, tightness figure, and sign-pattern pair.")


if __name__ == "__main__":
    main()
