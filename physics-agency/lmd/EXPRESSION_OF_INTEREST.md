# Expression of Interest — a hardware test of Latency-Metric Duality

**One-line ask.** We have a pre-registered, computationally validated prediction that
the *effective information-theoretic distance* between two **spatially pinned** sites
contracts as **d ∝ J^(−1/2)** when their coupling **J** is swept. We are seeking a
hardware partner to run the physical sweep on an existing platform. Either outcome —
the −½ contraction, or a flat null — is a clean, publishable result.

> **Framing (read first).** We lead with the **Layer-1** falsifiable protocol, *not*
> with any "spacetime is emergent" interpretation. We are not asking a lab to endorse a
> metaphysical claim. We are proposing a concrete measurement with a locked null.

---

## 1 · The prediction (already validated computationally)

The Telemetric Metric proposes that operational distance is round-trip information
latency: **d(i,j)² = κ · τ_rt(i,j)**, with τ_rt the commute time (= effective
resistance) of the coupling graph. On a fixed pair of sites, raising the coupling rate
collapses the round-trip latency, so:

- **Emergent (LMD):** `d ∝ J^(−1/2)`  → log-log slope **−0.5**
- **Fundamental container (null):** distance is set by a background metric; sweeping J
  on bolted-down sites does nothing → slope **≈ 0**

**Pre-registered computational result** (spec SHA-256 `7ea30999…`, reproducible offline,
`$0`):

| Test | Locked rule | Measured |
|---|---|---|
| metric axioms | 0 triangle violations, ≥8640 nets | **0 / 8640** |
| −½ scaling | slope ∈ [−0.52,−0.48], R² ≥ 0.999 | **−0.5000**, R² **1.000000** |
| discriminates | emergent range > 0, null range = 0 | **1.4525 vs 0.0000** |

Reproduce: `python3 physics-agency/lmd/run_lmd.py`. Provenance root over the whole
frozen record: `ebe46989…` (`provenance/verify_provenance.py`).

## 2 · The proposed physical experiment

1. **Pin** two probe sites at fixed physical positions (they must not move).
2. **Sweep** only their information coupling J across a geometric grid (≥6 points).
3. **Measure** their operational "distance" via the platform-native proxy for
   round-trip information latency / effective resistance:
   - qubit lattice → **OTOC decay / operator-spreading time**, or state-tomography
     mutual-information distance;
   - optical-clock network → **Ramsey / correlated-phase** accumulation between nodes.
4. **Fit** log(d) vs log(J). **Decision, locked in advance:** slope within [−0.52,−0.48]
   ⟹ contraction (LMD); slope ≈ 0 ⟹ fundamental container. We register the null and do
   the analysis blind to preserve the epistemic firewall.

## 3 · What we bring / what we ask

**We bring:** the SHA-256-locked protocol and pass/fail criteria (no post-hoc moving of
goalposts); a fully reproducible, provenance-sealed simulation; blinded analysis code;
and co-authorship terms that credit the hardware group as the experimental lead.
**We ask:** time on an existing tunable-coupling platform to run one coupling sweep on
a pinned pair — no new hardware required.

---

## 4 · Best candidate labs (chosen)

We recommend a **two-platform strategy**: a superconducting/atomic **qubit-lattice**
test and an orthogonal **optical-clock** cross-check. Agreement across two physically
unrelated platforms would be far stronger than either alone.

### Lead — Google Quantum AI (Santa Barbara)
**Best single match.** They pioneered **tunable couplers** on superconducting arrays —
exactly the "pin two sites, dial J from 0→max" capability — and have a mature stack for
measuring **information scrambling / OTOCs**, which is the most direct hardware proxy for
τ_rt (round-trip latency). Highest technical readiness for the exact sweep.

### Co-lead — Harvard, Lukin Lab (Cambridge)
**Cleanest realization of "pinned sites."** Rydberg **neutral-atom arrays** hold atoms in
fixed optical tweezers (literally bolted-down probes) with laser-tunable interactions, and
the group actively studies emergent phenomena from correlation networks — receptive to the
framing and able to run the sweep with very clean geometry.

### Orthogonal cross-check — JILA / NIST, Jun Ye Lab (Boulder)
**Best for the clock-network variant.** World leader in **entanglement-enhanced optical
clock networks**, with precision to resolve minute phase/latency effects. Entangle two
separated nodes, sweep the entanglement, and measure operational phase drift — a
completely different physical substrate testing the same law.

### Strong alternates
- **Duke / Maryland — Monroe Lab (trapped ions):** engineered long-range tunable Ising
  couplings, very clean control, and native OTOC measurement — an excellent third qubit
  platform if superconducting/neutral-atom access is constrained.
- **NIST — Ludlow Lab (distributed clock sensing / geodesy):** specialists in exactly the
  "quantum correlations redefine spatial/temporal intervals" regime — a natural second
  clock partner.

**Why this shortlist.** The measured observable is *information commute time*, whose
cleanest hardware proxies are OTOC/operator-spreading (qubits) and correlated Ramsey phase
(clocks). The lead/co-lead have the most mature versions of those readouts plus genuine
tunable coupling on **pinned** sites; Jun Ye provides an independent-substrate confirmation.

---

## 5 · Draft contact paragraph (Layer-1, native language)

> *"We propose measuring the effective information-theoretic distance (via OTOC decay /
> operator-spreading time, or correlated Ramsey phase) between two spatially fixed
> qubits/clock nodes as a function of their tunable coupling J. Our pre-registered
> computational model predicts a strict power-law contraction d ∝ J^(−1/2); we have locked
> the null hypothesis (flat slope) and the pass/fail thresholds under a public SHA-256, and
> we perform the analysis blind. We are seeking a hardware partner to execute one coupling
> sweep on a pinned pair. Either result is publishable, and the hardware group leads the
> experimental paper."*

**Honest scope.** This is a proposed physical experiment; the computational layer is
Layer-1 validated and reproducible, and no physical result is claimed until a lab runs it.
Contact via the origin repository: <https://github.com/evmotorcycles/ihcei-ecosystem>.
