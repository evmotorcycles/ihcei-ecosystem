# Epistemic Declarations & Operational Priors

No module may run on undeclared defaults. Update this file and its hash before
changing cutoffs. Layer-3 metaphysics are out of empirical scope.

## 1. Perception symmetrization

- **Module:** `stack/perception/lmd_distance.py`
- **Pinned:** `C_ij = A_ij + A_ji`  (code token: `"A+A.T"`)
- **Why:** attention `A` is row-stochastic and directed; commute time needs
  undirected weights.
- **API:** ratio / rank only — never absolute `d` as a product metric.
- **Connectivity:** a components walk runs before any reading. A pair in two
  different pieces **refuses**; it does not return a number. Bare `pinv` returns
  a confident finite value across components — measured 0.790569 on two disjoint
  4-rings — and that value is meaningless.
- **Pre-registration:** `stack/perception/prereg_perception.md`,
  sha256 `4cee849de5c8fe786c7bb1e22967a429d65cf077339dd318c5cd597d4ea7c4f5`

## 2. Organization cohort (ADG / CFE)

- **Module:** `stack/organization/adg_tqg.py` — **NOT BUILT.** See §6.
- **Cohort:** `adg-tqg/fixtures/experiment_cohort.json` (n = 22, fetched
  2026-07-17)
- **Cohort hash:** `020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`
- **Caveats, named rather than hidden:**
  - min-max / median κ / quartile bounds are **cohort-relative**; scores drift if
    the cohort changes
  - published p-values on n = 22 are **uncorrected for multiplicity**

## 3. Swarm (LISM / SENTRY) — information accounting

- **Module:** `stack/swarm/lism_sentry.py` — **BUILT, Commit 5.**
- **Law:** `E = U * prod(D_k)` — a fidelity product. **Not thermodynamic
  entropy**, and the word is not to appear in the module.
- **Floor:** `min_ratio` is a **required argument with no default**, expressed
  as a fraction of `U`. The absolute form ships as
  `absolute_floor_trip_depth` **only so its defect is measurable**, and nothing
  calls it. Measured: identical hops at `min = 0.6` trip at depth **5** with
  `U = 1` and at depth **71** with `U = 1000` under the absolute form, and at
  depth **5** under both `U` values under the ratio form.
- **Pre-registration:** `stack/swarm/prereg_sentry.md`, sha256
  `9e45f3b272faff4389e1126e6c71034a955fd480a3e112eeed3702d18ec964df`
- **Two route readouts, never fused.** `ratio_best` is the highest-fidelity
  simple route — what an attacker gets, because an attacker picks its route —
  and `ratio_worst` the lowest. Both are returned side by side.
- **The sentry is a THIRD sensor the declared-padding attack defeats.**
  Registered before running and confirmed: bypass padding lifts `ratio_best`
  from `0.59049` to `0.729`, clearing a floor of `0.6` that the unpadded chain
  breached. Subdivision padding moves the other way, to `0.531441`. So padding
  beats cut vertices, maximum load **and** best-route fidelity; only
  `ratio_worst` and deepest dependence survive it. This is recorded as a
  defeat, in those words.
- **The OR-gate is earned, not asserted.** A 5-agent star trips structure
  (1 cut vertex) and not fidelity (`0.81`); a 12-agent ring trips fidelity
  (`0.531441`) and not structure (0 cut vertices — a ring is 2-connected).
  Each sensor misses a fixture the other catches.
- **Scope:** synthetic fixtures only. No handoff telemetry exists in this
  repository and none is reachable from this container.

## 4. Audit / LINTEL

- Foster total `= n - k` is a **harness invariant only**. It is conserved under
  every rewrite measured so far — `lmd-scaling/`, `jepa-probe/`, `lintel/` — and
  a quantity true of every drawing prefers none of them. It does not gate health.
- Certificates must name their **invariance group**. Measured on 2026-07-17:
  - rewrites of the drawing (shims, splits, merges) — names survive **27/27**
  - what the drawing omits (candidate undeclared edges) — names survive **18/27**
  Those two figures are **cited as of that date and are not invariants.** Adding
  `stack/` moved them to 31 and 23 with no certificate changing, which is §4b.
- Gates compose as **OR** only.

## 4b. Certificate schema — amended

Every certificate carries four fields:
**`(readout, invariance_group, subject_hash, date)`**, plus `schema`. The
schema lives in `stack/governance/certificate.py` at version `cert/2`.

- **`subject_hash` hashes the edge list actually audited, at audit time.** It
  was added because `27 → 31` and `18 → 23` happened without any certificate
  changing: a certificate said what it held *under* and never what it held
  *about*.
- **`combined_report` refuses two certificates whose subjects differ.**
  Intersecting them would read agreement off two different graphs. This is the
  teeth; without it the field is decoration.
- **An audit reading carries `invariance_group = GROUP_NONE`.** `stack/audit/`
  is a raw reading that has survived no transformation family, and was measured
  to be *defeated* by declared padding. Stamping it with a group would be the
  overclaim the schema exists to prevent; naming the absence is the honest
  value.
