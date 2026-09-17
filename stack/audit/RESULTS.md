# Results — Commit 3, the guarded Laplacian audit

Run 2026-09-17. Offline, deterministic, no network.
Predictions locked in `prereg_audit.md`, sha256
`bd6aaae34e41cb2a66b39044d3124fcb282cf383f7ad72093e2283e86d4eb283`.

**Seven predictions hit. A8 missed — and the miss breaks the proposed OR-gate.**

---

## The headline

> **Padding defeats both sensors in the proposed gate, not just one.**

| | cuts | max load | deepest dependence |
|---|---|---|---|
| before | 3 | 0.5714 | 0.133333 |
| after four declared edges | **0** | **0.3088** | **0.257161** |

**A7 hit**: padding clears every cut vertex. **A8 missed**: the maximum load
**falls**, it does not rise. Padding adds routes, and routes *spread*
current-flow betweenness rather than concentrating it.

So an OR-gate of *(cuts fell)* OR *(load rose)* **does not trip** on the padding
attack. A cuts-only gate misses it, and the proposed two-sensor gate misses it
too. Both sensors move in the attacker's favour.

**The sensor that does move against the attacker is `fathom`'s deepest
dependence** — 0.133 → 0.257 here. `agi-stack/` measured 0.111 → 0.619 on a
graph with nothing in common with this one except the attack. Two independent
constructions, same direction.

**The OR-gate's second sensor should be deepest dependence, not load.** That is a
change to a proposed design, so it is recorded here and asserted in
`test_the_sensor_that_does_move_against_the_padding`, not made quietly inside
the module.

---

## The supplied regime numbers skip the pinned symmetrization

Measured before the pre-registration was written, so recorded as a finding.

| n | supplied | `C = A` | `C = A + Aᵀ` (pinned) |
|---|---|---|---|
| 16 | 3.358 | **3.358** | 1.679 |
| 32 | 6.558 | **6.558** | 3.279 |
| 64 | 12.958 | **12.958** | 6.479 |
| 128 | 25.758 | **25.758** | 12.879 |

A banded conductance matrix is **already symmetric**, so `A + Aᵀ = 2A` — every
conductance doubles and every resistance halves. The pinned rule is right for
raw attention, which is directed and row-stochastic. Applied to a fixture that is
already symmetric it silently rescales by two.

Regime 1 reproduces independently and agrees: `R ≡ 1`, max deviation 1.1e-15
against a supplied 9.99e-16 — both floating-point dust. Regime 3 reproduces in
shape (0.421 here against 0.415 supplied) and still reverses.

**This is why the perception layer ships a ratio API.** Under ratios the factor
cancels; in a quoted absolute number it does not.

---

## The contract, and one deviation

| | requirement | |
|---|---|---|
| 1 | component guard → `inf` | **A4 hit**, and `R` is masked as well as `D` |
| 2 | pinned `tol_ratio`, never default `rcond` | held; `1e-10` recorded as a *declared preference*, not a found number |
| 3 | Foster is a self-check, never returned | **A6 hit** — absent at every nesting depth |
| 4 | per-component load | held; components of ≤ 2 nodes get 0.0 rather than an error |

**The deviation, stated rather than made quietly:** the Foster check **raises**
instead of `assert`ing. `python -O` strips assert statements, and a self-check
that can be compiled away is not a self-check. `test_the_self_check_raises_rather_than_asserts`.

**One defect fixed from the draft:** the drafted `audit()` returned the raw `R`
while masking only `D`. A caller reading `R` would get exactly the confident
finite number across a void that the guard exists to refuse — 0.790569 on two
disjoint 4-rings, which **A5** pins as the control.

## What hit

- **A1** an injected assembly bug is caught by the two-path check
- **A2** clean graphs do not raise, connected or not
- **A3** a deliberately wrong component count is caught by the null-mode cross-check
- **A4/A5** cross-component pairs are `inf` in both `R` and `D`; bare `pinv` answers 0.790569
- **A6** no Foster total in the result, at any depth — and the check still runs
- **A7** padding clears every cut vertex

## What this cannot do

- **It reads a declared graph.** Absence of an edge is absence of a declaration.
  `invisible-edges/` measured candidate undeclared edges moving 9 of 27 names on
  a real import graph; nothing here recovers them.
- **A cut vertex is a routing fact, not a fault.** So is load concentration.
  Neither is a health score and the two are never combined into one number.
- **The Foster self-check catches assembly bugs, not wrong graphs.** `n − k` is
  true of every drawing — measured three separate ways in `lmd-scaling/`,
  `jepa-probe/` and `lintel/`.
- **`tol_ratio = 1e-10` is chosen, not derived.** It replaces numpy's default
  `rcond`, which `lmd-scaling/` measured flipping a published verdict depending
  on how the matrix had been assembled. Replacing an undeclared default with a
  declared one is an improvement; it is not a solution.
- **A7/A8 use one hand-built 9-node fixture.** The dependence result agrees with
  `agi-stack/` on a different graph, which is two, not many.

## Reproduce

```
python3 -m pytest stack/audit -q
```
