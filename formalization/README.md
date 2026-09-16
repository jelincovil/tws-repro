# Formalization Directory

Lean 4.33.0 / mathlib `db584cd6` companion to
*Explicit \(L^\infty\) stability bounds for undecimated Daubechies smoothing
and wavelet-filtered persistence landscapes* (arXiv:XXXX.XXXXX, placeholder).
This directory is not the manuscript.

What is actually certified:

- **Theorem A composition** (`TWS.stability_Linf`): analytic lemmas enter as
  named hypotheses. Not a proof of bottleneck stability or of landscapes.
- **db2 operator norm** (`TWS.Daubechies`): QMF identities, \(\ell^1=9/8\),
  two-dimensional row-sum \((9/8)^2\).
- **Sorry count**: 0. Axioms of the audited declarations:
  `[propext, Classical.choice, Quot.sound]`.

`TWS.stability_two_term` remains in `Skeleton.lean` as leftover from a
two-term bound **removed from the manuscript**. Do not cite it as a paper
theorem.

## Overview

The main results are mechanically verified in Lean 4 with explicit tracking of:
- **Axioms used**: `[propext, Classical.choice, Quot.sound]` for every
  audited declaration, including `l2_norm_rev_tri` and `TWS.Daubechies.*`
- **Hypotheses**: landscape and frame-projection bounds for Theorem A enter
  as `Prop` arguments rather than assumed globally
- **Sorry count**: 0

**Last verified end to end** (2026-09-10, Lean 4.33.0, mathlib
`db584cd6d46c`):

| Check | Command | Result |
|-------|---------|--------|
| Type-checks | `lake build` | `Build completed successfully (2543 jobs).`, exit 0 |
| Sorry count | `./scripts/check_all.sh` | `real sorry count: 0` |
| Axiom audit | `lake env lean scripts/print_axioms.lean` | matches `docs/axioms_audit.txt` literal block |

## Structure

```
formalization/
├── TWS.lean                    # Library root; re-exports everything
├── TWS/
│   ├── Skeleton.lean           # Theorem A composition (0 sorry)
│   └── DaubechiesOpNorm.lean   # QMF + ℓ¹ = 9/8 + 2-D row-sum
├── lakefile.toml               # Lake build configuration
├── lean-toolchain              # leanprover/lean4:v4.33.0
├── lake-manifest.json          # Dependency lock (mathlib pinned by rev)
├── scripts/
│   ├── README.md               # what each script does
│   ├── check_all.sh            # cache get + lake build + sorry report
│   ├── print_axioms.sh         # wrapper around the audit below
│   └── print_axioms.lean       # #print axioms on the exported theorems
└── docs/
    ├── README.md
    └── axioms_audit.txt        # archived literal output of the audit
```

`Skeleton.lean` is still one file with `/-! ## Module: ... -/` headers
(including leftover Besov/cardinality material not used by the paper).
The operator-norm certificate is the separate file `DaubechiesOpNorm.lean`.

### Windows: build from a short path

Lean writes `.olean` and `.olean.server` files deep inside
`.lake/packages/mathlib/.lake/build/...`. Under this repository's own location
those paths reach **264 characters**, past the Windows `MAX_PATH` limit of 260,
and the build fails with `failed to create file`. `lean.exe` is not long-path
aware, so setting `LongPathsEnabled=1` in the registry is not enough, and
neither `subst` nor a directory junction helps: lake resolves both back to the
physical path.

Build from a genuinely short directory instead, for example:

```bash
mkdir -p /c/twsl
cp lakefile.toml lean-toolchain lake-manifest.json TWS.lean /c/twsl/
cp -r TWS scripts /c/twsl/
cd /c/twsl && lake exe cache get && lake build
```

Linux and macOS have no such limit, and neither does the `lean_check.yml`
workflow, which runs on `ubuntu-latest`.

## Quick Start

### Build the Project

```bash
# From formalization/ directory
# (on Windows, from the short-path copy — see "Windows: build from a
#  short path" above; `lake build` fails in place under this repository)
lake exe cache get
lake build
```

**Expected output** — the literal last line lake prints, and its exit code:
```
Build completed successfully (2543 jobs).
$ echo $?
0
```

Everything before that line is mathlib progress. A `declaration uses
'sorry'` warning is a regression: the closed fragment has no `sorry`.

**First build**: May take 10-30 minutes (compiles mathlib4)

**Subsequent builds**: < 1 minute

### Verify All Proofs

```bash
./scripts/check_all.sh
```

