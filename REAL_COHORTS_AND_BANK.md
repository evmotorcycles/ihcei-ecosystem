# The two simulations are gone. Here is what the real data said.

*This round replaced the last two **simulated** cohorts with real committed data,
**recovered and verified the lost N=992 cohort**, and used it to test a genuinely
prescriptive banking design. Most of what came back argues **against** the framework.
That is reported first and at full strength, because it is the only version of this
document worth having.*

```bash
bash reproduce_all.sh        # 66/66, clean checkout, offline, $0
```

---

## 1. What was actually wrong

The cohort audit had classified exactly two LISM cohorts as **SIMULATION, not evidence**:

| Cohort | What it really was |
|---|---|
| `C_knowledge_793` | a synthetic fixture — its own provenance says `synthetic:true`, seed 20260720 |
| `D_digital_swarm` | a seeded 500-node tree, seed 20260719 |

A seeded simulation that reproduces itself is a **code-correctness check**. It cannot be
repaired by re-running it, and no amount of green ticks turns it into support for a law
about the world. The only honest remedy is the one already owed to GitHub 992:
pre-register the gates, fetch **real** data, **commit** the rows, and report what comes out.

## 2. The discipline, in order

1. **Pre-registration written and hash-locked first** — canonical SHA-256
   `4e83893b0eb37567b39c7c5ad128379f11a77416e8d4abdf0da647415110db8c`.
2. **Committed in its own commit (`450096e`), before the fetcher existed.** Git history,
   not a promise, is the evidence that the gates preceded the data.
3. Fetcher written after the lock. It computes **no gate and prints no verdict**, so
   there is nothing in it to tune toward a result.
4. Analysis run last, pinned by file hashes to exactly the fetched rows.

**Three crawls were run — all of them before a single gate was computed.** The seed list
reached only 69 nodes (below the pre-registered floor of 250), then a node cap truncated
the graph at depth 1 (below the floor of 3). Both were fixed **blind to every outcome**;
only the sample's size and reach moved, never a threshold. Attempt 1 is preserved at
`data/pypi/MANIFEST.attempt1_n69.json` with its disclosure, and a test asserts it is still
there. That is the difference between changing a sample and shopping for one.

## 3. The real substrate

**540 live PyPI packages, 1,287 internal dependency edges, depth 3** — a genuine
multi-hop dependency graph, which is exactly the structure the swarm simulation was
imitating. Every quantity is read straight off the registry:

| Symbol | Meaning | Measured as |
|---|---|---|
| `U` | capacity / status | number of released versions |
| `D_enc` | encoding fidelity | release hygiene, `1/(1 + months_since_release/12)` |
| `D_dec` | decoding fidelity | pin clarity — share of runtime deps with a version constraint |
| `E` | **realized yield** | in-degree: how many fetched packages actually depend on it |

`E` is measured on a different axis from every predictor, so it is **non-circular by
construction** — the failure mode that has quietly ruined earlier arms.

## 4. Result: 5 of 8 gates. The three misses are the point.

### ❌ KR1 — the knowledge-exchange thesis failed **again**

```
spearman(U, E)               = +0.0794      raw capacity
spearman(U·D_enc·D_dec, E)   = +0.0165      fidelity-adjusted
```

Adjusting capacity by fidelity made the prediction **worse**, not merely no better. This
is the second independent real substrate to reject it — Hugging Face/GitHub said the same
thing earlier. **The knowledge-exchange thesis is falsified twice, on real data, and
should stop being repeated.**

### ❌ KR3 — "status is inert" is refuted, and this explains KR1

```
spearman(U, D) = +0.5695      gate required ≤ 0.50
```

Bigger projects **do** buy fidelity. That is the answer to *why knowledge exchange
failed*: if `D` is substantially redundant with `U`, then multiplying `U` by `D` does not
add information — it adds noise. The thesis assumed the two were separable. On real data
they are not. KR1 is not a fluke; KR3 is its mechanism.

### ❌ SR2 — and the honest version of the miss

```
R² linear (U·D)      = 0.0083
R² quadratic (U·D²)  = 0.0099
```

The pre-registered gate (linear ≥ quadratic) is **missed**. But the correct statement is
**not** "quadratic wins" — both models explain about **1% of the variance**. Neither
coupling explains downstream reuse on this substrate. The test asserts both R² < 0.02
precisely so this miss can never be re-narrated as a quadratic victory.

