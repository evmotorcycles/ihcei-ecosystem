# ihcei-ecosystem
The IHCEI Ecosystem is a Sovereign Operating System replacing standard AI with Centric and Ethical Intelligence. Built on the ADGE and TQG-CFE frameworks, it optimizes for Network Cognitive Development (C_{dev}) rather than profit. It features the Neural Ethical Reasoning Engine (NERE) to audit all decisions against the 10 Elements of Deen.

---

## For researchers & engineers — two concrete, reproducible tracks

Everything here runs **offline, `$0`, one command**, and is pre-registered under public
SHA-256 hashes with a verifiable provenance root. No hype: where a result is an algebraic
identity we say so, and the open questions are stated as open.

### 🛰️ Physics track — Latency-Metric Duality (LMD)
A pre-registered test of whether operational **distance emerges from information latency**:
`d(i,j)² = κ · τ_rt`. On a graph this is exact (effective resistance ⇒ slope **−0.5000**,
R² 1.0, 0/8640 metric violations — *analytically expected, not a discovery*). **The open,
falsifiable question is physical:** on a tunable-coupling qubit array, does measured
operator-scrambling latency contract as `d ∝ J^(−1/2)`, or stay flat (`∂d/∂J = 0`)?

```bash
python3 physics-agency/lmd/run_lmd.py                 # the -0.5 law + discriminator
python3 hardware_interfaces/mock_willow_sweep.py       # map your coupler flux here
```
Hardware teams: `hardware_interfaces/mock_willow_sweep.py` is the coupler-sweep template —
the prediction is real; `measure_scrambling_latency()` is the hook you fill in (it refuses
to fabricate). Protocol + objections: [`physics-agency/lmd/`](physics-agency/lmd/).

### 🧭 Systems track — a circuit breaker for agent swarms
Sequential multi-agent pipelines lose fidelity multiplicatively (`E = U · ∏Dᵢ`); at silicon
speed they keep running past the point of usefulness — a **zombie network**. Drop-in tool:

```python
from circuit_breaker import LISM_CircuitBreaker      # lism-cohorts/circuit_breaker.py
cb = LISM_CircuitBreaker(d_min=0.10, tau_v=0)         # halt when joint fidelity < floor
for d_i in per_hop_fidelities:
    if cb.step(d_i)["tripped"]:
        break                                         # stop calling the next agent
```
Validated against real 39-hop telemetry (`lism-cohorts/appendix/cohort_D_decay.csv`,
fidelity 0.84 → 0.01). Standard library only.

---

## Reproduce every test — one command

```bash
bash reproduce_all.sh          # 33/33 suites; then: python3 provenance/verify_provenance.py
```

No keys, no network (needs `python3`+`pytest` and `node`≥18). Runs **all 33 test suites**
across NERE/IHCEI, HELM, Page Code, Echo, Agency Internet, the Novora suite/PAGES, EI/EI-LLM,
the **Hinton** and **Russell** tests, the LISM cohorts + circuit breaker, and the telemetry /
physics experiments. See **[REPRODUCE.md](REPRODUCE.md)** for the full map. Provenance:
`PROVENANCE.md` (Merkle root `ebe46989…`). CI runs it on every push
(`.github/workflows/reproduce.yml`).

---

## Audit Gap Closures & Data Integrity

To ensure maximum transparency and allow researchers to run the LISM pipeline completely offline without access to private raw fetches, we have implemented the following resolutions to audit gaps:

- **K1 Falsification:** The central pre-registered thesis (K1)—that fidelity out-predicts popularity in knowledge propagation—was **falsified** on real data. Status predicts reach better because reach metrics (forks/downloads) are popularity measures. Thus, reach and verified quality are decoupled orderings.
- **Knowledge 793 & Digital Swarms:** The Stack Exchange N=793 cohort and the Digital Swarm are explicitly **simulations/synthetic** used to verify pipeline mathematics, carrying no real-world empirical weight. The Knowledge 793 claim has been retracted as a real-world cohort.
- **Yeast 4825 & GitHub 992 Gaps:** Because the original raw essentiality labels and the 992 labelled repository rows were not committed, we have provided **synthetic placeholders** (`repro/data/yeast_essential_ORFs_SYNTHETIC.csv` and `lism-cohorts/data/github_992_synthetic.csv`). These allow the CI pipeline (VIF gates, curvature tests) to be verified deterministically.

For a comprehensive explanation, please read the [LISM Audit Artifact](LISM_Audit_Artifact.md).
