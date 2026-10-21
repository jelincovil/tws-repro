import TWS.BoundComposition
import TWS.DaubechiesOpNorm

/-!
# TWS — library root

Root module of the `TWS` Lean library.  It re-exports exactly the two
verified components of the companion code:

* `TWS.BoundComposition`: the abstract composition inequality for a bounded
  linear operator and a Lipschitz-controlled functional summary, including
  its localized-window specialization and a concrete non-constant instance;
* `TWS.DaubechiesOpNorm`: the exact `db2` level-1 tap computation and the
  absolute-product sum `(9/8)^2`, together with the QMF/autocorrelation
  identities.

The old `Skeleton.lean` has been moved to
`archive/Skeleton_v2_historical.lean`.  It is not imported here, is not
built by the `TWS` target, and is not part of the formal result: its
`projection` was the identity, its `projDgmK` was empty, and its
`landscape` ignored the landscape index.

No persistent homology, bottleneck stability, or landscape-stability
theorem is formalized in this library.  Those are external mathematical
inputs of the paper.

Note: in Lean 4 every `import` must precede all other commands, module
docstrings included, so the imports above come first by necessity.
-/
