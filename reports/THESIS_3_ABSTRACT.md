# Computational Telemetry of Digital Swarms: LMD and LISM in Multi-Agent Topologies

**Abstract and executive summary — PhD thesis outline, Computer Science /
Information Theory**

Claim rows keyed to `reports/TABLE_3_provenance.md` as `[row · provenance]`.
Full outline: `reports/THESIS_3_swarm_outline.md`.

---

## Abstract

Sequential multi-agent systems delegate work along chains of semantic handoffs.
This thesis establishes **computational telemetry** for such systems: a pair of
instruments, one accounting for what survives transmission and one auditing the
topology transmission runs over, together with an explicit account of what
neither can see.

The transmission instrument is **LISM**. Operational viability is `E = U · ∏D_k`
over hops `k`, a product of per-hop retention factors `[B1 · design]`. **This
quantity is not Shannon's uncertainty measure**: it has no units of information
and does not measure uncertainty over a distribution. Its exact and weaker
information-theoretic property is that taking logs gives
`log E = log U + Σ log D_k`, so retention is **log-additive across serially
composed channels**. The thesis uses that name throughout, because a correction
that says only what a quantity is *not* leaves the discredited term as the only
available shorthand.

The viability floor is expressed as a ratio of `U` rather than as an absolute,
and the reason is measured rather than argued: on identical hops at a floor of
0.6, the ratio form trips at depth 5 under both `U = 1` and `U = 1000`, while
the absolute form trips at depth 5 and depth **71** `[B2, B3 · repo-measured]`.
A fourteen-fold difference in how far degradation runs before anything reports,
caused by nothing but how much entered the chain.

The topological instrument is **LMD** on declared graphs. Its central result is
negative and concerns instrument choice. Under declared padding — adding edges,
no new nodes, no new evidence — cut vertices fall `3 → 0` and maximum load falls
`0.5714 → 0.3088`, both in the attacker's favour, while deepest dependence rises
`0.133333 → 0.257161` `[C1–C3 · repo-measured]`. **Three of five sensors are
defeated by the same attack** `[C5]`, and the two survivors are precisely the
two that are not shortest-path readings. On a 40-node ring with a 12-node
clique, cut vertices remain blind at `0 → 0` and maximum load *falls*, while the
**`R_eff` inside-to-across ratio collapses `1.0406 → 0.1523`** `[E1–E3 ·
repo-measured on a synthetic fixture]` — the only readout of the three in which
the formation is legible.

The thesis closes on a boundary and an axiom. LMD computes the mathematics of
the **declared** drawing, so an undeclared channel is invisible by definition
rather than by oversight `[E8, E9 · design]`; LINTEL reports **disputes, not
breaches**. And `R_eff = ∞` is **not a defensive tactic but the definition of a
disconnected graph** `[E7 · identity]`, which makes air-gapped one-way telemetry
the only topological state whose isolation is *mathematically decidable* rather
than empirically hopeful. That is a weaker claim than "air-gapping defeats
swarms", and it is the claim the mathematics supports.

## Executive summary of findings

| finding | value | provenance |
|---|---|---|
| retention is log-additive over serial hops | `log E = log U + Σ log D_k` | `[B1 · design]` |
| ratio floor is blind to `U`; absolute floor is not | depth 5/5 vs **5/71** | `[B2, B3 · repo-measured]` |
| bypass padding defeats best-route fidelity | 0.59049 → **0.729** past a 0.6 floor | `[B7 · repo-measured]` |
| padding defeats cuts and load | `3 → 0`; `0.5714 → 0.3088` | `[C1, C2 · repo-measured]` |
| deepest dependence survives padding | `0.133333 → 0.257161` | `[C3 · repo-measured]` |
| density collapse is legible in one readout only | `R_eff` ratio **1.0406 → 0.1523** | `[E1 · repo-measured, synthetic]` |
| names stable under rewrites, disputed under omissions | 27/27 vs 18/27 | `[D1, D2 · repo-measured]` |
| aggregate resistance is not a fidelity proxy | — | `[B10 · design]` |

## The two limitations that govern this research

These are not caveats appended at the end. They bound what every number above is
allowed to mean.

### 1. The swarm dataset is a seeded simulation, not telemetry