- **Legacy certificates are marked, never back-dated.** `mark_legacy` sets
  `subject_hash = None`. A hash computed today over today's graph would attest
  to a subject the old certificate never saw, which is worse than no hash.
- **Tests assert relationships, never frozen counts.** `stable ⊆ declared`,
  `stable == declared ∩ completed`, `lost ∪ gained == declared △ completed`,
  and Foster `== n − k` as a harness self-check. A tolerance band on a ratio is
  a frozen count in disguise and was removed with the counts.

## 4c. `stack/structure/lintel.py` is a wrapper, not a vendored copy

The decision was between **(a)** a wrapper importing root `lintel/` and **(b)** a
vendored copy regression-tested against a frozen fixture snapshot external to
both. **(a) is recorded**, with its consequences taken in full:

- every engine symbol is a rebinding — `stack.structure.lintel.cuts is
  lintel.cuts`, the same function object
- **drift is impossible by construction**; there is one implementation
- **therefore no engine regression ships here in any form.** An earlier draft
  shipped one labelled "a tautology, recorded rather than claimed". That was
  still an identity check occupying a slot where evidence is expected, and a
  reader skimming a green suite counts it. It was deleted, and its absence is
  asserted from the parse tree rather than by grepping for its own name.
- had **(b)** been chosen the obligation would have been the opposite: a frozen
  fixture snapshot outside both copies, with drift a real and testable failure.

**In neither case does an identity check ship labelled as evidence.**

## 5. Firewall

- No fused scalar "integrity".
- Scope sentences are grepped in CI.

## 6. Organization module — A1 resolved

`stack/organization/adg_cfe.py` ships as a **faithful rename** of the arithmetic
in `adg-tqg/experiment.py`, with engineering parameter names:
`utility, d_enc, d_dec, noise, dissonance, eps, kappa, quartile_bound,
cohort_hash`.

- **Tradition vocabulary appears nowhere under `stack/`.** The mapping — both the
  display labels and the older parameter names — lives in `ncu/adapter.py` and
  only there. `test_the_tradition_vocabulary_is_absent_from_the_whole_stack`
  walks `stack/` and asserts it. The ledger deliberately does not restate the
  words, because restating them here would put them back inside `stack/`.
- **Render labels:** `aligned | misaligned | high_dissonance`. A label names what
  was measured; the class is a top-quartile say–do gap, and a stronger word
  would overstate it. The display adapter carries the older correspondence.
- **Faithfulness is asserted, not asserted-about:** the rename is bit-identical
  to the pre-rename arithmetic on all 22 records, to 1e-12.
- **`kappa` is `sorted(alignment)[n//2]`**, not a mean of the two middle values.
  On n = 22 those differ (0.861235 against 0.844392) and records between them
  would render on opposite sides.
- **`dissonance` carries no push-date input.** The fixture's label rule is
  `E = 0 iff archived or days_since_push > 365`, so a push-based dissonance
  would be a function of the label. `leaky_dissonance()` exists only so the
  leakage can be measured and reported; nothing shipped calls it.
- **Cohort-relative and hash-carried.** Every emitted reading carries the cohort
  hash, computed from the fixture bytes — a typed hash cannot enter. A probe
  appended to the cohort marks the hash, so a probe reading can never be
  mistaken for a fixture reading.
- **Pre-registration:** `stack/organization/prereg_organization.md`,
  sha256 `e2c7b6567ae0b05111bf0f5332632d42f4d8f34c23975937dc48aa70b1a92e3c`

## 6b. Audit module — Commit 3

`stack/audit/laplacian_audit.py`. Pre-registration
`stack/audit/prereg_audit.md`, sha256
`bd6aaae34e41cb2a66b39044d3124fcb282cf383f7ad72093e2283e86d4eb283`.

- **Component guard masks `R` as well as `D`.** Returning a raw `R` would hand
  the caller the confident finite number across a void the guard exists to
  refuse (0.790569 on two disjoint 4-rings).
- **`tol_ratio = 1e-10` is a declared preference**, replacing numpy's default
  `rcond` — which flipped a published verdict in `lmd-scaling/` depending on
  matrix assembly. A declared default is better than an inherited one; it is not
  a solution.
- **Foster raises, it does not assert.** `python -O` strips assert statements
  and a self-check that can be compiled away is not a self-check.
- **The OR-gate's second sensor is deepest dependence, NOT load.** Measured:
  under declared padding, cuts fall 3 → 0 and maximum load falls 0.5714 →
  0.3088, so both proposed sensors move in the attacker's favour and the gate
  does not trip. `fathom`'s deepest dependence rises 0.133 → 0.257 on the same
  fixture, agreeing in direction with `agi-stack/`'s 0.111 → 0.619 on an
  unrelated graph.

## 6c. Symmetrization is not free on an already-symmetric input

