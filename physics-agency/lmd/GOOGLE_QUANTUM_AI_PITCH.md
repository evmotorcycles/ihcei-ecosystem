# Expression of Interest — Google Quantum AI (+ DeepMind)

**Joint empirical test of Latency–Metric Duality (LMD) via operator scrambling, and a
validated stability law for sequential agent swarms.**

**From:** Novora Research Initiative (Open Science Division) · open-science via
<https://github.com/evmotorcycles/ihcei-ecosystem>
**To:** Google Quantum AI (hardware prong) · Google DeepMind (agent-systems prong)

---

## 0. Read this first — why we are *not* overselling the simulation

A ruthless reviewer will immediately notice that our Layer-1 numbers are **analytically
expected**, and we agree. Our metric is defined from the graph's *effective resistance*,
and two facts are mathematical identities, not surprising empirical findings:

- resistance distance **is** a metric ⟹ **0 triangle-inequality violations** (we confirmed
  0 / 11,140 networks across n = 5…9 and 8,640 locked trials);
- effective resistance scales as 1/coupling ⟹ **d ∝ J^(−1/2)**, log-log slope **−0.5000,
  R² = 1.0** (we confirmed slope = −0.5 exactly on **240** stress runs spanning n = 4…10 and
  three different coupling grids — it is a law, not a fitted fluke, *because* it is algebra).

So the computation proves the framework is **internally consistent** and that the
**discriminator logic is sound** — nothing more. **The genuinely open, falsifiable question
is physical, and only your hardware can answer it:** does the *measured* operator-scrambling
latency between two pinned qubits, under a tunable-coupler sweep, actually track the
effective-resistance law (slope −0.5), or is it flat (a fixed background)? That is the
experiment. We are bringing a locked protocol and a blinded analysis to a question we
cannot answer in simulation.

---

## 1. Executive summary (two prongs)

1. **Hardware prong — Quantum AI.** Run a non-destructive **tunable-coupler sweep** on two
   pinned qubits of a Willow-class superconducting processor, read out **operator-scrambling
   latency** via an OTOC / Lieb-Robinson-front sequence, and fit log(distance) vs log(coupling).
   A **−0.5 slope** supports the emergent-metric reading; a **flat slope** supports the
   fixed-container null. Both are publishable; the null is pre-registered.
2. **Systems prong — DeepMind.** Our pre-registered **LISM** telemetry gives a validated,
   quantitative **stability law and circuit-breaker** design for *sequential* multi-agent
   pipelines — the failure mode where Agent A's output becomes Agent B's input and joint
   fidelity decays multiplicatively. Directly usable as the "systemic circuit breaker" that
   distributed-agent safety work calls for.

---

## 2. Hardware prong: distance as information lag

**Telemetric Metric:** `d(i,j)² = κ · τ_rt(i,j)`, with τ_rt the round-trip information latency
(commute time = effective resistance R_ij of the coupling graph). LMD runs Einstein's
clock-synchronization construction in reverse: instead of fixing a geometry to synchronize
clocks, it *defines* distance as the latency.

**Hardware mapping.**

| LMD primitive | Superconducting-processor manifestation |
|---|---|
| node i, j | two pinned, physically fixed qubits |
| coupling W_ij / J_ij | tunable-coupler bias (flux-controlled) |
| round-trip latency τ_rt | operator-scrambling time via OTOC forward–reverse sweep |
| distance d(i,j) | reconstructed interval `d = √(κ · τ_rt)` |

**Protocol.** (1) Pin two qubits i, j separated by an intermediate chain; keep their physical
positions fixed. (2) Sweep the tunable-coupler bias J along the path across ≥ 6 geometric
steps, near-zero → hardware max. (3) At each step, extract the OTOC decay / scrambling latency.
(4) Fit log(d) vs log(J). **Pre-registered decision (locked, SHA-256 `7ea30999…`):**

- slope ∈ [−0.52, −0.48] ⟹ **emergent (LMD)**: `d ∝ J^(−1/2)`
- slope ≈ 0 (`∂d/∂J = 0`) ⟹ **fundamental container** — reported as such, not rescued.

We perform the analysis **blind** and publish **either** outcome with full force, including a
flat null.

**Prior Layer-1 validation (analytically expected — see §0):** 0 / 8,640 triangle violations;
slope −0.5000, R² 1.000000; discriminator emergent-range 1.4525 vs fixed-null 0.0000.
Reproduce offline: `python3 physics-agency/lmd/run_lmd.py`.

