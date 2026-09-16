"""Tests for :mod:`tws_validation.persistence_bounds` (Module B, thm:A).

This module is the slow one: the published run uses 160 trials (= 1280
    landscape comparisons).  Everything
here is deliberately kept to ``n_trials=1`` on 32x32 fields with the C_fp value
passed in explicitly, which sidesteps the internal ``estimate_cfp`` call.
Measured cost of the whole file: well under a second.

Requires ``gudhi``. Landscapes are sampled from tent functions; ``persim``
is not imported.
"""

from __future__ import annotations

import numpy as np
import pytest

from tws_validation.persistence_bounds import (
    clean_dgm,
    cubical_diagrams,
    gaussian_bump_field,
    landscape_l2_window,
    run_thm_a_trials,
)

#: Optional explicit C_fp override for tests that pin the denominator.
KERNEL_BOUND_K7 = 362.9793901406838

EXPECTED_TRIAL_COLUMNS = [
    "trial",
    "grid_shape",
    "j",
    "k",
    "boundary",
    "noise_sigma",
    "delta_linf",
    "lhs_l2",
    "rhs_thm_a",
    "tightness_ratio",
    "holds",
    "cfp",
    "C_fp_used",
    "constant_type",
    "pdelta_linf",
    "rho_op",
    "rho_top",
]


# ---------------------------------------------------------------------------
# gaussian_bump_field
# ---------------------------------------------------------------------------


def test_gaussian_bump_field_places_the_two_bumps_where_requested():
    """Default centres: +1.0 at (16, 16) sigma 5, -0.8 at (31, 28) sigma 7."""
    field = gaussian_bump_field()
    assert field.shape == (48, 48)
    assert np.unravel_index(np.argmax(field), field.shape) == (16, 16)
    assert np.unravel_index(np.argmin(field), field.shape) == (31, 28)
    # amplitudes are slightly attenuated by the other bump's tail
    assert 0.95 < field.max() < 1.0
    assert -0.8 <= field.min() < -0.75


def test_gaussian_bump_field_honours_a_custom_shape_and_centres():
    field = gaussian_bump_field(shape=(16, 16), centers=((8, 8, 2.0, 3.0),))
    assert field.shape == (16, 16)
    assert field.max() == pytest.approx(2.0, rel=1e-9)
    assert field.min() > 0.0


# ---------------------------------------------------------------------------
# cubical_diagrams / clean_dgm
# ---------------------------------------------------------------------------


def test_cubical_diagrams_returns_one_array_per_homological_degree():
    field = gaussian_bump_field(shape=(32, 32))
    diagrams = cubical_diagrams(field, max_dim=1)
    assert len(diagrams) == 2
    for dgm in diagrams:
        assert dgm.ndim == 2
        assert dgm.shape[1] == 2
        assert dgm.dtype == np.float64
    # a two-bump landscape has at least one essential H0 class
    assert len(diagrams[0]) >= 1


def test_cubical_diagrams_respects_max_dim():
    field = gaussian_bump_field(shape=(16, 16))
    assert len(cubical_diagrams(field, max_dim=0)) == 1
    assert len(cubical_diagrams(field, max_dim=2)) == 3


def test_clean_dgm_drops_infinite_and_degenerate_bars():
    raw = np.array([[0.0, np.inf], [0.0, 1.0], [0.5, 0.5], [-np.inf, 2.0], [0.2, 0.9]])
    cleaned = clean_dgm(raw)
    assert cleaned.shape == (2, 2)
    assert np.array_equal(cleaned, np.array([[0.0, 1.0], [0.2, 0.9]]))


def test_clean_dgm_handles_the_empty_diagram():
    cleaned = clean_dgm(np.empty((0, 2)))
    assert cleaned.shape == (0, 2)


# ---------------------------------------------------------------------------
# landscape_l2_window
# ---------------------------------------------------------------------------


def test_landscape_distance_of_a_diagram_with_itself_is_zero():
    dgm = np.array([[0.0, 1.0], [0.2, 0.7]])
    assert landscape_l2_window(dgm, dgm) == 0.0


def test_landscape_distance_of_two_empty_diagrams_is_zero():
    empty = np.empty((0, 2))
    assert landscape_l2_window(empty, empty) == 0.0


def test_landscape_distance_is_symmetric_and_non_negative():
    a = np.array([[0.0, 1.0], [0.1, 0.6]])
    b = np.array([[0.05, 0.9]])
    forward = landscape_l2_window(a, b)
    backward = landscape_l2_window(b, a)
    assert forward > 0.0
    assert forward == pytest.approx(backward, rel=1e-12)


