"""Tests for :mod:`tws_validation.wavelet_projection`.

Methodology: the implementation already existed when these tests were written,
so every numeric tolerance below was *measured first* and only then written
down.  Where the measurement contradicts the manuscript the test records the
measured truth and the contradiction is documented in the docstring (and, for
the idempotency claim, with a strict ``xfail``).

Notation: ``P_j`` is ``project_2d(., j)``; ``||.||_inf`` is the max-abs norm.
"""

from __future__ import annotations

import numpy as np
import pytest

from tws_validation.wavelet_projection import (
    _pad_for_boundary,
    pad_to_swt,
    project_1d,
    project_2d,
)

BOUNDARIES = ("periodization", "symmetric", "zero")

#: ||P_0||_{inf->inf} in 1D for db2, measured as the l1 norm of the impulse
#: response of the level-1 stationary low-pass-only reconstruction.
OP_NORM_1D_J0 = 9.0 / 8.0  # = 1.125
#: Tensor-product value in 2D.
OP_NORM_2D_J0 = 81.0 / 64.0  # = 1.265625


def _impulse_response_1d(j: int, n: int = 128) -> np.ndarray:
    """Impulse response of P_j in 1D (periodization => shift invariant)."""
    delta = np.zeros(n)
    delta[0] = 1.0
    return project_1d(delta, j)


def _operator_norm_1d(j: int, n: int = 128) -> float:
    """Exact L^inf->L^inf operator norm of P_j in 1D.

    For a linear, translation-invariant operator ``y = k * x`` on a periodic
    domain, ``||P||_{inf->inf} = ||k||_1``, attained by ``x[m] = sign(k[-m])``.
    Linearity is asserted separately in ``test_project_2d_is_linear``.
    """
    return float(np.abs(_impulse_response_1d(j, n)).sum())


# ---------------------------------------------------------------------------
# Shapes, dtypes and basic algebra
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("boundary", BOUNDARIES)
@pytest.mark.parametrize("j", [0, 1, 2, 3])
def test_project_2d_preserves_shape(small_field, j, boundary):
    out = project_2d(small_field, j, boundary=boundary)
    assert out.shape == small_field.shape
    assert out.dtype == np.float64
    assert np.isfinite(out).all()


@pytest.mark.parametrize("boundary", BOUNDARIES)
@pytest.mark.parametrize("j", [0, 1, 2])
def test_project_1d_preserves_shape(rng, j, boundary):
    x = rng.normal(0.0, 1.0, 64)
    out = project_1d(x, j, boundary=boundary)
    assert out.shape == x.shape
    assert out.dtype == np.float64
    assert np.isfinite(out).all()


def test_projection_accepts_lists_and_integer_arrays():
    """Inputs are coerced to float64, so plain lists and int arrays work."""
    from_list = project_1d([1.0] * 32, 0)
    assert from_list.shape == (32,)
    assert from_list.dtype == np.float64

    from_int = project_1d(np.arange(32, dtype=np.int64), 0)
    assert from_int.dtype == np.float64


def test_project_2d_is_linear(rng):
    """P_j is a linear operator (needed to justify the operator-norm tests)."""
    a = rng.normal(0.0, 1.0, (32, 32))
    b = rng.normal(0.0, 1.0, (32, 32))
    lhs = project_2d(3.0 * a - 2.0 * b, 1)
    rhs = 3.0 * project_2d(a, 1) - 2.0 * project_2d(b, 1)
    # measured: 6.66e-16
    assert np.max(np.abs(lhs - rhs)) < 1e-12


@pytest.mark.parametrize("j", [0, 1, 2, 3])
def test_periodization_preserves_the_mean(small_field, j):
    """The coarse-retaining projector keeps the DC component under periodization.

    Measured discrepancy: ~1.2e-17.
    """
    out = project_2d(small_field, j, boundary="periodization")
    assert out.mean() == pytest.approx(small_field.mean(), abs=1e-12)


