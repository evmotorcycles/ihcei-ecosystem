# The two simulations are gone. Here is what the real data said.

*This round replaced the last two **simulated** cohorts with real committed data,
**recovered and verified the lost N=992 cohort**, and used it to test a genuinely
prescriptive banking design. Most of what came back argues **against** the framework.
That is reported first and at full strength, because it is the only version of this
document worth having.*

```bash
bash reproduce_all.sh        # 63/63, clean checkout, offline, $0
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
