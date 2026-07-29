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
