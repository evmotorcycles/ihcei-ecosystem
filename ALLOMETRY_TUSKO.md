# The Tusko test: scaling laws for enforcement latency

**Spec** `6666f1a958139c6b661b6df61b42c5c2863d4bd7001ab60aa6599b03d8c32710` · locked before
any extrapolation was run · **3/5**

```bash
python3 -m pytest -q allometry/test_allometry.py
```

---

## First: two of the three arms you asked for are blocked

I couldn't get Hugging Face. Not "couldn't find good data" — the network refuses:

```
huggingface.co:443              403 to CONNECT (policy denial)
datasets-server.huggingface.co  403 to CONNECT
genomics.senescence.info:443    403 to CONNECT      ← AnAge, the mammal allometry database
```

GitHub is worse than it looks. `api.github.com/rate_limit` answers 200 at 15,000/hour, but
**every repository endpoint outside this session's scope answers 403** — so no new repos
could be sampled. The capacity floor is 99 stars, not the 1 star the design asked for.

There *is* a frozen Hugging Face fixture in this repo: 24 models. **I didn't use it.** It's
a trending-sort snapshot, not capacity-stratified, and a scaling test on 24 trending models
would produce a number with no power to fail. Substituting it would have been the fake.

**BLOCKED is not REFUTED and not UNTESTABLE-HERE.** The data exists, the tests are well
posed, this session can't reach them. To unblock: allow-list `huggingface.co` and
`genomics.senescence.info` in the environment's egress policy.

## And one disclosure about my own procedure

While checking whether the GitHub cohort could support the test at all, I printed the
median τ_v per star decade. That sequence fixes the sign of the scaling exponent — so I
already knew the answer to "which way does latency scale."

**So the exponent gate scores nothing.** It's reported without credit. The three gates that
*do* score depend on out-of-sample extrapolation error, cross-validated fold error, and
held-out invariance — none of which I computed or glimpsed before locking.

---

## What ran

866 real public GitHub repositories with **directly measured** issue-close latency.

| | |
|---|---|
| Stars | 99 → 442,738 (**3.65 orders of magnitude**) |
| Measured τ_v | 866 |
| Imputed τ_v — **excluded entirely** | 126 |
| Per star decade | 44 · 362 · 185 · 253 · 22 |
| Simulated quantities | **0** |

Imputed latencies are model outputs. They cannot test how latency scales, so they're gone.

Three models, calibrated on the small decades, extrapolated to the largest:

- **Linear** — `τ̂ = k·U`. Dose proportional to mass. *This is the rule that killed Tusko.*
- **Power** — `τ̂ = c·U^α`, α fitted log-log.
- **Constant** — `τ̂ = median(τ)`. Capacity ignored entirely.

---

## The primary gate passed. The reference arm reverses what it means.

```
                                                    error on the top decade
  linear rule (dose ∝ mass — the 1962 error)              4,406 ×
  power law fitted on the small end                          42 ×
  constant — assume nothing changes with scale              8.3 ×
```

**G3 PASSED**: linear/power ratio 2.24 against a locked bar of 2.0.

**But the constant model beats both.** The spec required that outcome to be stated first if
it occurred, and it occurred. Assuming big repositories behave exactly like small ones is
**five times more accurate** than extrapolating a power law fitted at small scale.

### Why — and this is the sharpest thing in the run

```
α fitted on the small decades alone     +0.3211
α fitted across all 866 rows            −0.1741
```

**The sign flips.**

At small scale, latency *appears to rise* with capacity. Across the full range it *falls*.

The 1962 error was using the wrong **exponent** — 1 instead of a fractional one. This is
worse: **the small-scale data supports the wrong direction.** A law fitted at small scale
isn't merely mis-scaled when extrapolated; it points the wrong way. That is exactly why the
power law errs 42-fold while assuming nothing changes errs 8-fold.

---

## The two gates that failed

### G4 — capacity doesn't predict latency at all

Five-fold cross-validation over all 866 repositories, seeded:

```
mean held-out error    power law   0.4728 dex
                       constant    0.4251 dex   ← lower
```

**The constant wins outright.** Once within-decade spread is accounted for, capacity carries
no usable predictive information about enforcement latency. The pre-registration named this
as the gate it would bet against, and it lost.

A fitted exponent on data like this is a decoration on noise.

### G5 — there is no "one billion heartbeats" for software

