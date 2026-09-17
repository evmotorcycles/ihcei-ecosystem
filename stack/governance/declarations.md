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

- **Module:** `stack/swarm/lism_sentry.py` — not built in this patch.
- **Law:** `E = U * prod(D_k)` — a fidelity product. **Not thermodynamic
  entropy**, and the word is not to appear in the module.
- **Floor:** `min_E` is a **required argument**; prefer the ratio-of-`U` form in
  unit tests.

## 4. Audit / LINTEL

- Foster total `= n - k` is a **harness invariant only**. It is conserved under
  every rewrite measured so far — `lmd-scaling/`, `jepa-probe/`, `lintel/` — and
  a quantity true of every drawing prefers none of them. It does not gate health.
- Certificates must name their **invariance group**. Measured so far:
  - rewrites of the drawing (shims, splits, merges) — names survive **27/27**
  - what the drawing omits (candidate undeclared edges) — names survive **18/27**
- Gates compose as **OR** only.

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