def test_landscape_distance_grows_with_the_perturbation():
    base = np.array([[0.0, 1.0]])
    near = np.array([[0.0, 1.0 - 0.01]])
    far = np.array([[0.0, 1.0 - 0.20]])
    assert landscape_l2_window(base, near) < landscape_l2_window(base, far)


def test_landscape_distance_is_lipschitz_in_the_bottleneck_shift():
    """Shifting a single bar by eps moves the landscape by O(eps)."""
    base = np.array([[0.0, 1.0]])
    eps = 0.01
    shifted = np.array([[eps, 1.0 + eps]])
    # the tent function moves by eps, over a window of length 2
    assert landscape_l2_window(base, shifted) <= eps * np.sqrt(2.0) + 1e-9


# ---------------------------------------------------------------------------
# run_thm_a_trials -- Theorem A, single trial
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def single_trial():
    """One trial, 32x32, j in {0,1}, exact per-scale operator norm."""
    return run_thm_a_trials(
        n_trials=1,
        seed=20260715,
        shape=(32, 32),
        j_values=(0, 1),
    )


def test_trial_frame_has_the_expected_schema(single_trial):
    assert list(single_trial.columns) == EXPECTED_TRIAL_COLUMNS
    # 1 trial x 2 scales x 2 homological degrees
    assert len(single_trial) == 4
    assert sorted(single_trial["j"].unique()) == [0, 1]
    assert sorted(single_trial["k"].unique()) == [0, 1]
    assert (single_trial["boundary"] == "periodization").all()


def test_theorem_a_bound_holds_on_the_trial(single_trial):
    """sec:empirical -- "No violation was observed in any comparison"."""
    assert single_trial["holds"].all()
    assert (single_trial["lhs_l2"] <= single_trial["rhs_thm_a"]).all()


def test_rhs_matches_the_closed_form(single_trial):
    """rhs = C_fp(j) * ||Z1 - Z2||_inf * sqrt(|U|) with |U| = 2."""
    from tws_validation.cfp_estimation import exact_opnorm
    expected = [
        exact_opnorm(int(j)) * delta * np.sqrt(2.0)
        for j, delta in zip(single_trial["j"], single_trial["delta_linf"])
    ]
    assert np.allclose(single_trial["rhs_thm_a"], expected, rtol=1e-12)


def test_tightness_ratio_is_below_one(single_trial):
    """Against the exact operator norm, generic fields stay strictly below 1."""
    ratios = single_trial["tightness_ratio"]
    assert (ratios > 0.0).all()
    assert ratios.max() < 1.0


def test_default_cfp_is_the_exact_opnorm():
    """cfp=None uses exact_opnorm(j), not the discarded kernel estimate."""
    from tws_validation.cfp_estimation import exact_opnorm

    df = run_thm_a_trials(
        n_trials=1, seed=20260715, shape=(16, 16), j_values=(0,),
    )
    expected = exact_opnorm(0) * df["delta_linf"] * np.sqrt(2.0)
    assert np.allclose(df["rhs_thm_a"], expected, rtol=1e-12)
    assert np.allclose(df["cfp"], exact_opnorm(0), rtol=1e-12)


def test_run_thm_a_trials_is_deterministic():
    import pandas as pd

    kwargs = dict(n_trials=1, seed=7, shape=(32, 32), j_values=(0,), cfp=KERNEL_BOUND_K7)
    pd.testing.assert_frame_equal(run_thm_a_trials(**kwargs), run_thm_a_trials(**kwargs))


def test_noise_sigma_lies_in_the_documented_range(single_trial):
    """The trial generator draws sigma ~ U(0.005, 0.05)."""
    assert (single_trial["noise_sigma"] >= 0.005).all()
    assert (single_trial["noise_sigma"] <= 0.05).all()
    # delta_linf is the sup-norm of the drawn noise field
    assert (single_trial["delta_linf"] > 0.0).all()
    assert (single_trial["delta_linf"] < 0.3).all()


@pytest.mark.parametrize("boundary", ["symmetric", "zero"])
def test_theorem_a_bound_also_holds_for_the_other_boundary_modes(boundary):
    df = run_thm_a_trials(
        n_trials=1,
        seed=20260715,
        shape=(32, 32),
        j_values=(0,),
        boundary=boundary,
        cfp=KERNEL_BOUND_K7,
    )
    assert (df["boundary"] == boundary).all()
    assert df["holds"].all()
    assert df["tightness_ratio"].max() < 1e-2