---

## 3. Systems prong: the sequential-swarm stability law (LISM)

**The category correction.** High-bandwidth *parallel weight-averaging* (the "trillion-bit"
advantage) is real for copying static weights across identical nodes. It does **not** apply to
**sequential inference pipelines**, where agents translate, act, and re-encode for the next
agent. There, joint fidelity obeys a multiplicative law:

```
E = U · ∏ D_i,     D_i = D_enc,i · D_dec,i
```

**Cohort D (pre-registered, reproduced here).** A 500-node sequential agent tree, seeded,
offline:

- joint fidelity **decays 0.84 (depth 2) → 0.01 (depth 39)** — real per-hop curve in
  `lism-cohorts/appendix/cohort_D_decay.csv`;
- **corr(depth, D) = −0.887** (robust: −0.85…−0.93 across 30 seeds); realized success couples
  **linearly** to U·D (R² 0.93) and **not** quadratically (0.90) — the accelerating prior is
  disconfirmed.

**Consequence — the "zombie network."** Because agents run at silicon speed, this decay
unfolds in milliseconds: a pipeline can stay hyper-active while its semantic payload has
rotted (D below a usable floor). **Bandwidth does not save it; sequence does the damage.**

**The circuit breaker.** A receiver-side **Epistemological Intelligence (EI)** check at each
hop enforces a minimum-fidelity floor `D ≥ D_min` and a low enforcement-latency `τ_v`; when a
hop's decoded fidelity drops below the floor, it halts propagation and forces a reset /
human-in-the-loop. This is exactly the *systemic circuit breaker* that distributed sub-AGI
agent-safety work asks for — with a measured law behind the threshold.

---

## 4. Bring vs. ask

**We bring:** a pre-registered, SHA-256-locked protocol and pass/fail thresholds; a fully
reproducible, provenance-sealed simulation + analysis stack (31/31 offline, `$0`; origin
Merkle root `ebe46989…`, verify with `provenance/verify_provenance.py`); blinded analysis; and
co-authorship crediting the hardware group as experimental lead.
**We ask:** engineering time to translate our Laplacian commute-time equations into a Willow
pulse sequence; minor non-destructive diagnostic runtime for the coupler sweep; joint OTOC
analysis and a co-authored paper. (Systems prong: a pilot applying `E=U·D` + `τ_v`
circuit-breakers to a real multi-agent pipeline.)

---

## 5. Epistemic firewall (non-negotiable, and in any joint press)

Our Layer-1 telemetry shows only that a coordinate geometry is a mathematically consistent
consequence of information latency on a graph. The claim that **macroscopic physical spacetime
is likewise emergent (Layer 3) is NOT asserted as proven** — it is the motivating question the
experiment tests. Any joint communication must state: *"the experiment measures the scaling of
operator scrambling on a physical substrate (Layer 1); it does not prove the universe is a
simulation (Layer 3)."* We will not co-sign a "Google proves spacetime is a simulation"
headline.

---

## Appendix A — collaboration guardrails (symmetric partnership)

To keep this a peer collaboration rather than an absorption, we ask for:

- **Raw data, not smoothed summaries.** Access to the *unfiltered* OTOC decay profiles and
  Lieb-Robinson front velocities (not only post-processed "capability" curves), so the fit is
  done on transit-time data, not a black box.
- **Symmetric-null publication.** A flat/coordinate-invariant result (`∂d/∂J = 0`) is published
  with the same access and force as a positive one. No IP structure may block reporting a
  physical *failure* of the emergent metric.
- **Independent verification preserved.** Our locked, open analysis code runs on both sides; we
  do not transfer it under an exclusive license that removes our ability to verify.
- **Layer discipline in press** (as in §5).

## Appendix B — targeted routing (verify before sending)

For low-latency routing, address the note to the principal investigators who **currently lead**
(a) the tunable-coupler / OTOC–scrambling effort and (b) the quantum-chemistry / structure
work on the Willow program, plus a DeepMind contact on **distributed-agent safety** for the
systems prong. **Do not rely on names from secondary summaries — confirm the current
investigators and their exact roles from an authoritative Google source before sending**, so the
salutation is accurate. This document deliberately does not hard-code individual names/titles,
to avoid misattribution.

---

**Contact:** via the origin repository (issues / discussions):
<https://github.com/evmotorcycles/ihcei-ecosystem>. Honest scope: the physical experiment is
*proposed*; no physical result is claimed until a partner runs it.