`C = A + Aᵀ` is pinned because raw attention is directed. A conductance matrix
that is **already symmetric** is thereby doubled, and every resistance halves.
The B2 regime figures supplied with Patch 2 match the **unsymmetrized** reading
exactly (3.358, 6.558, 12.958, 25.758 against 1.679, 3.279, 6.479, 12.879).
Under the ratio API the factor cancels; in a quoted absolute number it does not.

## 7. Two rules earned by failures in this stack

**The horizon rule.** Any monotonicity or trend claim registers a **horizon**,
and one probe **past** the horizon is mandatory and reported whichever way it
falls. Earned twice: `geometric-gate/`'s coarse leak sweep showed an empty band
that finer sampling filled, and `stack/perception/`'s P2R hit at 3.112x inside
its registered range and reversed one doubling past it.

**The lexical-detector rule.** A text check collapses whitespace before
matching, uses boundaries that exclude path separators as well as word
characters, carries a **two-sided named decoy** — one string it must not fire on
and one it must — and is scoped to precision: it may demonstrate its false
positives and must not claim recall. Earned repeatedly: `"ema"` matched inside
`"semantically"`; `\busr\b` fired inside `/usr/local` because a slash is a word
boundary, caught by its own decoy before shipping; and a rule-forbidding
sentence matched its own rule **thirteen** times this session, including the
write-up of the eleventh.

**Grep exemptions are scoped by ROLE, not by name.** Four kinds of file must be
able to quote what they forbid: the ledger, a pre-registration (`prereg_*.md`),
a test (`test_*.py`), and a results write-up (`RESULTS.md`). A hand-listed
allowlist was tried first and needed a new entry for every module added, which
is an exemption list that grows silently — the thing this rule exists to stop.
Shipped module code is never exempt, and a decoy asserts it.

## 8. Both doors are shut ON CONTAINER EGRESS, and the human check is OPEN

Neither verdict below rests on inspection. Both rest on what this container
could reach on 2026-09-17, and **a network limitation must not harden into a
finding.**

### Door 1 — trained attention (`DOOR1_STATUS.md`)

- `torch`, `transformers`, `safetensors`: **absent**. `numpy` 2.4.6 present.
- `huggingface.co`, `cdn-lfs.huggingface.co`, `hf.co`: **000**, no response.
- `pypi.org`: **200**. So the libraries are installable and the **weights are
  not** — the blocker is weight egress, not tooling. The install was not
  attempted, because a runtime with nothing to load is still a shut door.
- The Hugging Face connector reaches the Hub and read a 70M model's
  `config.json` and file listing, then **refused the weights as non-text by
  design**. It can deliver a model's shape, never its parameters.
- **No pre-registration was written.** An attention matrix from untrained
  weights is a synthetic fixture and must be labelled one; it is not a cheap
  way through this door.

### Door 2 — per-hop swarm payloads (`DOOR2_STATUS.md`)

- Dataset search returned 0 results; both first-party disclosures were
  **egress-blocked from this container and were not read directly**.
- **P24, P25 and P26 remain unwritten.** `stack/swarm/test_sentry.py` asserts by
  ROLE that no `prereg_*.md` in that package locks any of them — not by one
  hard-coded filename, which would pass the moment a second pre-registration
  appeared under a different name.

### The human check — status OPEN

A reader with network access is asked to establish two things this container
could not:

1. **Door 2:** whether either first-party disclosure contains per-hop message
   payloads. If it does, the Door 2 verdict is wrong and P24–P26 must be
   locked before any code touches the data.
2. **Door 1:** whether the weight hosts are blocked by this environment's
   network policy rather than by an outage on the probe date.

Neither has been done. **Status: OPEN**, and it stays recorded as open until a
named reader records an answer. The portable form of both requests — feasibility
gate, unlocked pre-registration text, data provenance and acceptance criteria —
is `phase5/runner_spec.md`.

## 9. The lexical matcher is a MECHANISM, not a rule to remember

`stack/governance/matcher.py`. The discipline that §7 states in prose is now the
only available implementation:

- `forbid()` **collapses whitespace itself**, on every string it is handed. A
  caller never sees the raw text and so cannot forget.
- `scan()` takes `must_not_fire`, `must_fire` and `min_seen` as **required
  keyword arguments**. A one-sided check cannot be written with it, and a walk
  that read nothing cannot report clean.
- Exemption is computed from **role**, and shipped module code has no role that
  exempts it.
- The claim is scoped to **precision**. Boundary-safety costs inflections —
  `"gate"` no longer matches inside `"gates"` — so both forms must be listed.

Fourteen self-matches in one session is a memory failure, and the fix for a
memory failure is a mechanism. Two more arrived immediately and both are kept as
cases: the **fifteenth** was `matcher.py` itself, flagged by the first scan ever
run because its docstring illustrated the inflection cost with a word a caller
bans — fixed by neutralising the example, **not** by exempting the file. The
**sixteenth** was a test that grepped its own source for a deleted function's
name, with the name in the assertion; fixed by reading the parse tree instead of
matching text.