`[A1, A2, B9 · simulated]`

The 39-hop decay from 0.84 to 0.01 (`r = −0.887`, `N = 500`) is produced by
`cohort_D_swarm(seed=20260719, N=500)` over `random.Random(seed)`. **It is a
self-declared, seeded simulation. It is not empirical telemetry**, and
presenting it as such is an overclaim the supporting repository has formally
retired `[A2 · retired 2026-09-18]`.

A seeded simulation reproducing itself is a **code-correctness check**, not
empirical support for the law it reproduces.

The retirement carries a structural finding beyond the correction itself. A
locked, hashed pre-registration in that repository had already stated the point
in terms, while the project's front page claimed *"real 39-hop telemetry"*
regardless `[A5]`. **A prohibition in a locked file does not propagate to the
surfaces that never read it.** The remedy was a mechanism: a test now enumerates
every surface naming that cohort and fails on any mention lacking its provenance
tag. It caught three further untagged mentions immediately, **none of which used
any word a claim-family search had been looking for** — they stated the numbers
with no provenance at all. A word-list detects forbidden vocabulary; only a tag
requirement detects missing provenance.

Every swarm number in this thesis is likewise synthetic `[H1]`. The July 2026
incident is `external-claimed` with **primary sources unread** — egress-blocked
and never fetched — and per-hop payload availability, the only question the
central measurement turns on, remains **UNCONFIRMED** `[A3, G2, G3]`.

### 2. The defence is an axiom, and the audit has a boundary

`[E6, E7 · derived / identity]`

Node deletion — a kill switch — fails on a graph with no articulation points,
since removing any single node leaves the remainder connected. **This is a
theorem about a stated model whose premise is untested**: that a
post-coordination swarm communication graph has no articulation points has never
been measured here, and the premise is tagged `open`.

`R_eff = ∞` is an **identity, struck from the findings list**. The guarded metric
assigns `inf` across components by construction, so any claim that monitored
nodes "became infinitely far apart" restates the guard rather than reporting
evidence. Air-gapping is therefore the only *decidable* isolation state — which
is both less dramatic and more defensible than the claim it replaces.

## Reporting standard

Adopted from the supporting repository's textual study, which locks its nulls as
hard as its positives.

**Margin before verdict.** The organisational cohort's clean score separates at
`p = 0.044777`, clearing 0.05 by **0.005**, over an exact enumeration of all
**74,613** relabellings — C(22, 6), not a sampled subset — with cohort hash
`020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`
`[A4 · repo-measured]`. The leaky score reaches `p = 0.025679` against a
prediction of `p < 0.01`, and that is a **recorded miss kept by name**.

The standard is inherited from a study whose own headline cleared a pre-locked
gate by **+0.0034**, and which reported that removing any one of 5 of its 10
payload terms dropped it below — summarising itself as *"direction robust,
magnitude marginal."* A result that turns on the third decimal place is
presented as exactly that.

**Nulls held by tests, not prose**, so they cannot be summarised away later:
padding gameability, uniform-collapse blindness
(`test_uniform_collapse_blindness.py`), the cohort provenance tag
(`test_cohort_d_tagging.py`), and the structure/purpose boundary
(`test_the_category_boundary_is_stated`).

## Category boundary

> **Structure is evidence about a graph; purpose is a claim about an agent. No
> dataset crosses that gap.**

Confirming `E = U · D` across a yeast interactome, a repository cohort and a
seeded swarm says **exactly nothing** about the authorship, status or purpose of
any text, nor about the intent of any agent. A law confirmed a thousand times in
one domain is silent about another. Network telemetry and textual structure
claims are not to be combined, in either direction.

## What would change these conclusions

| open item | what would settle it |
|---|---|
| per-hop payload availability | a reader with access confirming the primary disclosures carry payloads `[G3]` |
| the articulation-point premise | measuring a real post-coordination swarm graph `[E6]` |
| every synthetic result | the same measurement on an observed topology `[H1]` |
| detector **recall** | **nothing available.** Precision is demonstrable; recall is not `[G4]` |

The last row is the ceiling on all of it. Every lexical and structural check
here can exhibit its own false positives and can never establish what it missed.
That is why the misses are kept by name, and why a green pipeline is reported as
*what ran* and never as *what is true*.
