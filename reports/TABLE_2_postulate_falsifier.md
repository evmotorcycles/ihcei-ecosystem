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
| **A2** | `smi/test_smi.py::test_nothing_printed_claims_a_result_about_the_physical_world` **forbids** five named emergence phrases in shipped output, listed verbatim in that test and deliberately not reproduced here. | The repository contains an **active guard against** this thesis's claim. That is the thesis's honest starting position, and the guard is a feature to cite, not an obstacle to route around. |
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
| **C4a** | **UNIFORM** collapse: all conductances scale together | **postulate** | Every distance shrinks by the same factor | **Invisible to every ratio, pair ratios included** — uniform rescaling cancels in any quotient. Tested only by the geometric gate's **absolute** sensors: trace ratio against a declared reference, and effective rank |
| **C4b** | **DIFFERENTIAL** collapse: background conductance rises relative to structure | **postulate** | Tokens *drown in proximity*; inside/across separation compresses | Tested on **pair ratios** — `R_eff` inside a clique ÷ `R_eff` across background, mirroring the 40-agent ring's **1.0406 → 0.1523** |
| **C5** | Scale-dependence distinguishes Layer-3 from Layer-1 | **derived** | Foster (B3) is scale-invariant accounting; `d` is not | If a scale-invariant quantity tracked latency, C1 would lose its discriminating power |

## D. Falsification programme — the examinable core

| # | Experiment | Medium | Independent variable | Refutes | Null admissible? |
|---|---|---|---|---|---|
| D1 | Vary propagation latency at **fixed physical geometry** | sensor network with programmable delay | τ_rt at constant layout | C1 if `d` fails to track | **yes, pre-specified** |
| D2 | Vary geometry at **fixed latency** | same, delay-compensated | layout at constant τ_rt | C1 if `d` tracks geometry anyway | yes |
| D3 | Measure κ in two topologies, one medium | coupled oscillator array | topology | C2 if κ differs beyond error | yes |
| D4a | **Uniform** rescale of all conductances, read **absolute** sensors (trace ratio vs declared reference, effective rank) | any of the above | global scale | C4a if absolutes do not shrink | yes |
| D4b | Raise background conductance **relative to** structure, read **pair ratios** | any of the above | noise floor | C4b if inside/across does not compress | yes |
| **D0** | **Blindness control:** uniform rescale must leave **every** pair ratio unchanged | any | global scale | the instrument itself, if a pair ratio moves | **null is the expected result** |
| D5 | Trajectory audit against least-resistance paths | trained JEPA | — | C3 | yes |
| D6 | **Horizon probe** — one measurement past every registered range, reported whichever way it falls | all | — | any trend claim | **mandatory** |

**D0 — the mandatory blindness decoy (ruling 5).** Preregister it: a **uniform
rescale must leave every pair ratio unchanged**. That null result is the
**control**, not a failure — it is what shows the pair-ratio instrument cannot
see uniform collapse. Any test in Chapter 4 claiming "collapse" without naming
it **uniform** or **differential** is unexaminable and gets sent back.

D6 is not optional. `geometric-gate/` found an empty band that finer sampling
filled, and `stack/perception/` hit 3.112× inside its range and **reversed** one
doubling past it. Both would have shipped a confident wrong number.

## E. Effect sizes and horizons — declared, per ruling 3

**No estimate of κ exists in any medium. None is invented here.** Chapter 4
opens with that sentence and pivots: it does not claim κ is a known constant, it
proposes the methodology required to measure κ from live attention matrices —
which is **Door 1**, currently shut on container egress.

| # | Item | Value | Tag |
|---|---|---|---|
| **E1** | **Identifiability of κ.** κ is identifiable **only** from absolute latency and absolute distance in a physical medium. It is **not** identifiable from normalised graph readouts: ratio-API blindness (B7) cancels it exactly. | — | **analysis** |
| **E2** | **Minimum detectable effect:** 10% relative deviation of the latency–distance coupling from the postulate's prediction. Rationale: smaller effects sit below the sweep- and solver-noise this repository has demonstrated — the verdict flip across dtype, pinv library and assembly, and the empty band that finer sampling filled. | 10% rel. | **declared** |
| **E3** | **Horizon:** one decade of latency variation, with a single mandatory probe at **1.5 decades**, reported whichever way it falls. | 1 decade + 1.5× probe | **declared** |
| E4 | Symmetrisation choice declared per experiment (B6) | — | required |
| E5 | Pre-registration hashed before any measurement | — | required |