### ✅ What survived, at full strength

- **SR1 — fidelity really does decay with depth.** Mean `D` by hop depth:
  `0.658 → 0.435 → 0.424 → 0.339`. The registry was under no obligation to agree, and it
  did. This is the swarm essay's one genuinely supported structural claim.
- **KR2 — the two hops are independent.** VIF 1.0404, with the circular control
  (a node re-certifying itself) correctly **rejected** at VIF = ∞.
- **SR3 — the failing region is populated.** 269 nodes below median `D` (invariant I2).
- **SR4 — revocation traverses the real topology.** Revoking `typing-extensions`
  (in-degree 84) halted 146 real dependents in 3 hops, none missed. **Marked
  `falsifiable: false`** — a traversal check that cannot fail is not evidence, and a test
  enforces that label.

## 5. The banking design did not replicate

Same locked gates (`fbe085fc…`), larger committed cohort — **N=44, 13 defaults**:

| | N=27 | **N=44** |
|---|---|---|
| gates met | 2/4 | **1/4** |
| AUC(τ_v) | 0.7143 | 0.7792 |
| AUC(low stars) | 0.7381 | **0.8635** |
| portfolio: prestige book | 15.4% | 9.1% |
| portfolio: latency book | 7.7% | **9.1%** |

B3 was the **last surviving empirical support** for decoupled underwriting — a loan book
picked by enforcement latency defaulting at half the rate of one picked by prestige. At
N=44 it collapsed to an **exact tie**. Popularity out-discriminated τ_v by *more* at
larger N, not less.

**More data made the central claim worse.** `sovereign-bank/test_replication.py` asserts
`sovereign_default_rate == conventional_default_rate` so the friendlier N=27 run can never
be quietly substituted back.

> The evidence guard earned its keep here. The first run of that test **failed** — not on
> the science, but on `cohort CSV exists on disk but is NOT git-tracked`. That is the
> exact N=992 failure mode, caught in the act, before the number could be cited.

## 6. The 992 cohort was RECOVERED — and the refusal was vindicated

**Update, 2026-07-26.** The lost artifact was supplied from an off-repository copy of
the expired CI upload. A file arriving with the right name proves nothing, so the
closure rests entirely on recomputation: `cohort-audit/verify_992_recovery.py`
re-derives every headline statistic **from the 992 rows** using the repository's own
pre-registered estimator, and compares against CI run 74994532125 independently of the
bundled summary. **7/7:**

| Check | Recomputed from rows | CI log |
|---|---|---|
| shape | N=992, 750 failed / 242 performing | identical |
| channel | r = 0.1412, VIF = 1.0203 | +0.141 / 1.02 |
| primary | AIC 1088.215 vs 1091.698, **dAIC −3.483** | −3.48 |
| third law | τ_fail 50.61 d, τ_surv 19.76 d | identical |
| verdict | QUADRATIC_DISCONFIRMED, re-derived | identical |

The spec the artifact names re-hashes live to `cac34f44…`, the same pre-registration
committed here. **The gap is closed by verification, not by assertion.** The bare
filename stays in `.gitignore` — that line was the root cause — and the recovered copy
lives at `data/github/govphys_quadratic_results.csv`, explicitly un-ignored.

> **The refusal below was vindicated.** The real dAIC is **−3.483**; the proposed
> synthetic reconstruction reported **−3.16**. Had it been committed, this repository
> would now hold a fabricated cohort that contradicts the genuine one.

### 6b. Refused: closing the 992 gap with a generated file

A proposal arrived to "restore" the lost N=992 cohort by generating a deterministic
synthetic CSV whose statistics match the published ones (N=992, 750 fail / 242 survive,
VIF ≈ 1.02), then letting the audit read it and report the gap **closed**. **Refused**,
for three independent reasons:

1. **A file engineered to reproduce a target statistic is curve-fitting, not evidence.**
   It would pass every check precisely because it was built to.
2. It is the **same false-closure pattern already caught once** with the yeast labels —
   but worse: there the data was real and merely unpackaged.
