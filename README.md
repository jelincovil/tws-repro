# Companion code: TWS persistence-stability

Numerical and Lean 4 artefacts for

> J. E. Lincovil Curivil, C. D. Reinoso Reinoso, N. Pacheco-Barrios.
> *Explicit \(L^\infty\) stability bounds for undecimated Daubechies
> smoothing and wavelet-filtered persistence landscapes*.
> **arXiv:XXXX.XXXXX** *(placeholder — replace when the preprint is posted)*.

**This repository is not the paper.** It does not contain `main.tex` or the
PDF. Cite the arXiv note; use this repo to regenerate the numbers, the
Lean certificate, and the frozen medical table/figure.

Software: MIT. Radiograph JPEGs are **not** redistributed.

---

## What you can reproduce

| Claim (in the note) | How | Needs extra data? |
|--|--|--|
| 1280 synthetic Theorem A checks, \(\rho\le 1\) | `experiments/` | no |
| Sign-pattern \(\rho_{\mathrm{op}}=1\) | `experiments/` | no |
| db2 level-1 absolute-product sum \((9/8)^2\) in Lean (no periodic convolution) | `formalization/` | no |
| 200/200 medical checks, \(\max\rho=0.38222\) | `medical/` from frozen CSV | no |
| Re-run medical pipeline on Kermany JPEGs | `experiments/medical_validation/` | local `chest_xray/test/` |

Verify frozen hashes:

```bash
shasum -a 256 -c SHA256SUMS
```

---

## Quick start

### A. Frozen medical kit (no GUDHI, no JPEGs)

```bash
cd medical
python -m pip install -r requirements.txt
python verify_results.py
python render_final_figure.py
python check_caption.py
```

Anchors: 200 rows, all `holds`; max \(\rho = 0.38221852267456186\) at
`person33_virus_72.jpeg`, \(\varepsilon=0.02\).

### B. Synthetic suite

```bash
cd experiments
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt   # pytest + pytest-cov (pyproject enables --cov)
PYTHONPATH=src python -m pytest tests/ -q        # 203 passed, 3 xfailed
# optional, ~2.5 min, overwrites the committed CSVs:
# PYTHONPATH=src python -m tws_validation.run_all
```

### C. Lean 4.33.0 (mathlib `db584cd6`)

```bash
cd formalization
lake exe cache get
lake build
lake env lean scripts/print_axioms.lean
```

The exported Lean result is the abstract composition
`TWS.summary_comp_bound` (plus its localized-window specialization and a
concrete non-constant instance) and the finite `db2` computation in
`TWS.DaubechiesOpNorm`.  Persistent homology, bottleneck stability, frame
projection bounds and landscape stability are **external mathematical
inputs**, not formalized.  Axioms of the audited declarations:
`{propext, Classical.choice, Quot.sound}`. Zero `sorry`.  See
[`formalization/README.md`](formalization/README.md) for the
result-to-declaration table and the verification record (2026-10-21:
`lake build` completed with 3009 jobs; 25 audited declarations clean).

### D. Optional: recompute medical rows from images

Place the public Kermany test split under `chest_xray/test/{NORMAL,PNEUMONIA}`
(see `chest_xray/README.md`). Then:

```bash
cd experiments
PYTHONPATH=src python medical_validation/run_medical_experiment.py
```

Two full runs must produce a byte-identical `medical_bounds.csv`.

---

## Layout

```
experiments/       Python validation + committed CSVs
formalization/     Lean 4 companion (abstract bound composition + db2 certificate)
medical/           Autonomous kit (CSV/JSON + figure from frozen numbers)
chest_xray/        README only (how to obtain JPEGs)
```

---

## Citation

Replace `XXXX.XXXXX` when the preprint exists. Until then keep the
placeholder; do not invent an identifier.

```
Lincovil Curivil, J. E., Reinoso Reinoso, C. D., & Pacheco-Barrios, N. (2026).
Explicit L-infinity stability bounds for undecimated Daubechies smoothing
and wavelet-filtered persistence landscapes. arXiv:XXXX.XXXXX.
```

`CITATION.cff` carries the same placeholder under `preferred-citation`.

---

## Reproducibility level, and two known gaps

Reproduction here is **value-level, not byte-level**. Re-running the synthetic
suite on a different NumPy/PyWavelets build reproduces every number quoted in
the note to ~15 significant digits but moves the last float digit (measured
maximum absolute difference: `2.2e-16` on `cfp_estimates.csv`, `8.6e-14` on
`thm_a_trials.csv`). Do not expect `git diff` to be empty after a re-run, and
do not treat that as a failure.

Timings measured on Python 3.12.12 (macOS): `cfp_estimation` 2m24s,
`persistence_bounds` 5.6s, `sign_pattern_extremal` and `extremal_tightness`
under 0.3s each. The canonical pipeline is **~2.5 minutes**, not the hour that
older drafts claimed.

Two artefacts are frozen but not regenerable by any committed command:

- `experiments/results/csv/sign_pattern_extremal.csv` is a **five-row summary**
  (j=0 n=48 ε=0.05; j=1,2,3 n=128 ε=0.03; j=4 n=256 ε=0.02) that documents the
  note's "remains at 1 through j=4" claim. The CLI emits a single richer
  one-row record instead, and the per-grid anchor points used for rows j=1..4
  are not recorded anywhere. Only the j=0 row (n=48, default anchors) is
  reproducible as committed. The underlying quantity is robust — every anchor
  pair tried returns `rho_op = 0.99999…` — but the exact five-row table is not.
  **`run_all` would overwrite this file with the one-row form**, so do not run
  it over the frozen evidence.
- The medical figure is rebuilt from the frozen CSV (numbers asserted against
  hardcoded anchors, zero text overlaps enforced), but its PDF bytes change on
  every run because matplotlib embeds a creation timestamp. The frozen table
  `medical/tables/medical_rho_by_epsilon.tex` and
  `medical/results/global_results.json` **are** byte-reproducible.

---

## What this repo does not do

- Compile or host the LaTeX manuscript.
- Ship Kermany JPEGs.
- Claim a clinical validation or class-wise significance (\(n=20\) per class).
