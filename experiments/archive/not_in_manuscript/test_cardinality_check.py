"""Tests for :mod:`tws_validation.cardinality_check` (Module D, lem:cardbound).

The headline claim under test is the fitted-exponent claim of sec:empirical --

    "a pure counting experiment for lem:cardbound recovered fitted log-log
     slopes for d in {2,3,4} that differed from the expected dimension by at
     most 0.045 in the asymptotic range tested."

The counting model implemented is
``count(d, r, diam, K) = ceil(diam * 2**r + 2K) ** d``.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from tws_validation.cardinality_check import (
    count_indices,
    fit_exponents,
    make_table,
    plot,
)

#: Threshold quoted by the manuscript for |fitted slope - d|.
PAPER_SLOPE_TOLERANCE = 0.045

EXPECTED_TABLE_COLUMNS = [
    "d",
    "diam",
    "r",
    "count",
    "log2_count",
    "old_exponent2_proxy",
    "undercount_factor_vs_old",
]
EXPECTED_FIT_COLUMNS = [
    "d",
    "diam",
    "fit_r_min",
    "fitted_exponent_vs_r",
    "abs_error_vs_d",
    "n_points",
]


@pytest.fixture(scope="module")
def table() -> pd.DataFrame:
    """Default table: ds=(2,3,4), diam in (0.25,0.5,1.0), r in 1..16."""
    return make_table()


@pytest.fixture(scope="module")
def fits(table: pd.DataFrame) -> pd.DataFrame:
    return fit_exponents(table)


# ---------------------------------------------------------------------------
# count_indices
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "d, r, diam, K, expected",
    [
        # Hand-computed as ceil(diam * 2**r + 2K) ** d.
        (1, 0, 1.0, 0.0, 1),        # ceil(1) ** 1
        (1, 1, 1.0, 0.0, 2),        # ceil(2) ** 1
        (1, 2, 1.0, 0.0, 4),        # ceil(4) ** 1
        (1, 2, 0.25, 7.0, 15),      # ceil(1 + 14) ** 1
        (2, 0, 1.0, 0.0, 1),        # ceil(1) ** 2
        (2, 0, 0.25, 1.0, 9),       # ceil(0.25 + 2) = 3 ; 3**2
        (2, 1, 1.0, 7.0, 256),      # ceil(2 + 14) = 16 ; 16**2
        (2, 2, 1.0, 7.0, 324),      # ceil(4 + 14) = 18 ; 18**2
        (3, 1, 1.0, 7.0, 4096),     # 16**3
        (3, 2, 1.0, 1.0, 216),      # ceil(4 + 2) = 6 ; 6**3
        (3, 2, 1.0, 7.0, 5832),     # 18**3
        (4, 1, 1.0, 0.0, 16),       # ceil(2) = 2 ; 2**4
        (4, 2, 0.5, 7.0, 65536),    # ceil(2 + 14) = 16 ; 16**4
        (4, 2, 1.0, 1.0, 1296),     # 6**4
    ],
)
def test_count_indices_exact_small_values(d, r, diam, K, expected):
    assert count_indices(d, r, diam, K) == expected


@pytest.mark.parametrize("d", [1, 2, 3, 4])
@pytest.mark.parametrize("r", [0, 1, 3, 6, 11])
@pytest.mark.parametrize("diam", [0.25, 0.5, 1.0])
def test_count_indices_matches_the_documented_closed_form(d, r, diam):
    expected = int(math.ceil(diam * (2 ** r) + 14.0)) ** d
    assert count_indices(d, r, diam, K=7.0) == expected


def test_count_indices_returns_a_python_int():
    value = count_indices(4, 12, 1.0, 7.0)
    assert isinstance(value, int)
    assert not isinstance(value, (np.integer, float))


@pytest.mark.parametrize("d", [1, 2, 3, 4])
@pytest.mark.parametrize("diam", [0.25, 1.0])
def test_count_indices_is_non_decreasing_in_r(d, diam):
    values = [count_indices(d, r, diam, 7.0) for r in range(0, 15)]
    assert all(b >= a for a, b in zip(values, values[1:])), values
    # and strictly increasing once the window dominates the K-halo
    tail = values[6:]
    assert all(b > a for a, b in zip(tail, tail[1:])), tail


@pytest.mark.parametrize("r", [2, 5, 10])
def test_count_indices_is_strictly_increasing_in_d(r):
    values = [count_indices(d, r, 1.0, 7.0) for d in range(1, 6)]
    assert all(b > a for a, b in zip(values, values[1:])), values


def test_count_indices_grows_like_two_to_the_dr():
    """Incrementing r multiplies the count by ~2**d once r is large.

    Measured relative gap to 2**d at r = 14 -> 15: 8.5e-4 (d=2), 1.3e-3 (d=3),
    1.7e-3 (d=4) -- the residual is the ceil() halo.
    """
    for d in (2, 3, 4):
        ratio = count_indices(d, 15, 1.0, 7.0) / count_indices(d, 14, 1.0, 7.0)
        assert ratio == pytest.approx(2.0 ** d, rel=2.5e-3)
        assert ratio < 2.0 ** d


# ---------------------------------------------------------------------------
# make_table
# ---------------------------------------------------------------------------


def test_make_table_has_the_expected_columns(table):
    assert list(table.columns) == EXPECTED_TABLE_COLUMNS


def test_make_table_has_the_expected_number_of_rows(table):
    # ds (3) x diam_values (3) x rs (16)
    assert len(table) == 3 * 3 * 16 == 144
    assert sorted(table["d"].unique()) == [2, 3, 4]
    assert sorted(table["diam"].unique()) == [0.25, 0.5, 1.0]
    assert sorted(table["r"].unique()) == list(range(1, 17))


def test_make_table_honours_custom_axes():
    df = make_table(ds=(1, 5), rs=range(3, 8), diam_values=(0.5,))
    assert len(df) == 2 * 5 * 1
    assert sorted(df["d"].unique()) == [1, 5]
    assert sorted(df["r"].unique()) == [3, 4, 5, 6, 7]


def test_log2_count_is_consistent_with_count(table):
    assert np.allclose(table["log2_count"], np.log2(table["count"].astype(float)))


def test_old_proxy_column_is_the_d_equals_two_count(table):
    for _, row in table.iterrows():
        assert row["old_exponent2_proxy"] == count_indices(2, int(row["r"]), row["diam"], 7.0)


def test_undercount_factor_is_exactly_one_for_d_equals_two(table):
    """main.tex: the old exponent-2 accounting is invisible in d = 2.

    Measured: every one of the 48 d=2 rows has factor exactly 1.0 (not merely
    within tolerance), since the proxy is by construction count_indices(2, ...).
    """
    d2 = table[table["d"] == 2]
    assert len(d2) == 48
    assert (d2["undercount_factor_vs_old"] == 1.0).all()
    assert d2["undercount_factor_vs_old"].unique().tolist() == [1.0]


@pytest.mark.parametrize("d", [3, 4])
def test_undercount_factor_exceeds_one_for_d_above_two(table, d):
    """For d > 2 the exponent-2 accounting undercounts, increasingly with r."""
    sub = table[table["d"] == d].sort_values(["diam", "r"])
    assert (sub["undercount_factor_vs_old"] > 1.0).all()
    for _, group in sub.groupby("diam"):
        factors = group["undercount_factor_vs_old"].to_numpy()
        assert all(b >= a for a, b in zip(factors, factors[1:]))
    # measured range for d=3: [15.0, 6.55e4]; for d=4: [225.0, 4.30e9]
    assert sub["undercount_factor_vs_old"].min() == pytest.approx(15.0 ** (d - 2), rel=1e-9)


# ---------------------------------------------------------------------------
# fit_exponents -- the manuscript claim
# ---------------------------------------------------------------------------


def test_fit_exponents_has_the_expected_columns(fits):
    assert list(fits.columns) == EXPECTED_FIT_COLUMNS
    # 3 dimensions x 3 window diameters
    assert len(fits) == 9
    assert (fits["fit_r_min"] == 10).all()
    assert (fits["n_points"] == 7).all()  # r = 10..16


@pytest.mark.parametrize("d", [2, 3, 4])
def test_fitted_exponent_is_within_0045_of_the_dimension(fits, d):
    """THE PAPER CLAIM (sec:empirical, lem:cardbound).

    Measured |slope - d| for r_min = 10:

        d=2: 0.022452 (diam 0.25), 0.011356 (0.5), 0.005712 (1.0)
        d=3: 0.033678 (diam 0.25), 0.017035 (0.5), 0.008567 (1.0)
        d=4: 0.044904 (diam 0.25), 0.022713 (0.5), 0.011423 (1.0)
    """
    sub = fits[fits["d"] == d]
    assert len(sub) == 3
    for _, row in sub.iterrows():
        assert row["fitted_exponent_vs_r"] == pytest.approx(d, abs=PAPER_SLOPE_TOLERANCE)
        assert row["abs_error_vs_d"] <= PAPER_SLOPE_TOLERANCE
        # the reported error column agrees with the slope column
        assert row["abs_error_vs_d"] == pytest.approx(
            abs(row["fitted_exponent_vs_r"] - d), abs=1e-12
        )


def test_worst_slope_error_is_0044904_and_only_just_clears_the_claim(fits):
    """FINDING: the 0.045 claim holds, but with a margin of only 9.6e-5.

    Worst case over all nine (d, diam) fits is d=4, diam=0.25:
    |slope - d| = 0.0449041723, i.e. 99.79% of the quoted 0.045 budget.
    Any slightly coarser fitting range or wider window set breaks the claim.
    """
    worst = float(fits["abs_error_vs_d"].max())
    assert worst == pytest.approx(0.0449041723, rel=1e-6)
    assert worst <= PAPER_SLOPE_TOLERANCE
    assert PAPER_SLOPE_TOLERANCE - worst < 1e-4

    worst_row = fits.loc[fits["abs_error_vs_d"].idxmax()]
    assert int(worst_row["d"]) == 4
    assert float(worst_row["diam"]) == 0.25


@pytest.mark.parametrize(
    "r_min, expected_worst_error, clears_paper_claim",
    [
        (8, 0.116760476346, False),
        (10, 0.044904172287, True),
        (12, 0.017632857881, True),
        (14, 0.007380866649, True),
    ],
)
def test_slope_accuracy_depends_on_the_fitting_window(
    table, r_min, expected_worst_error, clears_paper_claim
):
    """FINDING: the claim is conditional on r_min >= 10.

    At r_min = 8 the worst error is 0.1168, i.e. 2.6x the quoted 0.045.  The
    manuscript's qualifier "in the asymptotic range tested" is load-bearing;
    the number is not a property of the estimator at any range.
    """
    worst = float(fit_exponents(table, r_min=r_min)["abs_error_vs_d"].max())
    assert worst == pytest.approx(expected_worst_error, rel=1e-6)
    assert (worst <= PAPER_SLOPE_TOLERANCE) is clears_paper_claim


def test_slope_error_shrinks_monotonically_as_r_min_grows(table):
    errors = [float(fit_exponents(table, r_min=rm)["abs_error_vs_d"].max()) for rm in (8, 10, 12, 14)]
    assert all(b < a for a, b in zip(errors, errors[1:])), errors


def test_fitted_slope_is_never_above_the_dimension(fits):
    """The ceil() halo biases the finite-r slope downwards, never upwards."""
    assert (fits["fitted_exponent_vs_r"] < fits["d"]).all()


def test_larger_windows_give_more_accurate_slopes(fits):
    """diam = 1.0 always beats diam = 0.25 for the same d."""
    for d in (2, 3, 4):
        sub = fits[fits["d"] == d].set_index("diam")
        assert sub.loc[1.0, "abs_error_vs_d"] < sub.loc[0.5, "abs_error_vs_d"]
        assert sub.loc[0.5, "abs_error_vs_d"] < sub.loc[0.25, "abs_error_vs_d"]


# ---------------------------------------------------------------------------
# plot
# ---------------------------------------------------------------------------


def test_plot_writes_a_png_into_the_requested_directory(table, tmp_path):
    out = tmp_path / "nested" / "cardinality_exponent.png"
    returned = plot(table, out=str(out))
    assert returned == str(out)
    assert out.is_file()
    assert out.stat().st_size > 1000
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
