import TWS

/-!
# Axiom audit for the TWS formalization

Run with:

    lake env lean scripts/print_axioms.lean

(from `formalization/`, after `lake build`).  It prints, for every exported
theorem of the development, the axioms the kernel-checked proof term
depends on.  A clean result is exactly

    [propext, Classical.choice, Quot.sound]

Any occurrence of `sorryAx` means the statement is NOT proved.

The audited modules are `TWS/BoundComposition.lean` and
`TWS/DaubechiesOpNorm.lean`.  The archived skeleton under
`formalization/archive/` is not part of the library and is not audited.

Note: in Lean 4 the `import` must precede every other command, module
docstrings included, so it appears above this comment.
-/

/-! ## Abstract composition and localized specialization -/
#print axioms TWS.operator_apply_bound
#print axioms TWS.summary_comp_bound
#print axioms TWS.localized_summary_comp_bound

/-! ## Concrete non-constant instance -/
#print axioms TWS.exampleSummary_lipschitz
#print axioms TWS.exampleOperator_norm_bound
#print axioms TWS.example_bound
#print axioms TWS.exampleLocalized
#print axioms TWS.example_localized_bound
#print axioms TWS.example_outputs
#print axioms TWS.example_outputs_distinct

/-! ## db2 finite computation -/
#print axioms TWS.Daubechies.kernel1d_l1
#print axioms TWS.Daubechies.kernel1d_l1_real
#print axioms TWS.Daubechies.outer_l1
#print axioms TWS.Daubechies.db2_level1_opnorm_d2
#print axioms TWS.Daubechies.db2_level1_opnorm_d2_num
#print axioms TWS.Daubechies.c_sq
#print axioms TWS.Daubechies.R0
#print axioms TWS.Daubechies.R1
#print axioms TWS.Daubechies.R2
#print axioms TWS.Daubechies.R3
#print axioms TWS.Daubechies.autocorr_zero
#print axioms TWS.Daubechies.autocorr_one
#print axioms TWS.Daubechies.autocorr_two
#print axioms TWS.Daubechies.autocorr_three
#print axioms TWS.Daubechies.half_autocorr_l1
