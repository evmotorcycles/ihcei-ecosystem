# DCM — the Discriminating Capacity Model

**Novora open-source initiative · model two**

**Spec** `3a33d53e178b9c6f9178a77fe9d2e60780eff74d63c5606878b8bf61f9947ffe` · locked before
any draw · **5/6**

```bash
python3 -m pytest -q dcm/test_dcm.py
```

> **Before you test a claim, measure whether your data could ever have answered it.**

---

## Why this model exists

LISM was model one. It asks what makes an institution stable: `E = U · D_enc · D_dec`, with
enforcement latency τ_v as a collapse indicator.

Across this programme's pre-registered runs, **the nulls outnumbered the passes.** And when
we lined them up, they shared a structure that had nothing to do with whether the mechanism
was real:

| Run | Score | What actually went wrong |
|---|---|---|
| Contract schedules `02e6bbba` | 3/6 | Property value: **min 400,000, max 400,000, sd 0.** No adverse event ever occurred |
| Outcome panels `caacef84` | 2/5 | Financier's balance fell **exactly −85.0% at every event** while the asset moved under 2% |
| IFSB panel `0d52c844` | 1/6 | Kuwait and Palestine booked **exactly zero** equity income across all 12 and all 21 quarters |
| Interbank network `db8c3a4f` | 3/5 | **No column in 74** distinguished a fixed claim from a participation |
| Allometry `6666f1a9` | 3/5 | A constant beat the fitted power law under cross-validation |
| Two-register `ed80430a` | 0/5 | Every gate missed |

**In none of these was a model shown to be wrong. The data was shown to be incapable.**

And sample size was never the problem. The outcome panels had **720 rows**. A power
calculation would have said that was plenty.

That gap — between "your claim is false" and "your data cannot see the difference" — is what
DCM measures.

---

## The model

For a dataset asked to adjudicate whether a grouping **G** changes an outcome **Y**:

```
Δ  =  V  ·  I  ·  C
```

| Factor | Definition | The failure it names |
|---|---|---|
| **V** — variation | `1 − modal fraction of Y` | *The outcome never moves.* The contract schedules' constant asset value |
| **I** — incidence | `4p(1−p)`, p = smaller group's share | *No populated failing region.* LISM invariant I2, made continuous |
| **C** — coupling | `distinct values of Y ÷ n` | *Administrative, not measured.* The flat −85%, the fixed 0.15 multiplier |

Each is one line of arithmetic with **no free parameter**. That's deliberate — a capacity
index with tunable weights could be fitted to any outcome and wouldn't be falsifiable.

**None of the three reads the association between G and Y.** They're functions of the
outcome's value distribution and the group sizes only. A test enforces this by scanning the
source.

### Why multiplicative

This was the model's substantive, falsifiable claim: **the three don't compensate.** An
enormous, perfectly balanced dataset whose outcome is a policy constant adjudicates nothing,
and no amount of the other two factors rescues it.

The form is inherited from LISM's own `D_enc · D_dec` — a chain fails at its weakest link.
**The form is inherited. No evidence is.** LISM's results are not evidence for DCM and
nothing in the run treats them as such.

### What DCM is not

**It is not a power calculation.** Power asks how many observations you need given an effect
size and a working measurement. DCM asks whether the measurement can express the effect *at
all*, which is prior to and independent of N.

---

## The test

**The risky prediction:** Δ, computed from a dataset's structure alone and *before* any
hypothesis is tested, predicts whether a test on that dataset will detect a relationship that
is genuinely present — and predicts it better than sample size does.

**Two real open-source substrates**, chosen because they are naturally opposite:

| | GitHub | PyPI |
|---|---|---|
| Rows | 866 repos, measured τ_v | 540 packages |
| Task | does survival status separate issue-close latency? | do widely-depended-on packages differ in pin clarity? |
| Distinct outcome values | **862 of 866** — naturally clean | **26 of 540**, 49% share one value — naturally degenerate |
| Mean C in draws | 0.999 | 0.125 |

Within one substrate V and C barely move — they're properties of how that substrate records
things. **Pooling a clean substrate with a degenerate one is what gives Δ a range to be
tested over.** A single-substrate test would have been circular.

**400 sub-datasets**, grid declared before any draw: n ∈ {20, 40, 80, 160, 320} × minority
proportion p ∈ {0.05, 0.15, 0.30, 0.50} × 10 seeded replicates × 2 substrates.

Detection = seeded 200-draw permutation of the group labels; detected iff the observed median
difference exceeds the 95th percentile of that null.

**Resampling real rows is not simulation.** Every row is a real observation about a real
package or repository, and the relationship being detected is whatever is genuinely there. No
mechanism is modelled and no value is invented.

---

## Results — 5/6

