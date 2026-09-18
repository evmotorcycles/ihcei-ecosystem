# Table 1 — Claim-status, for "The Future of AI as a Graph"

**GATE: this table awaits human review. No prose has been written.**

Status vocabulary: `measured` (produced in-repo by a tested engine),
`identity` (true by construction; carries no empirical content),
`external-claimed` (asserted by a source outside this repository, unverified
here), `simulated` (produced in-repo by a seeded generator, not observed),
`retired` (an earlier claim withdrawn, with the evidence that withdrew it),
`open` (recorded, not established).

Every row is sourced. Where a row contradicts the commissioning prompt, the
contradiction is the row's point.

---

## A. Three prompt premises that did not survive — ALL NOW RESOLVED BY RULING

| # | Prompt premise | What the repo said | Disposition |
|---|---|---|---|
| **A1** | *"cite the incident from **first-party disclosures only**"* | `DOOR2_STATUS.md`: both first-party domains **egress-blocked, never read**. Verdict rests on secondary reporting. | **Ruling 2 applied.** Tagged `external-claimed`, primaries unread. The prompt's adjective of confirmation was struck from every repo surface (`a9ac3e6`); ledger §16 holds the retired wording and is exempt by role. Ledger §16 lists the three URLs, their out-of-repo corroboration date 2026-09-17, and states the repository has never fetched them. Per-hop payload availability **UNCONFIRMED**. |
| **A2** | *"the 39-hop decay is **external-claimed**"* | `meta_lism.py:102` — `cohort_D_swarm(seed=20260719, N=500)` over `random.Random(seed)`. **Seeded simulation.** | **Ruling 1 applied.** Provenance vocabulary gained **`simulated`**; its absence is what let the overclaim survive, since a seeded cohort had nowhere correct to sit. |
| **A3** | — | Root `README.md:38`: *"Validated against **real** 39-hop telemetry."* | **RETIRED `a9ac3e6`.** Replaced with the seeded wording; claim family (`real`/`observed`/`production`/`live`) grepped and retired across **8 files in one commit**, including a test function name and the `REAL_REPRODUCIBLE` ledger label. Ledger §15. |
| **A4** | — | **`text-channel/PREREG.md` — a LOCKED prereg — already said it**: *"Cohort D is the sharpest case. It is a seeded simulation that reproduces itself… Presenting its 39-hop fidelity decay as evidence about real agent swarms would repeat exactly the error that the N=793 retraction was issued for."* | **The finding.** The correct analysis was locked, hashed and shipped while the front door claimed the opposite. **A prohibition in a locked file does not propagate to surfaces that never read it** — the same shape as §13. Ledger §15. |

## B. Layer-1 measured results

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| B1 | Declared padding clears every cut vertex | cuts **3 → 0** | `stack/audit/RESULTS.md`, 9-node fixture; commit `ae20cd4` | measured |
| B2 | Maximum load **falls** under the same padding (A8 registered the opposite) | **0.5714 → 0.3088** | same | measured — **registered miss** |
| B3 | Deepest dependence rises under the same padding | **0.133333 → 0.257161** | same | measured |
| B4 | Second, disjoint fixture agrees in direction | **0.111 → 0.619** | `agi-stack/`, unrelated graph | measured |
| B5 | Bare `pinv` returns a confident finite value across disconnected components | **0.790569** on two disjoint 4-rings | `stack/perception/`, `stack/audit/` | measured |
| B6 | Foster total `Σ w·R = n − k` | exact | `stack/audit/`, assert-only harness check, never returned | **identity** |
| B7 | Row-normalised `K_n`: all off-diagonal `R ≡ 1` | max dev < 1e-14 | `stack/audit/test_audit.py` regime 1 | **identity** |
| B8 | Symmetrisation is not free on an already-symmetric input | supplied 3.358 / 6.558 / 12.958 / 25.758 match **unsymmetrised**; pinned halves them | ledger §6c | measured |

## C. The scale identity and the growth regime

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| C1 | `pinv(cL) = pinv(L)/c`, so `d → d·c^(−1/2)`; the −0.5 slope | exact | `smi/PREREG.md` §H0, titled **"THE −0.5 SLOPE IS AN IDENTITY, NOT A RESULT"** | **identity** |
| C2 | Verdict flips on three knobs: dtype, pinv library, Laplacian assembly | S2/S3/S4 | `lmd-scaling/RESULTS.md` | measured — **registered miss** |
| C3 | Pinned-locality growth reaches 3.112× **inside** the registered range | 3.112 | `stack/perception/RESULTS.md`, range 16 → 128 | measured |
| C4 | …and **reverses** one doubling past the horizon | reversal | same; produced the CLAUDE.md horizon rule | measured — **the horizon probe** |

