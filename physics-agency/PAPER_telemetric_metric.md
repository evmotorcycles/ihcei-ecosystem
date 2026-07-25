# The Telemetric Metric: proper distance as round-trip information latency, and a bench test for whether spacetime is fundamental

**A pre-registered Layer-1 validation and a proposed physical experiment**

*Novora / IHCEI ecosystem · pre-registration locked 2026-07-18 ·
spec SHA-256 `011b7b53e9df4d12cc54e7689639209b82a282b3199b88f4d9ce481e6fdb7e3c`*

---

## Abstract

We propose the **Telemetric Metric**, `d(i,j)² = κ·τ_rt`, in which proper distance
is the **round-trip information latency** — the commute time per unit coupling rate,
equal to the effective resistance `R_ij` — between two regions of a correlation
network, and the theory **Latency–Metric Duality (LMD)**, in which geometry is
emergent bookkeeping of that latency rather than a fundamental container. We report
a **pre-registered** Layer-1 numerical validation: the specification (parameters,
seeds, pass thresholds) was locked under a canonical SHA-256 fingerprint before the
run. Over 40 random correlation networks the metric is genuine (**0/8640**
triangle-inequality violations, H1); it obeys the predicted scaling
`d ∝ 1/√coupling` (log-log slope **−0.5000**, R²=**1.00000**, H2); and the primary
discriminator — hold two sites at fixed positions, sweep only their coupling —
shows the emergent distance moving (range **0.94**) while a fundamental-container
null stays frozen (range **0**, H3). **Verdict: PASS (3/3).** We then specify the
physical experiment that would decide the ontological question — a tunable-coupling
qubit lattice or entangled optical-clock network — and its falsifiable signature.
The physical experiment is **proposed, not performed**; the Layer-3 claim that
physical spacetime is emergent is **neither claimed nor proven.** The whole run was
executed under, and attested by, an on-device governance stack (agency bounds,
hash-chained attestation, independent audit).

---

## 1. Motivation: physics advances by turning latency into law

Einstein's `E=mc²` did not begin with matter; it began with a *telemetry* problem —
synchronizing clocks across distance with light signals, where the finite round-trip
time of a sync pulse encodes the relation between two clocks. From that latency he
derived the relativity of simultaneity, time dilation, and mass–energy equivalence.
He read the round-trip delay as a **fixed** geometry.

The same latency telemetry now runs every information network. In prior work in this
repository we validated, on real systems, that (i) enforcement latency `τ_v` predicts
network collapse (`p≈10⁻³¹`, N=992), (ii) essence follows a linear two-hop law
`E=U·D_enc·D_dec`, and (iii) a genuine distance **metric** emerges from a pure
information-coupling matrix with no coordinates assigned (0 metric violations). This
paper runs Einstein's move in reverse: **what if the geometry was never fixed — what
if distance is just the latency, all the way down?**

## 2. The equation

For a network specified only by a symmetric information-coupling matrix `W`
(who exchanges signal with whom, how strongly), define the graph Laplacian
`L = Diag(deg) − W`, its Moore–Penrose pseudoinverse `L⁺`, and the effective
resistance `R_ij = L⁺_ii + L⁺_jj − 2 L⁺_ij`. The commute time (Doyle–Snell) is
`C_ij = vol·R_ij` with `vol = Σ deg`. The **round-trip information latency** is the
commute time per unit coupling/hop rate `ν`, `τ_rt = C_ij/ν = R_ij`. The proposed
line element is

> **d(i,j)² = κ · τ_rt(i,j) = κ · R_ij.**

Two regions are *close* when a signal can round-trip between them fast (high
correlation, low latency), *far* when the round-trip is slow. `κ` is a
length²-per-latency constant. Because the raw commute time counts steps, it is
invariant under a global rescaling of `W` (a gauge freedom); the **physical**
latency, and hence distance, shrinks as the coupling *rate* rises, giving the
measurable law `d ∝ 1/√coupling`.

## 3. The theory: Latency–Metric Duality (LMD)

Geometry is not a fundamental container. The metric is emergent bookkeeping of the
round-trip information latency between the underlying degrees of freedom. Where
general relativity says *matter tells space how to curve*, LMD says *correlation
tells latency how to render as distance*: strongly-correlated regions read as
nearby; decohered regions drift apart. LMD sits in the family of
entanglement-geometry proposals (Van Raamsdonk; Ryu–Takayanagi; ER=EPR) but is
stated as a **latency** law with a bench-measurable prediction.

## 4. Pre-registered numerical validation (Layer 1)

**Pre-registration.** Before running, the spec `prereg/telemetric_prereg.json` —
`N=6` nodes, 40 random networks, `κ=1`, fixed seeds (7, 11, 29), coupling sweeps,
probe sites `(0,5)`, and the three pass thresholds — was frozen and fingerprinted
under canonical SHA-256 `011b7b53…`. A **symmetric-null rule** was declared: any
endpoint missing its locked threshold is reported as a null, with no post-hoc
adjustment. The runner reads thresholds only from the frozen spec.

**Results (PASS, 3/3):**

