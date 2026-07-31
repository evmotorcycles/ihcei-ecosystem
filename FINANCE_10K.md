# Finance 10,000 — the third LISM cohort, and what it does and does not add

**Verification** `python3 finance-10k/verify_finance_10k.py` → **8/8 VERIFIED** ·
**75/75** suites green · four pre-registrations, all locked before implementation

LISM now rests on three committed cohorts. This document shows a peer reviewer how to
verify the third one from scratch, states plainly what kind of evidence it is, and sets out
how each of the three financial models is adopted.

---

## 1. The three cohorts are not the same kind of evidence

This is the first thing a reviewer needs, and getting it wrong would overstate the case.

| Cohort | N | What it tests | Status |
|---|---|---|---|
| **Yeast interactome** | 4,825 | the **coupling law** — does yield couple linearly or quadratically to two-hop fidelity? | linear won: CV AUC **0.666 vs 0.591**, VIF 1.0026 |
| **GitHub** | 992 | the **coupling law**, replicated | linear won: dAIC **−3.483**, QUADRATIC_DISCONFIRMED |
| **Finance** | 10,000 | **mechanism design** — what do these architectures *do* under a recorded event sequence? | four pre-registered runs, scores 3/6, 0/5, 4/5, 3/5 |

> **The finance cohort does not test the coupling exponent.** It is a **mechanism cohort**,
> not a **coupling cohort**. Saying "LISM now has three cohorts" is accurate only with that
> distinction attached, and a reviewer who assumed all three tested `E = U·D` versus
> `E = U·D²` would be misreading the record.

It also does not rescue the coupling law where that failed: on a real 540-package PyPI
graph **neither** coupling explained reuse (R² ≈ 0.01 both). That null stands.

## 2. How a peer reviewer verifies Finance 10,000

```bash
python3 finance-10k/verify_finance_10k.py     # 8/8, no network, ~2 min
```

The script **trusts no results file in this repository**. It is the finance counterpart of
`cohort-audit/verify_992_recovery.py`, which applied the same discipline to N=992: a
bundled summary proves nothing, because one engineered to match published statistics would
pass every check precisely because it was built to.

| Check | What it establishes |
|---|---|
| **R1** | the source workbook hashes to the committed manifest — `932247a7…` |
| **R2** | the cohort re-derives to exactly **4,886 debits + 5,114 credits = 10,000** |
| **R3** | the debit transform is `amount / balance` clipped to [0,1], recomputed from the raw workbook **without importing any experiment code** — n=4886, min 0.000141, max 1.000000, mean 0.112412 |
| **R4** | all four pre-registrations re-hash to the values their runners enforce |
| **R5** | every runner **aborts** if the source workbook changes |
| **R6** | each experiment re-run from a clean process reproduces its committed score |
| **R7** | runs are **byte-identical** across repetitions |
| **R8** | the seed-variation band re-derives from the per-seed record — CV **0.220** |

### The four locked pre-registrations

| Spec | Question | Score |
|---|---|---|
| `dca3694c` | is participation a loss reducer or a contagion control? | 3/6 |
| `ed80430a` | does routing claims by a risk signal beat random assignment? | 0/5 |
| `0b2328c5` | three named positions on one engine | 4/5 |
| `f14596f1` | v2, plus five-seed robustness | 3/5 |

Each hash is computed over the canonical JSON of the spec and re-verified by its runner
before any measurement. **13 of 21 scored gates failed.** That is the record, and the
failures are the reason the surviving claims are worth anything.

### The one number a reviewer should carry into every other section

> **CV = 0.220.** Single-seed results in this repository carry roughly **±22%** variation.
> Every single-seed finding here — including in the other two cohorts — should be read with
> that band attached until it has been re-run across seeds.

---

## 3. How Finance 10,000 upgrades LISM

Three extensions, each forced by measurement rather than chosen.

**① `D_dec` has a timing dimension, and it dominates.** LISM treated distribution fidelity
as *how well* value propagates. The measurement says **when** it propagates is worth
**50.9×** any structural choice about the channel. Distribution is not a coefficient —
**it is a rate.**

**② The two hops trade off; they are not independently improvable.** The product form
already implied either hop at zero collapses the result. What is new: **optimising one
actively costs the other** — 16.5% cascade reduction for 4.6× shortfall — so the product
cannot be maximised by improving both in isolation. An institution must pick an endpoint.

**③ `D_dec` can be structural rather than discretionary — and structural wins.** This came
from Al-Qudah's model, not ours. Amortising co-ownership makes value return continuously
because the *contract* is built that way, not because a policy layer says so. Measured
**36.1 against our 71.0**.

---

## 4. The three models, by specialisation

The five-seed sweep interpolates from containment share 0.00 to 1.00. At **0.00 the
architecture *is* Al-Qudah's model**; at **1.00 it *is* Irfan's**. No strawman is available.

