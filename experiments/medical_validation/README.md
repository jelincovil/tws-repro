# Medical illustration of Theorem A (chest X-rays)

figure QA: pass, 2026-09-15, 3-paneles. See `figure_qa_report.md`.

Not a clinical validation. Paper integration (`main.tex`) is a later step.

## Paso 0 — metric audit

`empirical_error_L2` **is (a)**: the pointwise
\(\lVert\lambda_1|_U(A_1Z_1)-\lambda_1|_U(A_1Z_2)\rVert_{L^2(U)}\)
computed by `tws_validation.persistence_bounds.landscape_l2_window`
(`sqrt(trapezoid((λ′−λ)², t))`). It is **not** (b) the reverse triangle
on landscape norms.

The first CSV (`results/medical_bounds_v1.csv`) already used (a), with a
512-point grid and local JPEG copies. The frozen invocation below uses
**200** landscape nodes, `cv2.INTER_AREA`, \(\rho_{\mathrm{op}}\) and
\(\rho_{\mathrm{top}}\), and **does not copy** radiographs into the repo.
That is why `medical_bounds.csv` was regenerated.

| | v1 (512-pt grid, local JPEG copies) | v2 (frozen invocation) |
|--|--:|--:|
| median \(\rho\) | 0.151 | 0.149 |
| max \(\rho\) | 0.376 | 0.382 |

## Frozen invocation

| Item | Value |
|------|--------|
| seed | `20260715` (`numpy.random.Generator`) |
| sample | 20 + 20 from `chest_xray/test/{NORMAL,PNEUMONIA}`, no replacement, names then sorted |
| resize | \(256\times 256\), `cv2.INTER_AREA`, grayscale \([0,1]\) |
| invert | \(Z\leftarrow 1-Z\) |
| \(A_1\) | \(k=\frac1{32}[-1,0,9,16,9,0,-1]\), \(k_{2D}=k\otimes k\), `scipy.ndimage.convolve(..., mode="wrap")`. No `pywt`. |
| noise | \(\Delta\sim U(-\varepsilon,\varepsilon)\), \(\varepsilon\in\{0.01,\ldots,0.05\}\), clip to \([0,1]\); RHS uses **measured** \(\lVert\Delta\rVert_\infty\) |
| topology | GUDHI cubical, top-dimensional cells, finite \(H_0\) |
| landscape | \(\lambda_1\), 200 points on \(U=[0.4,0.8]\), `np.trapezoid` |
| \(C_{\mathrm{fp}}\) | \((9/8)^2\) |

Sidecar: `invocation.json`. File list: `medical_subset_manifest.json`.

## Re-run

From `experiments/` (needs `gudhi`, `opencv-python-headless`, local `chest_xray/test/`):

```bash
PYTHONPATH=src python medical_validation/run_medical_experiment.py
PYTHONPATH=src python medical_validation/check_caption.py
```

Rebuild figure/caption from the CSV only:

```bash
PYTHONPATH=src python medical_validation/run_medical_experiment.py --from-csv
```

Two full runs must produce byte-identical `medical_bounds.csv`.

## Outputs

| File | Role |
|------|------|
| `results/medical_bounds.csv` | 200 rows, including `rho_op`, `rho_top`, `holds` |
| `results/medical_bounds_v1.csv` | archived first run (512-point grid) |
| `results/medical_summary.json` | medians / p90 / max |
| `figures/theorem_A_medical_illustration.pdf` | two-panel figure |
| `figures/medical_caption.tex` | caption; numbers from the JSON |
| `tables/medical_rho_by_epsilon.tex` | booktabs |

Radiographs stay in `chest_xray/` (gitignored). Do not copy them here.

## Cite

Kermany et al., *Identifying medical diagnoses and treatable diseases from
images*, Cell 172(5):1122–1131.e9, 2018.