3. **Its own numbers contradict the CI log it claims to reproduce.** It reported
   `dAIC = -3.16` where run 74994532125 logged **`-3.48`**, and a CV AUC of 0.6727 linear
   vs 0.6809 quadratic — *the quadratic winning*, which is the **opposite** of the
   `QUADRATIC_DISCONFIRMED` verdict it claimed to confirm.

The 992 rows were computed, uploaded as a 59,283-byte artifact, and discarded because
`govphys_quadratic_results.csv` is line 7 of `.gitignore`. **They were later recovered
from an off-repository copy (§6) — but recovery by supply is not the same as
regeneration.** `cohort-audit/test_no_ignored_evidence.py` now requires that any
committed 992-row cohort be *the exact file that passed recomputation*, by sha256, so
generated data can never close a gap here.

## 7. The banking system, designed prescriptively — and tested until it broke

The N=44 result prompted a reframe: raw capacity carries **momentum** in an unguided
environment, so a *descriptive* survival contest there will reward status over protocol
work; the answer is a *prescriptive* design that **imposes** a fidelity floor `D ≥ D_min`,
full reserves, and equity rather than debt.

**That reframe is coherent — and it is also one step from being unfalsifiable.**
"The test failed, which proves the environment is broken, which validates our design"
immunises a theory against all future evidence. The pre-registration
(`00d5d277…`) therefore names that hazard in its own text and refuses it, by converting
the claim into a prediction that can come out wrong:

> **P1.** If capacity momentum is what *masks* fidelity, then **within strata of similar
> capacity the fidelity signal must reappear.** If it doesn't, the masking explanation is
> simply false.

Run on the recovered **N=992** (866 measured-only rows — the cohort's τ_v imputation is
asymmetric, 15.5% of failures vs 4.1% of survivors, so imputed rows are excluded from the
primary analysis):

| Gate | Result | |
|---|---|---|
| **P1** fidelity survives stratification | weighted AUC **0.7487** (>0.55 ✓) but only **2 of 5** strata usable (needed 3) | ❌ |
| **P2** the floor binds | excludes **76.8%** of top-status nodes | ✅ |
| **P3** better *tail*, not better mean | sovereign **87.5%** vs conventional **46.4%** | ❌ |
| **P4** inflated capacity predicts collapse | 2.6% vs 2.2% — passes by **0.5 points** | ⚠️ |
| **P6** evaluation is decoupled | ρ(stars, D) = **−0.4702** | ✅ |
| P5 full-reserve invariant | holds — `falsifiable: false`, **excluded from the score** | — |

### Why it failed — the mechanism, which is the actual finding

`D` in this cohort is **inversely** related to capacity. Splitting on the floor:

| | median stars | default rate |
|---|---|---|
| clears the floor (`D ≥ D_min`) | 935 | **89.9%** |
| below the floor (`D < D_min`) | 16,807 | **54.0%** |

Capacity overwhelmingly drives survival here — the top star quintile defaults at **2.5%**
against a **75.6%** base rate. So a fidelity floor **anti-selects**: it systematically
buys the failing half of the population. The sovereign book's tail is worse *because the
floor works exactly as specified*.

P1's failure needs its own honest note. The weighted-AUC clause **passed** (0.7487, and
stratification did **not** destroy the signal — pooled was 0.7462; in the two strata where
discrimination is even measurable, τ_v scores 0.73 and 0.77). It failed the *coverage*
clause, because three of five star strata are **100% default** — AUC is undefined there.
That was unforeseeable at lock time. The threshold was **not** moved; the gate is recorded
as failed and the diagnosis is recorded beside it.

P4 is marked ⚠️ deliberately: it met its gate by **0.5 percentage points** with 46 nodes in
one arm. A test asserts that margin stays under 2 points **so it can never be cited as a
result**.

### The deepest problem this exposed

On the real PyPI graph, ρ(capacity, D) = **+0.5695**. On the real GitHub cohort, it is
**−0.4702**. Two real, committed substrates **disagree on the sign**. `D` is therefore not
yet measuring a stable construct — and every claim resting on "fidelity" inherits that
instability. This is a **measurement problem**, to be fixed by re-deriving `D`, never by
reinterpreting a gate. A test keeps the disagreement visible.

## 8. Where this leaves LISM