It runs `lake exe cache get`, then `lake build`, then reports the `sorry`
occurrences that are real proof obligations (backtick-quoted prose and
`sorry-free` in docstrings are filtered out). The expected tail is:

```
real sorry count: 0
RESULT: BUILD OK
```

Or manually:
```bash
lake exe cache get  # Download mathlib cache
lake build TWS      # Build project
```

### Check Axioms

```bash
./scripts/print_axioms.sh              # print
./scripts/print_axioms.sh out.txt      # print and archive
```

Or, equivalently, elaborate the audit file directly. Note it is a Lean file
to be **elaborated**, not an executable: `--run` is wrong and will fail.

```bash
lake env lean scripts/print_axioms.lean
```

The declarations it audits are the exported results, by their real
Lean names:

```lean
#print axioms TWS.localEnergy_nonneg
#print axioms TWS.l2_norm_rev_tri
#print axioms TWS.stability_Linf      -- Theorem A composition
#print axioms TWS.stability_two_term  -- leftover; not in the manuscript
#print axioms TWS.Daubechies.half_autocorr_l1
#print axioms TWS.Daubechies.db2_level1_opnorm_d2
#print axioms TWS.energy_stability    -- Corollary
#print axioms TWS.frame_proj_bound_of_id
#print axioms TWS.geometric_factor_two_le_dim
#print axioms TWS.local_index_card_exponent_is_dim
#print axioms TWS.energy_weight_recovers_s_add_one_at_d_two
```

**Expected axioms**:
- `propext` (propositional extensionality)
- `Classical.choice` (axiom of choice)
- `Quot.sound` (quotient soundness)

**Actual audit** (2026-09-10, Lean 4.33.0, mathlib `db584cd6d46c`; the literal
output is archived in `docs/axioms_audit.txt`):

```
'TWS.localEnergy_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.l2_norm_rev_tri'    depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.stability_Linf'     depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.stability_two_term' depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.energy_stability'   depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.frame_proj_bound_of_id' depends on axioms: [propext, Classical.choice, Quot.sound]
'TWS.local_index_card_exponent_is_dim' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Every audited declaration is sorry-free. There is no `sorry` in the source.

All are standard mathlib axioms.

## Main Theorems

The statements below are copied from `TWS/Skeleton.lean`, not paraphrased.
`{d : Nat}`, `(Psi : WaveletFrame d)` and `(s : ℝ)` are section `variable`s
(lines 68, 138, 178), so Lean inserts them as leading binders in any
declaration that mentions them; `#check` shows them explicitly.

### Theorem A: localized `L∞` bound

**Lean name**: `TWS.stability_Linf` (`TWS/Skeleton.lean:337`)

```lean
theorem stability_Linf
    (h_bounds : frame_bounds_pos Psi)
    (Z1 Z2 : (Fin d → ℝ) → ℝ) (j j0 : Int) (k n : Nat)
    (U : Set ℝ) (D : Set (Fin d → ℝ))
    (h_landscape : landscape_stability_hyp Psi Z1 Z2 j j0 k n U D)
    (h_proj : frame_proj_bound_hyp Psi (Z1 - Z2) j j0 D) :
    ∃ C2 : ℝ, 0 < C2 ∧
      L2Norm (fun t => landscape n (projDgmK Psi j j0 Z1 k) t
                      - landscape n (projDgmK Psi j j0 Z2 k) t) U
        ≤ C2 * LinfNorm (Z1 - Z2) D * Real.sqrt (Metric.diam U)
```

**Status**: proved and sorry-free. Conditional on the two named hypotheses
`landscape_stability_hyp` and `frame_proj_bound_hyp` being supplied by the
caller — it is a theorem *about* those hypotheses, which is why the axiom
audit is clean.

### Leftover: two-term composition (not in the manuscript)

**Lean name**: `TWS.stability_two_term`. Kept so the old skeleton still
type-checks. The paper does not state Theorem B.