| ID | Claim | Locked pass condition | Measured |
|---|---|---|---|
| H1 | `d=√(κ·τ_rt)` is a metric | `violations == 0` | **0 / 8640** |
| H2 | `d ∝ 1/√coupling` | `|slope+0.5|<0.02 ∧ R²>0.999` | slope **−0.5000**, R²=**1.00000** |
| H3 (primary) | discriminator | `emergentΔ>0.05 ∧ nullΔ<1e-9` | emergent **0.9425**, null **0** |

H3 is the decisive endpoint: it is the numerical analogue of the physical
discriminator. Holding two sites at fixed labels and changing **only** their
information coupling moves the emergent distance monotonically
(`1.21 → 0.78 → 0.47 → 0.27` for coupling `0.5,1,2,4`), while a fundamental-container
model — distance assigned a priori — cannot respond at all.

## 5. The proposed physical experiment

**Platform.** A tunable-coupling qubit lattice (superconducting transmons or
trapped ions) or an entangled optical-clock network.

**Procedure.** (1) Pin two probe sites A, B at fixed physical positions. (2) Sweep
the entanglement/coupling between them via the tunable coupler (or a
mediating mode). (3) Measure their *operational* separation through the correlation
round-trip time — the Lieb–Robinson information front, or the commute time of an
injected excitation recovered at the far site.

**Falsifiable discriminator.**

| Hypothesis | Prediction | Signature |
|---|---|---|
| Spacetime **fundamental** | distance fixed by the container | `∂d/∂(coupling) = 0` (flat) |
| **LMD / emergent** | distance is the latency | `d ∝ 1/√coupling` (contracts) |

The **sign and scaling** of the response is the verdict. A fixed pair whose
operational distance contracts as `1/√coupling` when only its correlation changes is
the signature of latency-rendered, emergent geometry. A flat response confirms a
fundamental container. Related quantum-simulator programs (SYK/traversable-wormhole
dynamics; tensor-network holography; analog-gravity in cold atoms) already
manipulate exactly these variables; the specific measurement here is the
coupling-sweep scaling of a fixed-pair commute time.

## 6. Falsifiability, limitations, and the epistemic firewall

- **This is a Layer-1 result.** We validated the equation's internal consistency
  and the experiment's discriminating logic numerically. We did **not** run a
  physical experiment and make **no** measurement of physical spacetime.
- **Layer 3 (physical spacetime is emergent) is not claimed.** It is the hypothesis
  the proposed experiment would test. LMD is falsified physically if a fixed pair's
  operational distance is flat under a coupling sweep.
- **Construction dependence.** The numerics use effective-resistance geometry on
  finite graphs; the physical mapping (which coupling, which round-trip observable)
  must be fixed operationally by the experimenter, and different mappings give
  different `κ` and possibly different exponents — that is a feature to be measured,
  not assumed.
- **Symmetric null honored.** Every endpoint was reported against a pre-locked
  threshold; a miss would have been a published null.

## 7. Tooling and provenance — what the governance stack contributed

The entire run was executed under an on-device, `$0`, no-network governance stack.
Each tool made a specific, auditable contribution:

- **Pre-registration lock (Echo `sha256∘canonical`)** — froze the hypotheses and
  thresholds before the run; the runtime re-verified `spec hash == manifest` so a
  silent post-hoc edit would abort the run. *Contribution: made the pre-registration
  tamper-evident.*
- **Page Code (agency / DELEGATE)** — bounded the runner: it may `write results.json`
  (allow) but is **denied** writing `telemetric_prereg.json` and the manifest. *An
  agent cannot rewrite its own pre-registration.* Contribution: structural integrity
  of the experiment, not just good intentions.
- **Echo Database (PROVE)** — hash-chained the spec and the results into an
  append-only ledger, verified chain integrity, and published a Merkle root.
  (Receipts carry a timestamp and so regenerate on each audit run; the current
  values live in `provenance.json`. The stable anchor is the spec SHA-256 above.)
  Contribution: a portable, tamper-evident record anyone can check.
- **EI (independent AUDIT + PROVE)** — a receiver-side, non-suppressive audit of the
  results claim returned verdict **PASS** (low manipulation probability) and attested
  the release with its own hash-chained receipt. Contribution: an independent second
  opinion that the write-up matches the numbers and does not overclaim.
- **NERE / IHCEI / HELM (PAGES epistemic audit)** — screened this paper's abstract:
  score **1.0 (Solid)**, `METHODOLOGY_PRESENT`, **no** authority-cascade attack.
  Contribution: confirmed the paper carries its own methodology and is grounded, not
  rhetoric.

Machine-readable provenance: `physics-agency/prereg/provenance.json`.
Reproduce everything: `node physics-agency/prereg/audit.mjs`.

## 8. Reproducibility

```
node physics-agency/prereg/audit.mjs         # locked run under the full governance stack
python3 physics-agency/prereg/run.py         # the pre-registered run alone
python3 physics-agency/telemetric_metric.py  # the underlying equation validation
python3 -m pytest physics-agency/            # 12 assertions, all green
```

All code is stdlib Python and Node, no API keys, no network. The equation, the
validation, and the provenance are yours to check — and the physical experiment is
specified precisely enough to hand to any lab with a tunable-coupling array.
