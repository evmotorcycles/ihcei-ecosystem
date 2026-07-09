# From a Deterministic Floor to a Probabilistic Hazard Floor

*Why `D ≥ D_min` (a hard gate on measured two-hop fidelity) was retired in favour
of a probabilistic hazard floor built on enforcement latency (τ_v) and dissonance
(σ) — recorded with the real telemetry that forced the change.*

## The two floors

- **Deterministic floor `D ≥ D_min`.** Admit a transmission only if its *measured*
  two-hop fidelity clears a hard threshold. This requires a reliable **sensor for
  D** — the semantic `D_gap` sensor (encode-lexicon minus decode-lexicon).
- **Probabilistic hazard floor.** Do not gate on a measured D at all. Estimate a
  *hazard* of collapse from clean, timestamped signals — **τ_v** (enforcement
  latency) and **σ** (dissonance) — and act on rising hazard.

## What the telemetry showed (real data in this repo)

On the VS Code PR cohort (`dgap_vscode_results.csv`, N = 3,685):

- **The semantic sensor is blind most of the time.** `D_enc_raw = 0` for **89.8%**
  of PRs and `D_dec_raw = 0` for **83.7%**; the sensor fires on only **23.4%**.
  A hard gate on a quantity you cannot measure 3/4 of the time is not operable.
- **It collapses under lexical noise.** The pre-registered, SHA-256-locked
  confirmatory test on an unseen cohort (Kubernetes, ~4,979 PRs) returned a
  **fully-powered null, p = 0.735** — the `D_gap` signal on the discovery cohort
  (VS Code) did not survive on data dominated by dependabot/templated text.
- **The probabilistic floor is robust.** On the SRE validation, the hazard model
  on `[τ_v, σ]` reached **AUC 0.898** versus **0.828** for the deterministic
  `D_gap` floor and 0.500 for chance (`probabilistic_vs_deterministic.png`). It
  bypasses lexical sensing entirely, using clean timestamped latency.

The channel itself was intact where measurable (VIF ≈ 1.0), and the failing region
was populated (601 of 3,685 not-merged/reverted) — so the retirement is about the
**sensor's operability**, not a collapsed channel or a degenerate outcome.

## Why this is *expected*, not a defeat (and where the framework already said so)

The Governance-OS reading (Layer 3 in the framework's own discipline) makes the
retirement coherent rather than ad hoc:

- The **descriptive** law of the "wild" incubator is **linear** (`E = U·D`): nature
  degrades *gracefully* and tolerates low fidelity, so low-fidelity proxies survive
  a long time on raw utility. A hard deterministic cliff is simply not how the
  incubator behaves — which is exactly why a *deterministic* floor has nothing to
  latch onto here.
- The incubator (**Al-Hayaat-u-Dunya**) is a **testing ground**: a probabilistic
  hazard signal (is this system's backlog of unaddressed risk rising?) is the
  fitting instrument, because judgment here is provisional and latency-based, not a
  hard admissions gate.
- A **deterministic** `D ≥ D_min` gate belongs to a different regime — the
  framework's **Al-Aakhirah / Firdaus** reading (N186): a final, hard credentialing
  boundary, not a runtime filter inside the test. Transitioning to it is described
  as requiring specific fidelity, not graceful tolerance.

> Epistemic note (the framework's own layer discipline): the τ_v hazard floor and
> the linear descriptive law are **Layer 1** — measured, falsifiable, and tested
> here. The dunya-incubator / Akhirah-Firdaus reading is **Layer 3** — an
> interpretive prior that makes the engineering choice *coherent*, not a claim any
> dataset can prove or refute. Keeping those apart is what the retirement rests on.

## Engineering takeaway

If you must protect a real system, do **not** gate on a noisy semantic fidelity
sensor. Watch the **probabilistic hazard** — a rising τ_v (time to clear
self-flagged risk) and widening dissonance — which is measurable from clean
timestamps you already keep, and which achieved the higher AUC. The deterministic
fidelity floor is retained only as an *architectural* option for hard-boundary
transitions, not as a runtime filter in the wild.
