# tests/

Unit and characterisation tests for `experiments/src/tws_validation/`.

```bash
# From experiments/
PYTHONPATH=src python -m pytest tests/ -v
```

`pytest-cov` is required: `pyproject.toml` sets `--cov`. Install with
`pip install -r requirements.txt -r requirements-dev.txt`.

## Live files

| File | Covers |
|---|---|
| `test_wavelet_projection.py` | `wavelet_projection.py` |
| `test_cfp_estimation.py` | `cfp_estimation.py` (exact row-sum, \(81/64\)) |
| `test_persistence_bounds.py` | Theorem A on a cheap trial |
| `test_sign_pattern_extremal.py` | \(\rho_{\mathrm{op}}=1\) |
| `test_new_modules.py` | tightness figure |
| `conftest.py` | `sys.path`, Agg backend, fixed seeds |

Cardinality tests live with the archived module in
`../archive/not_in_manuscript/`. They are not part of this suite.

Writes never go to `results/`; disk tests use `tmp_path`. Seeds are fixed.

## Claims that the suite still guards

| Claim | Result |
|---|---|
| \(\|A_1\|_{\infty\to\infty}=(9/8)^2=1.265625\) | holds |
| Theorem A bound on a trial | holds |
| Sign-pattern \(\rho_{\mathrm{op}}=1\) | holds |
| \(P_j\) / \(A_{j+1}\) is idempotent | **fails** → `xfail(strict=True)` |

No theorem in the manuscript uses idempotence.
