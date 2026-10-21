# Formalization Directory

Lean 4.33.0 / mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`
companion to

> J. E. Lincovil Curivil, C. D. Reinoso Reinoso, N. Pacheco-Barrios.
> *Explicit \(L^\infty\) stability bounds for undecimated Daubechies
> smoothing and wavelet-filtered persistence landscapes*.
> arXiv:XXXX.XXXXX *(placeholder)*.

This directory is **not** the manuscript.  It contains two verified Lean
components:

1. `TWS/BoundComposition.lean` — an abstract composition inequality for a
   bounded linear operator and a Lipschitz-controlled functional summary,
   with an explicit localized-window specialization and a concrete
   non-constant instance.
2. `TWS/DaubechiesOpNorm.lean` — the exact finite `db2` level-1 tap and
   autocorrelation computation, including the absolute-product sum
   `(9/8)^2`.

It does **not** formalize persistent homology, bottleneck stability,
persistence landscapes, Besov energies, or a periodic convolution operator.

## What is actually proved

The old `Skeleton.lean` was withdrawn from the library.  It is preserved
only as `archive/Skeleton_v2_historical.lean` and is not built or exported.
Its `projection` was the identity, `projDgmK` returned the empty multiset,
`landscape` ignored the landscape index, and its “Theorem A” was a
conditional composition about those placeholders.  Do not cite it as a
paper result.

| Mathematical result | Lean declaration | Hypotheses received | Proved content | Not formalized |
|---|---|---|---|---|
| Abstract composition \(\|\Phi(Ax)-\Phi(Ay)\|\le L C\|x-y\|\) | `TWS.summary_comp_bound` | `SummaryLipschitz Φ L` (nonnegative `L` and a global Lipschitz bound on `Φ`); `OperatorNormBound A C` (nonnegative `C` and `‖A‖ ≤ C`); `A : E →L[ℝ] F`, `Φ : F → G` | The composition: `‖A x - A y‖ ≤ C‖x-y‖` from `A.le_opNorm`, then the summary bound; `L` and `C` are explicit parameters, not existential witnesses | No concrete frame/projection, no persistence backend, no derivation of the hypotheses from the paper’s (A1)–(A4) |
| Localized composition \(\|\Phi_U(Ax)-\Phi_U(Ay)\|\le L_\lambda C\sqrt{\lvert U\rvert}\|x-y\|\) | `TWS.localized_summary_comp_bound` | `LocalizedSummaryLipschitz Φ L windowLength` (nonnegative `L`, nonnegative real `windowLength`, and the localized inequality itself); `OperatorNormBound A C` | Only the algebraic composition with the explicit factor `Real.sqrt windowLength` | The localized inequality is **received**, not proved. No integration, measure-theoretic window length, bottleneck stability, or landscape stability is formalized |
| Non-constant interface test | `TWS.example_bound`, `TWS.example_localized_bound`, `TWS.example_outputs`, `TWS.example_outputs_distinct` | Concrete maps on `ℝ`: `A x = 2x`, `Φ x = 3x` | The general theorems apply; the two inputs `0` and `1` give outputs `0` and `6`; hence the interface admits genuinely non-constant objects | This is not an instance of persistent homology or of a persistence diagram |
| db2 taps and autocorrelation at lags 0–3 | `TWS.Daubechies.kernel1d_l1`, `kernel1d_l1_real`, `R0`–`R3`, `autocorr_zero`–`autocorr_three`, `half_autocorr_l1` | None | Exact rational/real arithmetic: the seven taps `[-1,0,9,16,9,0,-1]/32` have `ℓ¹` norm `9/8`; the QMF/autocorrelation identities hold | No convolution operator, no periodic mesh, no infinite-dimensional kernel |
| Two-dimensional absolute-product sum | `TWS.Daubechies.outer_l1`, `db2_level1_opnorm_d2`, `db2_level1_opnorm_d2_num` | None | The finite identity `∑ᵢ ∑ⱼ \|kᵢ kⱼ\| = (9/8)^2 = 81/64` and its algebraic factorization | The name `db2_level1_opnorm_d2` is historical: the theorem does **not** construct a periodic convolution or prove its operator norm, and does not tensorize to general dimension `d` |
| Bottleneck stability / Cohen–Steiner–Bubenik / frame projection bound / Besov energy | — | — | — | External mathematical inputs of the paper; not formalized in this repository |
| Numerical medical and synthetic experiments | — | — | — | Python/CSV artefacts; not formalized in Lean |

Explicitly:

- **Formalized — abstract composition:** `summary_comp_bound`,
  `localized_summary_comp_bound`, and the concrete instance.
- **Formalized — filter identities:** the finite `db2` tap,
  autocorrelation, and absolute-product computations.
- **Used externally — topology and analysis:** bottleneck stability,
  Cohen–Steiner–Bubenik, the frame-projection bound, and the Besov/energy
  estimate.  These are paper-level mathematical inputs, not Lean theorems.
- **Not formalized — numerical experiments:** the synthetic and medical
  CSV/JSON results.

## Main declarations

The statements below are the actual Lean signatures.  `E`, `F`, `G` are
real normed spaces; `SeminormedAddCommGroup` is used so the API also covers
seminormed spaces.

```lean
def SummaryLipschitz {F G : Type*} [SeminormedAddCommGroup F]
    [SeminormedAddCommGroup G] (Φ : F → G) (L : ℝ) : Prop :=
  0 ≤ L ∧ ∀ u v : F, ‖Φ u - Φ v‖ ≤ L * ‖u - v‖

