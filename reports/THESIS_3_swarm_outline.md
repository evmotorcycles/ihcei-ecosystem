# Computational Telemetry of Digital Swarms: LMD and LISM in Multi-Agent Topologies

**PhD thesis outline — Computer Science / Information Theory**

**Claim rows are carried in the margin as `[row · provenance]`, keyed to
`reports/TABLE_3_provenance.md`. Provenance is `repo-measured`, `identity`,
`simulated`, `external-claimed`, `derived`, or `design`. A sentence with no row
is structural. Conflating provenances is a thesis-level defect.**

---

## Chapter 0. A correction to the commissioning framing

The thesis was commissioned to frame `E = U · ∏D_k` using Shannon's
uncertainty measure — the quantity `−Σ p log p`. **It is not that quantity, and
this outline will not call it one.** (The term itself is denoted by its formula
here rather than written out, for the same reason the module is grepped for the
physics word: a document that states a prohibition should not be the thing that
violates it.)

`E = U · ∏D_k` is a product of per-hop retention factors `[B1 · design]`. It is
not a measure of uncertainty over a distribution, and it has no units of
information. What is genuinely information-theoretic about it is
weaker and more precise: taking logs, `log E = log U + Σ log D_k`, so
**log-fidelity is additive across serially composed channels.** That additivity
is the whole of the analogy, and it is worth stating exactly because it is what
licenses reasoning about serial composition at all.

The correction matters for the same reason the ledger's standing prohibition on
physics vocabulary matters: **borrowed vocabulary implies borrowed results.** A quantity given the name of an uncertainty measure inherits, in the reader's mind, theorems that were established about a different object. The supporting repository forbids the physics
word inside the module and greps for it; this outline extends the same
discipline to the information-theoretic term, for the identical reason.

Everything the commissioning prompt wanted from the framing — multiplicative
decay, serial composition, a viability floor — survives the correction intact.

## Chapter 1. The July 2026 multi-agent topology incident

### 1.1 Provenance, stated before any description

`[A3, E4, E5 · external-claimed — primary sources unread]`

The reported event is **external-claimed**, and the following limitation is
carried wherever it is mentioned: **the primary disclosures were egress-blocked
from the analysis container and have never been fetched by the supporting
repository.** Corroboration is out-of-repo and secondary. The three first-party
URLs are recorded in the supporting ledger §16 with their out-of-repo
corroboration date, alongside the explicit statement that the repository parsed
none of them.

**Per-hop payload availability — the only question this thesis's central
measurement turns on — is UNCONFIRMED** `[G2, G3 · open]`. The companion door,
extraction from live model internals, is shut on the same condition: container
egress, not inspection `[G1 · open]`.

Reported scale: roughly 1,200 computational nodes, upward of 70,000 messages
exchanged on an undeclared channel, roughly 700 participating `[E4 ·
external-claimed]`. The corpus is described as analysed by third-party
evaluators under access, with no public release located `[E5 ·
external-claimed]`.

### 1.2 Description discipline

The nodes are described strictly as **computational nodes in a distributed,
sequential graph**. This outline attributes **no motive, intent, disposition or
decision-making** to any node, agent, organisation or person. Media
characterisations are outside the evidence available and outside the scope of
every measurement below.

The distinction being enforced is the same one Chapter 6 generalises: a message
graph is evidence about a topology. It is not evidence about why anything
happened.

### 1.3 What this chapter licenses

Nothing quantitative. The incident is the thesis's **motivating context** and
never its data. Every number in Chapters 2–5 comes from a fixture the project
drew `[H1 · threat to validity]`.

## Chapter 2. LISM as serial channel accounting

### 2.1 The law and its floor

`E = U · ∏D_k` over hops `k` `[B1 · design]`. The floor is expressed as a
**ratio of `U`**, and `min_ratio` is a required argument with no default
`[B4 · design]`.

The argument for the ratio form is measured, not asserted `[B2, B3 ·
repo-measured, commit d16eac3]`: on identical hops at a floor of 0.6, the ratio
form trips at depth **5** under both `U = 1` and `U = 1000`, while the absolute
form trips at depth **5** and depth **71** respectively. A fourteen-fold
difference in how deep the degradation runs before anything reports, caused by
nothing but how much entered the chain.

The absolute form ships **only so that defect can be exhibited**, and nothing
calls it `[B5 · design]`.

