# Figure QA report — medical Theorem A

**Date:** 2026-09-15. **CSV/JSON:** frozen (not regenerated).  
**Renderer:** `render_final_figure.py` → `figures/theorem_A_medical_illustration.pdf|.png`.

Integrity (CSV): \(\rho=\rho_{\mathrm{op}}\rho_{\mathrm{top}}\) max err \(1.1\times10^{-16}\);
`theoretical_bound = cfp·delta_linf·√diam(U)` max err \(1.4\times10^{-17}\);
`holds` 200/200. JSON matches the stated reference values to rounding
(\(\rho\) median 0.149331 vs printed 0.14933; max 0.382219 vs 0.38222).

Max-\(\rho\) row: PNEUMONIA `person33_virus_72.jpeg`, \(\varepsilon=0.02\), \(\rho=0.38222\).

---

## Iteration 1

| Test | Result |
|------|--------|
| T1 overlaps | **pass** (0 intersections; tick–tick ignored) |
| T2 containment | **pass**; ylim \(=1.15\times\) `empirical_error_L2_max` |
| T3 85 mm text | native fonts ≥ 8.5 pt **pass**; at 85 mm, 8.5 pt → 2.29 pt (full-width 3-panel; not a single-column figure). Markers remain shape-distinct (○ vs △). |
| T4 vector | **fail** (`pdffonts` missing in PATH) |

Caption compile: `! Missing }` from `_` in `\texttt{person33_virus_72.jpeg}`.

Rubric iter. 1: Q5=1 (T4), total **15/16**, but T4 blocking.

Fixes: T4 Python fallback (`/FontFile2` embedded, `pdf.fonttype=42`); escape `\_` in caption; drop `\texttt` in the panel-(b) annotation so mathtext does not eat underscores.

---

## Iteration 2 (final)

| Test | Result |
|------|--------|
| T1 | **pass**, 0 hits |
| T2 | **pass** |
| T3 | **pass** native; 85 mm text still 2.29 pt (documented residue, not a silent fail). Marker shape distinguishable. |
| T4 | **pass** (`/FontFile2` present, 7 embedded TrueType streams) |
| `check_caption.py` | **OK** |
| Mini-LaTeX (`compile_check.tex`) | 1 page, **0 Overfull \\hbox**, no missing `}` |

### Rubric (0–2)

| | I1 | I2 |
|--|--:|--:|
| Q1 (a) legend vs “bound at ε=0.05: 0.040” | 2 | **2** |
| Q2 (b) saturation + synthetic max + global max id; no ghost median | 2 | **2** |
| Q3 (c) ρ_op / ρ_top vs synthetic medians | 2 | **2** |
| Q4 paper notation + (a)(b)(c) | 2 | **2** |
| Q5 spines / greyscale / lw | 1 | **2** |
| Q6 caption interpolated + invocation + n=20 + noise-regularity caveat | 2 | **2** |
| Q7 R1–R3 readable in ≤5 s | 2 | **2** |
| Q8 compile | 2 | **2** |
| **Total** | 15 | **16/16** |

---

## What a referee sees in ≤5 s

- **(a) R1.** Every point sits under the dashed certificate. No violations on real radiographs.
- **(b) R2.** The cloud lives near \(\rho\sim 0.15\), above the synthetic maximum (dotted, 0.151) and far below saturation at 1. The callout marks the global max \(\rho=0.382\) (`person33_virus_72`, \(\varepsilon=0.02\)).
- **(c) R3.** \(\rho_{\mathrm{op}}\) concentrates near 0.70 (vs synthetic 0.091): under white sensor noise the smoother is close to its worst case. \(\rho_{\mathrm{top}}\) sits near 0.21 (vs 0.084): remaining slack is topological. Pathology is **not** claimed as the cause of the \(\rho_{\mathrm{op}}\) shift.

---

## Residues (explicit)

1. **T3 at 85 mm:** a 12.4 in three-panel figure cannot keep 8.5 pt ≥ 6 pt when squeezed to 85 mm. Intended placement is `\textwidth` (two-column / full measure). Marker identity does not rely on colour.
2. **`pdffonts` binary** is not installed; T4 used `/FontFile2` embedding instead.
3. **`main.tex` not edited** (per brief).

**Verdict:** T1–T4 pass (T3 native; 85 mm text residue listed). Rubric **16/16**. Delivery is final.