Fit α on the middle decades, apply to the two decades it never saw:

```
raw gap between decade 1e1 and 1e5          1.069 dex   (12-fold)
after normalising by the held-out exponent  0.592 dex   ( 4-fold)
locked bar                                  0.301 dex   ( 2-fold)
```

Normalising **did** flatten it — 12-fold down to 4-fold is real. It didn't flatten it to
invariance. The scale-invariant product that makes every mammal get roughly a billion
heartbeats **does not appear in this substrate at this range**. Reported without credit.

---

## The exponent, reported without credit

```
α over all 866 measured rows   −0.1741

median τ_v by star decade
  1e1   49.97 days
  1e2   35.30
  1e3   33.43
  1e4   10.74
  1e5    4.26
```

**α is negative: larger repositories close issues faster.** That inverts the naive reading of
the analogy, in which bigger systems are assumed slower and more sclerotic.

There is a biological parallel — Kleiber's law also gives a *rate* that falls with mass,
heart rate as `m^(−1/4)`. **That parallel is Layer 3, it is not evidence, and nothing here
is inferred from it.** A test asserts the results file makes no claim that software confirms
or obeys any biological law. Tusko and Kleiber generated the hypothesis and supplied the
vocabulary. They cannot confirm it.

---

## What this changes for LISM

LISM says `E = U · D_enc · D_dec` — linear in *fidelity*. It says nothing about how τ_v
scales with *capacity*, and now there's a measurement.

**The Tusko lesson survives, but not the form it was proposed in.** The proposed remedy for
naive linear extrapolation was a power law. On this substrate the power law is *also* bad —
just less catastrophically. The correct operational lesson is stronger and simpler:

> **A rule calibrated at one scale should not be extrapolated to another at all.**
> The linear rule is catastrophic. The power law is bad. Assuming nothing changes is merely
> poor — and it's the best of the three.

That has a direct governance reading. A supervisory threshold, a service-level target or an
enforcement deadline tuned on small institutions and scaled up by a size multiplier is the
Tusko error, and this data says the fix is not a better multiplier. It is to recalibrate at
the scale you are regulating.

## A confound this run exposed in earlier work

If τ_v falls with scale, then any τ_v-based comparison between groups that differ in scale is
partly a size comparison. The manuscript's headline τ_v result compares failed against
thriving repositories — and those strata differ by **a factor of ten in median stars**
(42,966 thriving vs 4,237 failed).

Restricting to a single star decade removes that by construction. Only the 10⁴ decade has
≥20 measured repositories in both strata:

| stratum, 10⁴-star decade | n | median τ_v |
|---|---|---|
| failed | 35 | 21.8 days |
| thriving | 218 | 8.0 days |

**The effect survives at 2.7×.** This check was **not pre-registered**, it rests on one
decade chosen because it is the only one that supports the comparison, and it is recorded in
the manuscript as post-hoc. A properly scale-stratified τ_v test has not been run.

## Disclosures carried in the results file

- **5 repositories sit at exactly 365.0 days** — a collection ceiling, not an observation —
  and **6 sit below 0.01 days**, almost certainly bot closure. **Both retained**, because the
  spec said so and dropping them after seeing results would be a threshold move. Sensitivity
  shown: α would be −0.1812 instead of −0.1741.
- **Stars are not a cause of latency.** Both plausibly follow from project maturity, funding
  and maintainer count, none of which are in this cohort. Every result is an association
  across scale, not a mechanism.
- **Nothing extrapolates below 99 stars or above 442,738.** The Tusko lesson applies to this
  result too.

## What would close the gaps

| Gap | What it needs |
|---|---|
| Capacity floor at 99 stars | GitHub API access beyond session scope, to sample 1–99 stars |
| AI model lineage arm | `huggingface.co` allow-listed; then ≥500 models stratified by downloads, not trending |
| Biological arm | `genomics.senescence.info` allow-listed — though this would reproduce Kleiber, not test software |
| SME ledger arm | Transaction-level loan ledgers with pass-through timestamps. Not public data; no supplied dataset contains them |

## Reproduce

```bash
python3 allometry/allometry.py
python3 -m pytest -q allometry/test_allometry.py
bash reproduce_all.sh
```

The cohort is hash-pinned and the runner aborts if the spec or the data changed. Exit 0
means **"reproduces including its failures"** — never "the scaling law is validated."