def OperatorNormBound {E F : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [NormedSpace ℝ E] [NormedSpace ℝ F]
    (A : E →L[ℝ] F) (C : ℝ) : Prop :=
  0 ≤ C ∧ ‖A‖ ≤ C

theorem summary_comp_bound {E F G : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [SeminormedAddCommGroup G]
    [NormedSpace ℝ E] [NormedSpace ℝ F] [NormedSpace ℝ G]
    (A : E →L[ℝ] F) (Φ : F → G) (L C : ℝ)
    (hΦ : SummaryLipschitz Φ L) (hA : OperatorNormBound A C) :
    ∀ x y : E, ‖Φ (A x) - Φ (A y)‖ ≤ L * C * ‖x - y‖
```

The localized specialization receives the localized Lipschitz inequality
as a hypothesis:

```lean
def LocalizedSummaryLipschitz {F G : Type*} [SeminormedAddCommGroup F]
    [SeminormedAddCommGroup G] (Φ : F → G) (L : ℝ)
    (windowLength : ℝ) : Prop :=
  0 ≤ L ∧ 0 ≤ windowLength ∧
    ∀ u v : F, ‖Φ u - Φ v‖ ≤ L * Real.sqrt windowLength * ‖u - v‖

theorem localized_summary_comp_bound {E F G : Type*} [SeminormedAddCommGroup E]
    [SeminormedAddCommGroup F] [SeminormedAddCommGroup G]
    [NormedSpace ℝ E] [NormedSpace ℝ F] [NormedSpace ℝ G]
    (A : E →L[ℝ] F) (Φ : F → G) (L C windowLength : ℝ)
    (hΦ : LocalizedSummaryLipschitz Φ L windowLength)
    (hA : OperatorNormBound A C) :
    ∀ x y : E,
      ‖Φ (A x) - Φ (A y)‖ ≤ L * C * Real.sqrt windowLength * ‖x - y‖
```

`windowLength` is a nonnegative real parameter standing for `|U|`; it is
not a measure-theoretic integral.  The theorem proves the composition, not
the localized inequality, bottleneck stability, or landscape stability.

### Non-constant instance

`TWS.exampleOperator` is multiplication by `2` on `ℝ`, and
`TWS.exampleSummary` is multiplication by `3`.  The general theorem gives

```lean
theorem example_bound :
    ‖exampleSummary (exampleOperator 0) - exampleSummary (exampleOperator 1)‖ ≤
      3 * 2 * ‖(0 : ℝ) - 1‖
```

and `example_outputs` proves that the two chosen inputs produce `0` and
`6`, while `example_outputs_distinct` proves they are different.  The
localized theorem is likewise instantiated with `windowLength = 4`
(`example_localized_bound`).  These are interface checks, not homology
computations.

## db2 scope

The theorem named `db2_level1_opnorm_d2` has the literal statement

```lean
theorem db2_level1_opnorm_d2 :
    ∑ i : Fin 7, ∑ j : Fin 7, |((kernel1d i : ℝ) * (kernel1d j : ℝ))| =
      ((9 : ℝ) / 8) ^ 2
```

It is an absolute-product sum (the `ℓ¹` row-sum of the outer product),
obtained from `outer_l1` and `kernel1d_l1_real`.  It is **not** a proof that
a periodic convolution operator has norm `(9/8)^2`, and it does not cover a
general dimension `d`.  The Lean name is retained for continuity with older
listings; the module docstring states the limitation.

## Scope statement (paper-ready)

> The Lean 4 development (Lean 4.33.0, mathlib
> `db584cd6d46c92f209a44c0f1c829460d327499d`) mechanically verifies an
> abstract composition lemma for signal bounds: if a functional summary
> `Φ` is `L`-Lipschitz on a real normed space and `A` is a bounded linear
> operator with operator norm at most `C`, then
> `‖Φ(Ax) − Φ(Ay)‖ ≤ L C ‖x − y‖`.  A localized variant is also verified,
> but it takes the windowed Lipschitz inequality as an explicit hypothesis;
> the factor `√|U|` is represented by a nonnegative real parameter rather
> than a measure-theoretic integral.  A concrete non-constant instance on
> `ℝ` is checked.  The development also verifies the finite `db2` level-1
> tap and autocorrelation identities and the absolute-product sum
> `(9/8)^2`; it does not construct a periodic convolution operator or prove
> its norm.  Persistent homology, bottleneck stability, persistence-
> landscape stability, the frame-projection bound, and the Besov/energy
> estimates are external mathematical inputs and are not formalized.  All
> audited declarations depend only on `propext`, `Classical.choice`, and
> `Quot.sound`; there is no `sorry` and no added axiom.

## Historical skeleton

```
archive/Skeleton_v2_historical.lean
```

This file is outside the `TWS` library target.  It is not imported by
`TWS.lean`, is not built by `lake build`, and is not audited.  It contains
the withdrawn placeholder definitions (`projection = id`,
`projDgmK = ∅`, first-landscape-only `landscape`) and the old conditional
`stability_Linf` / `stability_two_term` statements.  The file header
explains why they are not a formalization of the paper’s theorem.

## Build and audit

From this directory:

```bash
lake exe cache get
lake build
lake env lean scripts/print_axioms.lean
```

Pins are frozen:

```bash
cat lean-toolchain
# leanprover/lean4:v4.33.0
grep -A3 '"name": "mathlib"' lake-manifest.json
# rev db584cd6d46c92f209a44c0f1c829460d327499d
```

Do **not** run `lake update`; it would re-resolve mathlib and break the
pin.

`./scripts/check_all.sh` runs the cache fetch, `lake build`, and a source
audit for `sorry`, `admit`, and explicit `axiom` declarations.
`./scripts/print_axioms.sh` runs the axiom audit, rejects any axiom outside
`propext`, `Classical.choice`, `Quot.sound`, and can archive the literal
output.

### Verification record (2026-10-21)

| Check | Command | Result |
|---|---|---|
| Cache | `lake exe cache get` | `Already decompressed 8690 file(s)`, exit 0 |
| Build | `lake build` | `Build completed successfully (3009 jobs).`, exit 0 |
| Source audit | `./scripts/check_all.sh` | sorry 0, admit 0, explicit axioms 0, `RESULT: BUILD OK` |
| Axioms | `lake env lean scripts/print_axioms.lean` | all 25 audited declarations: `[propext, Classical.choice, Quot.sound]`; no `sorryAx` |
| Archived audit | `./scripts/print_axioms.sh docs/axioms_audit.txt` | literal output matches `docs/axioms_audit.txt` |

The archived literal output is in `docs/axioms_audit.txt`.

## Structure

```
formalization/
├── TWS.lean                         # Root; exports the two verified modules
├── TWS/
│   ├── BoundComposition.lean        # Abstract composition + localized form + example
│   └── DaubechiesOpNorm.lean        # db2 taps/QMF/autocorrelation/absolute sum
├── archive/
│   └── Skeleton_v2_historical.lean  # Withdrawn placeholders; not in the library
├── lakefile.toml                    # Lake build configuration
├── lean-toolchain                   # leanprover/lean4:v4.33.0
├── lake-manifest.json               # Dependency lock (mathlib pinned by rev)
├── scripts/
│   ├── check_all.sh                 # cache get + lake build + sorry report
│   ├── print_axioms.sh              # wrapper around the audit
│   └── print_axioms.lean            # #print axioms on the exported declarations
└── docs/
    ├── README.md
    └── axioms_audit.txt             # archived literal output of the audit
```

## Windows: build from a short path

Lean writes `.olean` files deep inside `.lake/packages/mathlib/...`.  Under
this repository’s own location those paths can exceed the Windows
`MAX_PATH` limit (260 characters), and `lean.exe` is not long-path aware.
Build from a genuinely short directory if necessary:

```bash
mkdir -p /c/twsl
cp lakefile.toml lean-toolchain lake-manifest.json TWS.lean /c/twsl/
cp -r TWS scripts /c/twsl/
cd /c/twsl && lake exe cache get && lake build
```

The `lean_check.yml` workflow runs on `ubuntu-latest`, where this limit
does not apply.

## Resources

- Lean 4: <https://lean-lang.org/lean4/doc/>
- Mathlib: <https://leanprover-community.github.io/mathlib4_docs/>
- Lean Zulip: <https://leanprover.zulipchat.com/>

## Citation

See [`CITATION.cff`](../../CITATION.cff) at the repository root.