## D. LINTEL — names versus counts

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| D1 | Count inflatable by behaviour-preserving rewrites | **27 → 39 → 46**, ≈**1.7×** | `lintel/RESULTS.md` | measured |
| D2 | All original names survive every rewrite | **27/27** | `lintel/`, `stack/structure/` | measured, group = rewrites |
| D3 | Names survive completion of omissions far less | **18/27** | `invisible-edges/RESULTS.md` | measured, group = omissions |
| D4 | The subject grew, and the figures moved with no certificate changing | modules **156 → 169**; cuts **27 → 31**; stable **18 → 23** | `stack/structure/RESULTS.md`; commit `5ac72a2` | measured — motivates `subject_hash` |
| D5 | Candidate edges are not real edges | **31 of 92** sat only in comments/docstrings | `invisible-edges/RESULTS.md` | measured |
| D6 | The quotient pass | **Q3 missed**; quotient does **not** ship | `invisible-edges/RESULTS.md` | measured — **negative result** |
| D7 | Counts are emitted marked untrusted and never compared | contract | `stack/structure/lintel.py` | design |

## E. Swarm / LISM

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| E1 | `E = U · ∏D_k` is a **fidelity product**; the physics vocabulary ledger §3 names is absent from the module and grepped for | law | ledger §3 | design constraint |
| E2 | Ratio floor is blind to `U`; absolute floor is not | depth **5** vs **5**; **5** vs **71** at `U=1000` | `stack/swarm/RESULTS.md`; commit `d16eac3` | measured |
| E3 | Subdivision padding lowers best-route fidelity | 0.59049 → **0.531441** | same | measured |
| E4 | **Bypass padding defeats the best-route sentry** | 0.59049 → **0.729**, clearing a 0.6 floor | same | measured — **recorded as a defeat** |
| E5 | Three of five sensors fall to declared padding | cuts, max load, best-route fidelity | ledger §3 | measured |
| E6 | OR-gate earned: star trips structure only; 12-ring trips fidelity only | 0.81 vs 0.531441; cuts 1 vs 0 | same | measured |
| E7 | `R_eff` inside/across is the only formation sensor that moves | **1.0406 → 0.1523** | `DOOR2_STATUS.md`, **synthetic** 40-agent ring + 12-agent clique | measured **on a synthetic fixture** |
| E8 | 2026 incident scale | ~1,200 agents, >70,000 messages, ~700 participating | `DOOR2_STATUS.md`, now reading *"externally-reported… (primary sources unread)"* | **external-claimed**, primaries unread; no motive attribution |
| E9 | Corpus availability | analysed by third-party evaluators under access; **no public release found** | `DOOR2_STATUS.md` | external-claimed |
| E10 | 39-hop decay 0.84 → 0.01, r = −0.887 | N=500 | `lism-cohorts/`, `seed=20260719` | **`simulated`** — retired from every "real" surface, `a9ac3e6` |

## F. Organization cohort — exact permutation nulls

Recomputed during this inventory, not copied from a write-up.

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| F1 | Exact enumeration, not a sampled subset | **74,613** = C(22,6) | `stack/organization/test_organization.py` | measured |
| F2 | Clean score separates, thinly | **p = 0.044777** | recomputed 2026-09-18 | measured |
| F3 | Leaky score separates more | **p = 0.025679** | recomputed 2026-09-18 | measured |
| F4 | P14-a predicted leaky `p < 0.01` | **missed** — 0.025679 | test named `test_the_first_prediction_that_missed` | measured — **registered miss** |
| F5 | Cohort provenance | hash `020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`, n=22, k=6 | ledger §2 | measured |
| F6 | p-values uncorrected for multiplicity; cohort-relative bounds | caveat | ledger §2 | **declared limitation** |
| F7 | `leaky_dissonance()` is called by nothing shipped | design | ledger §6 | design |

## G. Geometric gate / JEPA