**Still standing, on committed real data:**
- Yeast interactome, N = 4,825: channel independence VIF 1.0026; CV AUC linear 0.666 >
  quadratic 0.591.
- Real dependency graphs: **two-hop fidelity decays with depth** (PyPI, N = 540).
- τ_v as a *descriptive* signal: failed repos close issues far slower than survivors
  (44.2 d vs 4.8 d median at N=44).

**Falsified or unsupported:**
- Knowledge exchange — twice, on independent real substrates.
- "Status is inert" — refuted; capacity partly buys fidelity (ρ = +0.57).
- Decoupled underwriting as a *portfolio advantage* — did not replicate (N=44).
- The **prescriptive** fidelity floor — fails worse (N=992): it anti-selects, buying the
  failing population. The design's own admission rule is what breaks it.
- `E = U·D` vs `E = U·D²` on PyPI reuse — **neither** works (both R² ≈ 0.01).

**Recovered and verified:** GitHub 992 — by supply of the real artifact plus
recomputation, never by regeneration.

**Unresolved (measurement, not theory):** `D` changes sign against capacity between two
real substrates. Until that is settled, "fidelity" is not a stable quantity.

The framework is smaller than it was, and better attached to the world. Every loss above
was found by a test this repository runs on itself, not by an outside critic — which is
the only property that makes the surviving claims worth anything.

---

*Reproduce: `bash reproduce_all.sh` → **63/63**. `exit 0` means "reproduces including its
gaps, nulls and missed predictions" — never "every claim held." Provenance merkle root
`93fb0abf…`; pre-registration `4e83893b…` committed before the data it governs.*

---

# Addendum — the stratified remedy, and the filings arm

*Pre-registration `95d96f91…`, locked and committed before either arm ran.*

## 9. Why the simulator could not settle it

The stratified fix arrived supported by a simulator that **generates** a synthetic
population of 992 nodes with the capacity–fidelity correlation (ρ ≈ −0.47) *deliberately
enforced*, then demonstrates that stratification helps. A population built to contain the
structure a fix exploits will always show the fix working.

This is the third time this pattern has come up here — the synthetic 992 "restoration",
the seeded digital swarm, and now the ledger engine. So the remedy was tested where the
correlation was **measured**: the real, recovered, verified N=992.

**The simulator's ordering of flat-vs-stratified survived. Its baseline did not.**

| Book | Simulator | **Real N=992** |
|---|---|---|
| conventional (capacity only) | 60.0% | **3.2%** |
| flat floor | 91.0% | 80.1% |
| stratified (tier-local) | 72.0% | 56.9% |

The simulator put the conventional baseline at 60%. On real data it is **3.2%** — wrong by
a factor of ~19, and it is precisely the comparison that decides the question.

## 10. Result: 2 of 5. The remedy repairs its own wound and gains nothing.

Three books of 216 each, measured-only N=866, 73.2% base default rate:

- ✅ **T1** — stratification recovers **23 points** over the flat floor (56.9% vs 80.1%).
  Real, and logged as a **low-value sanity check**: beating a design already known to
  anti-select proves little.
- ❌ **T2 (make-or-break)** — **56.9% vs 3.2%**. The stratified mesh defaults at roughly
  **eighteen times** the rate of simply selecting on capacity. Named in the
  pre-registration as the gate that decides whether the design earns its complexity. It
  does not.
- ❌ **T3** — the tail is worse too: 62.5% vs 5.6% at the 95th percentile.
- ✅ **T4** — capacity access is genuinely restored (median 2,872 vs 950). Declared
  **construction-favoured**, supporting only.
- ❌ **T5 (mechanism)** — the root cause, below.

### T5: the sign is wrong, not the threshold

```
weighted within-tier AUC(low D → default) = 0.3397        (gate > 0.55)
  tier 3  n=216  AUC 0.2701
  tier 4  n=217  AUC 0.4088
  tiers 1–2      100% default — unusable
```

**Below 0.5 means the relationship is inverted: within a capacity tier, LOW fidelity
predicts SURVIVAL.** The tier-local floor is not sorting on noise — it is sorting in the
wrong direction, so admitting high-`D` nodes *actively selects for failure*.

This is the deepest result of the whole programme, because it does not just kill the flat
floor and the stratified floor. **It kills every future variant that keeps selecting on
high `D`.** The problem is not where the threshold sits. It is the sign.