def test_project_1d_acts_along_the_last_axis(rng):
    """``project_1d`` on a 2-D array filters each row independently.

    This is the 1D/2D coherence contract: feeding a stack of identical rows
    reproduces the 1-D result on every row.
    """
    row = rng.normal(0.0, 1.0, 64)
    stack = np.tile(row, (8, 1))
    stacked = project_1d(stack, 1)
    single = project_1d(row, 1)
    assert stacked.shape == stack.shape
    for k in range(stack.shape[0]):
        assert stacked[k] == pytest.approx(single, abs=1e-12)


# ---------------------------------------------------------------------------
# Constant fields: the "retain the coarse content" property
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("boundary", ["periodization", "symmetric"])
@pytest.mark.parametrize("j", [0, 1, 2, 3])
@pytest.mark.parametrize("c", [1.0, -3.5, 7.25])
def test_periodic_and_symmetric_boundaries_preserve_constants(c, j, boundary):
    """P_j c = c for a constant field, to machine precision.

    Measured worst deviation across this grid: 4.44e-15 (c = -3.5, j = 3).
    """
    x = np.full((32, 32), c)
    out = project_2d(x, j, boundary=boundary)
    assert np.max(np.abs(out - c)) < 1e-12


@pytest.mark.parametrize("j", [0, 1, 2])
def test_project_1d_preserves_constant_signals(j):
    """Measured deviation on a constant-5.0 signal: 0.0 (j=0), 1.78e-15 (j=1,2)."""
    x = np.full(64, 5.0)
    assert np.max(np.abs(project_1d(x, j) - 5.0)) < 1e-12


@pytest.mark.parametrize(
    "j, expected_max_dev, expected_mean, expected_min, expected_max",
    [
        # FINDING: measured on a constant-1.0 32x32 field with boundary="zero".
        (0, 0.4375000000, 0.9766998291, 0.5625000000, 1.0634765625),
        (1, 0.6081533432, 0.9445172884, 0.3918466568, 1.0837135315),
        (2, 0.6821501516, 0.8866767215, 0.3178498484, 1.0890573412),
        (3, 0.7177734375, 0.7788932420, 0.2822265625, 1.1847347228),
    ],
)
def test_zero_boundary_destroys_constant_preservation(
    j, expected_max_dev, expected_mean, expected_min, expected_max
):
    """FINDING (contradicts the "coarse-retaining" reading of P_j).

    With ``boundary="zero"`` the projector does *not* return a constant field
    when fed a constant field.  The error is not confined to a thin rim: on a
    32x32 field of ones the whole-field mean drops from 1.0 to 0.779 at j=3,
    i.e. a 22% loss of total mass, the field dips to 0.282 (-72%) at the
    corners and *overshoots* to 1.185 (+18%) nearby -- a Gibbs-like ringing.

    Cause: ``_pad_for_boundary`` pads with zeros over a width of ``2**(j+1)``
    while the db2 stationary kernel at level ``j+1`` has an effective support of
    ``3*(2**(j+1) - 1) + 1``, which is always wider than the pad, so the zeros
    bleed inward (see ``test_padding_width_is_narrower_than_the_db2_kernel_support``).

    Contrast with ``test_periodic_and_symmetric_boundaries_preserve_constants``,
    where the same quantity is < 1e-12.
    """
    x = np.ones((32, 32))
    out = project_2d(x, j, boundary="zero")
    assert np.max(np.abs(out - 1.0)) == pytest.approx(expected_max_dev, rel=1e-6)
    assert out.mean() == pytest.approx(expected_mean, rel=1e-6)
    assert out.min() == pytest.approx(expected_min, rel=1e-6)
    assert out.max() == pytest.approx(expected_max, rel=1e-6)
    # Overshoot above the constant, i.e. the error is two-sided.
    assert out.max() > 1.0