| # | Claim | Value | Source | Status |
|---|---|---|---|---|
| G1 | **No threshold is picked out by the data** | sensor walks continuously through the candidate band | `geometric-gate/RESULTS.md` | measured — **negative result** |
| G2 | G9 missed on both clauses | twice | same | measured — **registered miss** |
| G3 | Coarse sweep showed an empty band that finer sampling filled | — | same; co-produced the horizon rule | measured |
| G4 | Collapse prevention is **stop-gradient**, not EMA | symmetric arm collapses on all 5 seeds, ~12 orders of magnitude | `jepa-probe/RESULTS.md` | measured |
| G5 | Structural readouts are **blind** to the collapse they were pointed at | — | `jepa-probe/` | measured — **blindness result** |
| G6 | JEPA filter **abstains**; `energy is None` | design | `nere/jepa_filter.py` | design |

## H. Retired / retirement-candidate

| # | Claim | Evidence that retired it | Replacement | Status |
|---|---|---|---|---|
| H1 | Hard gate `D ≥ D_min` at p = 0.735 | sensor read zero on **76.6%** of records; fully-powered null | removed | **retired** — `FLOOR_RETIREMENT.md` |
| H2 | Identity check shipped labelled as a tautology | a reader skimming a green suite counts it | deleted; wrapper decision recorded | **retired** — ledger §4c |
| H3 | Frozen band `0.5 < stable/raw < 0.95` | a ratio band is a frozen count in disguise | relationship assertions | **retired** — ledger §4b |
| H4 | `each_settles == 1/484`; hub `echo/echo.mjs` | repo grew; hub moved to `spar/spar.py`, 1/676 | denominator derived at runtime | **retired** — ledger §13b, commit `f50ab22` |
| H5 | `"Validated against real 39-hop telemetry"` | Cohort D is `seed=20260719` simulation; a locked prereg already said so | seeded wording, 8 surfaces, ledger §15 | **RETIRED 2026-09-18** — `a9ac3e6` |
| H6 | Physics claims about latent space | `smi/test_smi.py` forbids printing five named emergence phrases (listed verbatim in that test, not reproduced here) | scope held to software | **guarded by test** |

## I. Lineage — labelled lineage, never evidence

| # | Link | Status |
|---|---|---|
| I1 | SNE/t-SNE → perception metric | **lineage**, not evidence |
| I2 | Capsules → geometric gate | **lineage** |
| I3 | Autoencoders / contrastive → JEPA | **lineage** |
| I4 | Immortal computation → LISM | **lineage** |
| I5 | "Karpathy Graph" as a named object | **framing supplied by the commissioning prompt**; no in-repo measurement defines it |

## J. Open

| # | Item | Status |
|---|---|---|
| J1 | Door 1 shut on **container egress**, not inspection: no ML runtime; `huggingface.co`/`cdn-lfs`/`hf.co` → 000; `pypi.org` → 200 | open — `DOOR1_STATUS.md` |
| J2 | Door 2 shut on egress; P24–P26 unwritten; text unlocked in `phase5/runner_spec.md` | open |
| J3 | Human check: per-hop payloads; weight-host block policy vs outage | **OPEN**, ledger §8 |
| J4 | §11 churn, §12 detector-self-read | **closed** — `95d3dc0`, `d05ca19` |
| J5 | §13 orphans 45 → 0; pipeline 100 → **123 suites**, ALL GREEN, tree clean | **closed** — `70a3fc5` |
| J6 | §14 cross-suite ordering dependency in `cohort-audit` | **open** |
| J7 | Lexical/omission detector **recall** is unmeasurable; precision only | open by construction |

---

## Status after rulings — resubmitted for re-approval

| ruling | disposition |
|---|---|
| 1 — H5 retirement | **applied** `a9ac3e6`: 8 surfaces, vocabulary amendment, ledger §15 |
| 2 — incident provenance | **applied** `a9ac3e6`: the prompt's unsupported adjective struck from every surface — ledger §16 holds the retired wording and is exempt by role — plus URLs and corroboration date recorded as never-fetched |
| — | `simulated` added to the provenance vocabulary; `cohort_*` output carries it; the 22-repo fixture stays `measured` |

**Remaining for your call, unchanged:** I5 — whether "the Karpathy Graph"
appears as commissioning framing or is dropped, since nothing in-repo measures
it; and whether §J belongs in the body or an appendix.
