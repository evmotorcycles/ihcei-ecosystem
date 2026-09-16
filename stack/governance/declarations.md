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

## 6. Blocked, and why — the organization module

`stack/organization/adg_tqg.py` is **not built in this patch**, and not for
engineering reasons.

The proposed signature is
`adg_score(U, salat, zakat, hbar, cohort_hash, eps)` with
`cfe_render(phi, kappa, quartile_bound, shirk, cohort_hash)`.

Three of those parameter names are religious-tradition vocabulary. This
repository's standing rule is that such terminology lives **only** in `ncu/` and
never in measurement code or in anything an ordinary person operates —
`LAYERS.md` and `test_layers.py` enforce the interface half of it. A public
scoring function that takes `salat` and `zakat` as arguments puts that
vocabulary into every traceback, every log line and every API signature that
touches it.

The rebrand to **ADG = Applied Governance** and **CFE = Cognitive Field
Equivalence** addresses the *acronyms*, which was the smaller half. The
parameter names are the larger half and are unchanged.

**This needs a decision before Patch 2**, and the decision is not mine to make
silently. The measurement is unaffected either way — `U · D / (eps + h)` with
`D = a · b` does not care what `a` and `b` are called.
