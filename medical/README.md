# Medical illustration of Theorem A (autonomous kit)

Frozen numerics and the Python that rebuilds the 3-panel figure.
Run from **this folder**. No radiographs, no GUDHI, no `PYTHONPATH`
into `experiments/src`.

Not a clinical validation. No class-wise significance (\(n=20\) per class).

Companion note: **arXiv:XXXX.XXXXX** *(placeholder)*.

## Frozen files

| File | Role |
|------|------|
| `results/medical_bounds.csv` | 200 rows (`rho`, `rho_op`, `rho_top`, `holds`) |
| `results/medical_summary.json` | medians / p90 / max |
| `results/global_results.json` | globals + max-ρ row + hashes |
| `invocation.json` | seed, \(U\), operator, grid |
| `medical_subset_manifest.json` | 20 + 20 filenames (no JPEG payloads) |
| `figures/theorem_A_medical_illustration.{pdf,png}` | 3-panel figure |
| `tables/medical_rho_by_epsilon.tex` | booktabs |

CSV md5: `6be3272f5570ea123fba7de6cb036fcc`.
Summary md5: `738bf317b5fda722ec8c50e269998337`.

- 200/200 rows satisfy \(\rho\le 1\)
- \(\max\rho = 0.38222\) at `person33_virus_72.jpeg`, \(\varepsilon=0.02\)
- global median \(\rho = 0.14933\)
- median \(\rho_{\mathrm{op}} = 0.70147\), \(\rho_{\mathrm{top}} = 0.21228\)

LHS is the pointwise \(L^2(U)\) landscape distance, not
\(|\|\lambda\|_2-\|\lambda'\|_2|\).

## Reproduce

```bash
python -m pip install -r requirements.txt
python verify_results.py
python render_final_figure.py
python check_caption.py
```

To recompute from JPEGs see `../chest_xray/README.md` and
`../experiments/medical_validation/`.