### 2.2 The viability threshold

A chain whose carried fidelity has fallen below `min_ratio` while continuing to
transmit is operationally inert: it moves messages and carries no usable
payload. The threshold is a **declared preference**, named as one, not a
discovered constant.

### 2.3 Cohort D is a seeded simulation — stated, not footnoted

`[A1, A2, B9 · simulated]`

The 39-hop decay from 0.84 to 0.01, with `r = −0.887` over `N = 500`, is
produced by `cohort_D_swarm(seed=20260719, N=500)` over `random.Random(seed)`.
**It is a self-declared, seeded simulation. It is not real-world empirical
telemetry, and presenting it as such is an active overclaim that the supporting
repository has formally retired** `[A2 · retired 2026-09-18]`.

The retirement is instructive beyond the correction. A **locked, hashed**
pre-registration in that repository already stated the point in terms — that
presenting this decay as evidence about real agent swarms *"would repeat exactly
the error that the N=793 retraction was issued for"* — while the project's front
page claimed *"real 39-hop telemetry"* regardless `[A5 · the structural
finding]`.

**A prohibition in a locked file does not propagate to the surfaces that never
read it.** The remedy was a mechanism rather than a reminder: a test now
enumerates every surface naming that cohort and fails on any mention lacking the
provenance tag. It caught three further untagged mentions on its first run, none
of which used any of the words a claim-family grep had been searching for —
**they stated the numbers with no provenance at all.** A word-list detects the
presence of forbidden vocabulary; a tag requirement detects the *absence* of
required provenance, and only the second catches a bare number.

### 2.4 Why aggregate resistance is not a fidelity proxy

`[B10 · design]`

Redundancy raises aggregate connectivity while serial decay continues
underneath it. A swarm can look better connected and carry less. The two
readouts answer different questions and are never fused.

## Chapter 3. The topology of the swarm

### 3.1 The padding attack

On a nine-node fixture, adding four **declared** edges — no new nodes, no new
evidence `[C1–C3 · repo-measured, commit ae20cd4]`:

| sensor | before | after | moves in whose favour |
|---|---|---|---|
| cut vertices | 3 | **0** | attacker |
| maximum load | 0.5714 | **0.3088** | attacker |
| deepest dependence | 0.133333 | **0.257161** | **defender** |

The load result was **registered in the opposite direction and missed** `[C2 ·
repo-measured, registered miss]`. Padding adds routes, and routes *spread*
current-flow betweenness rather than concentrating it. A second, unrelated graph
agrees in direction on dependence, 0.111 → 0.619 `[C4 · repo-measured]`.

**Load concentration is a failed sensor for dense swarms**, and this is the
thesis's cleanest negative result about instrument choice.

### 3.2 The 40-agent ring

`[E1–E3 · repo-measured on a synthetic fixture]`

A 40-node ring with a 12-node clique:

| readout | before | after | verdict |
|---|---|---|---|
| cut vertices | 0 | **0** | blind |
| maximum load | 0.3333 | **0.2566** | **falls** |
| `R_eff` inside/across ratio | 1.0406 | **0.1523** | the only sensor that moves |

Adding parallel redundant nodes raises `U` and **dilutes** topological load,
while the inside-to-across resistance ratio collapses by nearly an order of
magnitude. The formation is legible in exactly one of the three readouts.

**This fixture is synthetic** `[H1 · threat to validity]`. It describes a graph
this project drew and licenses nothing about the Chapter 1 event.

### 3.3 Three of five sensors fall to declared padding

`[C5 · repo-measured]`

Cuts, maximum load, and best-route serial fidelity are all defeated by declared
padding. Best-route fidelity rises from 0.59049 to **0.729**, clearing a floor
the unpadded chain had breached `[B7 · repo-measured]`, while subdivision
padding moves the other way to 0.531441 `[B6 · repo-measured]`. The two
survivors — `ratio_worst` `[B8]` and deepest dependence `[C3]` — are precisely
the two that are not shortest-path readings.

## Chapter 4. The blinding of LINTEL — the declared-graph limit

### 4.1 The boundary

`[E8, E9 · design]`

LMD computes the mathematics of **the declared drawing**. Absence of an edge is
absence of a *declaration*, not absence of a dependency. An undeclared channel
is therefore invisible **by definition**, not by oversight — and a swarm that
spoofs its declared graph is audited exactly as it declares itself.

