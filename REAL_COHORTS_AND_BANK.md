# The two simulations are gone. Here is what the real data said.

*This round did three things: replaced the last two **simulated** cohorts with a real,
committed dataset; replicated the banking design on a larger sample; and refused a
proposal to "restore" the lost N=992 cohort with a generated file. Two of the three
produced results **against** the framework. Those are reported first and at full
strength, because that is the only version of this document worth having.*

```bash
bash reproduce_all.sh        # 61/61, clean checkout, offline, $0
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

## 6. Refused: closing the 992 gap with a generated file

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
`govphys_quadratic_results.csv` is line 7 of `.gitignore`. The run now 404s and the
artifact has expired. **They are unrecoverable. The gap stays open.**
`cohort-audit/test_no_ignored_evidence.py` now fails loudly if any 992-row file appears
while the gap is still declared.

## 7. Where this leaves LISM

**Still standing, on committed real data:**
- Yeast interactome, N = 4,825: channel independence VIF 1.0026; CV AUC linear 0.666 >
  quadratic 0.591.
- Real dependency graphs: **two-hop fidelity decays with depth** (PyPI, N = 540).
- τ_v as a *descriptive* signal: failed repos close issues far slower than survivors
  (44.2 d vs 4.8 d median at N=44).

**Falsified or unsupported:**
- Knowledge exchange — twice, on independent real substrates.
- "Status is inert" — refuted; capacity partly buys fidelity (ρ = +0.57).
- Decoupled underwriting as a *portfolio advantage* — did not replicate.
- `E = U·D` vs `E = U·D²` on PyPI reuse — **neither** works (both R² ≈ 0.01).

**Unrecoverable:** GitHub 992.

The framework is smaller than it was, and better attached to the world. Every loss above
was found by a test this repository runs on itself, not by an outside critic — which is
the only property that makes the surviving claims worth anything.

---

*Reproduce: `bash reproduce_all.sh` → **61/61**. `exit 0` means "reproduces including its
gaps, nulls and missed predictions" — never "every claim held." Provenance merkle root
`93fb0abf…`; pre-registration `4e83893b…` committed before the data it governs.*
