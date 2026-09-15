# Pre-registration — what does the −0.5 coupling slope actually measure?

Written and hashed **before the run**. 2026-09-15.

---

## The claim under test

A GPU notebook sweeps a coupling strength `J` across a weighted ring Laplacian,
reconstructs `d_ij = sqrt(R_ij)` from `pinv(L)`, fits a log–log line, and reports:

> Reconstructed Log-Log Contraction Slope: −0.500000
> Correlation R²: 1.000000
> VERDICT: PASS. Space is Emergent via Latency-Metric Duality (slope is −0.5 exactly).

Its own plot labels a −0.5 line **"Theoretical LMD Null"**. The measured curve
lands on that line. So the run declares PASS on landing exactly where its
declared null sits. That inversion is the first thing to check.

The second is arithmetic. The sweep builds `L = J · L₀`, where `L₀` is the
unweighted ring Laplacian and `J` is one scalar multiplying **every** edge.
For any `c > 0` the Moore–Penrose pseudo-inverse is homogeneous of degree −1:

    pinv(cL) = pinv(L) / c    =>    R(cL) = R(L)/c    =>    d(cL) = d(L)·c^(−1/2)

so a log–log slope of exactly −0.5 follows from the definition of `pinv`, before
any graph is drawn. If that is the whole content, the sweep cannot return any
other number, and fifteen sampled couplings carry no more information than one.

This repository already relies on that identity in the opposite direction.
`spar.scaled(structure, factor)` carries the docstring *"Bearings must not
move."* — because bearing is `w·R`, and `w` rising by `c` cancels `R` falling by
`c`. The notebook measures the half of that cancellation that does move.

---

## Predictions

### Arm 1 — is −0.5 a property of the ring, or of the scalar?

Same sweep, same 15 couplings (`logspace(-1, 2, 15)`), five different graphs at
n = 100: the ring, a star, a path, a complete graph, and one Erdős–Rényi draw at
seed 0.

| # | Prediction | Value |
|---|---|---|
| S1 | The ring reproduces the notebook: slope −0.5 and d(0,50) = 5·J^(−1/2) | \|slope + 0.5\| < 1e-9 |
| S2 | **Every one of the other four gives the same −0.5**, including graphs with no ring, no symmetry and no lattice | all \|slope + 0.5\| < 1e-9 |
| S3 | R² = 1 to floating point for all five — the line is exact, not well-fitted | 1 − R² < 1e-12 |
| S4 | One coupling determines all fifteen: `d(J) = d(1)·J^(−1/2)` | max rel. dev < 1e-12 |

**S1–S4 are listed as verification of an identity, not as discovery** — the same
convention `agi-stack/prereg_stack.md` used for L1–L3. Their point is the
contrapositive: a result that holds for a star, a path and a random graph
equally is not evidence about lattices, rings, or space.

### Arm 2 — the version that can fail

Break the homogeneity. Ring at n = 100 with every edge at weight 1 **except one**
edge (0,1) whose weight is swept as `J`. Now `J` is not a global scalar, the
cancellation does not apply, and the exponent is not fixed by `pinv`.

| # | Prediction | Value |
|---|---|---|
| S5 | The fitted slope is **not** −0.5, by a wide margin | \|slope + 0.5\| > 0.3 |
| S5b | It is shallow, because 99 unswept edges carry a J-independent parallel route | \|slope\| < 0.15 |
| S5c | The log–log relation is **not** a straight line: it flattens at both ends | R² < 0.99 |

**S5 is the only prediction here I could be wrong about**, and it is the only one
worth running. If S5 fails and the heterogeneous sweep also returns −0.5, then
the exponent survives the loss of homogeneity and my reading of the identity is
incomplete.

### Arm 3 — does the instrument refuse when there is no path?

Two disjoint rings of 50, swept identically. Nodes 0 and 50 are in different
components; the true effective resistance between them is undefined.

| # | Prediction | Value |
|---|---|---|
| S6 | `pinv` returns a **finite** number for that pair anyway | finite |
| S7 | And it still scales at −0.5, so the disconnected case is indistinguishable from the connected one by slope alone | \|slope + 0.5\| < 1e-9 |

**S6–S7 are the finding that matters for this project's standing rule** that
absence of an edge is absence of a declaration. If a bare `pinv` sweep reports a
confident coordinate for a pair with no route between them, then the sweep has
no way to say "not connected", and any claim that geometry was *reconstructed*
has to name which pairs were reachable.

### Arm 4 — precision

The notebook printed `d(0,50) = 15.811394` at J = 0.1. The exact value is
`5·sqrt(10) = 15.8113883008...`, so the printed figure is wrong in the 7th
significant figure — a relative error near 4e-7, which is float32, not float64.
JAX defaults to float32 unless `jax_enable_x64` is set, and the notebook does not
set it.

| # | Prediction | Value |
|---|---|---|
| S8 | At float64 the ring matches the closed form `sqrt(d(n−d)/n / J)` | max rel. dev < 1e-12 |
| S9 | At float32 it does not, and the error is ~1e-7, matching the published digits | rel. dev > 1e-8 |

The notebook's own gate is `np.isclose(slope, -0.5, atol=1e-4)`. **No prediction
is registered for the float32 slope**: a least-squares fit can average noise
either way and I do not know which. It is measured and reported, not predicted.

---

## Nulls, registered in advance

**NULL-S1.** Nothing here shows the notebook is *wrong*. Every number it printed
is reproducible and the ring arithmetic is correct. The claim under test is what
the number means, not whether it was computed.

**NULL-S2 — the one that governs the verdict.** "Space is emergent" is not a
statement this run can reach, in either direction. An identity about `pinv`
cannot confirm a physical thesis and cannot refute one. If S2 holds, the correct
report is *the sweep does not discriminate*, which is an **inconclusive**, not a
disproof.

**NULL-S3.** The GPU is irrelevant to every result here. These are 100×100
pseudo-inverses; the backend changes the runtime and the default dtype, not the
mathematics. `jax.default_backend()` printing `gpu` is not evidence for anything
the sweep concludes.

**NULL-S4.** Arm 2 sweeps one chosen edge on one chosen topology. A different
edge on a different graph gives a different exponent, and no claim is made about
heterogeneous graphs in general.

**NULL-S5.** n = 1 notebook, reproduced. Nothing generalises to other coupling
sweeps, and nothing here evaluates latency–metric duality as a physical
proposal — only this script's ability to bear on it.

**NULL-S6.** I did not run the original on a GPU and cannot verify its provenance.
Arm 4 infers float32 from published digits. That inference could be wrong for
reasons I cannot see from a pasted transcript.

---

## What would falsify this

1. **S2 fails** — the −0.5 is specific to the ring, the sweep discriminates
   topology after all, and the identity is not the whole story.
2. **S5 fails** — breaking homogeneity leaves the exponent at −0.5, which would
   mean −0.5 is not a consequence of the global scalar.
3. **S6 fails** — the pseudo-inverse refuses or returns infinity across
   components, and the instrument does report unreachability on its own.