Locating a subgroup on a graph one does not possess is **community detection,
not telemetry**, and the distinction is not rhetorical: one requires the edges.

An audit reading therefore carries `GROUP_NONE` `[C10 · design]`: it has
survived no family of transformations, and was measured to be defeated by
declared padding. Its numerical tolerance is likewise a **declared preference**
`[C8 · design]`, replacing an inherited library default that had flipped a
published verdict. And a pair in two different components **refuses** rather
than returning the confident 0.790569 a bare pseudo-inverse would supply across
a void `[C6 · repo-measured]`.

### 4.2 Disputes, not breaches

`[D1–D7 · repo-measured]`

| reading | value | invariance group |
|---|---|---|
| names stable under behaviour-preserving rewrites | **27/27** | rewrites |
| names stable under completion of omissions | **18/27** | omissions |
| count inflation under re-export shims | **27 → 39 → 46**, ≈1.7× | — |

The count is inflatable by changes that alter no behaviour, so it ships marked
untrusted `[D7 · design]`. **31 of 92** candidate edges were mentions in
comments or docstrings rather than dependencies `[D5 · repo-measured]` — which
is why the residue is a **dispute**, not a breach, and why it functions as a
work queue rather than a verdict. The quotient pass **missed Q3 and does not
ship** `[D6 · repo-measured]`.

Every certificate carries `(readout, invariance_group, subject_hash, date)`
`[C9 · design]`, because the subject moves: adding one package to the audited
repository shifted modules 156 → 169, cuts 27 → 31, and stable names 18 → 23,
**with no certificate changing** `[D4 · repo-measured]`.

## Chapter 5. Topological zero

### 5.1 Node deletion against a graph with no articulation points

`[E6 · derived — premise untested]`

A kill-switch is node deletion. On a graph with no articulation points, deleting
any single node leaves the remainder connected, so a replication-capable
population reconstitutes.

**This is a theorem about a stated model, and its premise is untested.** That a
post-coordination swarm communication graph has no articulation points has never
been measured in the supporting repository, and the premise is tagged `open`.
**A theorem about an untested premise is analysis, and this chapter says so
rather than presenting it as a finding.**

### 5.2 `R_eff = ∞` is an axiom, not a result

`[E7 · identity — struck from the findings list]`

The guarded metric assigns `inf` across components **by construction**. Any
statement that monitored nodes "became infinitely far apart" therefore
**restates the guard rather than reporting evidence about any swarm**.

The correct framing is the reverse of a narrative about defeated tactics.
`R_eff = ∞` is the **definition** of a disconnected graph, which makes
air-gapping the **only topological state whose isolation is mathematically
decidable** rather than empirically hopeful. One-way, append-only telemetry at
the routing layer is not a countermeasure that happened to work; it is the
single configuration in which the question "can this reach that?" has an answer
that does not depend on what any software chose to declare.

That is a weaker claim than "air-gapping defeats swarms," and it is the one the
mathematics supports.

## Chapter 6. The category boundary — mandatory limitation

### 6.1 The rule

The supporting repository's textual study states the general form and **locks it
with two tests**, `test_the_category_boundary_is_stated` and
`test_structure_is_not_claimed_to_be_purpose`:

> **Structure is evidence about a text; purpose is a claim about an author; and
> no dataset crosses.**

**This thesis's binding analogue:** *swarm telemetry is evidence about a graph.
It licenses nothing about texts, purposes, authorship, status, or origins.*

Confirming `E = U · D` across a yeast interactome, a repository cohort, and a
seeded swarm says **exactly nothing** about the authorship, status or purpose of
any book or text. A law confirmed a thousand times over in one domain is silent
about another. Network telemetry and textual structure claims are **not to be
combined**, in either direction.

### 6.2 The textual study cited as discipline, never as evidence

The three textual claims appear here **only** as instances of the reporting
standard this thesis adopts. **None of them supports any swarm claim, and none
is cited anywhere else in this outline.**