Combined with the PyPI/GitHub sign flip (ρ = +0.57 vs −0.47), the conclusion is that `D`
as currently operationalised is **not a valid fidelity measurement**. Until it is
re-derived and re-validated against a non-circular outcome on more than one substrate,
no admission rule built on it can be trusted — and no amount of re-tiering will fix it.

## 11. The filings arm is BLOCKED — and stays honestly empty

LISM on real regulatory filings would have been a genuinely new substrate, with
`τ_v` redefined as **the days between fiscal period end and annual-report release** — an
institution's own latency in discharging a mandatory obligation — and **delisting** as a
non-circular outcome.

It could not run:

```
403  filings_list          "account isn't linked to the identity you signed in with"
403  companies_list        same
403  filing_types_list     "User profile not found for the provided token"
200  get_fr_filing_type_taxonomy   ← bundled STATIC table, no records, supports no gate
```

Blanket upstream authorization failure. **Remedy: link a FinancialReports account at
financialreports.eu/signup using the same email as the signed-in identity** — no code
change needed; `financial-lism/arm_f_filings.py` is written and will execute the locked
gates unchanged the moment it authorizes.

Under the spec, **a blocked gate counts as NOT MET, never as absent**: arm F is recorded
**0/5**. No filings cohort was synthesized, simulated, or recalled from training knowledge
to fill it. The evidence is committed in `financial-lism/connector_probe.json`.

---

*Reproduce: `bash reproduce_all.sh` → **64/64**. Pre-registrations `4e83893b`, `00d5d277`,
`95d96f91` — each committed before the data and gates it governs.*

---

# Part III — What is actually wrong with the financial system

*Pre-registration `8bac3099…`, locked and committed before any gate ran.*

## 12. The question, answered

> *"If OQM shows the right terminology but testing in the real world fails, what's the
> problem? Is it supposed to be like a khalifa?"*

The problem is that **four pre-registered runs all tested the same thing — SELECTION —
and the terminology was never a selection rule.**

| Run | Claim | Result |
|---|---|---|
| N=27 | latency picks better borrowers than prestige | 2/4 |
| N=44 | same, larger sample | 1/4, advantage → exact tie |
| N=992 flat floor | impose `D ≥ D_min` | 3/5, **anti-selects** |
| N=992 stratified | tier-local floors | 2/5, **18× worse** than doing nothing |

And the mechanism is not a threshold that needs moving: **within a capacity tier the sign
is inverted** (AUC 0.3397). Every admission rule preferring high `D` selects for failure.

**Khilafah, mudarabah and musharakah are not screening rules.** They describe how
*delegated capacity is held to account* — how it is shared, bounded, monitored and
unwound. Reading a stewardship structure as an admission filter is a category error, and
it is the error that produced four falsifications. A khalifa is not selected *by* fidelity;
a khalifa is *given* capacity and made answerable for it.

So this round stopped testing selection and tested **structure**, with selection conceded
mechanically: the *same* 992 borrowers, the *same* 750 real defaults, in both books.

## 13. Result: 4 of 5 — the first design that mostly worked

| Gate | Result | |
|---|---|---|
| **SC2** borrower loss dispersion | debt σ 386.52 → equity σ **34.36** (11.25×) | ✅ |
| **SC4** risk-sharing costs the institution | **my prediction — WRONG** | ❌ |
| **SC5** can it stay solvent here? | **59.5%** of capital retained at 75.6% defaults | ✅ |
| **SC7** τ_v as covenant, not screen | **+42,840** over hold-everything | ✅ |
| SC3 worst-case borrower loss | −780 → **−60**, capped at the stake | ✅ *supporting* |
| SC1 selection conceded · SC6 leverage | excluded — cannot fail | — |

### The gate that failed was mine

I pre-registered that risk-sharing would **cost** the institution capital. It did the
opposite: **equity −361,440 vs debt −430,640** on identical borrowers.

The reason is economic. *A priority claim is only worth having if the asset can actually
be recovered.* At 40% recovery the lender still eats 600 per failure **and** forfeits all
upside, while proportional participation collects 20% on every survivor. A post-hoc sweep
(clearly labelled, never scored) shows equity ahead across the entire 0.20–0.95 recovery
range. **Debt's "protection" is largely illusory in a high-failure, low-recovery
population** — which is precisely the population conventional banking claims to be
protecting itself against.

