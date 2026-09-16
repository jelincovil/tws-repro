"""Shared pytest configuration for the tws_validation test-suite.

Two jobs:

1. Make ``tws_validation`` importable without relying on the caller exporting
   ``PYTHONPATH=src``.  The Makefile target does export it, but the CI job in
   ``.github/workflows/python_tests.yml`` runs a bare ``pytest tests/ -v``, so
   the package must be discoverable from the test package itself.
2. Force a headless matplotlib backend before any test imports ``pyplot``.

No test in this suite touches the network, and none of them write into
``results/`` -- anything that needs a file uses pytest's ``tmp_path``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

# --- headless plotting (must precede any pyplot import) --------------------
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib  # noqa: E402

matplotlib.use("Agg", force=True)

# --- make src/ importable --------------------------------------------------
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# --- shared numeric fixtures ----------------------------------------------
#: Seed used throughout the empirical modules; reused so that the suite
#: characterises exactly the configuration the paper reports.
PAPER_SEED = 20260715


@pytest.fixture
def rng() -> np.random.Generator:
    """Deterministic generator, fresh per test."""
    return np.random.default_rng(PAPER_SEED)


@pytest.fixture
def small_field(rng: np.random.Generator) -> np.ndarray:
    """32x32 Gaussian field: divisible by 2**4, so j <= 3 is legal."""
    return rng.normal(0.0, 1.0, (32, 32))


@pytest.fixture
def medium_field(rng: np.random.Generator) -> np.ndarray:
    """48x48 Gaussian field: divisible by 2**4, wide enough for interior tests."""
    return rng.normal(0.0, 1.0, (48, 48))


@pytest.fixture(autouse=True)
def _close_figures():
    """Never leak matplotlib figures between tests."""
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
