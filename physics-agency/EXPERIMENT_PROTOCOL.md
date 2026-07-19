# Physical experiment protocol — a bench test of Latency–Metric Duality

**Objective.** Decide, on real hardware, whether the *operational distance* between
two spatially-fixed quantum sites depends on the information coupling between them.
LMD predicts a fixed pair contracts as `d ∝ 1/√coupling`; a fundamental container
predicts no response (`∂d/∂coupling = 0`). This is a Layer-3 test of the Telemetric
Metric `d² = κ·τ_rt`; the equation and its discriminating logic are pre-registered
and Layer-1 validated in this repository.

> This is a **design blueprint** for a group with the apparatus. It is not a claim
> that the measurement has been performed.

---

## 1. Choice of platform

| Platform | Coupling knob | Round-trip observable | Notes |
|---|---|---|---|
| **Superconducting transmons** (e.g. tunable couplers) | flux-tunable coupler `g(Φ)` between two fixed qubits, mediated by a bus resonator or chain | commute time of an injected excitation; or correlation-front arrival time | fastest turnaround; `g` tunable over ~10–100 MHz; fixed lithographic positions |
| **Trapped ions** | Mølmer–Sørensen / phonon-mediated coupling strength via laser detuning & power | spin-excitation transport time across the chain | long coherence; positions fixed by the trap; coupling range tunable |
| **Entangled optical-clock network** | shared-mode / cavity-mediated entanglement between two clocks | synchronization round-trip / mutual-information distance | ties directly to Einstein's clock-sync telemetry origin of `E=mc²` |

Recommended first realization: **two fixed transmons coupled through a short chain of
buffer qubits with a flux-tunable coupler**, because the coupling can be swept
in-situ over a wide range while the qubit positions are lithographically fixed.

## 2. The three registers (map the theory onto the device)

- **Fixed sites A, B.** Two named qubits at fixed physical positions. They never
  move; only the coupling changes. (The pre-registered numerical analogue: probe
  sites `(0,5)`.)
- **Coupling `g` (↔ network coupling / `ν`).** The tunable-coupler setpoint, swept
  over at least a decade, e.g. `g ∈ {0.5, 1, 2, 4, 8}·g₀`.
- **Operational distance `d` (↔ `√(κ·τ_rt)`).** Extracted from a round-trip
  information latency — see §4.

## 3. State preparation

1. Cool to base (≈10–20 mK for transmons); calibrate single-qubit gates, readout,
   and the coupler transfer function `g(Φ)`.
2. Verify the sites are at **fixed positions** and that only `g` changes across the
   sweep (control: image/park the qubit frequencies; confirm no frequency-crowding
   artifacts masquerade as "motion").
3. For each `g` setpoint, prepare the standard probe: inject a localized excitation
   (a π-pulse) on A, or prepare a Bell-like correlation between A and B of controlled
   strength.

## 4. The round-trip / commute-time observable

Two interchangeable, pre-specified estimators of `τ_rt(A,B)`:

**(a) Excitation commute time.** Inject an excitation at A; measure the population
transfer to B and back. Fit the round-trip return time `τ_rt` from the first
recurrence of A-population (or the two-point correlator's round-trip). Convert to
distance via `d = √(κ·τ_rt)`, with `κ` fixed once by calibration at `g₀`.

**(b) Correlation-front (Lieb–Robinson) time.** Measure the out-of-time-order
correlator or the connected two-point function `⟨A(t)B⟩`; define the arrival time of
the information front as `τ_rt`. This is the operational "ping" time.

Both estimators must be **pre-registered and fixed before data taking**, along with
the fit windows and the exclusion criteria.

## 5. Controls (essential — these defeat the obvious confounds)

- **C1 Position invariance.** Independently confirm the qubit physical positions and
  frequencies are unchanged across the `g` sweep, so any `d(g)` response cannot be a
  literal spatial displacement.
- **C2 Decoupled null.** Repeat the full sweep with the coupler nominally off / a
  spectator pair; the operational distance must be flat (the fundamental-container
  behavior), validating that the estimator is not trivially `g`-dependent.
- **C3 Calibration lock.** `κ` is fixed once at `g₀` and never re-fit per point;
  otherwise the scaling test is circular.
- **C4 Blind analysis.** The fit pipeline and the pass thresholds are frozen (SHA-256
  lock, mirroring `prereg/`) before unblinding the `d(g)` curve.

## 6. Pre-registered decision rule (mirrors the numerical prereg)

Fit `log d` vs `log g` over the sweep.

| Outcome | Interpretation |
|---|---|
| slope `≈ −0.5` (within CI), `d` monotonically contracting, C2 null flat | **consistent with LMD** — emergent, latency-rendered geometry |
| slope `≈ 0`, `d(g)` flat within error | **consistent with a fundamental container** — LMD disfavored |
| slope significantly `≠ 0` and `≠ −0.5` | new scaling — report the measured exponent; neither hypothesis in its stated form |

**Symmetric null:** publish whatever the fixed pipeline returns, including a flat/null
result, with no post-hoc re-tuning. A flat C1-verified `d(g)` **falsifies** LMD on
this construction.

## 7. Error budget (to be filled per apparatus)

- coherence-limited timing resolution on `τ_rt` (T₂, gate errors);
- coupler transfer-function nonlinearity `g(Φ)` (calibrate & propagate);
- readout/SPAM errors on the population/correlator estimators;
- finite-chain / boundary effects on commute time (model with the same graph math);
- statistical: shots per `(g, t)` point sufficient for a target CI on the slope
  (power-analyze for `|slope+0.5| < 0.1` discrimination at chosen confidence).

## 8. Deliverables

Raw correlators, the fitted `τ_rt(g)`, the `log d`–`log g` slope with CI, the C1–C4
control results, and a provenance bundle (frozen pipeline hash + analysis receipts)
in the same tamper-evident form as `prereg/provenance.json`. The measured slope and
the C2 null together are the verdict.

---

*Companion documents: the equation and theory (`PAPER_telemetric_metric.md`), the
pre-registered numerical validation (`prereg/`, `REGISTERED_REPORT.md`), and the
firewall — Layer 1 is proven; this Layer-3 test is proposed, not performed.*
