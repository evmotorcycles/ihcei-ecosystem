# Table 2 — Postulate / consequence / falsifier, for the Physics thesis

**GATE: this table awaits human review. No chapters have been written.**

Subject: `d(i,j)² = κ · τ_rt(i,j)` — coordinate distance as an emergent
projection of information latency.

Label vocabulary: `identity` (true by construction), `derived` (follows from an
identity plus a stated modelling choice), `postulate` (an empirical claim this
repository has **not** tested).

---

## A. The epistemic situation, stated before anything else

| # | Fact | Consequence for the thesis |
|---|---|---|
| **A1** | **Nothing in this repository measures κ in a physical medium.** `physics-agency/prereg/run.py` takes `kappa` as a *simulation parameter* read from a prereg JSON. | κ is an **unmeasured free parameter**. No chapter may present any in-repo number as a value of κ. |
| **A2** | `smi/test_smi.py::test_nothing_printed_claims_a_result_about_the_physical_world` **forbids** the strings `"Space is Emergent"`, `"spacetime"`, `"the nature of space"`, `"physical distance"`, `"dead matter"` in shipped output. | The repository contains an **active guard against** this thesis's claim. That is the thesis's honest starting position, and the guard is a feature to cite, not an obstacle to route around. |
| **A3** | Every Layer-1 result is an identity or a measurement **on a declared graph**. | The repository is the thesis's **substrate**, never its evidence. |

## B. Identities — the substrate

| # | Statement | Label | Repo status |
|---|---|---|---|
| B1 | `L⁺ = pinv(L)`; `R_ij = L⁺_ii + L⁺_jj − 2L⁺_ij`; `d_ij = √R_ij` | identity | definitional |
| B2 | `pinv(cL) = pinv(L)/c`, hence `d → d·c^(−1/2)`; **the −0.5 slope** | **identity** | `smi/PREREG.md` §H0: *"IDENTITY, NOT A RESULT"* |
| B3 | Foster: `Σ w_ij R_ij = n − k` | **identity** | assert-only harness check; never returned |
| B4 | Row-normalised `K_n` ⇒ all off-diagonal `R ≡ 1` | identity | max dev < 1e-14 |
| B5 | Commute time `= 2m·R_ij` on an undirected reversible walk | identity | standard; requires B6 |
| B6 | `C = A + Aᵀ` — symmetrisation | **declared modelling choice, not an identity** | ledger §1, §6c. On an already-symmetric input it **doubles** conductance and halves every resistance. |
| B7 | Ratio API is invariant to uniform scale — which is exactly why it is **blind** to it | derived from B2 | the property that makes bearings ungameable makes them blind |

## C. The postulate and its consequences

| # | Statement | Label | Consequence if true | Falsifier |
|---|---|---|---|---|
| **C1** | `d² = κ·τ_rt` | **postulate** | Latency is not a proxy for distance; it *is* distance up to κ | A medium where τ_rt varies at fixed geometry and `d` does not track it, or the converse |
| **C2** | κ is a constant of the medium, not of the graph | **postulate** | κ measurable once per medium, transferable across topologies | Fitting κ per-topology in one medium and finding it varies beyond stated error |
| **C3** | Prediction in latent space = trajectory of least resistance | **postulate** | JEPA's objective is a physical minimisation | A JEPA whose latent trajectories are measurably *not* minimal-resistance paths while training succeeds |
| **C4** | Metric collapse under parallel background conductance: as noise ↑, τ_rt → 0 and emergent distance shrinks | **postulate, partially substrate-supported** | In large contexts tokens *drown in proximity*, they do not stretch apart | A regime where added parallel conductance **increases** resistance. **Note:** B7 says the ratio API cannot see uniform scale, so this must be measured on *ratios between pairs*, not absolutes |
| **C5** | Scale-dependence distinguishes Layer-3 from Layer-1 | **derived** | Foster (B3) is scale-invariant accounting; `d` is not | If a scale-invariant quantity tracked latency, C1 would lose its discriminating power |

## D. Falsification programme — the examinable core

| # | Experiment | Medium | Independent variable | Refutes | Null admissible? |
|---|---|---|---|---|---|
| D1 | Vary propagation latency at **fixed physical geometry** | sensor network with programmable delay | τ_rt at constant layout | C1 if `d` fails to track | **yes, pre-specified** |
| D2 | Vary geometry at **fixed latency** | same, delay-compensated | layout at constant τ_rt | C1 if `d` tracks geometry anyway | yes |
| D3 | Measure κ in two topologies, one medium | coupled oscillator array | topology | C2 if κ differs beyond error | yes |
| D4 | Inject parallel background conductance, read **pair ratios** | any of the above | noise floor | C4 if ratios do not compress | yes |
| D5 | Trajectory audit against least-resistance paths | trained JEPA | — | C3 | yes |
| D6 | **Horizon probe** — one measurement past every registered range, reported whichever way it falls | all | — | any trend claim | **mandatory** |

D6 is not optional. `geometric-gate/` found an empty band that finer sampling
filled, and `stack/perception/` hit 3.112× inside its range and **reversed** one
doubling past it. Both would have shipped a confident wrong number.

## E. Effect sizes and horizons — to be registered *before* any run

| # | Item | Status |
|---|---|---|
| E1 | κ estimate + CI, per medium | **unregistered** — needs your numbers |
| E2 | Minimum detectable effect for D1/D2 | **unregistered** |
| E3 | Registered range for every trend, plus its mandatory past-horizon probe | **unregistered** |
| E4 | Symmetrisation choice declared per experiment (B6) | required |
| E5 | Pre-registration hashed before any measurement | required by CLAUDE.md |

## F. Related work — recorded as retractions, not as support

| # | Item | Status |
|---|---|---|
| F1 | Holographic / emergent-gravity analogies | **motivation only**; no in-repo bearing |
| F2 | This repository's own physics claims | **guarded against** by A2 — cite the guard, not a retraction, because the claim was blocked rather than published |
| F3 | Emergent-spacetime comparison suite | exists and is labelled *"honest"* in the pipeline; **its content must be read before Chapter 5 is written** — not yet inventoried |

## G. Limitations to carry into every chapter

| # | Limitation | Source |
|---|---|---|
| G1 | Growth regimes are **model-dependent**; the verdict flipped on dtype, pinv library and assembly | `lmd-scaling/` S2/S3/S4 |
| G2 | Perception distances are **best-conductance-path** quantities, not geodesics | `stack/perception/` |
| G3 | The **declared-graph boundary**: absence of an edge is absence of a declaration | `stack/audit/` |
| G4 | Disconnected pairs **refuse**; bare `pinv` would answer 0.790569 into a void | measured |
| G5 | κ has never been measured in any medium by this work | A1 |

---

## Rulings needed before chapters

1. **A2** — the repository actively forbids this thesis's claim in shipped
   output. Confirm the thesis proceeds as an explicitly *untested postulate with
   a falsification programme*, citing that guard as its starting position.
2. **E1–E3** — κ estimates, effect sizes and horizons are yours to set. I will
   not invent them; without them Chapter 4 is unexaminable.
3. **F3** — may I read the emergent-spacetime comparison suite before drafting
   Chapter 5? I have not inventoried it and will not characterise it unread.
4. **C4** — confirm the collapse claim is to be tested on **pair ratios**. As
   written it is invisible to the ratio API (B7).
