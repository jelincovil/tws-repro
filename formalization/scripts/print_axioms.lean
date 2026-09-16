import TWS

/-!
# Axiom audit for the TWS formalization

Run with:

    lake env lean scripts/print_axioms.lean

(from `formalization/`, after `lake build`). It prints, for every exported
theorem of the development, the axioms the kernel-checked proof term
depends on. A clean result is exactly

    [propext, Classical.choice, Quot.sound]

Any occurrence of `sorryAx` means the statement is NOT proved.

Note: in Lean 4 the `import` must precede every other command, module
docstrings included, so it appears above this comment.
-/

#print axioms TWS.localEnergy_nonneg
#print axioms TWS.l2_norm_rev_tri
#print axioms TWS.stability_Linf
#print axioms TWS.stability_two_term
#print axioms TWS.energy_stability
#print axioms TWS.frame_proj_bound_of_id
#print axioms TWS.geometric_factor_two_le_dim
#print axioms TWS.local_index_card_exponent_is_dim
#print axioms TWS.energy_weight_recovers_s_add_one_at_d_two
#print axioms TWS.Daubechies.kernel1d_l1
#print axioms TWS.Daubechies.kernel1d_l1_real
#print axioms TWS.Daubechies.outer_l1
#print axioms TWS.Daubechies.db2_level1_opnorm_d2
#print axioms TWS.Daubechies.R0
#print axioms TWS.Daubechies.R1
#print axioms TWS.Daubechies.R2
#print axioms TWS.Daubechies.R3
#print axioms TWS.Daubechies.autocorr_zero
#print axioms TWS.Daubechies.half_autocorr_l1