**E1 is the chapter's load-bearing claim**, and it cuts against the repository:
every reading this project ships is a ratio or a rank, and κ is precisely the
quantity ratios destroy. Door 1 is not an inconvenience for the measurement — it
is the only route to it.

## F. Related work — read, with the suite's OWN labels quoted (ruling 6)

`physics-agency/lmd/comparison/` was read before this row was written. Its four
verdicts, verbatim:

| Theory | The suite's own verdict |
|---|---|
| Holographic / AdS-CFT (RT, Van Raamsdonk) | `COMPARABLE (qualitatively)` |
| Quantum-information / emergent spacetime | `MOST ALIGNED (in spirit)` |
| Loop Quantum Gravity / spin networks | `SILENT (offers nothing on its core claims)` |
| Amplituhedron / positive geometry | `NOT COMPARABLE (different problem)` |

Its own disclaimer, verbatim, and asserted by `test_comparison.py`:

> *"LMD is a Layer-1 toy; not quantum gravity; no Google collaboration; hardware
> test only proposed."*

**The finding that matters for Chapter 5.** Both of the suite's experiments are
already in §B as identities:

| Experiment | What it reports | What it is |
|---|---|---|
| A — Van Raamsdonk analogue | sweep `J → d`: 2.0→0.7071, 1.0→1.0, 0.5→1.4142, 0.25→2.0, 0.01→10.0; `inverse_sqrt_law: True` | **`d = J^(−1/2)` exactly** — identity **B2**, relabelled as a physics analogue |
| B — metric axioms | 200 networks, 43,200 triangle checks, **0 violations** | resistance distance **is** a metric; a theorem, not a measurement |

So the suite carries **no live claim of physical emergence** — one identity, one
theorem, and four comparison verdicts of which two are `SILENT` and `NOT
COMPARABLE`. Chapter 5 cites it as **substrate and as the project's own
disclaimer**, never as support. There is no retraction to record, because the
claim was **guarded against rather than published** (A2).

## G. Limitations to carry into every chapter

| # | Limitation | Source |
|---|---|---|
| G1 | Growth regimes are **model-dependent**; the verdict flipped on dtype, pinv library and assembly | `lmd-scaling/` S2/S3/S4 |
| G2 | Perception distances are **best-conductance-path** quantities, not geodesics | `stack/perception/` |
| G3 | The **declared-graph boundary**: absence of an edge is absence of a declaration | `stack/audit/` |
| G4 | Disconnected pairs **refuse**; bare `pinv` would answer 0.790569 into a void | measured |
| G5 | κ has never been measured in any medium by this work | A1 |

---

## Status after rulings — this table is resubmitted for re-approval

| ruling | disposition |
|---|---|
| 3 — κ, effect sizes, horizons | **applied.** No κ invented. E1 identifiability, E2 10% MDE declared, E3 one-decade horizon + 1.5× probe. Chapter 4 pivots to *how to measure κ* via Door 1. |
| 5 — collapse mode | **applied.** C4 split into C4a uniform / C4b differential. Uniform is invisible to **all** ratios, not only absolutes — pair ratios included — so it is tested by absolute sensors; D0 preregisters the blindness decoy as a control. |
| 6 — comparison suite | **applied.** Read first; labels quoted; both experiments identified as identity + theorem. |

**One correction to my own earlier row.** The pre-ruling C4 said the collapse
"must be measured on ratios between pairs, not absolutes." That was wrong in the
same direction the ruling corrects: pair ratios cannot see **uniform** collapse
either, because uniform rescaling cancels in *any* quotient. Only differential
collapse is a pair-ratio quantity.