```lean
theorem stability_two_term
    (h_bounds : frame_bounds_pos Psi)
    (Z1 Z2 : (Fin d → ℝ) → ℝ) (j j0 : Int) (k n : Nat)
    (U : Set ℝ) (D : Set (Fin d → ℝ)) (coeffSq : Int → ℝ)
    (hU : 0 < Metric.diam U)
    (h_landscape : landscape_stability_hyp Psi Z1 Z2 j j0 k n U D)
    (h_proj : frame_proj_bound_hyp Psi (Z1 - Z2) j j0 D)
    (h_se : scale_energy_bound Psi s j j0 (Z1 - Z2) U D coeffSq) :
    ∃ C1 C2 : ℝ, 0 < C1 ∧ 0 < C2 ∧
      L2Norm (fun t => landscape n (projDgmK Psi j j0 Z1 k) t
                      - landscape n (projDgmK Psi j j0 Z2 k) t) U
        ≤ min
            (C1 * Real.sqrt (Psi.B / Psi.A) * (2 : ℝ) ^ (-(j : ℝ) * s)
               * Real.sqrt (localEnergy Psi s j j0 (Z1 - Z2) U D coeffSq)
               * Real.sqrt (Metric.diam U))
            (C2 * LinfNorm (Z1 - Z2) D * Real.sqrt (Metric.diam U))
```

**Status**: proved and sorry-free, conditional on the three named
hypotheses above.

**Key hypothesis**: `scale_energy_bound` holds under fine-scale dominance at
level `(j, m₀)` with `χ⋆ > 0`; the manuscript derives `Cse` there, Lean takes
it as given.

### Corollary: topological energy stability

**Lean name**: `TWS.energy_stability` (`TWS/Skeleton.lean:440`)

```lean
theorem energy_stability
    (a b Γ : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (h : |a - b| ≤ Γ) :
    |a ^ 2 - b ^ 2| ≤ Γ * (a + b)
```

**Status**: proved and sorry-free. Note it takes `|a - b| ≤ Γ` as a
hypothesis, so the standalone statement does **not** depend on
`l2_norm_rev_tri`; only the intended application does.

### Key declarations

Names as they appear in `TWS/Skeleton.lean`; the `_hyp` suffix marks a
`Prop`-valued predicate supplied by the caller, not a proved lemma.

| Role | Lean name | Line | Status |
|------|-----------|------|--------|
| Localized landscape Lipschitz | `landscape_stability_hyp` | 286 | 🔶 Named hypothesis |
| Frame projection `L∞` bound | `frame_proj_bound_hyp` | 269 | 🔶 Named hypothesis |
| Scale-energy (Bernstein) bound | `scale_energy_bound` | 300 | 🔶 Named hypothesis |
| Abstract `L∞` frame bound | `linf_frame_bound_hyp` | 237 | 🔶 Named hypothesis |
| Localized index cardinality | `local_index_card_hyp` | 247 | 🔶 Named hypothesis |
| Cardinality exponent is `d` | `local_index_card_exponent_is_dim` | 276 | ✅ Proved, sorry-free |
| Precursor `x^2 ≤ x^d` | `geometric_factor_two_le_dim` | 265 | ✅ Proved, sorry-free |
| Energy weight at `d=2` | `energy_weight_recovers_s_add_one_at_d_two` | 236 | ✅ Proved, sorry-free |
| Identity witness for `C_fp` | `frame_proj_bound_of_id` | 277 | ✅ Proved, sorry-free |
| `localEnergy` nonnegativity | `localEnergy_nonneg` | 214 | ✅ Proved, sorry-free |
| Safe `L∞` norm nonnegativity | `LinfNorm_nonneg` | 82 | ✅ Proved, sorry-free |
| Reverse triangle (`L²`) | `l2_norm_rev_tri` | 317 | ✅ Proved, sorry-free |

**Legend**:
- ✅ Proved, sorry-free
- 🔶 Named hypothesis (a `Prop` the caller must supply; not proved here)

## Hypothesis Status

### The three named hypotheses of Theorem B

These are the three `Prop`s that appear in the binder list of
`stability_two_term`. Bodies are copied from the source.

#### 1. `landscape_stability_hyp` (line 286)

```lean
def landscape_stability_hyp (Z1 Z2 : (Fin d → ℝ) → ℝ)
    (j j0 : Int) (k n : Nat) (U : Set ℝ) (D : Set (Fin d → ℝ)) : Prop :=
  ∃ Lk : ℝ, 0 < Lk ∧
    L2Norm (fun t => landscape n (projDgmK Psi j j0 Z1 k) t
                    - landscape n (projDgmK Psi j j0 Z2 k) t) U
      ≤ Lk * LinfNorm (projection Psi j j0 (Z1 - Z2)) D
            * Real.sqrt (Metric.diam U)
```

**Why needed**: converts the `L∞` control of the projected difference into
`L²(U)` control of the landscape difference — the first link of both proofs.

