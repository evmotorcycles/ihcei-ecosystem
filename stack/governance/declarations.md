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

## 10. Two legacy frozen-artifact defects, resolved

Both were pre-existing, both were the defect this session has been chasing, and
both surfaced in code outside `stack/`. Neither was resolved by moving a
threshold.

### `cohort-audit/test_gap_closure.py` — a gate on a fit that never converged

The suite asserted `multivariate_insample_auc < 0.50`. That value is scored on
whatever parameters the optimiser held when it stopped, because
`multivariate_converged` is `False` three lines above it. It moved
`0.4275 → 0.7237` with no change to the data, purely on this container's
statsmodels version — deterministic across three runs, so not flakiness. Same
shape as the three-knob verdict flip in `lmd-scaling/`.

**The assertion was deleted, not relaxed.** The decisive fact is that it was
**never a locked prediction**: `prereg/gapclosure_prereg.json` registers Y4 as
*"single-term quadratic CV AUC >= 0.55 ... AND the multivariate U+D+D^2 logit
reports converged == False"*, and nothing else. The `~0.49` appears only in the
honesty disclosure as an earlier observation. Removing it restores the test to
what the pre-registration actually locks, and
`test_the_locked_spec_still_carries_the_y4_prediction_this_test_asserts` fails
if Y4 ever gains an in-sample clause. The removal is pinned from the **parse
tree**, not by grepping the source, because the comment explaining it quotes the
expression it forbids.

### `governance-os/os.test.mjs` — two frozen artifacts, only one of them failing

- **The permissions list.** `assert.deepEqual(e.permissions.sort(),
  ["activeTab", "scripting"])` went stale when the manifest legally gained
  `storage` in `1866cc1`. The expectation is now **derived from the manifest**,
  which is the same source the scanner reads, plus the finding stated directly:
  no declared permission matches the blocking set, and `can_block` is `false`.
  A decoy confirms it: adding `webRequestBlocking` to the manifest fails the
  test — and now fails it for the right reason, the verdict rather than the
  spelling.
- **`files_scanned` was never asserted at all.** The reported count moved
  `487 → 663` and broke nothing, because nothing read it. That is the worse of
  the two defects: the empty `blocking_call_sites` finding rested on a walk
  nobody had shown was non-empty, and a detector that reads zero files also
  reports zero call sites. A **non-vacuity floor** was added (`> 480`, one-sided
  by construction so repository growth never touches it) together with the
  relationship `cited ⊆ scanned`, which holds at any size. This is the same role
  `min_seen` plays in `stack/governance/matcher.py`.

## 11. Recorded and NOT resolved — two reproducibility gaps

Flagged rather than fixed. Neither is in any directive's scope, and neither is
called a defect here, because what they are has not been established.

- **`hinton-test` does not reproduce across runs.** The recorded Merkle root
  differs on every invocation on unchanged inputs — measured `052dc44e1bc0`
  then `6c65527d0693` on two consecutive runs. The suite still passes, because
  it checks that the chain is **intact within a run**, not that it reproduces
  between runs. If the generation timestamp is inside the hashed content then
  this is correct behaviour and the reproducibility claim is what needs
  narrowing; if it is not, something else is varying. **Not established.**
- **The repository cannot be clean after a reproduce run.** Nine `results*.json`
  files rewrite `generated_at` on every invocation, so `reproduce_all.sh` always
  leaves a dirty tree. This makes "the tree is clean" unusable as a check and
  quietly trains a reader to ignore the diff — which is how the `0.4275 →
  0.7237` change above went unnoticed until a full run was read line by line.

## 12. The governance-os detector greps its own output — RECORDED, not fixed

Found by accident while showing that the rewritten observer test in §10 can
fail. Adding `webRequestBlocking` to the extension manifest wrote that string
into `governance-os/results_os.json`. The next walk read that file **as it stood
before the run rewrote it**, matched the blocking pattern inside it, and recorded
a phantom finding — *"blocking browser extension"*, citing `results_os.json`
itself. It survived a full cycle, including a green 12/12, because the existing
self-match test excludes one **filename** and the contamination sat in a
different file.

