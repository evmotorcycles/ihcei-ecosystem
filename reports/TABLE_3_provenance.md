# Table 3 — Provenance, for the CS / Information-Theory thesis

**GATE: this table awaits human review. No chapters have been written.**

Provenance vocabulary: `repo-measured` (produced in-repo by a tested engine,
commit given), `identity` (true by construction), `simulated` (produced in-repo
by a **seeded generator** — not observed), `external-claimed` (asserted outside
this repository, unverified here), `design` (a contract, not a number).

**Rule enforced here:** conflating these is a thesis-level defect. Two rows
below correct the provenance the commissioning prompt assigned.

---

## A. Provenance corrections — ALL RESOLVED BY RULING

| # | Prompt said | Correct provenance | Disposition |
|---|---|---|---|
| **A1** | *"the 39-hop decay is **external-claimed**"* | **`simulated`** — `meta_lism.py:102`, `cohort_D_swarm(seed=20260719, N=500)` | **Ruling 1.** `simulated` added to the vocabulary. Its **absence** is what let the overclaim survive: with only `measured` and `external-claimed` available, a seeded cohort drifted to the nearest label. |
| **A2** | — | Root `README.md:38` claimed *"real 39-hop telemetry"* | **RETIRED `a9ac3e6`** across 8 surfaces, including a test function name and the `REAL_REPRODUCIBLE` → `SIMULATED_REPRODUCIBLE` ledger label. |
| **A3** | the prompt applied an adjective of confirmation to the July 2026 incident (retired wording quoted in ledger §16) | **`external-claimed`, primaries unread** | **Ruling 2.** The adjective was struck (retired wording in ledger §16). `DOOR2_STATUS.md` now reads *"externally-reported facts … (primary sources unread)"*. Ledger §16 records the three URLs, corroborated out-of-repo 2026-09-17, **never fetched by this repository**; per-hop payload availability **UNCONFIRMED**. |
| **A4** | — | Confirmed `repo-measured`: `p_clean = 0.044777`, `p_leaky = 0.025679`, 74,613 enumerations | Recomputed 2026-09-18, not copied. The prompt's pairing was correct. |
| **A5** | — | **A locked prereg already carried the correct analysis.** `text-channel/PREREG.md` named Cohort D *"the sharpest case… a seeded simulation that reproduces itself"* and warned that presenting it as evidence about real swarms *"would repeat exactly the error that the N=793 retraction was issued for."* | **The structural finding for Chapter 6.** Correct analysis, locked and hashed, while the front door said the opposite. **A prohibition in a locked file does not propagate to surfaces that never read it.** |

## B. LISM — channel accounting

| # | Quantity | Value | Provenance | Notes |
|---|---|---|---|---|
| B1 | `E = U · ∏D_k` | law | **design** | Fidelity product. Ledger §3 forbids physics vocabulary in the module; a test greps for it. |
| B2 | Ratio floor blind to `U` | depth 5 at `U=1` and `U=1000` | repo-measured `d16eac3` | |
| B3 | Absolute floor **not** blind to `U` | depth **5 → 71** | repo-measured `d16eac3` | The whole argument for the ratio form |
| B4 | `min_ratio` required, no default | contract | design | Ships only as a fraction of `U` |
| B5 | `absolute_floor_trip_depth` exists so the defect is measurable; nothing calls it | contract | design | Same arrangement as `leaky_dissonance()` |
| B6 | Subdivision padding | 0.59049 → **0.531441** | repo-measured `d16eac3` | moves against the attacker |
| B7 | **Bypass padding defeats `ratio_best`** | 0.59049 → **0.729** past a 0.6 floor | repo-measured `d16eac3` | recorded as a **defeat** |
| B8 | `ratio_worst` survives bypass | 0.59049, trips | repo-measured | why both are returned, never fused |
| B9 | 39-hop decay 0.84 → 0.01, r = −0.887, N=500 | seed 20260719 | **`simulated`** | must not be described as telemetry; retired `a9ac3e6` |
| B10 | Aggregate resistance is **not** a fidelity proxy | claim | design | redundancy masks serial decay |

## C. LMD telemetry on declared graphs

| # | Quantity | Value | Provenance | Notes |
|---|---|---|---|---|
| C1 | cuts under padding | **3 → 0** | repo-measured `ae20cd4` | A7 hit |
| C2 | max load under padding | **0.5714 → 0.3088** | repo-measured `ae20cd4` | **A8 registered miss** — predicted a rise |
| C3 | deepest dependence under padding | **0.133333 → 0.257161** | repo-measured `ae20cd4` | the surviving sensor |
| C4 | second disjoint fixture | **0.111 → 0.619** | repo-measured, `agi-stack/` | agrees in direction |
| C5 | three of five sensors defeated | cuts, load, best-route fidelity | repo-measured | ledger §3 |
| C6 | `pinv` across components | **0.790569** | repo-measured | the value the guard refuses |
| C7 | Foster `= n − k` | exact | **identity** | assert-only; raises, never returned |
| C8 | `tol_ratio = 1e-10` | declared preference | design | replaces an inherited numpy default that flipped a verdict |
| C9 | Certificate contract `(readout, invariance_group, subject_hash, date)` | schema `cert/2` | design | `d16eac3` |
| C10 | Audit reading carries `GROUP_NONE` | — | design | it has survived no transformation family |

## D. LINTEL metrology