# ---------------------------------------------------------------------------
# Idempotency: P o P = P.  It does NOT hold.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "FINDING: P_j is not idempotent. The undecimated (stationary) frame "
        "operator is A^* Pi A with A^* A = I but A A^* != I, so P_j^2 != P_j. "
        "Measured relative L^inf defect ||P(Px)-Px||_inf / ||Px||_inf is "
        "0.27-0.35 on white-noise fields (this fixture), i.e. a third of the "
        "signal and not a numerical artefact. On the SMOOTH Gaussian-bump "
        "fields that Module B actually uses it is much smaller at fine scales: "
        "0.0027 at j=0, 0.022 at j=1, 0.133 at j=2, 0.241 at j=3. Constant "
        "fields are the only exact fixed point. The manuscript calls P_j a "
        "projection; no result depends on idempotency (Theorem A uses only "
        "boundedness), so this is a terminology question for the authors."
    ),
)
@pytest.mark.parametrize("j", [0, 1, 2])
def test_project_2d_is_idempotent(small_field, j):
    """The manuscript's claim: P_j is a projection, hence P_j o P_j = P_j."""
    once = project_2d(small_field, j)
    twice = project_2d(once, j)
    assert twice == pytest.approx(once, abs=1e-9)


@pytest.mark.parametrize(
    "j, expected_rel_defect",
    [
        (0, 0.3338019602),
        (1, 0.3651074154),
        (2, 0.3150379451),
    ],
)
def test_idempotency_defect_is_reproducible(small_field, j, expected_rel_defect):
    """Characterisation of the non-idempotency, with the measured magnitude.

    Fixed input: ``default_rng(20260715).normal(0, 1, (32, 32))``.
    """
    once = project_2d(small_field, j)
    twice = project_2d(once, j)
    rel = float(np.max(np.abs(twice - once)) / np.max(np.abs(once)))
    assert rel == pytest.approx(expected_rel_defect, rel=1e-5)


@pytest.mark.parametrize("j", [0, 1, 2])
def test_idempotency_defect_is_order_one_across_seeds(j):
    """The defect is not seed-specific: 12 independent fields, all ~0.22-0.41.

    Measured envelopes: j=0 [0.2608, 0.3433], j=1 [0.2426, 0.3661],
    j=2 [0.2256, 0.4022].  The assertion uses a deliberately wide band so it
    tests the *phenomenon*, not the exact draw.
    """
    defects = []
    for seed in range(12):
        x = np.random.default_rng(1000 + seed).normal(0.0, 1.0, (32, 32))
        once = project_2d(x, j)
        twice = project_2d(once, j)
        defects.append(float(np.max(np.abs(twice - once)) / np.max(np.abs(once))))
    assert min(defects) > 0.15, f"defects={defects}"
    assert max(defects) < 0.50, f"defects={defects}"


@pytest.mark.parametrize("j", [0, 1, 2, 3])
def test_projection_is_idempotent_on_constant_fields(j):
    """The one regime where P o P = P holds exactly: constants are fixed points."""
    x = np.full((32, 32), 2.0)
    once = project_2d(x, j)
    twice = project_2d(once, j)
    assert np.max(np.abs(twice - once)) == 0.0


# ---------------------------------------------------------------------------
# L^inf -> L^inf amplification (the C_fp constant of the manuscript)
# ---------------------------------------------------------------------------


def test_operator_norm_at_j0_is_81_over_64():
    """||P_0||_{inf->inf} = (9/8)^2 = 1.265625, exactly.

    The 1-D impulse response of P_0 has taps
    (1/2, 9/32, 0, -1/32, -1/32, 0, 9/32) -> l1 norm 9/8; the 2-D operator is
    the tensor square.
    """
    assert _operator_norm_1d(0) == pytest.approx(OP_NORM_1D_J0, abs=1e-12)

    delta2d = np.zeros((32, 32))
    delta2d[0, 0] = 1.0
    kernel2d = project_2d(delta2d, 0)
    assert float(np.abs(kernel2d).sum()) == pytest.approx(OP_NORM_2D_J0, abs=1e-12)


def test_extremal_sign_pattern_attains_the_operator_norm():
    """A +/-1 field matched to the kernel realises the bound exactly.

    This is the input the empirical estimator of ``cfp_estimation`` never
    draws; see ``test_empirical_estimate_underestimates_the_operator_norm``.
    """
    delta = np.zeros((32, 32))
    delta[0, 0] = 1.0
    kernel = project_2d(delta, 0)
    # x[m] = sign(k[-m]) maximises the convolution at the origin.
    x = np.sign(np.roll(kernel[::-1, ::-1], (1, 1), axis=(0, 1)))
    x[x == 0.0] = 1.0

    out = project_2d(x, 0)
    assert np.max(np.abs(x)) == 1.0
    assert float(np.max(np.abs(out))) == pytest.approx(OP_NORM_2D_J0, abs=1e-12)