**Status**: 🔶 named hypothesis. Proved informally in the manuscript
(Cohen-Steiner–Bubenik plus the elementary `L²(U)/L∞(U)` inequality,
Lipschitz constant `1` under Bubenik's normalization); not derived in Lean
from a fully instantiated frame object.

#### 2. `frame_proj_bound_hyp` (line 269)

```lean
def frame_proj_bound_hyp (Δ : (Fin d → ℝ) → ℝ) (j j0 : Int)
    (D : Set (Fin d → ℝ)) : Prop :=
  ∃ Cfp : ℝ, 0 < Cfp ∧
    LinfNorm (projection Psi j j0 Δ) D ≤ Cfp * LinfNorm Δ D
```

**Why needed**: bounds the multiscale projection in `L∞`; supplies the `Cfp`
that becomes Theorem A's constant.

**Status**: 🔶 named hypothesis. Derivable from (A1)–(A4) via dual
reconstruction; that derivation is in the manuscript, not in Lean.

#### 3. `scale_energy_bound` (line 300)

```lean
def scale_energy_bound (j j0 : Int) (Δ : (Fin d → ℝ) → ℝ)
    (U : Set ℝ) (D : Set (Fin d → ℝ)) (coeffSq : Int → ℝ) : Prop :=
  ∃ Cse : ℝ, 0 < Cse ∧
    LinfNorm (projection Psi j j0 Δ) D ≤
      Cse * Real.sqrt (Psi.B / Psi.A) * (2 : ℝ) ^ (-(j : ℝ) * s)
          * Real.sqrt (localEnergy Psi s j j0 Δ U D coeffSq)
```

**Why needed**: gives the second (scale-decay) branch of the `min` in
Theorem B; Theorem A does not use it.

**Status**: 🔶 named hypothesis. The manuscript derives `Cse` under
fine-scale dominance at level `(j, m₀)` with `χ⋆ > 0`; formalizing it would
need a Bernstein-type inequality mathlib does not have.

### Structural predicates are placeholders

`VanishingMoments`, `Regularity` and `Localization` (lines 147, 150, 153)
have body `True`. They are interface markers for (A2)–(A4), and **no closed
proof depends on them** — they do not appear in the binder list of either
main theorem. `Tame` (line 113) records only the `L∞` bound; the finiteness
half is carried by `PersistenceDiagram` being a `Multiset`.

A clean axiom list is therefore not a claim that the analytic content is
proved. It certifies that, once the three hypotheses above are granted, the
compositions are machine-checked and use nothing beyond mathlib's axioms.

### Reverse triangle — closed (2026-09-10)

**Location**: `TWS/Skeleton.lean:317`, `l2_norm_rev_tri`.

**Statement**:
```lean
theorem l2_norm_rev_tri (f g : ℝ → ℝ) (U : Set ℝ)
    (hf : MeasureTheory.MemLp (U.indicator f) 2)
    (hg : MeasureTheory.MemLp (U.indicator g) 2) :
    |L2Norm f U - L2Norm g U| ≤ L2Norm (fun t => f t - g t) U
```

**Proof**: `L2Norm g U` is `(eLpNorm (U.indicator g) 2).toReal`, which
`Lp.norm_toLp` identifies with the `Lp 2` norm of `MemLp.toLp`. After
rewriting `U.indicator (f - g) = U.indicator f - U.indicator g`, the
claim is mathlib's `abs_norm_sub_norm_le`.

Hypotheses are `MemLp` of the indicated functions (square-integrability
on `U`, including measurability). The older `IntegrableOn (f^2)` encoding
did not imply measurability of `f` and did not type-check as written.

**Impact**: `#print axioms TWS.l2_norm_rev_tri` reports
`[propext, Classical.choice, Quot.sound]`. There is no `sorry` in the
source. The remaining analytic content is the three named hypotheses
above, not a kernel gap.

## Development Workflow

### Editing in VS Code

1. Install Lean 4 extension
2. Open `formalization/` in VS Code
3. Edit `TWS/Skeleton.lean`
4. See real-time diagnostics

### Checking a Single Theorem

In a scratch Lean file next to the project:
```lean
import TWS
open TWS
#check @TWS.stability_Linf
#check @TWS.stability_two_term
#print TWS.stability_Linf
```
then elaborate it with `lake env lean scratch.lean`. Prefix with `@` to see
the section variables (`{d}`, `Psi`, `s`) that Lean inserts as leading
binders.

In terminal, to build a single module:
```bash
lake build TWS.Skeleton
```
There is no `TWS.MainTheorem` target — `Preliminaries / FrameStructure /
BesovEnergy / AuxiliaryLemmas / MainTheorem / Corollaries` are `/-! ## Module:
... -/` headers inside the one file, not separate modules.

### Adding New Theorems

1. Define theorem statement
2. Add docstring
3. Provide proof or mark with `sorry`
4. Record its status in the "Hypothesis Status" section above
5. Update paper Section 7 to match

### Maintaining Sync with Paper

**Critical**: Section 7 of the paper must exactly match the Lean file.

After editing Lean:
1. Update paper Section 7 (`sec:leanstatus`) and the `lst:linf`, `lst:frame`,
   `lst:main` listings in `paper/main.tex`
2. Regenerate the archived audit:
   `./scripts/print_axioms.sh docs/axioms_audit.txt` (then restore the
   header prose around the literal block)
3. Verify the sorry count matches the paper claim: `./scripts/check_all.sh`

To check a paper listing really is the Lean statement, transcribe it into a
scratch file and discharge it with the real theorem — if the `exact` closes,
the printed statement is the proved one:

```lean
theorem paper_lst_main <binders copied verbatim from the listing> :
    <conclusion copied verbatim from the listing> :=
  TWS.stability_two_term Psi s h_bounds Z1 Z2 j j0 k n U D coeffSq
    hU h_landscape h_proj h_se
#print axioms paper_lst_main   -- must not mention sorryAx
```

## Modularization Plan

Current status: **Monolithic file** `TWS/Skeleton.lean`

Future: Split into modules in `TWS/` directory:

```
TWS/
├── Preliminaries.lean        # Basic definitions (L∞, L², diagrams)
├── FrameStructure.lean       # Frame axioms and projections
├── BesovEnergy.lean          # Localized energy definitions
├── AuxiliaryLemmas.lean      # Helper lemmas
├── MainTheorem.lean          # Theorem A & B statements
└── Corollaries.lean          # Derived corollaries
```

**Benefits**:
- Faster incremental compilation
- Better organization
- Easier collaboration
- Cleaner imports

**To modularize**: done by hand — split `TWS/Skeleton.lean` at the
`/-! ## Module: ... -/` headers, add an `import` line per new module to
`TWS.lean`, and re-run `./scripts/check_all.sh`. There is no
`scripts/modularize.sh`.

## Common Issues

### `failed to create file` (Windows)

Not a Lean error — the `MAX_PATH` limit. See "Windows: build from a short
path" above; build from `C:\twsl` or another short directory.

### "unknown package 'mathlib'"

The dependency has not been materialized yet. Fetch it at the **pinned**
revision recorded in `lake-manifest.json`:

```bash
lake exe cache get
lake build
```

> Do **not** run `lake update`. It re-resolves `[[require]]` to the current
> mathlib master and rewrites `lake-manifest.json`, silently breaking the
> `db584cd6d46c92f209a44c0f1c829460d327499d` pin that makes this build
> reproducible. If a manifest has already drifted, restore it with
> `git checkout -- lake-manifest.json`.

### Build Takes Forever

First build compiles all of mathlib4. Download precompiled cache:

```bash
lake exe cache get
```

### "type mismatch" Errors

Almost always a toolchain/mathlib mismatch. Check that the pin is intact —
do not "fix" it with `lake update` (see above):

```bash
cat lean-toolchain                                   # leanprover/lean4:v4.33.0
grep -B2 -A2 '"name": "mathlib"' lake-manifest.json  # rev db584cd6d46c…
git diff -- lean-toolchain lake-manifest.json        # must be empty
```

### Proof Timeouts

Increase timeout in VS Code settings:
```json
{
  "lean4.serverArgs": ["-DmaxHeartbeats=500000"]
}
```

## Resources

- **Lean 4 Documentation**: https://lean-lang.org/lean4/doc/
- **Mathlib4 Docs**: https://leanprover-community.github.io/mathlib4_docs/
- **Lean Zulip Chat**: https://leanprover.zulipchat.com/
- **Theorem Proving in Lean 4**: https://leanprover.github.io/theorem_proving_in_lean4/

## Contributing

When contributing to formalization:

1. Follow mathlib naming conventions
2. Add docstrings to all declarations
3. Update the "Hypothesis Status" section of this file
4. Sync with paper Section 7 and the `lst:*` listings in `paper/main.tex`
5. Run `./scripts/check_all.sh` before committing; the sorry count must not
   go up, and **never discharge a `sorry` by weakening a statement**

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for details.

## Citation

See [`CITATION.cff`](../../CITATION.cff) at the repository root. There is no
public git URL yet; do not invent one.

## Contact

Corresponding author of the manuscript: Jaime Enrique Lincovil Curivil,
`jlincovilc@uni.edu.pe`.
