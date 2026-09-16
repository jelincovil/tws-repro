"""Tests for the tightness figure (pure function of the Theorem A CSV)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tws_validation.tightness_figure import plot_tightness

# --------------------------------------------------------------------------
# Tightness figure
# --------------------------------------------------------------------------


def _fake_trials(ratios):
    return pd.DataFrame({"tightness_ratio": np.asarray(ratios, dtype=float)})


def test_plot_tightness_writes_a_png_and_reports_the_right_stats(tmp_path):
    out = tmp_path / "fig.png"
    stats = plot_tightness(_fake_trials([1e-5, 2e-5, 3e-5, 4e-4]), str(out))
    assert out.is_file() and out.stat().st_size > 0
    assert stats["n"] == 4
    assert stats["median"] == pytest.approx(2.5e-5)
    assert stats["max"] == pytest.approx(4e-4)
    assert stats["n_violations"] == 0


def test_plot_tightness_counts_violations_rather_than_hiding_them(tmp_path):
    stats = plot_tightness(_fake_trials([1e-5, 1.5, 2.0]), str(tmp_path / "f.png"))
    assert stats["n_violations"] == 2


def test_plot_tightness_ignores_non_finite_and_non_positive_ratios(tmp_path):
    stats = plot_tightness(
        _fake_trials([1e-5, np.nan, np.inf, 0.0, -1.0, 3e-5]),
        str(tmp_path / "f.png"),
    )
    assert stats["n"] == 2


def test_plot_tightness_refuses_an_empty_input(tmp_path):
    with pytest.raises(ValueError):
        plot_tightness(_fake_trials([]), str(tmp_path / "f.png"))


def test_plot_tightness_matches_the_committed_module_b_csv(tmp_path):
    """The figure in the manuscript must agree with the CSV in the repository."""
    csv = (
        pytest.importorskip("pathlib").Path(__file__).resolve().parents[1]
        / "results" / "csv" / "thm_a_trials.csv"
    )
    if not csv.is_file():
        pytest.skip("Module B results not generated in this checkout")
    stats = plot_tightness(pd.read_csv(csv), str(tmp_path / "f.png"))
    assert stats["n"] == 1280
    assert stats["n_violations"] == 0
    assert stats["median"] == pytest.approx(5.631617e-03, rel=1e-4)
    assert stats["max"] == pytest.approx(0.150615, rel=1e-4)