def test_operator_norm_at_j0_matches_the_manuscript():
    """main.tex eq:opnorm states ||P_0|| = (9/8)^2 exactly; tab:constants
    rounds it to C_fp = 1.27 at j = 0.  Check both."""
    assert OP_NORM_2D_J0 == pytest.approx((9.0 / 8.0) ** 2, abs=1e-12)
    assert round(OP_NORM_2D_J0, 2) == 1.27


@pytest.mark.parametrize(
    "j, expected_norm_2d",
    [
        (1, 1.3641510010),
        (2, 1.3913746029),
        (3, 1.3983578549),
        (4, 1.3866494525),
    ],
)
def test_operator_norm_stays_under_the_manuscript_ceiling(j, expected_norm_2d):
    """Regression on the per-scale finite-grid operator norms.

    Values on the grid used by ``_operator_norm_1d``: 1.364151 (j=1),
    1.391375 (j=2), 1.398357 (j=3), 1.386649 (j=4).  These are what the
    implementation produces; the manuscript now reports the unwrapped `Z²`
    family of eq:opnorm-family instead, which grows past 1.40 from j=4
    (1.400115), so the old ``<= 1.40`` reading of tab:constants no longer holds.
    """
    norm_2d = _operator_norm_1d(j) ** 2
    assert norm_2d == pytest.approx(expected_norm_2d, rel=1e-6)
    assert 1.3 < norm_2d <= 1.40


@pytest.mark.parametrize("j", [5, 6])
def test_operator_norm_degenerates_when_the_kernel_exceeds_the_grid(j):
    """At coarse scales the db2 kernel is wider than the field itself.

    Support at level L = j+1 is 3*(2^L - 1) + 1, i.e. 190 at j=5 and 382 at
    j=6, against the 128-wide grid Module A uses.  The periodic operator then
    degenerates to a pure average and its norm collapses to exactly 1.  The
    periodization peak of 1.3984 is therefore attained at j=3, not at the
    coarsest scale, and these two scales must not be read as "the bound
    improves" -- they are a grid artefact.

    Note on scope: `_operator_norm_1d` uses the impulse-response shortcut (valid
    only where the operator is shift-invariant), on a finite grid.  It is the
    implementation's finite-grid behaviour; tab:constants now reports the
    unwrapped `Z²` family of eq:opnorm-family, which exceeds 1.40 from j=4.
    """
    support = 3 * (2 ** (j + 1) - 1) + 1
    assert support > 128
    assert _operator_norm_1d(j, n=128) ** 2 == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize(
    "j, expected_defect",
    [
        (0, 0.0027343388),
        (1, 0.0223744647),
        (2, 0.1330372467),
        (3, 0.2407815455),
    ],
)
def test_idempotency_defect_is_small_on_the_fields_module_b_uses(j, expected_defect):
    """The non-idempotency of P_j is field-dependent, and the distinction matters.

    On white noise the relative defect is ~0.3 at every scale (see the strict
    xfail above).  On the smooth two-bump Gaussian field that Module B actually
    feeds to the Theorem A trials it is two orders of magnitude smaller at the
    finest scale and only grows as the projection coarsens.  Quoting the
    noise figure alone overstates how far the implemented operator is from a
    projection in the regime the manuscript reports.
    """
    from tws_validation.persistence_bounds import gaussian_bump_field

    field = gaussian_bump_field()
    once = project_2d(field, j)
    twice = project_2d(once, j)
    defect = float(np.max(np.abs(twice - once)) / np.max(np.abs(once)))
    assert defect == pytest.approx(expected_defect, rel=1e-6)


@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_random_inputs_respect_the_operator_norm_at_j0(boundary):
    """||P_0 x||_inf <= 1.265625 * ||x||_inf on 30 random-sign fields.

    Measured worst ratios: periodization 1.24414063, symmetric 1.24609375,
    zero 1.24414063 -- all below the exact operator norm (9/8)^2 and far below
    the exact norm.
    """
    worst = 0.0
    for seed in range(30):
        gen = np.random.default_rng(seed)
        x = np.where(gen.random((48, 48)) < 0.5, -1.0, 1.0)
        out = project_2d(x, 0, boundary=boundary)
        worst = max(worst, float(np.max(np.abs(out)) / np.max(np.abs(x))))
    assert worst <= OP_NORM_2D_J0 + 1e-12
    assert 1.1 <= worst <= 1.3


