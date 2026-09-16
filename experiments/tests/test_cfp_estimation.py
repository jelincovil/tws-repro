"""Tests for :mod:`tws_validation.cfp_estimation` (Module A, the C_fp constant).

Claims under test:

* prop:opnorm -- ``exact_opnorm(0, d=2) = (9/8)^2``.
* leftover ``cfp_kernel_bound(K=7)`` is ~363 and is not used in Theorem A.
* sec:empirical -- "the largest observed empirical L^inf -> L^inf ratio was
  1.248 (at j = 0, periodization)".
* tab:constants / eq:opnorm-family -- C_fp = 1.265625 at j = 0 and the exact
  per-scale family on `Z²`, which exceeds 1.40 from j = 4. Earlier drafts
  quoted an informal 1.1-1.3 band, valid only at j = 0.

NOTE ON THE IMPORT BELOW: ``cfp_estimation`` exports a generator called
``test_inputs``.  Imported under that name into a test module it would be
collected by pytest as a (broken) test, so it is aliased on import.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tws_validation.cfp_estimation import (
    exact_opnorm,
    cfp_kernel_bound,
    estimate_cfp,
    scaling_function_norms,
)
from tws_validation.cfp_estimation import test_inputs as build_test_inputs

PAPER_SEED = 20260715
#: sec:empirical / app:cfp -- "C_fp^ker ~ 363"
PAPER_KERNEL_BOUND = 363.0
#: historical: the 39-input sample maximum, retired in favour of the
#: exact operator norm (9/8)^2. Kept as a regression anchor.
PAPER_MAX_EMPIRICAL_RATIO = 1.2480468750000002
#: Exact L^inf->L^inf operator norm of P_0 (see test_wavelet_projection.py).
OP_NORM_2D_J0 = 81.0 / 64.0

EXPECTED_CFP_COLUMNS = [
    "grid_shape",
    "j",
    "boundary",
    "constant_type",
    "n_inputs",
    "max_ratio",
    "q95_ratio",
    "median_ratio",
    "kernel_bound_K7",
]


# ---------------------------------------------------------------------------
# scaling_function_norms
# ---------------------------------------------------------------------------


def test_scaling_function_norms_reports_the_db2_support_and_norms():
    """db2 (Daubechies-4) has support [0, 3].

    Measured at level 12: ||phi||_inf = 1.36593604, ||phi||_1 = 1.18105218.
    """
    norms = scaling_function_norms("db2", level=12)
    assert set(norms) == {"phi_linf", "phi_l1", "support_grid_min", "support_grid_max"}
    assert norms["support_grid_min"] == 0.0
    assert norms["support_grid_max"] == 3.0
    assert norms["phi_linf"] == pytest.approx(1.3659360421, rel=1e-8)
    assert norms["phi_l1"] == pytest.approx(1.1810521754, rel=1e-8)


@pytest.mark.parametrize(
    "level, expected_linf",
    [
        (8, 1.3645956223),
        (10, 1.3656679603),
        (12, 1.3659360421),
        (14, 1.3660030580),
    ],
)
def test_scaling_function_linf_converges_with_refinement_level(level, expected_linf):
    """The cascade converges from below; ||phi||_1 is already stable at level 8."""
    norms = scaling_function_norms("db2", level=level)
    assert norms["phi_linf"] == pytest.approx(expected_linf, rel=1e-8)
    assert norms["phi_l1"] == pytest.approx(1.1810521754, rel=1e-6)


def test_all_values_are_positive_and_finite():
    norms = scaling_function_norms("db2", level=10)
    assert all(np.isfinite(v) for v in norms.values())
    assert norms["phi_linf"] > 1.0
    assert norms["phi_l1"] > 1.0


# ---------------------------------------------------------------------------
# exact_opnorm -- Proposition / eq:opnorm-family
# ---------------------------------------------------------------------------


def test_exact_opnorm_j0_is_nine_eighths_to_the_d():
    assert exact_opnorm(0, d=1) == pytest.approx(9.0 / 8.0, rel=1e-12)
    assert exact_opnorm(0, d=2) == pytest.approx((9.0 / 8.0) ** 2, rel=1e-12)


def test_exact_opnorm_family_matches_paper_decimals():
    """eq:opnorm-family, db2, d=2, j=0..6."""
    paper = [1.265625, 1.364151, 1.391375, 1.398358, 1.400115, 1.400555, 1.400665]
    for j, v in enumerate(paper):
        assert exact_opnorm(j, d=2) == pytest.approx(v, abs=5e-7)


def test_exact_opnorm_db3_level1_one_d():
    assert exact_opnorm(0, d=1, wavelet="db3") == pytest.approx(612 / 512, rel=1e-12)
    assert exact_opnorm(0, d=3, wavelet="db2") == pytest.approx((9 / 8) ** 3, rel=1e-12)


# ---------------------------------------------------------------------------
# cfp_kernel_bound -- leftover estimate, not used in the theorems
# ---------------------------------------------------------------------------


def test_kernel_bound_with_K7_is_about_363():
    """Historical kernel estimate (~363). Not the constant of Theorem A.
    """
    bound = cfp_kernel_bound(d=2, K=7)
    assert bound == pytest.approx(362.9793901407, rel=1e-9)
    assert round(bound) == PAPER_KERNEL_BOUND
    assert abs(bound - PAPER_KERNEL_BOUND) < 0.05


def test_kernel_bound_follows_the_2K_plus_1_to_the_d_law():
    """The bound is ((2K+1)**d) * ||phi||_inf * ||phi||_1."""
    norms = scaling_function_norms("db2", 12)
    unit = norms["phi_linf"] * norms["phi_l1"]
    for d in (1, 2, 3):
        for K in (1, 3, 7):
            expected = ((2 * K + 1) ** d) * unit
            assert cfp_kernel_bound(d=d, K=K) == pytest.approx(expected, rel=1e-12)


def test_kernel_bound_is_monotone_in_d_and_K():
    assert cfp_kernel_bound(d=3, K=7) > cfp_kernel_bound(d=2, K=7)
    assert cfp_kernel_bound(d=2, K=7) > cfp_kernel_bound(d=2, K=1)


def test_kernel_bound_is_deliberately_loose():
    """The unused kernel estimate exceeds (9/8)^2 by a factor of ~287.
    """
    assert cfp_kernel_bound(d=2, K=7) / OP_NORM_2D_J0 == pytest.approx(286.8, rel=1e-3)


# ---------------------------------------------------------------------------
# test_inputs (aliased as build_test_inputs)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n_random", [0, 1, 5, 12])
def test_input_generator_yields_n_random_plus_seven_fields(n_random):
    """7 deterministic probes: 4 deltas + 3 sinusoidal textures."""
    items = list(build_test_inputs(shape=(32, 32), n_random=n_random, seed=PAPER_SEED))
    assert len(items) == n_random + 7
    kinds = [k for k, _ in items]
    assert kinds.count("random_sign") == n_random
    assert kinds.count("delta") == 4
    assert kinds.count("deterministic_texture") == 3


def test_input_fields_have_the_requested_shape_and_unit_scale():
    items = list(build_test_inputs(shape=(32, 48), n_random=3, seed=PAPER_SEED))
    for kind, field in items:
        assert field.shape == (32, 48), kind
        assert np.isfinite(field).all(), kind
        assert np.max(np.abs(field)) == pytest.approx(1.0, rel=1e-12), kind


def test_input_generator_is_deterministic_for_a_fixed_seed():
    first = [f for _, f in build_test_inputs(shape=(16, 16), n_random=4, seed=123)]
    second = [f for _, f in build_test_inputs(shape=(16, 16), n_random=4, seed=123)]
    other = [f for _, f in build_test_inputs(shape=(16, 16), n_random=4, seed=124)]
    for a, b in zip(first, second):
        assert np.array_equal(a, b)
    assert not np.array_equal(first[0], other[0])


def test_random_sign_inputs_are_plus_minus_one():
    for kind, field in build_test_inputs(shape=(16, 16), n_random=3, seed=PAPER_SEED):
        if kind == "random_sign":
            assert set(np.unique(field)) <= {-1.0, 1.0}


def test_delta_inputs_have_exactly_one_nonzero_cell():
    deltas = [f for k, f in build_test_inputs(shape=(16, 16), n_random=0, seed=1) if k == "delta"]
    assert len(deltas) == 4
    for field in deltas:
        assert np.count_nonzero(field) == 1
        assert field.sum() == 1.0


# ---------------------------------------------------------------------------
# estimate_cfp
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def small_estimate() -> pd.DataFrame:
    """Cheap sweep (measured ~0.1 s): j in {0,1}, all three boundaries."""
    return estimate_cfp(
        shape=(64, 64),
        j_values=[0, 1],
        boundaries=("periodization", "symmetric", "zero"),
        n_random=8,
        seed=PAPER_SEED,
    )


def test_estimate_cfp_returns_the_expected_frame(small_estimate):
    assert list(small_estimate.columns) == EXPECTED_CFP_COLUMNS
    # 2 scales x 3 boundaries
    assert len(small_estimate) == 6
    assert sorted(small_estimate["j"].unique()) == [0, 1]
    assert sorted(small_estimate["boundary"].unique()) == ["periodization", "symmetric", "zero"]


@pytest.mark.parametrize("n_random", [4, 8])
def test_n_inputs_equals_n_random_plus_seven(n_random):
    df = estimate_cfp(
        shape=(32, 32),
        j_values=[0],
        boundaries=("periodization",),
        n_random=n_random,
        seed=PAPER_SEED,
    )
    assert (df["n_inputs"] == n_random + 7).all()


def test_quantiles_are_ordered(small_estimate):
    assert (small_estimate["max_ratio"] >= small_estimate["q95_ratio"]).all()
    assert (small_estimate["q95_ratio"] >= small_estimate["median_ratio"]).all()


def test_every_empirical_ratio_is_far_below_the_kernel_bound(small_estimate):
    """sec:empirical: "All values stay far below the deliberately loose kernel
    bound of app:cfp with K = 7 (C_fp^ker ~ 363)"."""
    assert np.allclose(small_estimate["kernel_bound_K7"], 362.9793901407, rtol=1e-9)
    assert (small_estimate["max_ratio"] < small_estimate["kernel_bound_K7"]).all()
    assert (small_estimate["max_ratio"] < 2.0).all()