| # | Quantity | Value | Provenance |
|---|---|---|---|
| D1 | names stable under rewrites | **27/27** | repo-measured |
| D2 | names stable under omissions | **18/27** | repo-measured |
| D3 | count inflation | **27 → 39 → 46**, ≈1.7× | repo-measured |
| D4 | subject growth moved every figure | 156→169 modules; 27→31 cuts; 18→23 stable | repo-measured `5ac72a2` |
| D5 | candidates that were mentions, not dependencies | **31 of 92** | repo-measured |
| D6 | quotient pass | **Q3 missed; does not ship** | repo-measured — negative result |
| D7 | counts emitted marked untrusted | contract | design |

## E. Swarm governance case study

| # | Quantity | Value | Provenance |
|---|---|---|---|
| E1 | `R_eff` inside/across | **1.0406 → 0.1523** | repo-measured, **synthetic** 40-agent ring + 12-agent clique |
| E2 | cuts on that fixture | **0 → 0** (blind) | repo-measured |
| E3 | max load on that fixture | 0.3333 → 0.2566 (**falls**) | repo-measured |
| E4 | incident scale ~1,200 agents / >70,000 messages / ~700 participating | — | **external-claimed**, primaries unread (A3) |
| E5 | corpus analysed under access, no public release found | — | external-claimed |
| **E6** | Kill-switch failure as node deletion | theorem about a stated model | **`derived`** | A theorem whose **premise is untested**: that a post-coordination swarm communication graph has no articulation points. That premise is tagged **`open`** and has never been measured here. A theorem about an untested premise is analysis, and this row says so. |
| **E7** | `R_eff = ∞` across components | — | **`identity`** — **struck from the findings list** | The guarded metric assigns `inf` across components **by construction**. Any claim that monitors "became infinitely far" **restates the guard rather than reporting evidence**. Chapter 5 frames air-gapping not as a defeated swarm tactic but as **the only mathematically valid topological state that guarantees isolation**. |
| E8 | Unsanctioned channels are undeclared **by definition** | boundary | design — the declared-graph limit |
| E9 | Subgroup finding on an undeclared graph is community detection, not telemetry | boundary | design |

## F. Pipeline epistemology — repo-measured

| # | Quantity | Value | Provenance |
|---|---|---|---|
| F1 | pre-registrations hashed before running | 34 prereg files inventoried | repo-measured 2026-09-18 |
| F2 | registered misses kept by name | S2/S3/S4, A8, G9, Q3, N3/N5, P14-a | repo-measured |
| F3 | pipeline coverage | **100 → 123 suites; orphans 45 → 0** | repo-measured `f50ab22`, `70a3fc5` |
| F4 | orphans run before wiring | Python **520 passed / 1 skipped / 0 failed** | repo-measured |
| F5 | frozen count and air gap were **one** defect | `1/484` → `1/676`; hub `echo/echo.mjs` → `spar/spar.py` | repo-measured `f50ab22` |
| F6 | denominator now derived; growth-probed | `claimed` 26 → 27, `each_settles` → 1/729, test held | repo-measured |
| F7 | clean-tree-after-run restored as a signal | 123/123 + clean tree | repo-measured `70a3fc5` |
| F8 | churn boundary set empirically | all 69 deleted → **93/100**; 9 deleted → **99/100**; untracked **9** | repo-measured `d05ca19`, `70a3fc5` |
| F9 | detector read its own output | phantom finding citing `results_os.json` | repo-measured `cff4c10`, `95d3dc0` |
| F10 | lexical self-match count | **17** occurrences | repo-measured, ledger §9 |

## G. Open problems

| # | Item | Status |
|---|---|---|
| G1 | Door 1: no ML runtime; weight hosts → 000; `pypi.org` → 200 | open — egress, not inspection |
| G2 | Door 2: P24–P26 unwritten; text unlocked in `phase5/runner_spec.md` | open |
| G3 | Human check on primaries and on block-vs-outage | **OPEN**, ledger §8 |
| G4 | **Recall** of omission and lexical detectors is unmeasurable; precision only | open by construction |
| G5 | §14 cross-suite ordering dependency | open |
| G6 | Certificates require subject hash and date; legacy marked, never back-dated | closed, ledger §4b |

## H. Threats to validity — mandatory chapter

| # | Threat |
|---|---|
| H1 | Every swarm number is **synthetic**; E1–E3 describe a graph this project drew |
| H2 | Cohort n=22, p uncorrected for multiplicity, bounds cohort-relative |
| H3 | Single-fixture results (C1–C3) rest on one 9-node hand-built graph; only C4 is independent |
| H4 | Declared-graph boundary makes the adversary's channel invisible by construction |
| H5 | `simulated` rows (B9) must never be read as deployment evidence |
| H6 | The incident rows are secondary reporting with primaries unread |

---

## Status after rulings — resubmitted for re-approval

| ruling | disposition |
|---|---|
| 1 | **applied** — `simulated` in the vocabulary; `cohort_*` output carries it; 22-repo fixture stays `measured`; retirement `a9ac3e6` |
| 2 | **applied** — the adjective struck from every surface; ledger §16 records the retired wording, the URLs, the corroboration date, the never-fetched status, and that payload availability is unconfirmed |
| 4 | **applied** — E6 re-tagged `derived` with its premise tagged `open`; E7 re-tagged `identity` and **struck from findings** |

**Chapter 5 must state, in the register the ledger uses:** it analyses
**secondary topological reporting, not primary logs**. That sentence is not a
caveat at the end; it is the chapter's scope line.

**Remaining for your call:** whether Chapter 5 may cite E1–E3 at all given H1 —
every one of those numbers describes a graph this project drew.
