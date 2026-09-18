# The Future of AI as a Graph: what this repository actually did

**Claim rows are carried in the margin as `[row · status]`, keyed to
`reports/TABLE_1_claim_status.md`. A sentence without a row is a statement about
design or about this document, never a result.**

Status vocabulary: `measured` · `identity` · `simulated` · `external-claimed` ·
`design` · `retired` · `open`.

---

## 1. The structural transition this report is about

Two kinds of graph are in play, and the whole argument turns on refusing to
confuse them.

The first is **soft**: a probabilistic attention network over tokens, in which
every pair of positions carries a weight and nothing is ever strictly absent.
It is an extraordinary engine for *proposing* edges. It is also
data-dependent, dense by construction, and — as this repository measures below
— structurally invisible to several of the audits one would most want to run on
it. In the commissioning framing this is *"the Karpathy Graph"*
`[I5 · framing — unmeasured in-repo; Door 1 shut]`. That name appears in this
report exactly twice: here, and in §5's lineage. Everywhere else, including
every diagram caption and every claims row, it is **the proposer layer**,
because nothing in this repository has measured the object the name denotes.

The second is **rigid**: a declared graph — parts and links someone wrote down
— audited with effective resistance, cut vertices, current-flow load and
deepest dependence. Absence of an edge here is absence of a *declaration*, which
is a much weaker and much more honest thing than absence of a dependency.

The transition from the first to the second is not a refinement. It is a change
of epistemic type: from *what the model finds plausible* to *what a drawing
commits to*. Everything this repository can audit lives on the second side.
**Everything the proposer layer is good at lives on the first.** The interesting
engineering is the interface, and the interesting failures are all at that seam.

## 2. The stack, and what each layer is blind to

Five packages under `stack/`, each with a declared blindness stated in the same
size type as its capability.

| layer | reads | **declared blindness** |
|---|---|---|
| `perception` | attention → resistance bearings | **Scale.** The ratio API is invariant to uniform rescaling, which is exactly what makes it ungameable *and* what makes it unable to see uniform collapse `[C1 · identity]`. Refuses across components rather than guessing `[B5 · measured]`. |
| `audit` | declared graph → cuts, load, resistance | **Padding.** Measured, not supposed: three of five sensors are defeated by adding declared edges `[B1–B4, E5 · measured]`. Carries `GROUP_NONE`: it has survived no transformation family. |
| `structure` | certificates over findings | **Subject drift.** A finding's stability is meaningless without the graph it held on; hence `subject_hash` `[D4 · measured]`. |
| `swarm` | handoff chains → serial fidelity | **Bypass.** `ratio_best` is defeated by exactly the attack that beats cuts and load `[E4 · measured]`. |
| `organization` | cohort → alignment readings | **Cohort-relativity.** Bounds are relative to a fixture; p-values uncorrected `[F6 · declared limitation]`. |

The pattern worth naming: **every layer's blindness is the shadow of its
strength.** Scale-invariance buys ungameability and costs collapse-detection.
Declared-graph reading buys precision and costs the undeclared channel.

## 3. Per-instrument results

### 3.1 Resistance, cuts, and the padding attack

On a nine-node fixture, adding four *declared* edges — no new nodes, no new
evidence — moves the sensors like this `[B1–B3 · measured, commit ae20cd4]`:

| sensor | before | after | direction |
|---|---|---|---|
| cut vertices | 3 | **0** | attacker's favour |
| maximum load | 0.5714 | **0.3088** | attacker's favour |
| deepest dependence | 0.133333 | **0.257161** | **against** the attacker |

The load result was **registered the other way and missed** `[B2 · registered
miss]`. Padding adds routes, and routes *spread* current-flow betweenness rather
than concentrating it. A second, unrelated graph agrees in direction on
dependence, 0.111 → 0.619 `[B4 · measured]`.

So an OR-gate of *(cuts fell)* OR *(load rose)* does not trip on this attack.
The gate's second sensor has to be deepest dependence.

### 3.2 The −0.5 slope is an identity

`pinv(cL) = pinv(L)/c`, therefore `d → d·c^(−1/2)` `[C1 · identity]`. The
pre-registration that carries it is titled **"THE −0.5 SLOPE IS AN IDENTITY, NOT
A RESULT"**, and that title is doing real work: the same exponent appears in the
emergent-spacetime comparison suite as "Experiment A", where its sweep is
`d = J^(−1/2)` exactly. A number true of every graph prefers none of them.

Foster's total `Σ w·R = n − k` is treated the same way `[B6 · identity]`:
assert-only harness check, never returned in a reading, because a quantity true
of every drawing cannot gate a decision about one.

Against those identities sits a genuine instability: the published verdict in
`lmd-scaling/` **flips** on three knobs — dtype, pinv library, and Laplacian
assembly `[C2 · registered miss]`. Three of its predictions missed for that
reason, and the misses are kept by name.

### 3.3 Growth, and the horizon rule