```
AUC(Δ)              0.9442      ← K3 primary, bar 0.70          PASS
AUC(n rows)         0.6700      ← K4 ablation                    PASS  (predicted to fail)
AUC(V) alone        0.9207      ← K5 multiplicativity            FAIL
AUC(C) alone        0.8084
AUC(I) alone        0.6912
detection rate       29.0%      ← K2 populated region            PASS
```

### K4 passed against my own written prediction

The spec recorded K4 as **expected to fail** — sample size is the incumbent explanation for
why a test does or doesn't detect, it's trivially available, and it varies 16-fold across the
grid. Δ scored **0.9442 against n's 0.6700**.

That's a genuine surprise and it's the strongest result here. **Whether a dataset can see an
effect is not mainly a question of how big it is.**

### K5 failed — and it tested what the model actually asserts

The pre-registration named multiplicativity as *"the substantive and falsifiable content of
the model."* It was tested, and it **did not earn its keep**:

```
Δ = V·I·C     0.9442
V alone       0.9207
improvement   0.0235      against a locked bar of 0.03
```

**A one-factor model — does the outcome actually move? — does nearly all the work.**

The formula is **not** being rewritten to fit this. DCM is reported as specified with K5
recorded as failed. Rewriting after seeing the AUC is exactly the immunisation move the
pre-registration exists to prevent.

One caveat in the model's favour, pre-disclosed before the run: **V and C are correlated by
construction**, both being functions of the outcome's value distribution. Two substrates
where they move together cannot separate them. A substrate with wide-ranging values but few
distinct ones — high V, low C — would decouple them, and none was available. That makes the
test *weak on this point*, not the result discountable.

**What the next spec must do:** find a substrate that decouples V from C, or drop to the
one-factor model and pre-register it against this same harness before claiming anything.

### Two passes that should not be read as support

**The pooled 0.9442 is partly a substrate label.** It sits just under the 0.95 too-perfect
trigger and is *not* the model's accuracy. GitHub is naturally clean, PyPI naturally
degenerate, so much of the pooled separation is Δ acting as a substrate indicator — exactly
what K6 was written to catch. **The honest figures are within-substrate: 0.8754 and 0.6690.**

**K6 passed on the PyPI side on four events.** Only 4 of 200 PyPI sub-datasets detected
anything, so its 0.669 AUC rests on 4 positive cases and clears the 0.65 bar by 0.019. **That
is not a result.** The gate stands because the threshold was locked and isn't being moved;
the weakness is disclosed rather than absorbed into the score.

---

## The clearest demonstration scores nothing

Coarsen the **recording** while leaving the relationship untouched:

```
natural                     29.0%  detected
quantised to 10 levels       5.5%
quantised to  3 levels       0.5%
```

**The effect was still there. The data stopped being able to see it.**

That is DCM's central claim visible directly — and it is **excluded from the score** by the
locked spec, because it's a manipulation of real data rather than an observation. The
quantised-3 arm carries 2 detections in 400, so its AUC is meaningless and isn't quoted. It's
reported for the detection collapse only.

---

## What a low Δ does **not** mean

> **A low Δ says: this dataset cannot settle this question.**
> **It never says the claim is false.**

Using Δ to dismiss someone's claim would invert the model's entire purpose, which is to stop
nulls being read as refutations.

Worked from this programme's own record: the contract schedules scored 3/6 and the outcome
panels 2/5. **Neither is evidence that Islamic contracts are debt.** Both are evidence that
the supplied data could not tell the difference. DCM exists so that distinction is measurable
in advance instead of argued about afterwards.

## What it would license, and what it would not

**Would:** that across 400 sub-datasets from two real open-source substrates, a three-factor
structural index computed without reference to the relationship predicted whether a
permutation test would detect it — better than sample size did.

**Would not:** that Δ is calibrated, that any threshold on it is meaningful, or that it
transfers to substrates unlike these two.

## Open gaps

| Gap | What closes it |
|---|---|
| **K7 — the C factor on panel data** | The sharpest coupling failure (successive values following a fixed multiplicative rule, as in the −85%-every-period write-downs) needs repeated observations per unit. Both substrates here are cross-sectional. Recorded **UNTESTABLE-HERE** |
| **V and C are entangled** | A substrate with high V and low C |
| **PyPI detects almost nothing** | A second degenerate substrate with a stronger true effect |
| **Δ is uncalibrated** | No threshold on Δ is claimed or implied |

## Reproduce

```bash
python3 dcm/dcm.py
python3 -m pytest -q dcm/test_dcm.py
bash reproduce_all.sh
```

Both substrates are hash-pinned and the runner aborts if the spec or either file changed.
Exit 0 means **"reproduces including its failures"** — never "the model is validated."
