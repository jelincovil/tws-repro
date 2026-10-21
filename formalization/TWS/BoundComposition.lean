import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Analysis.Normed.Module.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic

/-!
# Abstract composition of signal and operator bounds

This module isolates the elementary composition step used by the companion
paper.  It is deliberately independent of persistence homology, diagrams,
landscapes and Besov energies:

* `E`, `F`, `G` are real normed (semi)normed spaces;
* `A : E →L[ℝ] F` is a bounded linear operator;
* `Φ : F → G` is an arbitrary functional summary.

The two analytic inputs are kept as separate hypotheses:

* `SummaryLipschitz Φ L` controls the summary at every pair of points of `F`;
* `OperatorNormBound A C` controls the operator by its operator norm.

From them the module proves

`‖Φ (A x) - Φ (A y)‖ ≤ L * C * ‖x - y‖`

for all `x y : E`.  No hypothesis is the desired conclusion: the summary
bound is stated on all of `F`, and the operator bound is stated on `‖A‖`.

The localized corollary below is *conditional by design*.  It receives

`‖Φ_U u - Φ_U v‖ ≤ L * sqrt(windowLength) * ‖u - v‖`

as a hypothesis and only composes it with the operator bound.  In
particular it is **not** a formal proof of integration, bottleneck
stability, or persistence-landscape stability; those results are external
mathematical inputs of the paper.

The final section contains a concrete, non-constant instance on `ℝ`.  It is
an interface test only and is not an instance of persistent homology.
-/

namespace TWS

/-- A functional summary `Φ : F → G` is Lipschitz-controlled by `L`.

The first component is the explicit nonnegativity of the constant; the
second is the control at *every* pair of points of `F`.  In particular the
hypothesis is not restricted to the pairs `(A x, A y)` appearing in the
conclusion. -/
def SummaryLipschitz {F G : Type*} [SeminormedAddCommGroup F]
    [SeminormedAddCommGroup G] (Φ : F → G) (L : ℝ) : Prop :=
  0 ≤ L ∧ ∀ u v : F, ‖Φ u - Φ v‖ ≤ L * ‖u - v‖

