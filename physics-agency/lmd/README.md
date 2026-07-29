# LMD — the spacetime verdict matrix (pre-registered)

Latency-Metric Duality tests one equation:

> **d(i,j)² = κ · τ_rt(i,j)** — proper distance² equals round-trip information
> latency (commute time = effective resistance of the coupling graph).

Pin two probe sites so they cannot move. Sweep only the information **coupling**
between nodes. If space is a fundamental container, distance is fixed and nothing
happens. If space is **emergent** — distance *is* the latency — raising coupling
collapses the round-trip lag and the two pinned points contract as
**d ∝ coupling^(−1/2)**.

```
python3 physics-agency/lmd/run_lmd.py          # stdlib only, seeded, offline, $0
python3 -m pytest -q physics-agency/lmd/test_lmd.py
```

## Result (this run — measured)

| Hypothesis | Locked rule | Measured | |
|---|---|---|---|
| **H1 metric** | 0 triangle violations over ≥ 8640 networks | **0 / 8640** (2,583,360 checks) | ✅ |
| **H2 scaling** | median slope ∈ [−0.52, −0.48], R² ≥ 0.999 | **−0.5000**, R² **1.000000** (M=200) | ✅ |
| **H3 discriminator** | emergent range > 0, null range = 0 | emergent **1.4525**, null **0.0000** | ✅ |

**Verdict on this substrate: EMERGENT (LMD).** A genuine coordinate distance
emerges from a pure information-coupling matrix, obeys the predicted −½ law, and
the bolted-down fundamental-container null is exactly flat.

## The pre-registered fork (symmetric null)

The spec is SHA-256-locked (`7ea30999…`) *before* the run; the runner re-hashes it
and refuses to start on any mismatch. Critically, the null is symmetric:

- slope ≈ **−0.5** → distance contracts with coupling → **emergent (LMD)**
- slope ≈ **0** → distance invariant to coupling → **fundamental container** — and
  this would be reported as evidence *against* LMD, not rescued.

The data gave −0.5000, so the emergent verdict is what we report — but the runner
was equally able to return the fundamental verdict.

## Layer discipline (what is and isn't claimed)

- **Layer-1 (measured, locked):** the metric axioms hold; `d ∝ coupling^(−1/2)`;
  the model discriminates against a fixed-container null.
- **Layer-3 (NOT claimed as proven):** that *physical* spacetime is emergent, a
  rendered interface, or that this settles Van Raamsdonk / Ryu-Takayanagi / ER=EPR
  or the 2022 Bell-inequality Nobel work. That interpretation is motivating, not
  demonstrated here.
- The **physical** qubit-lattice / entangled-optical-clock version is **proposed,
  not performed.** This is a numerical demonstration that the *mechanism* is
  self-consistent and falsifiable, not a laboratory result.

Reuses the already-merged, validated endpoint functions in
`physics-agency/telemetric_metric.py` (identical code path — no reinvention).

---

## CORRECTION (2026-07-26) — the −0.5 slope is an ALGEBRAIC IDENTITY, not a verified prediction

The H2 result reported here ("median slope −0.5000, predicted −0.5000, R² ≈ 1") **is not
empirical**. It follows from the definitions by algebra:

```
W → sW   ⟹   L → sL   ⟹   L⁺ → L⁺/s   ⟹   R → R/s   ⟹   d = √R → d/√s
so   log d = −0.5·log s + const     EXACTLY, for EVERY graph
```

Controls with no relation to any substrate — a random graph and a path graph — return the
identical −0.5000 with R² = 1.00000000. See `governance-physics/gphys.py`, which
reproduces this and **excludes the corresponding gates from its evidential score** under
the repository rule that *a test which cannot fail is not evidence*.

**What this does and does not change.** H1 (a metric with zero triangle violations) still
stands as an implementation-and-connectivity check. What must no longer be claimed is that
the −0.5 exponent is a *confirmed prediction of Latency-Metric Duality*: any definition of
the form `d = √(κ·τ)` with `τ` homogeneous of degree −1 in the coupling produces it
automatically. The genuinely empirical content on real graphs is in
`governance-physics/` — GP2 (the metric is not merely degree, ρ = +0.8686) and GP4
(distinguishable from a degree-preserving null, z = +7.43).

---

# What a physics laboratory would actually have to do

**Nothing in this repository is a physics result, and no amount of further numerical work
will make it one.** Every number here is computed from a coupling matrix we wrote down.
The question below is what an experiment would have to measure for `d² = κ·τ_rt` to earn
Layer-1 status about the physical world.

## Why the obvious experiment is worthless

The instinct is to sweep coupling strength and check for the −½ exponent. **That
experiment cannot fail, so it proves nothing.** As shown above, `W → sW` forces
`log d = −0.5 log s` for *every* graph, including a random graph and a path graph. Any
apparatus that reports the −½ exponent as its result is measuring our definition, not
nature.

A real test needs a prediction that is **not** algebraically forced. There is one, and it
is sharp.

## The discriminating prediction: diffusive versus ballistic

LMD says distance is the square root of round-trip latency:

```
LMD                d ∝ τ^(1/2)      diffusive spreading
local QFT          d ∝ τ^(1)        ballistic — a linear light cone
```

The second is not a rival speculation; it is the **Lieb–Robinson bound**, and for systems
with local interactions it is confirmed experimentally. Operator fronts in local spin
chains move at a finite butterfly velocity, giving an exponent of 1, not ½.

**So LMD, read literally, is already in tension with established physics for local
systems.** Stating that plainly is the honest starting point. LMD's live domain is the
regime where a coupling *graph* — not a lattice geometry — is the only meaningful notion of
adjacency: strongly non-local, all-to-all, or fast-scrambling systems. The experiments
below are designed to find out whether that domain exists and where its boundary is.

## E1 — OTOC butterfly-front scaling

**Platform.** A programmable quantum processor with 30+ qubits and OTOC readout:
superconducting transmon arrays (Sycamore-class, IBM heavy-hex) or a trapped-ion chain.

**Protocol.** Measure the out-of-time-order correlator
`C(i,j,t) = ⟨|[W_i(t), V_j]|²⟩` by the standard echo/interferometric scheme. For each pair
`(i,j)`, extract the **front arrival time** `τ(i,j)` at a fixed OTOC threshold. Regress
`log d(i,j)` on `log τ(i,j)`.

**What it decides.**

| Measured exponent | Verdict |
|---|---|
| 1.00 ± 0.05 | ballistic — **LMD refuted in this regime** |
| 0.50 ± 0.05 | diffusive — consistent with LMD |
| anything else | both descriptions are wrong here |

**What it cannot do.** A single passing exponent does not confirm LMD, because one fitted
constant can absorb a lot. That is what E2 is for.

## E2 — the κ-transfer test *(the decisive one, and nobody has run it)*

A relation with a constant refitted per system is a **parameterisation, not a law**. LMD
has genuine content only if `κ` transfers.

**Protocol.** On one machine, with the same qubits and the same gate set:

1. Engineer coupling graph **A** (say a ring). Measure `τ_rt`, fit `κ`.
2. Engineer graph **B** with a *different* topology (tree, small-world, all-to-all).
3. **Predict** `d` for B from A's `κ` — with **no refitting whatsoever**.
4. Compare prediction to measurement.

**What it decides.** If `κ` must be refit per topology, LMD is bookkeeping. If a single
`κ` predicts across topologies, that is the first genuinely non-trivial empirical support
the framework would have. **This is the experiment that matters most**, and it is the one
the numerics in this repository fundamentally cannot substitute for.

**Best current platform.** Trapped-ion systems with all-to-all connectivity (e.g.
Quantinuum H-series) can realise arbitrary coupling graphs on the same register, which is
exactly what steps 1–3 require. Superconducting devices have fixed lattice connectivity and
would need the graph emulated in circuit depth, weakening the comparison.

## E3 — the tunable-range test: where is the boundary?

**Protocol.** A trapped-ion chain gives programmable power-law couplings
`J_ij ∝ 1/|i−j|^α`, with α tunable roughly 0 → 3 by laser detuning. Repeat E1 across α.

**Prediction, stated so it can fail.** LMD should fail at large α (short range, ballistic)
and have its best chance as α → 0 (all-to-all, where effective resistance is the only
natural metric). A **crossover** should exist at intermediate α.

**What it decides.** If the exponent is 1 at every α, LMD has **no regime** and is finished
as a physical claim. If a crossover is found, LMD becomes a *bounded* effective description
with a measured domain of validity — which is a scientific gain, not a retreat.

## E4 — the mandatory negative control

Because the −½ exponent is an identity, **any** protocol must be run against structures
with no relation to the claim: a randomised coupling graph and a path graph, on the same
hardware, same readout. If they return the same "distance" law, the apparatus is measuring
the definition and the run is void.

This is the hardware version of the control that already forced the correction above. It
is not optional and it goes in the pre-registration, not the discussion section.

## What a clean sweep would — and would not — establish

**Would establish `[L1]`:** that round-trip information latency on a programmable coupling
graph induces a metric which predicts operator-spreading geometry across topologies with a
single transferable constant, within a measured range of α.

**Would NOT establish:** that physical spacetime is emergent, that this settles
Ryu–Takayanagi, Van Raamsdonk, or ER=EPR, or that the interpretive reading is correct.
Those remain **`[L3]`** and no version of these experiments adjudicates them.

**The gap that would still remain.** OTOC front geometry is *operator spreading*, not
proper distance in general relativity. Connecting the two requires an additional argument
that has not been made here and should not be smuggled in by shared notation. Anyone
presenting LMD must say this out loud.

## Pre-registration requirements before any beam time

1. Lock the exponent thresholds and the κ-transfer tolerance **before** the first shot.
2. Register E4's controls as gates, not checks — with the run voided if they fire.
3. Register the **symmetric null**: an exponent of 1.0 is reported as evidence *against*
   LMD, and is not to be rescued by redefining τ.
4. State in advance that a per-topology refit of κ counts as a **failure** of E2, not as a
   calibration step.