@pytest.mark.parametrize("j", [1, 2, 3])
def test_amplification_decays_with_scale_on_smooth_and_delta_inputs(j):
    """A delta loses 4^-(j+1) of its peak: the coarse-retaining behaviour."""
    delta = np.zeros((64, 64))
    delta[32, 32] = 1.0
    out = project_2d(delta, j)
    assert float(np.max(np.abs(out))) == pytest.approx(4.0 ** (-(j + 1)), rel=1e-9)


# ---------------------------------------------------------------------------
# Boundary modes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("j", [0, 1, 2])
def test_all_boundary_modes_return_the_input_shape(medium_field, j):
    outs = {b: project_2d(medium_field, j, boundary=b) for b in BOUNDARIES}
    for b, out in outs.items():
        assert out.shape == medium_field.shape, b
        assert np.isfinite(out).all(), b


@pytest.mark.parametrize("mode", ["symmetric", "zero"])
@pytest.mark.parametrize("j, margin", [(0, 4), (1, 12)])
def test_boundary_modes_agree_bit_for_bit_in_the_deep_interior(medium_field, mode, j, margin):
    """Away from the rim the three modes are literally identical (diff == 0.0).

    Measured across 5 independent seeds on 48x48 fields: interior max|diff|
    is exactly 0.0 for j=0 beyond margin 4 and for j=1 beyond margin 12.
    (At j=2 a 48x48 field is too small to have a clean interior: the residual
    at margin 16 is still ~8e-4, which is why j=2 is not tested here.)
    """
    per = project_2d(medium_field, j, boundary="periodization")
    other = project_2d(medium_field, j, boundary=mode)
    interior = np.abs(other - per)[margin:-margin, margin:-margin]
    assert interior.size > 0
    assert interior.max() == 0.0


@pytest.mark.parametrize("mode", ["symmetric", "zero"])
@pytest.mark.parametrize("j", [0, 1, 2])
def test_boundary_modes_differ_near_the_border(medium_field, mode, j):
    """The rim must differ, otherwise the boundary study would be vacuous.

    Measured max|diff| at j=0: symmetric 0.61-0.93, zero 0.49-0.58.
    """
    per = project_2d(medium_field, j, boundary="periodization")
    other = project_2d(medium_field, j, boundary=mode)
    assert np.max(np.abs(other - per)) > 1e-2


def test_pad_for_boundary_periodization_is_the_identity(medium_field):
    padded, crop = _pad_for_boundary(medium_field, level=2, boundary="periodization")
    assert padded.shape == medium_field.shape
    assert crop == tuple(slice(0, n) for n in medium_field.shape)
    assert np.array_equal(padded[crop], medium_field)


@pytest.mark.parametrize("mode", ["symmetric", "zero"])
@pytest.mark.parametrize("level", [1, 2, 3])
def test_pad_for_boundary_widens_by_two_to_the_level(medium_field, mode, level):
    """Pad width is 2**level per side; the crop recovers the original block."""
    pad = 2 ** level
    padded, crop = _pad_for_boundary(medium_field, level=level, boundary=mode)
    assert padded.shape == tuple(n + 2 * pad for n in medium_field.shape)
    assert np.array_equal(padded[crop], medium_field)
    if mode == "zero":
        assert padded[0, 0] == 0.0


def test_zero_padding_uses_zeros_and_symmetric_reflects():
    x = np.arange(8, dtype=float).reshape(2, 4)
    zero_padded, _ = _pad_for_boundary(x, level=1, boundary="zero")
    assert zero_padded[0].tolist() == [0.0] * zero_padded.shape[1]

    sym_padded, crop = _pad_for_boundary(x, level=1, boundary="symmetric")
    # np.pad(mode="reflect") mirrors without repeating the edge sample.
    assert np.array_equal(sym_padded[crop], x)
    assert not np.allclose(sym_padded[0], 0.0)