/-- A bounded linear operator `A : E →L[ℝ] F` is controlled by `C` when its
operator norm is at most `C`.  The nonnegativity of `C` is part of the
predicate. -/
def OperatorNormBound {E F : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [NormedSpace ℝ E] [NormedSpace ℝ F]
    (A : E →L[ℝ] F) (C : ℝ) : Prop :=
  0 ≤ C ∧ ‖A‖ ≤ C

/-- Pointwise form of the operator-norm bound.  This is the only place where
the operator norm is unfolded; the composition theorems below use it on the
difference `x - y`. -/
theorem operator_apply_bound {E F : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [NormedSpace ℝ E] [NormedSpace ℝ F]
    (A : E →L[ℝ] F) (C : ℝ) (hA : OperatorNormBound A C) (x : E) :
    ‖A x‖ ≤ C * ‖x‖ := by
  calc
    ‖A x‖ ≤ ‖A‖ * ‖x‖ := A.le_opNorm x
    _ ≤ C * ‖x‖ := mul_le_mul_of_nonneg_right hA.2 (norm_nonneg x)

/-- **Abstract composition of bounds.**

For every bounded linear operator `A : E →L[ℝ] F`, every functional summary
`Φ : F → G`, and every pair of explicit constants `L C`, the summary bound
and the operator bound compose to

`‖Φ (A x) - Φ (A y)‖ ≤ L * C * ‖x - y‖`.

Both constants are parameters of the theorem (not existential witnesses),
and their nonnegativity is carried by the two hypotheses. -/
theorem summary_comp_bound {E F G : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [SeminormedAddCommGroup G]
    [NormedSpace ℝ E] [NormedSpace ℝ F] [NormedSpace ℝ G]
    (A : E →L[ℝ] F) (Φ : F → G) (L C : ℝ)
    (hΦ : SummaryLipschitz Φ L) (hA : OperatorNormBound A C) :
    ∀ x y : E, ‖Φ (A x) - Φ (A y)‖ ≤ L * C * ‖x - y‖ := by
  intro x y
  have hA' : ‖A x - A y‖ ≤ C * ‖x - y‖ := by
    rw [← ContinuousLinearMap.map_sub]
    exact operator_apply_bound A C hA (x - y)
  calc
    ‖Φ (A x) - Φ (A y)‖ ≤ L * ‖A x - A y‖ := hΦ.2 (A x) (A y)
    _ ≤ L * (C * ‖x - y‖) := mul_le_mul_of_nonneg_left hA' hΦ.1
    _ = L * C * ‖x - y‖ := by ring

/-- Localized form of the summary hypothesis.

`windowLength` is a nonnegative real parameter standing for the length
`|U|` of the localization window.  The inequality

`‖Φ_U u - Φ_U v‖ ≤ L * sqrt(windowLength) * ‖u - v‖`

is an **input hypothesis**, not something derived here from an integral, a
persistence diagram, or a landscape construction. -/
def LocalizedSummaryLipschitz {F G : Type*} [SeminormedAddCommGroup F]
    [SeminormedAddCommGroup G] (Φ : F → G) (L : ℝ)
    (windowLength : ℝ) : Prop :=
  0 ≤ L ∧ 0 ≤ windowLength ∧
    ∀ u v : F, ‖Φ u - Φ v‖ ≤ L * Real.sqrt windowLength * ‖u - v‖

/-- **Localized abstract composition.**

This is the explicit-window version of `summary_comp_bound`:

`‖Φ_U (A x) - Φ_U (A y)‖ ≤ L * C * sqrt(windowLength) * ‖x - y‖`.

The localized inequality is received as `hΦ`; the theorem proves only that
it composes with the operator bound.  It does not prove integration,
bottleneck stability, or landscape stability, and it makes no claim about
persistence diagrams. -/
theorem localized_summary_comp_bound {E F G : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [SeminormedAddCommGroup G]
    [NormedSpace ℝ E] [NormedSpace ℝ F] [NormedSpace ℝ G]
    (A : E →L[ℝ] F) (Φ : F → G) (L C windowLength : ℝ)
    (hΦ : LocalizedSummaryLipschitz Φ L windowLength)
    (hA : OperatorNormBound A C) :
    ∀ x y : E,
      ‖Φ (A x) - Φ (A y)‖ ≤ L * C * Real.sqrt windowLength * ‖x - y‖ := by
  intro x y
  have hΦ' : SummaryLipschitz Φ (L * Real.sqrt windowLength) :=
    ⟨mul_nonneg hΦ.1 (Real.sqrt_nonneg windowLength), hΦ.2.2⟩
  have h := summary_comp_bound A Φ (L * Real.sqrt windowLength) C hΦ' hA x y
  calc
    ‖Φ (A x) - Φ (A y)‖ ≤ (L * Real.sqrt windowLength) * C * ‖x - y‖ := h
    _ = L * C * Real.sqrt windowLength * ‖x - y‖ := by ring

/-! ## A concrete non-constant instance

The following example checks that the interface is inhabited by ordinary
functions and operators, not only by abstract variables.  It is an interface
test on `ℝ`; it has no interpretation as a persistence diagram or as a
homological computation. -/

/-- Multiplication by `2`, as a bounded linear operator on `ℝ`. -/
def exampleOperator : ℝ →L[ℝ] ℝ := (2 : ℝ) • ContinuousLinearMap.id ℝ ℝ

@[simp] theorem exampleOperator_apply (x : ℝ) : exampleOperator x = 2 * x := by
  simp [exampleOperator]

/-- Multiplication by `3`, as a functional summary on `ℝ`. -/
def exampleSummary (x : ℝ) : ℝ := 3 * x

/-- The example summary is controlled by `L = 3`. -/
theorem exampleSummary_lipschitz : SummaryLipschitz exampleSummary 3 := by
  refine ⟨by norm_num, ?_⟩
  intro u v
  have h : (3 : ℝ) * u - 3 * v = 3 * (u - v) := by ring
  simp only [exampleSummary]
  rw [h, Real.norm_eq_abs, abs_mul]
  norm_num

/-- The example operator has operator norm exactly `2`. -/
theorem exampleOperator_norm_bound : OperatorNormBound exampleOperator 2 := by
  refine ⟨by norm_num, ?_⟩
  have h : ‖exampleOperator‖ = 2 := by
    calc
      ‖exampleOperator‖ = ‖(2 : ℝ) • ContinuousLinearMap.id ℝ ℝ‖ := rfl
      _ = ‖(2 : ℝ)‖ * ‖ContinuousLinearMap.id ℝ ℝ‖ := norm_smul _ _
      _ = 2 := by
        rw [Real.norm_eq_abs, ContinuousLinearMap.norm_id]
        norm_num
  rw [h]

/-- The example satisfies the abstract theorem with `L = 3` and `C = 2`. -/
theorem example_bound :
    ‖exampleSummary (exampleOperator 0) - exampleSummary (exampleOperator 1)‖ ≤
      3 * 2 * ‖(0 : ℝ) - 1‖ :=
  summary_comp_bound exampleOperator exampleSummary 3 2
    exampleSummary_lipschitz exampleOperator_norm_bound 0 1

/-- The example is non-constant: the two chosen inputs produce `0` and `6`. -/
theorem example_outputs :
    exampleSummary (exampleOperator 0) = 0 ∧
      exampleSummary (exampleOperator 1) = 6 := by
  constructor <;> norm_num [exampleSummary]

/-- The two outputs of the example are distinct. -/
theorem example_outputs_distinct :
    exampleSummary (exampleOperator 0) ≠ exampleSummary (exampleOperator 1) := by
  rw [example_outputs.1, example_outputs.2]
  norm_num

/-- The same summary also satisfies the localized hypothesis with
`windowLength = 4` and `L = 3` (the right-hand side is `6 ‖u - v‖`). -/
theorem exampleLocalized : LocalizedSummaryLipschitz exampleSummary 3 4 := by
  refine ⟨by norm_num, by norm_num, ?_⟩
  intro u v
  have h := exampleSummary_lipschitz.2 u v
  rw [show Real.sqrt 4 = 2 by norm_num]
  nlinarith [norm_nonneg (u - v)]

/-- The localized composition theorem is instantiated by the same concrete
objects, with the explicit factor `sqrt 4 = 2`. -/
theorem example_localized_bound :
    ‖exampleSummary (exampleOperator 0) - exampleSummary (exampleOperator 1)‖ ≤
      3 * 2 * Real.sqrt 4 * ‖(0 : ℝ) - 1‖ :=
  localized_summary_comp_bound exampleOperator exampleSummary 3 2 4
    exampleLocalized exampleOperator_norm_bound 0 1

end TWS