The loop is one cycle deep, not self-sustaining: once the manifest is restored,
a second run clears it. That makes it worse to find, not better.

`os_check.mjs`'s `isEvidence()` exempts `rel === SELF`, fixtures, tests and
prose — but **not the file it writes**. That is exemption **by name** where the
role is *generated output*, which is the pattern this repository has already
recorded as the one that grows silently. The module's own comment states the
principle it misses: *"A detector that matches its own source is measuring
itself."*

**The detector was NOT changed.** What changed is a test —
`the detector does not match its own OUTPUT either` — which asserts the property
the detector ought to have, so a recurrence fails loudly instead of reading as
evidence. The one-line alternative is a `results*.json` clause in
`isEvidence()`, exempting by role. **That is a decision about what the gate
measures, and it is open.** Recorded here so it is not inherited silently.

## 11b / 12b — both CLOSED, and what closing them cost

**§12 closed.** `isEvidence()` in `governance-os/os_check.mjs` now excludes
`results*.json`. The clause sits beside `rel === SELF`, which it generalises:
`SELF` exempts one **filename**; the role it means is *output of the detector*,
and the file the scanner writes has that role. Proven with a decoy rather than
asserted — injecting `"webRequestBlocking"` into `results_os.json` previously
produced a phantom *"blocking browser extension"* citing the report itself, and
now cites only `keel/build_exe.py`.

**§11 hinton closed by NARROWING THE CLAIM, not by fixing the determinism.**
`echo/echo.mjs` `put()` builds `body` with `ts: new Date().toISOString()` and
hashes `sha256(prev + canonical(body))`, so the timestamp is **inside the
attested content** and `root()` over those hashes must differ per run. That is
correct for a tamper-evident ledger: *when* a record was written is part of what
is attested, and making the root reproducible would mean dropping `ts` and
weakening it. The root is an **ephemeral run-ID**. Four assertions in
`echo/echo.test.mjs` §F pin this so it is not later "fixed" into a weaker
ledger.

**§11 churn closed at EIGHT files, not sixty-nine.** The instruction was to
ignore `results*.json` wholesale. Measured first: deleting all 69 gives
**93/100**, because seven suites read a committed copy they never rebuild.
`smi/test_smi.py` opens `results_smi.json` and asserts the recorded run said
*"INVARIANT (BY CONSTRUCTION)"*, and the pipeline never invokes
`smi/run_smi.py`. **That file is the thing under audit.** Deleting only the
eight that churn gives **99/100**, and the single failure named the exception —
see §14.

**A static classifier disagreed and was wrong.** It reported *"65 regenerated
somewhere, 0 read-only records"* because it asked whether any tracked script
writes the file, when the question is whether the **pipeline** regenerates it.
Recorded because the wrong number is the more quotable one.

## 13. Forty-five test files are unreachable from `reproduce_all.sh`

Found because a test added to `hinton-test/hinton_test.test.mjs` went red on an
assertion unrelated to the change: the pipeline runs `hinton_test.mjs` and
**never** the `.test.mjs`, which had been stale since the script's verdict moved
from *"Partially Grounded"* to *"Insufficient Evidence"*.

Resolving every pipeline target and its parent directories, **45 test files are
not reachable from a full run.** That includes all 19 in `plexus/` — the
directory `CLAUDE.md` names as where its rules are enforced: `test_gate.py`,
`test_packs.py`, `test_metaphor.py`, and `test_cohort.py`, which carries one of
the four recorded misses.

Run directly they give **518 passed, 2 failed, 1 skipped**. Both failures are
`page-code/test_blueprint.py`, and both are frozen counts against a growing
repository: `each_settles == 1/484` (= 1/22²) against a measured `0.001479…`
(= 1/26²) — the hub gained four importers. **Pre-existing**, identical at
`5ac72a2`.

**"100/100 suites" is true and narrower than it reads**: it counts suites named
in `reproduce_all.sh`, not tests in the repository. Wiring the 45 in would
surface those 2 known failures and whatever else, so it is **a decision about
what the gate covers and stays OPEN.**

## 14. A cross-suite ordering dependency, hidden by an artifact being committed