Pinned-locality growth reaches 3.112× **inside** its registered range, then
**reverses** one doubling past it `[C3, C4 · measured]`. A coarse sweep in
`geometric-gate/` separately showed an empty band that finer sampling filled
`[G3 · measured]`.

Both would have shipped a confident wrong number, and together they produced the
rule: **register a horizon, then probe past it, and report the probe whichever
way it falls.**

### 3.4 Names survive; counts do not

| reading | value | invariance group |
|---|---|---|
| names under behaviour-preserving rewrites | **27/27** `[D2 · measured]` | rewrites of the drawing |
| names under completion of omissions | **18/27** `[D3 · measured]` | what the drawing omits |
| count under re-export shims | **27 → 39 → 46**, ≈1.7× `[D1 · measured]` | — |

The count is inflatable at will by changes that alter no behaviour, so it ships
marked untrusted and is never compared across projects or time `[D7 · design]`.

Two negative results sit here and are load-bearing. **31 of 92** candidate edges
were mentions in comments or docstrings, not dependencies `[D5 · measured]` — so
a disputed name is *disputed, not wrong*. And the quotient pass **missed Q3 and
does not ship** `[D6 · measured]`.

### 3.5 The geometric gate, and a collapse the structure could not see

Two results here, and both are negative.

**No threshold is picked out by the data** `[G1 · measured]`. The sensor walks
continuously through the entire band where a cutoff would sit, so any hard-halt
number is a choice rather than a discovery. The gate's cutoffs are therefore
**required arguments with no defaults** — a declared preference, named as one.
Its ninth prediction missed on both of its clauses `[G2 · registered miss]`.

**The mechanism that prevents representation collapse is stop-gradient, not the
moving average** `[G4 · measured]`. Same data, same initialisation, same steps:
the symmetric arm collapses on all five seeds by roughly twelve orders of
magnitude.

And the finding that matters most for §2's table: **the structural readouts are
blind to that collapse** `[G5 · measured]`. The instrument was pointed directly
at a failure it had been built to be relevant to, and it did not move. This is
the scale-invariance blindness of §2 arriving as a measurement rather than as a
caveat — the property that makes bearings ungameable is the same property that
makes uniform collapse invisible to them.

The joint-embedding filter in the pipeline **abstains** rather than scoring when
it has nothing to say `[G6 · design]`, which is the same discipline as the
component guard: empty is not false, and a state with nothing checkable gets no
number at all.

One further modelling consequence, easy to miss and measured: symmetrisation is
**not free on an already-symmetric input** `[B8 · measured]`. `C = A + Aᵀ`
doubles conductance and halves every resistance, so a set of absolute figures
supplied for comparison matched the *unsymmetrised* reading exactly. Under a
ratio API the factor cancels; in a quoted absolute number it does not.

### 3.6 The certificate contract

A finding's stability is only meaningful against a stated subject. Adding
`stack/` to this repository moved modules 156 → 169, declared cut vertices
27 → 31, and stable-under-omission 18 → 23 — **with no certificate changing**
`[D4 · measured, commit 5ac72a2]`.

So every certificate now carries `(readout, invariance_group, subject_hash,
date)`, and two certificates over different subjects **refuse to combine** — a
design contract sourced to ledger §4b, carrying no claim row because it is a
rule rather than a result. The audit's own readings carry `GROUP_NONE`, because stamping a
group on a reading that survived nothing is the exact overclaim the schema
exists to prevent.

### 3.7 The organization cohort

Exact enumeration over all **74,613** relabellings — C(22,6), not a sampled
subset, because an `islice` cap takes combinations in lexicographic order and is
a biased subset rather than a null `[F1 · measured]`.

| score | exact p |
|---|---|
| clean | **0.044777** `[F2 · measured]` |
| leaky | **0.025679** `[F3 · measured]` |

The leaky score was predicted to separate at `p < 0.01`. It did not, and the
test that records this is named `test_the_first_prediction_that_missed`
`[F4 · registered miss]`. The clean result clears 0.05 by 0.005, and the suite
asserts that thinness explicitly so it reads as thin.

## 4. Retired claims

| claim | evidence that retired it | replacement |
|---|---|---|
| hard floor at `p = 0.735` | its sensor read zero on **76.6%** of records `[H1 · retired]` | removed |
| an identity check shipped labelled "a tautology" | a reader skimming a green suite counts it `[H2 · retired]` | deleted; wrapper decision recorded |
| tolerance band `0.5 < stable/raw < 0.95` | a ratio band is a frozen count in disguise `[H3 · retired]` | relationship assertions |
| `each_settles == 1/484`; hub `echo/echo.mjs` | repo grew; hub moved to `spar/spar.py` `[H4 · retired]` | denominator derived at runtime |
| **"Validated against real 39-hop telemetry"** | the cohort is `cohort_D_swarm(seed=20260719)` `[H5 · retired 2026-09-18]` | seeded wording on 8 surfaces |