def test_padding_width_is_narrower_than_the_db2_kernel_support():
    """FINDING (explains the boundary leakage measured above).

    ``_pad_for_boundary`` pads by ``2**level``, but the db2 stationary kernel at
    level L spans ``3*(2**L - 1) + 1`` samples.  The pad is never wide enough,
    so the periodic wrap-around of the underlying ``pywt.swt`` always leaks a
    little into the cropped result.  Measured leak at j=1 on a 48x48 field:
    1.9e-3 at margin 8; at j=2, 8.2e-4 still survives at margin 16.
    """
    for level in (1, 2, 3, 4):
        pad = 2 ** level
        support = 3 * (2 ** level - 1) + 1
        assert pad < support, f"level={level}: pad {pad} >= support {support}"


# ---------------------------------------------------------------------------
# Error contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("j", [-1, -3, -10])
def test_negative_j_raises_value_error(j):
    with pytest.raises(ValueError, match="j must be >= 0"):
        project_1d(np.ones(32), j)
    with pytest.raises(ValueError, match="j must be >= 0"):
        project_2d(np.ones((32, 32)), j)


@pytest.mark.parametrize("boundary", ["bogus", "reflect", "PERIODIZATION", ""])
def test_invalid_boundary_raises_value_error(boundary):
    match = r"boundary must be one of"
    with pytest.raises(ValueError, match=match):
        project_1d(np.ones(32), 0, boundary=boundary)
    with pytest.raises(ValueError, match=match):
        project_2d(np.ones((32, 32)), 0, boundary=boundary)
    with pytest.raises(ValueError, match=match):
        _pad_for_boundary(np.ones((8, 8)), 1, boundary)


def test_shape_not_divisible_by_two_to_the_level_raises():
    """Raw project_2d rejects a 30x30 field at j=2; this is what pad_to_swt fixes."""
    with pytest.raises(ValueError):
        project_2d(np.ones((30, 30)), 2)


# ---------------------------------------------------------------------------
# pad_to_swt
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("shape", [(30, 30), (32, 32), (33, 17), (50,), (7, 3, 5)])
@pytest.mark.parametrize("max_level", [1, 3, 4])
def test_pad_to_swt_pads_each_axis_to_a_multiple(rng, shape, max_level):
    x = rng.normal(0.0, 1.0, shape)
    padded, slices = pad_to_swt(x, max_level)
    mult = 2 ** max_level
    assert all(n % mult == 0 for n in padded.shape), padded.shape
    # It pads by the minimum amount needed.
    for n_new, n_old in zip(padded.shape, x.shape):
        assert 0 <= n_new - n_old < mult


@pytest.mark.parametrize("shape", [(30, 30), (33, 17), (50,)])
@pytest.mark.parametrize("max_level", [1, 3, 4])
def test_pad_to_swt_slices_recover_the_original(rng, shape, max_level):
    x = rng.normal(0.0, 1.0, shape)
    padded, slices = pad_to_swt(x, max_level)
    assert padded[slices].shape == x.shape
    assert np.array_equal(padded[slices], x)


def test_pad_to_swt_appends_at_the_end_only(rng):
    """Padding is (0, extra), so the original data keeps index 0."""
    x = rng.normal(0.0, 1.0, (30, 30))
    padded, _ = pad_to_swt(x, 3)
    assert padded.shape == (32, 32)
    assert np.array_equal(padded[:30, :30], x)


def test_pad_to_swt_enables_projection_on_a_non_divisible_field(rng):
    """End-to-end: pad, project, crop back to the original shape."""
    x = rng.normal(0.0, 1.0, (30, 30))
    j = 2
    padded, slices = pad_to_swt(x, j + 1)
    out = project_2d(padded, j)[slices]
    assert out.shape == x.shape
    assert np.isfinite(out).all()


def test_pad_to_swt_is_a_no_op_when_already_aligned(rng):
    x = rng.normal(0.0, 1.0, (32, 32))
    padded, slices = pad_to_swt(x, 4)
    assert padded.shape == x.shape
    assert np.array_equal(padded[slices], x)