`cohort-audit/test_cohort_audit.py` reads `results_gapclosure.json` at lines 48
and 75, and runs at pipeline line **109** — *before* `test_gap_closure.py`
generates it at line **110**.

On the committed tree this never shows, because the file is checked in.
Untracking it would make a clean clone fail its **first** run and pass its
second, which is the worst failure mode to diagnose. So that file **stays
tracked**, and it never churned anyway: zero changed lines across runs.

Whether to fix the ordering — have the consumer generate what it reads, or move
it after its producer — is **OPEN**. It is recorded here so that the next person
to see `results_gapclosure.json` in a churn list has the reason it is not there.

## 13b / 14b — §13 CLOSED; and closing it reopened §11 for one file

**§13 closed.** `reproduce_all.sh` went from **100 suites to 123**, and the
orphan count from **45 to 0** — re-running the coverage check (resolving every
pipeline target and its parent directories) reports none remaining. `plexus/` is
in, so the directory `CLAUDE.md` names as its enforcement layer is now actually
enforced by a full run.

Before wiring, every orphan was run rather than assumed green: Python **520
passed, 1 skipped, 0 failed**; Node all green except one.

**The frozen count and the air gap were the same defect.** `page-code/
test_blueprint.py` asserted `each_settles == 1/484` (= 1/22²) and the hub
`echo/echo.mjs`. Both had moved — to `1/676` (= 1/26²) and `spar/spar.py` —
and nobody saw it, *because the suite that rebuilds the artifact was air-gapped
from the pipeline*. Nothing regenerated it, so nothing noticed the numbers had
gone stale. Both are now derived at runtime: `each_settles == 1.0/claimed**2`,
and B4 asserts the claim (a hub exists, fan-in ≥ 5) plus internal consistency,
with the hub's identity recorded as a dated observation. Demonstrated, not
assumed: a probe module moved `claimed` 26 → 27 and `each_settles` → 1/729 and
the test still passed.

**One orphan was red and was NOT silenced.** `hinton_test.test.mjs` asserted the
literal verdict `Partially Grounded`; the script emits `Insufficient Evidence`.
Rather than update the test to match the code — which masks regressions — the
change was checked: PAGES bands *Hollow Assertion → Partially Grounded → Solid*,
and `Insufficient Evidence` is a separate **ABSTAIN** path. The engine gained
the ability to refuse to place a text with no methodology on the ladder at all.
That is a **tightening**, and it is this repository's own rule arriving in the
engine — *"nothing to check" is not a low score, it is no score*. The assertion
now states the claim, not the rung.

**§11 reopened for exactly one file, and that is the honest cost.**
`page-code/results_blueprint.json` was stable in git only because nothing ever
rebuilt it. Wiring `page-code/` in means the pipeline now regenerates it every
run, and every field in it counts a live tree — `edges`, `files_in_graph`,
`files_isolated`, `claimed`, `the_one_origin` — exactly like `files_scanned`.
Measured by the same boundary used for the other eight: only `run_blueprint.py`
writes it, only `test_blueprint.py` reads it *after* rebuilding it, and deleting
it then running `page-code/` gives **28 passed** and the file back. **Build
output.** Untracked, listed by name.

**Final tally: 123/123, zero orphans.** The earlier "100/100 was true and
narrower than it reads" is retired — the number now counts every test file in
the repository.

## 15. H5 — RETIRED 2026-09-18: "real 39-hop telemetry"

### The retired claim

Root `README.md:38`, as it stood until 2026-09-18:

> *"Validated against real 39-hop telemetry (`lism-cohorts/appendix/
> cohort_D_decay.csv`, fidelity 0.84 → 0.01)."*

### The evidence that retired it

`lism-cohorts/meta_lism.py:102` — `def cohort_D_swarm(seed=20260719, N=500)`,
over `random.Random(seed)`. Cohort D is a **seeded simulation**. There are no
observed handoff logs in this repository and none are reachable from this
container.

### The part that matters more than the line itself

**The repository already knew, in a locked pre-registration**, and the front
door said the opposite anyway. `text-channel/PREREG.md`:

> *"Cohort D is the sharpest case. It is a seeded simulation that reproduces
> itself. The repository's own audit says in terms: 'a seeded simulation
> reproducing itself is a code-correctness check, not empirical support for the
> law.' Presenting its 39-hop fidelity decay as evidence about real agent swarms
> would repeat exactly the error that the N=793 retraction was issued for."*

And `cohort-audit/cohort_audit.py:198` carries that sentence verbatim. So the
correct analysis was locked, hashed and shipped — while `README.md`, the file a
reader meets first, made the claim it forbids. **A prohibition in a locked file
does not propagate to the surfaces that never read it.** That is the same shape
as §13: the knowledge existed and nothing carried it to where it was needed.

### The replacement, and every surface it touched

> *"Validated against a seeded 500-agent, 39-hop simulation (`cohort_D_swarm`,
> seed 20260719); no observed handoff logs exist in this repository."*

The claim family — `real` / `observed` / `production` / `live` applied to
Cohort D or the 39-hop decay — was grepped across every surface and retired in
one commit, not just at the line that was found first:

| surface | was | now |
|---|---|---|
| `README.md:38` | "real 39-hop telemetry" | seeded simulation, seed named |
| `physics-agency/lmd/PROPOSAL_PACKAGE.md` ×2 | "from real 39-hop telemetry"; "on the real Cohort D profile" | "seeded" |
| `lism-cohorts/circuit_breaker.py` ×3 | "the repo's real Cohort D telemetry"; "REAL Cohort D profile" | "SEEDED … simulation", seed named |
| `lism-cohorts/test_circuit_breaker.py` ×2 | docstring + `test_matches_real_cohort_d_…` | `test_matches_seeded_cohort_d_…` |
| `lism-cohorts/meta_lism.py`, `lism-cohorts/README.md` | "live re-simulation" | "seeded simulation, re-run here (not observed)" |
| `cohort-audit/cohort_audit.py:289` | `REAL_REPRODUCIBLE` for `D_digital_swarm` | `SIMULATED_REPRODUCIBLE (seeded; code-correctness, not empirical support)` |
| `cohort-audit/test_cohort_audit.py:103` | pinned `REAL_REPRODUCIBLE` | pinned `SIMULATED_REPRODUCIBLE` |

`REAL_REPRODUCIBLE` was a vocabulary collision rather than a lie — it meant
*offline-reproducible*, not *real-world* — but on a seeded cohort it reads as the
claim being retired, and a label that has to be explained is not a label. The
precedent was already in the same dictionary: cohort C carries
`"SIMULATION (retracted as real-world, PR #111)"`.

### Vocabulary amendment: `simulated` is now a tag

Provenance tags are `measured`, `identity`, `simulated`, `external-claimed`,
`design`. **`simulated` was the missing one, and its absence is what let the
overclaim survive**: with only *measured* and *external-claimed* available, a
seeded cohort had nowhere correct to sit and drifted to the nearest label.

- Everything generated by a `cohort_*` seeded routine carries **`simulated`**.
- The 22-repo GitHub fixture stays **`measured`**: scraped real-world data, in
  repo, hashed `020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`.
- `simulated` and `measured` are different tags because they answer different
  questions. Neither is a grade.

## 16. The 2026 incident — `external-claimed`, primary sources UNREAD

"Verified" is dropped from every repository surface; `DOOR2_STATUS.md` now reads
*"externally-reported facts … (primary sources unread)"*.

The first-party disclosures below were **corroborated out-of-repo on 2026-09-17**
by a reader with network access. **This repository has never fetched them** —
all three were egress-blocked from this container, and nothing in this repo has
parsed a byte of them:

- `https://openai.com/index/hugging-face-incident-and-the-road-ahead/`
- `https://huggingface.co/blog/security-incident-july-2026`
- `https://huggingface.co/blog/agent-intrusion-technical-timeline`

**Per-hop payload availability remains UNCONFIRMED**, which is the only question
Door 2 turns on. Until a named reader records an answer, the incident is cited
as topology reported by others, with **no motive attribution to any agent,
organisation or person**, and every swarm number in this repository stays
synthetic.
