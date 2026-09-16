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
| db2 first-level norm \((9/8)^d\) in Lean | `formalization/` | no |
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
PYTHONPATH=src python -m pytest tests/ -q
# optional, ~1 h, overwrites committed CSVs:
# PYTHONPATH=src python -m tws_validation.run_all
```

### C. Lean 4.33.0 (mathlib `db584cd6`)

```bash
cd formalization
lake exe cache get
lake build
./scripts/print_axioms.sh
```

Axioms of the audited declarations:
`{propext, Classical.choice, Quot.sound}`. Zero `sorry`.

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
formalization/     Lean 4 companion (QMF + composition skeleton)
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

## What this repo does not do

- Compile or host the LaTeX manuscript.
- Ship Kermany JPEGs.
- Claim a clinical validation or class-wise significance (\(n=20\) per class).
