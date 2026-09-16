# Experiments

Empirical code for the companion note
(arXiv:XXXX.XXXXX, placeholder). Operator norms, Theorem A, sign-pattern.

Cardinality counting and the sample-pool growth study live in
**`archive/not_in_manuscript/`**. They are not claims of the note.

## Modules

| Module | Source | Main output |
|--------|--------|-------------|
| Operator norm | `cfp_estimation.py` | `results/csv/cfp_estimates.csv`, `daubechies_opnorms.csv` |
| Theorem A | `persistence_bounds.py` | `results/csv/thm_a_trials.csv` (1280 rows) |
| Sign-pattern | `sign_pattern_extremal.py` | `results/csv/sign_pattern_extremal.csv` |
| Tightness figure | `tightness_figure.py` | `thm_a_tightness.png` |

## Run

Relative imports: from this directory, with `PYTHONPATH=src`.

```bash
python -m pip install -r requirements.txt

PYTHONPATH=src python -m tws_validation.run_all
PYTHONPATH=src python -m tws_validation.cfp_estimation      # --n-random 64
PYTHONPATH=src python -m tws_validation.persistence_bounds  # --n-trials 160
PYTHONPATH=src python -m pytest tests/ -v
```

Python 3.11+; `numpy>=2.0` is required (`np.trapezoid`).

`run_all` takes **no** arguments and overwrites the committed CSVs plus
`results/figures/thm_a_tightness.png`.

## Layout

```
experiments/
├── src/tws_validation/
│   ├── wavelet_projection.py
│   ├── cfp_estimation.py
│   ├── persistence_bounds.py
│   ├── sign_pattern_extremal.py
│   ├── tightness_figure.py
│   ├── extremal_tightness.py
│   └── run_all.py
├── tests/
├── results/csv/               # tracked evidence
├── results/figures/
└── archive/not_in_manuscript/
```

There is **no** configuration file. Canonical sizes: `n_random=64`,
`n_trials=160`, seed `20260715`. Full parameter tables:
[`../README.md`](../README.md).

## Headline results

- \(j=0\) exact db2 norm: **1.265625** \(=(9/8)^2\)
- 1280/1280 Theorem A comparisons hold; median tightness \(5.63\times 10^{-3}\)
- Sign-pattern \(\rho_{\mathrm{op}}=1\); amplitude pair \(\rho_{\mathrm{op}}=0.510\)

The RHS of Theorem A uses `exact_opnorm(j)`, not a kernel envelope.

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH=src python -m pytest tests/ -v
```

`pyproject.toml` enables `--cov`; without `pytest-cov` the suite will refuse to
start.

## Troubleshooting

- `ImportError: attempted relative import` — you ran a file by path. Use `-m`.
- `No module named 'gudhi'` — `pip install gudhi` (or conda-forge).
- `numpy has no attribute 'trapezoid'` — NumPy < 2.0.
