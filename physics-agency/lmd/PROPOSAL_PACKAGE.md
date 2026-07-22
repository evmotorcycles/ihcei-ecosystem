# Proposal package — finalized

Everything needed to send the LMD/LISM collaboration proposal, assembled and corrected.
Companion files: `GOOGLE_QUANTUM_AI_PITCH.md` (full pitch), `RED_TEAM.md` (objections),
`OUTREACH.md` (contact plan), `EXPRESSION_OF_INTEREST.md` (lab-agnostic one-pager).

---

## 1. Technical abstract (for a preprint / proposal cover)

> **Probing Latency–Metric Duality: operator-scrambling geometry on superconducting qubits,
> and a cascade circuit-breaker for multi-agent pipelines.**
>
> We present a unified, pre-registered framework spanning two domains. **Prong 1 (hardware).**
> Latency–Metric Duality (LMD) defines operational distance as round-trip information latency,
> `d(i,j)² = κ·τ_rt`. On a correlation graph, τ_rt is the effective resistance, so a global
> coupling sweep yields `d ∝ J^(−1/2)` (slope −0.5000, R² 1.0, 0/8640 metric violations across
> 240 stress iterations). We stress that this is an **algebraic identity**, not a physical
> result. We propose a non-destructive experiment on a tunable-coupling superconducting array:
> pin two qubits, sweep the coupler bias J, read operator-scrambling latency via OTOC /
> butterfly-front sequences, and test the scaling against the null `∂d/∂J = 0`, with a
> pre-registered decoherence control. **Prong 2 (systems).** LISM models sequential agent
> pipelines, whose joint fidelity decays multiplicatively; from real 39-hop telemetry
> (fidelity 0.84→0.01, corr −0.887, linear R² 0.93) we derive a drop-in circuit breaker that
> halts a pipeline before it degrades into a hyper-active, zero-utility state. We offer the
> collaboration under symmetric guardrails: raw-data fitting, mandatory symmetric-null
> publication, and strict Layer-1 press discipline.

## 2. LISM formalization — CORRECTED

> ⚠️ **Correction.** A version circulated as `E = U·∏Dᵢ + D_min/τ_v`. That is **malformed** —
> it adds a fidelity floor over a time constant to a fidelity product; the terms are not
> commensurable and it is not our model. The correct formalization is below.

**Pipeline health.** For a sequential pipeline of hops `i = 1..n`, each with per-hop fidelity
`Dᵢ ∈ [0,1]`, joint fidelity is the product

```
H_n = ∏_{i=1}^{n} D_i
```

**Realized outcome.** Realized success couples to capacity × joint fidelity (LISM's linear
law, empirically favored over the quadratic):

```
E = U · H_n = U · ∏_{i=1}^{n} D_i
```

**Circuit-breaker trip rule.** `D_min ∈ (0,1]` is the minimum permissible joint fidelity; `τ_v`
(a non-negative integer number of hops) is the enforcement latency — how long the system may
remain below the floor before halting. The breaker trips at the first hop `n` such that

```
H_n < D_min   for   τ_v   consecutive hops     ⇒   halt propagation (E → 0 downstream)
```

(`τ_v = 0` ⇒ trip on first crossing.) This is exactly what `lism-cohorts/circuit_breaker.py`
implements and tests; on the real Cohort D profile with `D_min = 0.10` it trips at hop 23,
preventing ~19 further "zombie" hops.

## 3. Cover email — finalized (fill brackets; verify recipients first)

> **Subject:** Proposed non-destructive coupler-sweep test of a latency→distance scaling law
> on a superconducting array
>
> Dear Dr. [LAST NAME],
>
> I lead an open-science project proposing a small, non-destructive experiment your group is
> uniquely equipped to run: pin two qubits at fixed coordinates, sweep the tunable-coupler bias
> J between them, read out operator-scrambling latency (OTOC / butterfly front), and fit
> log(distance) vs log(J).
>
> The prediction is pre-registered under a public SHA-256, and the analysis is blind. We state
> upfront that our offline slope (−0.5000) is an algebraic property of graph effective
> resistance — **not** a hardware discovery. The open, falsifiable question is physical: does
> the array reproduce that −½ contraction under a coupler sweep, or is it flat (`∂d/∂J = 0`)?
> Either outcome is publishable; the null is pre-registered with equal weight.
>
> Reproducible offline at zero cost — `python3 physics-agency/lmd/run_lmd.py` (repo: [LINK];
> preprint: [arXiv LINK]; LMD spec hash `7ea30999…`). We bring the locked protocol, blinded
> analysis, and a pre-registered decoherence null control; we ask only for secondary diagnostic
> runtime and co-authorship with your group as experimental lead.
>
> Two paragraphs of detail and the full protocol are attached. Would a short call be worthwhile?
>
> With respect,
> [NAME] — Novora Research Initiative — [CONTACT]

**Candidate recipients (VERIFY current role & contact from a primary Google source before
sending).** Sergio Boixo and Ryan Babbush are long-standing, publicly-documented leads in
Google's quantum-algorithms / theory effort and are plausible high-value targets for the
hardware prong; confirm their current titles and preferred contact from the Google Quantum AI
team page or a recent primary paper — do not rely on secondary summaries. Do **not** assert
program names ("GPAR"), a specific intake form URL, or a named algorithm ("Quantum Echoes") /
report date unless you have confirmed them against a primary Google publication (see
`OUTREACH.md §4`).

## 4. Cirq scaffold — honest, not fabricated

A hardware-faithful OTOC simulation belongs on the collaboration side and requires `cirq`
(not a dependency here). `hardware_interfaces/mock_willow_sweep.py` provides the honest seam:
the **prediction** runs offline (the −0.5 identity), and `measure_scrambling_latency()` is the
hook a hardware team fills in. It deliberately raises `NotImplementedError` rather than
hard-coding `τ_rt = 1/J` and "confirming" the slope — a circular construction we explicitly
reject.

## 5. Pre-flight checklist

- [ ] Post preprint to arXiv (quant-ph / gr-qc) → citable priority + one-click link.
- [ ] Confirm `bash reproduce_all.sh` runs < ~5 min from a clean clone (33/33).
- [ ] `python3 provenance/verify_provenance.py` → root `ebe46989…` MATCH.
- [ ] Verify recipient names / roles / intake channel from primary sources (§3, `OUTREACH.md`).
- [ ] Cover email: one ask, one working link, no Layer-3 metaphysics in the body.
- [ ] Keep guardrails ready (`GOOGLE_QUANTUM_AI_PITCH.md` Appendix A; `RED_TEAM.md`).
