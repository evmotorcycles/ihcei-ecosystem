# SDL — the Scope Declaration Law

**Spec** `c025eb5170456d197c23259180b105e458720f0740ebc1d2f00eb38e134e646a` · locked before
any winner was computed · **2/6**

```bash
python3 -m pytest -q scoping/test_scoping.py
```

---

## The design is right. The hole is somewhere else.

Don't invent a new universal equation when you hit an empirical boundary. Keep the Layer 3
framework, deploy domain-specific Layer 1 equations, scope them to where they hold.
**Every result in this programme supports that.** The product form is 195× worse than the
single hop where records are redundant; a rule calibrated at one scale extrapolates 4,406×
wrong. Forcing one equation across those substrates *would* be the error.

But the architecture has a hole, and this run tests the hole rather than the design:

> **A family of equations plus a free choice of which one applies cannot be refuted.**
>
> Assign the scope condition *after* seeing which equation won, and every future failure is
> absorbed by adding a scope clause. The framework then predicts nothing — however well each
> individual equation performs.

**The scope condition is the theory.** So the question is not whether domain-scoping is a
good idea. It's whether a scope selector can be **declared in advance** and computed from
substrate structure **alone**.

## The selector, locked before any winner was known

```
R = modal share of the decode variable
    (fraction of units sharing the single most common value of D_dec)

R > 0.5   →  predict the single-hop form   U · D_enc
R ≤ 0.5   →  predict the two-hop form      U · D_enc · D_dec
```

**R reads the decode column and nothing else** — not the outcome, not `U`, not `D_enc`, not
which form won. A test scans the function's source to enforce it. The threshold is 0.5, the
midpoint: the only value needing no justification from the data.

**It is a proxy and it is labelled one.** Redundancy in the quantum sense means many carriers
*each sufficient* to reconstruct the signal. Modal share means many carriers holding the
*same value*. No single first-principles redundancy measure spans interactomes, repositories,
package graphs and environment qubits — and that absence is part of what this run exposes.

R is DCM's `V` factor inverted, applied to the decode channel: the programme's second model
supplying the scope selector for its first.

## Five substrates, four able to test the rule

| Substrate | n | R | predicted | actual | |
|---|---:|---:|---|---|---|
| yeast interactome | 4,825 | 0.179 | two-hop | two-hop | **OK** |
| GitHub repos | 992 | 0.179 | two-hop | single-hop | ✗ |
| PyPI packages | 540 | 0.493 | two-hop | single-hop | ✗ |
| interbank 2016 | 1,349 | 0.675 | single-hop | two-hop | ✗ |
| quantum spin-star | 95 | 0.900 | single-hop | single-hop | OK — *not independent* |

The quantum winner was known before the spec was written. It is **scored**, because dropping
the case that motivated the scope condition would flatter the rule, and **flagged**, because
counting it as confirmation would be circular.

**Among the four substrates that could actually test the rule, it scored 1 of 4.**

### The sharpest counter-case

The interbank network has the **second-highest decode redundancy** of the five, so the rule
predicted the single hop. **The two-hop form won.** Whatever makes a decode hop scarce or
not, modal share is not measuring it.

## Every gate that mattered failed

| Gate | Locked bar | Measured | |
|---|---|---:|---|
| S1 integrity | hashes, shapes, ranges | — | PASS |
| S2 substrates disagree | not unanimous | 2 forms | PASS |
| S3 rule assigns the winner | ≥ 4 of 5 | **2 of 5** | FAIL |
| S4 scoping beats one global form | > best baseline | **2 vs 3** | FAIL |
| S5 the threshold is doing work | beat ≥ 80% of thresholds | **0%** | FAIL |
| S6 DCM self-audit | Δ ≥ 0.20 | **0.1536** | FAIL |
| S7 is scoping right in general | — | — | UNTESTABLE-HERE |

**S4 is blunt: the rule is worse than not scoping at all.** Scoping got 2 right; always using
the single-hop form gets 3. On these five substrates the scope condition isn't decoration —
it's actively costly.

## S5 is the real methodological finding

Sweep every threshold from 0.00 to 1.00 on R and count correct assignments:

```
R    0.00 ──────────────── 0.45   score 3
     0.50 ──── 0.65               score 2   ← the locked threshold sits here
     0.70 ──── 0.85               score 3
     0.90 ──── 1.00               score 2
```

**Only two distinct scores are reachable at all: {2, 3}.**

A single threshold on a single number cannot express more than a handful of partitions of
five substrates. The sweep isn't measuring how good the threshold is — **it's measuring how
little room there was to be wrong.**

The locked 0.5 landed on the *worse* of the two available scores. **It is not being moved.**
And the punchline: the best reachable score is 3, which **merely ties** the always-single-hop
baseline. Even with hindsight and a free choice of threshold, scoping would not have beaten
using one form everywhere.

## The self-audit fired — and it binds everything above

The spec turned this programme's own second model, **DCM**, on this very experiment. DCM says
a dataset can only adjudicate a claim it can discriminate. This experiment has **five data
points.**

```
Δ = V 0.4000 × I 0.9600 × C 0.4000 = 0.1536      against a locked floor of 0.20
```

> **S6 was not met, so S3, S4 and S5 are UNINFORMATIVE.**
> **The rule's status is UNTESTED, not REFUTED.**

That constraint was written into the specification **before any winner was computed** —
deliberately, so a bad result could not be spun as a refutation any more than a good one
could have been spun as a confirmation. The rule scored 1 of 4 on independent substrates and
lost to always-single-hop. **I am not permitted to call that a refutation**, and the results
file says so in both directions.

## What this run does and does not establish

**It does establish one thing, and it isn't nothing.** The scope condition **can** be written
down in advance and computed from structure alone. That is the difference between an
architecture that could be tested and one that could not. Before this run, domain-scoping had
no declared selector at all.

**The hole is still open.** It does not establish that *this* scope condition is correct —
five substrates cannot calibrate a threshold. And a scoped family of equations remains
unfalsifiable until its selector is tested on substrates collected by **people who were not
testing it**. Five substrates, four from this programme's own shelf, do not clear that bar.

Worse: if the selector must itself be redefined per domain — and no first-principles
redundancy measure spans interactomes, repositories and qubits — then **domain-scoping has
moved the unfalsifiability rather than removed it.** That is the sharpest open question this
run leaves behind.

## What would close it

| Gap | What closes it |
|---|---|
| Five substrates | Dozens, with the selector declared before any were seen |
| Four from this shelf | Substrates collected by people not testing this architecture |
| R is a proxy | A redundancy measure derivable per domain from first principles, not fitted |
| A single threshold on one number | A selector with enough structure to be wrong in more than two ways |

## Reproduce

```bash
python3 scoping/scoping.py
python3 -m pytest -q scoping/test_scoping.py
bash reproduce_all.sh
```

All four data files are hash-pinned and the runner aborts if the spec or any file changed.
Exit 0 means **"reproduces including its failures"** — of which this run has four, plus a
self-audit that forbids me from making anything of them.