def test_estimate_cfp_reproduces_the_published_1248_ratio():
    """THE HISTORICAL VALUE (retired; see sec:empirical for the current one).

    Configuration used for the published table: shape (128, 128),
    n_random = 32, seed 20260715 -- 39 inputs in total.  Measured max ratio at
    j = 0, periodization: 1.2480468750000002.  Runtime ~0.15 s.
    """
    df = estimate_cfp(
        shape=(128, 128),
        j_values=[0],
        boundaries=("periodization",),
        n_random=32,
        seed=PAPER_SEED,
    )
    row = df.iloc[0]
    assert int(row["n_inputs"]) == 39
    assert row["max_ratio"] == pytest.approx(PAPER_MAX_EMPIRICAL_RATIO, rel=1e-12)
    # main.tex tab:constants band
    assert 1.1 <= row["max_ratio"] <= 1.3


def test_published_ratio_stays_below_the_exact_operator_norm():
    """FINDING: 1.248 is an empirical maximum, not the operator norm.

    The exact L^inf -> L^inf norm of P_0 is 81/64 = 1.265625 and is attained by
    a sign pattern matched to the kernel (see
    test_wavelet_projection.py::test_extremal_sign_pattern_attains_the_operator_norm).
    The 39-input sweep of this module reaches only 98.6% of it, and for j >= 1
    the true norm leaves the informal 1.1-1.3 band of earlier drafts entirely;
    the manuscript now states the exact per-scale family of eq:opnorm-family,
    which exceeds 1.40 from j = 4.
    """
    assert PAPER_MAX_EMPIRICAL_RATIO < OP_NORM_2D_J0
    assert PAPER_MAX_EMPIRICAL_RATIO / OP_NORM_2D_J0 == pytest.approx(0.9861, abs=5e-4)


def test_amplification_decays_with_scale(small_estimate):
    """Coarse-retaining behaviour: median ratio falls sharply as j grows."""
    for boundary, group in small_estimate.groupby("boundary"):
        by_j = group.set_index("j")["median_ratio"]
        assert by_j.loc[1] < by_j.loc[0], boundary
    deeper = estimate_cfp(
        shape=(64, 64),
        j_values=[0, 2, 4],
        boundaries=("periodization",),
        n_random=4,
        seed=PAPER_SEED,
    ).set_index("j")["median_ratio"]
    assert deeper.loc[4] < deeper.loc[2] < deeper.loc[0]


def test_estimate_cfp_is_deterministic():
    kwargs = dict(
        shape=(32, 32),
        j_values=[0],
        boundaries=("periodization",),
        n_random=4,
        seed=PAPER_SEED,
    )
    a = estimate_cfp(**kwargs)
    b = estimate_cfp(**kwargs)
    pd.testing.assert_frame_equal(a, b)


def test_all_ratios_are_finite_and_positive(small_estimate):
    for column in ("max_ratio", "q95_ratio", "median_ratio"):
        assert np.isfinite(small_estimate[column]).all()
        assert (small_estimate[column] > 0.0).all()