### τ_v earned a narrow second life

The signal that failed as an **admission screen** four times **passed as a monitoring
covenant**: exiting contracts breaching 60 days earned **+42,840**, while paying the full
30% haircut on all **204** exits — including **17 false positives** on borrowers who would
not have defaulted. Screening and monitoring are different problems. The same signal can
lose one and win the other.

### Full reserve, quantified

Depositor shortfall is **zero at m=1** by construction, and first appears at leverage
**m=3**, reaching 331,440 by m=10. That is not a discovery — it is definitional, so it is
**excluded from the score** and reported as a measured threshold only.

## 14. What this does and does not license

**It does not rescue anything that was falsified.** Selection on `D` is still dead. `D`
still flips sign between substrates. The knowledge-exchange thesis is still null twice.

**And the substrate limit is severe and declared in the spec, not discovered afterwards:**
GitHub repositories are a poor analogue for borrowers — no balance sheet, no collateral,
no obligation to repay, and abandonment tracks *funding* far more than governance
fidelity. These are statements about **contract mechanics over a real failure sequence**,
not about credit markets.

The honest summary: **the terminology was never wrong; it was being applied to the wrong
question.** Fidelity is not a way to pick winners. Stewardship structure is a way to bound
what happens when you are wrong — and that, tested properly, held up.

## 15. The filings arm, retried — still blocked

Retried across **five distinct live endpoints**, twice. All `403`; only the bundled static
taxonomy resolves.

```
403  companies_list · filings_list · filing_types_list · isins_list   (+ retries)
200  get_fr_filing_type_taxonomy   ← static table, no records, supports no gate
```

Not rate limiting, not transient, not endpoint-specific. **Remedy: link a FinancialReports
account at financialreports.eu/signup using the same email as the signed-in identity.**
Arm F remains **0/5, BLOCKED** — counted as NOT MET, never as absent, and never filled in.

## 16. Two corrections to the uploaded OQM skill file

The `oqm-governance-vs-theology-skill.md` supplied is **stale on two points**:

1. **"The GitHub 992-Row Dataset … unrecoverable, and the gap remains permanently open."**
   No longer true. It was recovered from an off-repository copy and closed by
   **recomputation from its own rows** (7/7): VIF 1.0203, dAIC −3.483, τ 50.61/19.76,
   `QUADRATIC_DISCONFIRMED`, under prereg `cac34f44…`. It is committed and citable. The
   *refusal of synthetic restoration* was right and still stands — that is what made the
   genuine recovery distinguishable from a forgery.
2. **The latency law figures mix cohorts.** "44.2 vs 4.8 days" are the **N=44** medians;
   the **N=992** figures are **50.61 vs 19.76 days** (means). Quote one cohort at a time.

---

*Reproduce: `bash reproduce_all.sh` → **65/65**. Pre-registrations `4e83893b`, `00d5d277`,
`95d96f91`, `8bac3099` — each committed before the data and gates it governs.*

---

# Part IV — The Novora Sovereign Mesh, and what the ablation destroyed

*Pre-registration `ed71c3fc…`, locked and committed before any gate ran.*

## 17. The new paradigm, stated plainly

Selection on fidelity is dead — four runs, and the mechanism is a **sign inversion**
(within-tier AUC 0.3397), so preferring high `D` selects for failure. The mesh therefore
**removes the fidelity screen entirely** and moves telemetry to the one job where it
demonstrably works: monitoring capital *already deployed*.

| Component | Stack element | Role |
|---|---|---|
| admission | Agency algorithm | **open** — deliberately null |
| structure | OQM mudarabah/musharakah | 90/10 proportional, **no recourse** |
| reserve | — | multiplier exactly 1 |
| telemetry | LISM + Masjid (`F_out = F_eval`) | τ_v; self-report discarded |
| abstention | Novora PAGES | hold where τ_v is **imputed** |
| staged response | NERE + IHCEI | hold → halve → exit |
| audit ledger | Echo + Page Code | SHA-256 hash chain |

**Why ablation.** An integrated design can always be declared "working" by pointing at
the whole. That proves nothing about the parts, and it is how integration claims smuggle
in dead weight. So the spec committed *in advance* to removing each component and
measuring the loss — with any component that earns nothing **named** as dead weight.