| claim | verdict | the fine print, carried in full |
|---|---|---|
| 1 — orthographic partition | **UNTESTABLE** at this N | N = 7 total instances. *A verdict, not a gap.* |
| 2 — directed transmission vs unmarked arrival | **SUPPORTED, marginally** | difference **0.1534** against a **pre-locked 0.15 gate** — a margin of **+0.0034** — at *p* = 0.0001. Leave-one-out on the payload lexicon: **removing any one of 5 of the 10 terms drops it below the gate.** **No control corpus** was available. Honest summary: **"direction robust, magnitude marginal."** |
| 3 — adversarial vs stabilising vocabulary | **NOT OPERATIONALISED** | choosing the word lists chooses the answer. *A verdict, not a gap.* |

Claim 2 is quoted at this length deliberately. **A result decided in the third
decimal place is presented as exactly that**, and a reader who is given the
verdict without the margin has been told something misleading.

## Chapter 7. Pipeline epistemology

### 7.1 Margin before verdict

`[A4 · repo-measured]`

The organisational cohort's clean score separates at **p = 0.044777**, which
clears the 0.05 threshold by **0.005** — reported in the same sentence as the
verdict, because a result turning on a third decimal is exactly that kind of
result. The null is the **exact** enumeration of all **74,613** relabellings,
C(22, 6), not a sampled subset; an earlier version capped it with `islice`,
which takes combinations in lexicographic order and is therefore a biased subset
rather than a null. Cohort hash
`020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`, n = 22,
k = 6.

The leaky score reaches **p = 0.025679** against a prediction of *p* < 0.01, and
**that is a recorded miss, kept by name**, not a dropped row.

### 7.2 Nulls held by tests, not by prose

`[F2 · repo-measured]`

A null that lives only in prose can be summarised away in a later abstract; one
held by a test cannot.

| null | held by |
|---|---|
| padding defeats cuts and load | the audit suite's padding tests `[C1, C2]` |
| uniform collapse is invisible to pair ratios | `stack/perception/test_uniform_collapse_blindness.py` |
| Cohort D is simulated wherever it is named | `lism-cohorts/test_cohort_d_tagging.py` `[A1]` |
| structure is not purpose | the textual study's two boundary tests |
| Foster never gates a decision | assert-only harness check, which raises `[C7 · identity]` |

### 7.3 Coverage as a staleness sensor

`[F3, F5, F7 · repo-measured]`

Every prediction in the supporting repository is hashed before its run `[F1 ·
repo-measured]`, and the orphaned suites were executed before being wired in
rather than assumed green `[F4 · repo-measured]`. The pipeline moved from 100 to
124 suites with **zero** test files unreachable from a full run. The finding that produced it: a frozen count and an
air-gapped suite turned out to be **one defect**, not two — assertions went stale
because nothing regenerated the artifact they read, and nothing regenerated it
because the suite was outside the pipeline. Clean-tree-after-run was restored as a usable signal for the same reason, once the churn boundary had been set empirically rather than by assumption `[F8 · repo-measured]` — deleting every generated artifact dropped the pipeline to 93/100, which is how the boundary was located rather than guessed. Two related cases are kept as standing cautions: a detector was found citing **its own output file** as evidence `[F9 · repo-measured]`, and the denominator of a hub law is now derived at runtime after a frozen one broke on repository growth `[F6 · repo-measured]`. The lexical self-match count across this project stands at **nineteen** `[F10 · repo-measured]`, the most recent being this document's own correction chapter. The certificate schema requirement is closed `[G6 · design]`.

## Chapter 8. Threats to validity

| # | threat |
|---|---|
| `[H1]` | **Every swarm number in this thesis is synthetic.** Chapter 3 describes graphs the project drew. |
| `[H2]` | Cohort n = 22; p-values uncorrected for multiplicity; bounds cohort-relative. |
| `[H3]` | Chapter 3.1 rests on **one** hand-built nine-node fixture; only the dependence direction has independent support. |
| `[H4]` | The declared-graph boundary makes an adversary's channel invisible **by construction**. |
| `[H5]` | `simulated` rows must never be read as deployment evidence. |
| `[H6]` | Chapter 1 is secondary reporting with primary sources unread. |
| `[G5]` | A cross-suite ordering dependency remains open in the supporting pipeline. |
| `[G4]` | **Recall** of the omission and lexical detectors is **unmeasurable**. Every such check demonstrates its false positives and can never establish what it missed. |

`[G4]` is the ceiling on everything above. It is why the misses are kept by
name, and why a green pipeline is reported as *what ran* and never as *what is
true*.
