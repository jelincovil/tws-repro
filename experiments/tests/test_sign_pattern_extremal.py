"""The sign-pattern pair attains the Theorem A Lipschitz constant."""
from __future__ import annotations

import numpy as np
import pytest

from tws_validation.cfp_estimation import exact_opnorm
from tws_validation.sign_pattern_extremal import run_sign_pattern


def test_sign_pattern_attains_the_operator_norm_and_rho_op_one():
    rec = run_sign_pattern(n=48, j=0, eps=0.05)
    assert rec["cfp"] == pytest.approx((9.0 / 8.0) ** 2, rel=1e-12)
    assert rec["cfp"] == pytest.approx(exact_opnorm(0), rel=1e-12)
    assert rec["op_saturation"] == pytest.approx(1.0, rel=1e-12)
    assert rec["rho_op"] == pytest.approx(1.0, rel=1e-12)
    assert rec["bar2_death"] == pytest.approx(rec["bar1_death"], rel=1e-12)
    assert rec["birth_shift"] == pytest.approx(rec["expected_shift"], rel=1e-10)
    assert rec["n_bars_1"] == rec["n_bars_2"]
    assert rec["diam_U"] > 0.0
    assert rec["lhs_l2"] <= rec["rhs_op"] + 1e-12


def test_sign_pattern_is_deterministic():
    a = run_sign_pattern(n=48, j=0, eps=0.05)
    b = run_sign_pattern(n=48, j=0, eps=0.05)
    assert a["rho_op"] == b["rho_op"]
    assert a["lhs_l2"] == b["lhs_l2"]