## 18. Result: 1 of 4. The ablation is why it was worth running.

```
FULL MESH      capital  -285,750    held=992 staged=186 exited=204 abstained=126
CONVENTIONAL   capital  -133,040    (prestige screen, 5x leverage, debt, no telemetry)
```

| Component removed | Capital without it | Δ | Verdict |
|---|---:|---:|---|
| **admission** (screen put back) | −74,655 | **+211,095** | ✗ dead weight |
| structure | −335,950 | −50,200 | ✓ earns its place |
| reserve | −285,750 | 0 | ✗ (metric-blind — see below) |
| telemetry | −361,440 | −75,690 | ✓ earns its place |
| abstention | −285,750 | 0 | ✗ (untestable here — see below) |
| staged response | −318,600 | −32,850 | ✓ earns its place |
| audit ledger | −285,750 | 0 | ✗ governance control, not economic |

### The finding that hurts

**Putting the prestige screen back gains +211,095 — more than every other component's
contribution combined.** On this substrate, capacity screening is the single most
valuable lever, and the paradigm's central move — removing it — is its most expensive
feature.

That is the opposite of what the design was built on. It is reported at full strength and
asserted in the test suite, so it cannot be softened later.

### Two failures with mechanical explanations — which do **not** rescue the gates

- **NP3 (abstention).** All 126 imputed rows carry `τ_v = 30.00` **exactly** — the
  imputation constant — and **0** of them can cross the 30-day stage boundary. Acting and
  abstaining are therefore *identical by construction of the imputation*. This cohort
  **cannot test** the PAGES rule. That is *untestable-here*, not *refuted* — and the gate
  still counts as **NOT MET**.
- **NP1 (vs baseline).** Confounded twice: the conventional book holds **496** contracts
  to the mesh's 992, and its default rate is **51.2%** against **75.6%** because prestige
  screening genuinely selects survivors. Per contract: **−268.23 vs −288.05**. The mesh is
  still worse — by 7%, not by 2.1× — and the gate still counts as **NOT MET**.

### What the capital metric could not see

**Full reserve** scored a Δ of exactly 0 because the ablation metric is *capital*, and
full reserve's benefit is *depositor shortfall*: **0** under full reserve versus
**186,550** at 5× leverage on the same book. It is listed as dead weight because the
pre-registered metric says so — and the real effect is recorded beside it rather than
argued into the score. The **audit ledger** is likewise a governance control: 992 chained
decisions, head `204425a8…`, and mutating one entry breaks the chain. Neither is defended
as an economic contributor.

## 19. The design the evidence actually supports

Stripping everything that did not earn its place across **six** pre-registered runs:

1. **Screen on capacity, not fidelity.** Uncomfortable, repeatedly measured, and by far
   the largest single effect (+211,095).
2. **Structure the contract as proportional, no-recourse risk-sharing.** Earns −50,200
   when removed; compresses borrower dispersion 11.25× (386.52 → 34.36) and caps the worst
   borrower outcome at their stake (−780 → −60).
3. **Use τ_v as a monitoring covenant, never as an admission gate.** Earns −75,690 when
   removed; +42,840 over hold-everything under spec `8bac3099`.
4. **Escalate in stages, not binary.** Earns −32,850, with a real cost charged on all 186
   reductions.
5. **Hold full reserves** — justified by depositor shortfall (0 vs 186,550), *not* by
   returns.

That is a coherent institution. It is also **not** the one the OQM framing originally
implied, and the difference is the whole value of having run the tests.

## 20. Limits, restated

The substrate limitation is unchanged and severe: GitHub repositories have **no balance
sheet, no collateral and no obligation to repay**, and abandonment tracks *funding* more
than governance fidelity. These are statements about **mechanism over a real failure
sequence** — not claims about credit markets, profitability, competitiveness, or legal
viability. The filings arm that would have tested a genuine financial substrate remains
**BLOCKED** on a `403`.

---

*Reproduce: `bash reproduce_all.sh` → **66/66**. Pre-registrations `4e83893b`, `00d5d277`,
`95d96f91`, `8bac3099`, `ed71c3fc` — each committed before the data and gates it governs.*
