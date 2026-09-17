# Pre-registration — Commit 3, the guarded Laplacian audit

Written and hashed **before the run**. 2026-09-17.

---

## Recorded before this file: the symmetrization discrepancy

Measured in a diagnostic pass, so reported as a finding, not a prediction.

The B2 regime numbers supplied with this patch reproduce **exactly** — to three
decimals — only when the pinned symmetrization is **not** applied:

| n | supplied | `C = A` | `C = A + Aᵀ` (pinned) |
|---|---|---|---|
| 16 | 3.358 | **3.358** | 1.679 |
| 32 | 6.558 | **6.558** | 3.279 |
| 64 | 12.958 | **12.958** | 6.479 |
| 128 | 25.758 | **25.758** | 12.879 |

A banded conductance matrix is **already symmetric**, so `A + Aᵀ = 2A`, which
doubles every conductance and halves every resistance. The pinned rule is right
for raw attention, which is directed and row-stochastic; applied to a fixture
that is already symmetric it silently rescales by two.

Regime 1 reproduces independently (`R ≡ 1`, max deviation 1.1e-15 here against
a supplied 9.99e-16 — both floating-point dust). Regime 3 reproduces in shape
(0.421 here against 0.415 supplied) and still reverses.

**This is exactly why the perception layer ships a ratio API and not absolute
distances.** Under ratios the factor cancels; in a quoted number it does not.

---

## The contract, as specified

| | requirement |
|---|---|
| 1 | **Component guard** — nodes in different pieces return `inf`, never a `pinv` value |
| 2 | **Pinned tolerance** — an explicit `tol_ratio`, never the library's default `rcond` |
| 3 | **Foster is a self-check** — two-path, compared, and **never returned** |
| 4 | **Per-component load** — current-flow betweenness needs a connected graph |

One deviation from the drafted code, stated rather than made quietly: the Foster
check **raises** rather than `assert`s. `python -O` strips assert statements, and
a self-check that can be compiled away is not a self-check.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| A1 | An injected assembly bug — an edge present in `C` but dropped from `L` — **raises** | raises |
| A2 | A clean graph does **not** raise, for connected and disconnected inputs alike | no raise |
| A3 | The null-mode count cross-check catches a **deliberately wrong** component count | raises |
| A4 | Cross-component pairs are `inf` in **both** `D` and `R`; within-component pairs stay finite | inf / finite |
| A5 | Bare `pinv` on that same graph returns a **finite positive** number — the control that makes A4 mean something | finite |
| A6 | The Foster total appears **nowhere** in the returned dict, at any nesting depth | absent |
| A7 | Padding a graph with declared edges **clears** its cut vertices | 0 cuts |
| A8 | And under the same padding the **maximum load rises** — so an OR-gate on (cuts fell) OR (load rose) trips where a cuts-only gate would not | load rises |

**A8 is the one I could be wrong about.** Current-flow betweenness is normalised
per component, and padding adds routes that could spread load rather than
concentrate it. Whether the maximum rises or falls is not settled by writing it
down, and if it falls the OR-gate as proposed does not trip and the proposal
needs a different second sensor.

---

## Nulls, registered in advance

**NULL-A1.** A cut vertex is a routing fact, not a fault. Load concentration is
a routing fact too. Neither is a health score and neither is combined with the
other into one.

**NULL-A2.** Every reading is of a **declared** graph. Absence of an edge is
absence of a declaration. `invisible-edges/` measured that candidate undeclared
edges move 9 of 27 names on a real import graph; nothing in this module recovers
them.

**NULL-A3.** The Foster self-check catches **assembly** bugs — a Laplacian that
does not match its conductance matrix. It cannot catch a wrong graph, because
`n − k` is true of every drawing. `lmd-scaling/`, `jepa-probe/` and `lintel/`
each measured that separately.

**NULL-A4.** `tol_ratio` is a declared preference, not a found number. It is a
required-looking default here because the drafted contract names `1e-10`; that
choice is recorded and is not derived from anything.

**NULL-A5.** Current-flow betweenness on a weighted graph depends on the weights,
which are whatever the caller declared. It measures a drawing.

**NULL-A6.** n = 1 construction family for A7/A8, hand-built.

---

## What would falsify this

1. **A8 fails** — padding does not raise the maximum load, and an OR-gate of
   these two sensors does not catch what a cuts-only gate misses.
2. **A4 fails** — the guard leaks a finite number across components.
3. **A1 or A3 fails** — the self-check does not catch an assembly bug, and it is
   decoration.