**H5 is the one worth dwelling on**, because the repository already knew. A
locked, hashed pre-registration said in terms that presenting that decay as
evidence about real agent swarms *"would repeat exactly the error that the N=793
retraction was issued for"* `[A4 · the finding]` — while the front door claimed
the opposite for months.

**A prohibition in a locked file does not propagate to the surfaces that never
read it.** That is the same defect as §7's air-gapped suites, and it now has a
mechanism rather than a memory: one test enumerates every surface naming that
cohort and fails on any mention lacking the tag. It caught three more on its
first run, none of which used the words the retirement grep had searched for.

## 5. Lineage — labelled lineage, never evidence

Four inheritances are worth stating, and none of them is a result.

- distributed representations and SNE/t-SNE → a learned metric read off
  structure `[I1 · lineage]`
- capsules and pose-agreement → a geometric gate `[I2 · lineage]`
- autoencoders and contrastive objectives → joint-embedding prediction
  `[I3 · lineage]`
- immortal computation and weight-sharing swarms → serial fidelity accounting
  `[I4 · lineage]`

The commissioning framing's *"Karpathy Graph"* `[I5 · framing — unmeasured
in-repo; Door 1 shut]` belongs in this list and nowhere else: it names why the
stack exists, and no measurement in this repository defines it.

Lineage explains why an instrument was built. It never licenses a claim about
what the instrument found.

## 6. Swarms

`E = U · ∏D_k` is a **fidelity product**, and the vocabulary ledger §3 forbids
is absent from the module and grepped for `[E1 · design]`.

The floor is a ratio of `U`, and the argument for that is measured: identical
hops trip at depth **5** under both `U = 1` and `U = 1000` with a ratio floor,
and at depth **5** versus **71** with an absolute one `[E2 · measured]`. The
absolute form ships only so its defect can be exhibited, and nothing calls it.

**The headline is a defeat.** Bypass padding lifts best-route fidelity from
0.59049 to **0.729**, clearing a floor the unpadded chain breached
`[E4 · measured]`. Subdivision padding moves the other way, to 0.531441
`[E3 · measured]`. So serial fidelity read on the best route joins cuts and load
as a sensor the padding attack beats — **three of five** `[E5 · measured]`. The
two survivors, `ratio_worst` and deepest dependence, are the two that are not
shortest-path readings.

On formation: a synthetic 40-agent ring with a 12-agent clique moves only the
`R_eff` inside/across ratio, 1.0406 → 0.1523, while cut vertices stay blind at
0 → 0 and maximum load *falls* `[E7 · measured on a synthetic fixture]`.

### The 2026 incident

Reported scale is roughly 1,200 agents, upward of 70,000 messages, roughly 700
participating `[E8 · external-claimed, primary sources unread]`. The corpus is
described as analysed by third-party evaluators under access, with no public
release found `[E9 · external-claimed]`.

Three constraints hold in this document. The first-party disclosures were
**egress-blocked from this container and have never been fetched by this
repository**; corroboration is out-of-repo and secondary. Per-hop payload
availability — the only question the swarm door turns on — is **unconfirmed**.
And the event is named as a topology observation with **no motive attribution to
any agent, organisation or person**.

**Nothing in this repository has measured that graph.** Every swarm number above
describes a fixture this project drew.

## 7. Plexus: what exists, and what is direction

**What exists** is an enforcement pipeline, and it is the only thing this
section claims. 124 suites, zero test files unreachable from a full run, and a
tree that stays clean after one `[J5 · measured, commit 70a3fc5]`.

Three of this session's findings were the same defect wearing different clothes:
a frozen count, an air-gapped suite, and a locked prohibition that never reached
the front door. In each, the knowledge existed and nothing carried it to where
it was needed. The fixes are mechanisms, not reminders — a matcher whose
signature makes a one-sided check unwritable, a denominator derived at runtime,
a tag the pipeline enforces.

**What is direction** is the operating system. Plexus as an OS that routes the
proposer layer's soft proposals through a geometric gate and then through
topological telemetry **is not a shipped system**, and no row in Table 1
supports calling it one. The gates exist; the composition is a design intent.

## 8. Open

| item | status |
|---|---|
| Door 1 — no ML runtime; weight hosts unreachable; `pypi.org` reachable | **shut on container egress, not on inspection** `[J1 · open]` |
| Door 2 — no obtainable per-hop corpus; P24–P26 unwritten, text unlocked | `[J2 · open]` |
| the human check — primaries, and block-versus-outage | **OPEN** `[J3 · open]` |
| cross-suite ordering dependency in `cohort-audit` | `[J6 · open]` |
| recall of omission and lexical detectors | **unmeasurable by construction** `[J7 · open]` |

The last row is the honest ceiling of everything above. Every lexical and
structural check in this repository can demonstrate its own false positives and
can never establish its recall. That is why the misses are kept by name, and why
a green pipeline is reported here as *what ran*, never as *what is true*.