```
containment    shortfall   secondary
      0.00         36.1         121     ← Al-Qudah — best shortfall tested
      0.25         71.0         119
      0.60        107.8         109
      1.00        167.6         101     ← Irfan — fewest cascades tested
```

**No interior point qualifies.** Cascades fall only 16.5% across the whole range while
shortfall rises 4.6×. **Deploy an endpoint, not a blend.**

| Model | Specialises in | Evidence | Deploy for |
|---|---|---|---|
| **Al-Qudah** — asset-backed co-ownership, unmixed | **routine value recovery** | shortfall **36.1**, best tested | ordinary business lending, equipment, trade credit |
| **Irfan** — full-reserve participation notes, unmixed | **contagion control** | **101** cascades, fewest tested | nodes whose failure takes others down |
| **Two-Register** — the substrate both run on | **payment velocity + audit** | **50.9×** flow effect; 1.99× substrate penalty | underneath either endpoint |

---

## 5. What is deployed, and what is not

**You are right that the substrate is the gap, and it is the honest place to put the
effort.** But I have to be careful about how the rest is stated.

### What this repository can and cannot vouch for

The specific deployment claims supplied — named platforms, firms and roles attached to
named individuals — are **user-supplied context that this repository has not verified**.
Nothing here checked them, and I am not going to publish factual claims about real people's
commercial affiliations on the strength of a summary I cannot audit. They are recorded as
context, not as findings, and a reviewer should treat them that way.

**What is safely sayable at the category level**, and is enough for the argument:

- **Asset-backed co-ownership finance is an operating model.** Diminishing-partnership home
  and equipment finance exists commercially, including outside the conventional secondary
  mortgage market. Al-Qudah's arm is a model *of a thing that runs*.
- **Non-bank participation vehicles are an operating model.** Private placements and equity
  risk-sharing intermediaries that sit outside commercial bank balance sheets exist. Irfan's
  arm is a model *of a thing that runs*.
- **The universal substrate is not deployed anywhere, by anyone, including us.**

### The substrate is the actual work

That gap is real and it is where effort belongs, because the substrate is the part carrying
the largest measured effect:

| Substrate component | Status | Measured |
|---|---|---|
| Full reserve, `ΔU = 0` | **specified and tested in simulation only** | identical contracts cost **1.99×** more fractional |
| Continuous distribution | **specified and tested in simulation only** | **50.9×** — largest effect in the programme |
| Echo claim register | **built and tested in this repository** | append-only, hash-chained, Merkle-provable |
| HELM on-device kernel | **built and tested in this repository** | no network call in the kernel, with a test proving it |
| Register routing | **deliberately absent** | lost to 18 of 20 coin flips |

**Two of the five are code that runs; two are designs measured only in a settlement
simulator; one was removed on evidence.** That is the honest deployment status, and the
first three lines of any adoption roadmap.

### What honest deployment would require next

1. **A live pilot of continuous distribution alone**, inside an existing institution, on
   real receivables. It needs no new infrastructure — it is a change to collection timing —
   and it carries the largest measured effect. This is the cheapest test of the biggest
   claim, and it has not been done.
2. **Echo as the claim register for a real book**, so "which register was this claim in,
   and was it altered?" is provable rather than asserted.
3. **Full reserve last**, because it is the hardest regulatory lift and its benefit is
   measured relative to the other two already being in place.

**Order matters.** Doing full reserve first would be doing the expensive thing before the
cheap thing that measured 50× larger.

---

## 6. Why this matters to each sector

**Conventional banks.** No cultural framing needed. Pay as you collect; don't lend what you
haven't got; use participation only where contagion is the real exposure; don't buy a
risk-routing model.

**Islamic banks.** The substrate critique is **vindicated on measurement, not doctrine** —
identical contracts cost 1.99× more fractional, so the label was never the problem. But
**risk-sharing does not lower your losses; it raises them 4.6×.** Its value is systemic.
Sold as prudential infrastructure it is defensible; sold as a superior return profile it is
not. And the audit register is the real differentiator, because the "oxymoron" charge lands
on **unverifiability**, which a hash-chained ledger answers directly.

---

## 7. Layer discipline

The Organic Qur'anic Methodology is **governance philosophy — Layer 3, philosophically
prior**. It supplies the abstract logic used to generate theories and engineer systems, and
it supplied the stock-versus-flow reading that pointed at the largest effect in this system
before it was measured.

**It did not supply the evidence and cannot.** Nothing here adjudicates a jurisprudential
question: a better settlement outcome is not a ruling. And the boundary held in the
direction that cost us something — the methodology generated v2's design and the telemetry
rejected two of its three claims.

---

## Reproduce

```bash
python3 finance-10k/verify_finance_10k.py     # 8/8 independent verification
bash reproduce_all.sh                          # 75/75, whole stack
```

Exit 0 means "reproduces including its failures", never "the model works".
