# The scarcity metric — and LISM's own domain limit failing

**Spec** `135355477e57ae681805b289f1234e003954a00d36146cd2f19ab31df137e095` · locked after a
power probe run on **permuted labels** · **5/6**

```bash
python3 -m pytest -q scarcity/test_scar.py
```

> The manuscript said the product form assumes the decode hop is scarce. Nobody had ever
> measured that. Now someone has, and **it's wrong** — in the opposite direction.

---

## First: the gap as posed cannot be closed

The ask was a first-principles graph-topological scarcity metric for the **Scope Declaration
Layer**, which ranges over five substrates. A topological measure needs a graph. **Three of
the five don't supply one, and a fourth is circular:**

| substrate | status | why |
|---|---|---|
| yeast | **BLOCKED** | interactome *edges* were never committed — only node-level rows |
| GitHub | **BLOCKED** | a per-repository table; no graph exists in the repository |
| quantum | **NOT APPLICABLE** | a closed-form derivation, no dataset |
| PyPI | **UNTESTABLE-HERE** | **circular** — its declared outcome `E_indegree` is derived from the *same graph* the metric would be computed on |
| **interbank** | **the one clean test** | metric from Q1 topology, outcome realised in Q2 |

Those are **three different verdicts** and they are not merged. PyPI is not blocked — the
data is right there. It is *circular*, and no amount of extra effort fixes that.

**So this tests one substrate.** One substrate cannot establish a cross-substrate scope
rule, which is exactly what SDL's Δ was for. That limit is in the locked spec, in the
results, and in the manuscript amendment.

## The metric has no free parameter

**Local bridge fraction** `B(v)`: the fraction of `v`'s neighbours `u` for which `N(v)` and
`N(u)` share no common member.

An edge whose endpoints share no neighbour has **no alternative path of length two** — the
hop across it is scarce in the strict sense that removing it leaves no two-step substitute.
`B(v) = 1` means *every* one of `v`'s connections is a local bridge.

No threshold chosen. No weight fitted. No distribution assumed. The HIGH/LOW split sits at
`B = 1.0` — the natural boundary of the metric, **not a cut picked from the outcome.**

Both functional forms were **copied verbatim** from `interbank-2016/network.py` so neither
could be re-specified in its own favour:

```python
L[i] = u * de * dd            # LISM product
Q[i] = u * (de + dd) ** 2     # quadratic rival
```

## The power probe saw precision but not direction

The HIGH stratum holds 131 nodes and 20 events — thin. So the pre-flight bootstrap ran on
**permuted labels**, giving the width of the interval without revealing which way the real
effect fell: **width 0.0798.**

The paired difference is far more precise than its component AUCs, because both forms are
scored on *identical labels* and are highly correlated, so most sampling noise cancels. The
real labels were never touched before the lock.

## The result

| stratum | `U·D_enc·D_dec` | `U·(D_enc+D_dec)²` | advantage |
|---|---:|---:|---:|
| **high scarcity** `B = 1` (n = 131, 20 events) | 0.4455 | 0.4383 | **+0.0072** |
| **low scarcity** `B < 1` (n = 1,218, 271 events) | 0.6159 | 0.6180 | **−0.0021** |

```
  difference-in-advantage   +0.0093     required  +0.05
  90% bootstrap CI          [−0.0283, +0.0424]   width 0.0707,  bar 0.20
  permutation control       [−0.0348, +0.0364]   contains 0 ✓
```

**K5 was met, so K4 is interpretable — and the interval excludes the pre-registered effect
size.** This is a **refutation at the declared effect size, not a failure to detect.**

## The direction is worse than a null

> **In the scarce-decode stratum, both forms are anti-predictive** — 0.4455 and 0.4383, below
> chance. In the low-scarcity stratum both work.

Where the decode hop has **no two-step substitute** is where the model performs **worst**.
That is the opposite of what §3.3c asserts.

## What was withdrawn, and what wasn't

The quantum result **stands**: the two-hop product really is 195× worse there. What is
withdrawn is the **explanation** — that decode-hop scarcity is what separates the domains
where the product form applies from those where it doesn't. On the one substrate where
scarcity is measurable independently of the outcome, **it separates nothing.**

`LISM_manuscript_REVISED.md` §3.3c(i) now carries the amendment, citing this spec hash. The
spec committed to that *before* the run — a test asserts the manuscript actually changed, so
it cannot stay a promise.

## The gates

| Gate | Bar | Measured | |
|---|---|---:|---|
| K1 integrity | reproduce 1,349 nodes / 291 events | exact | PASS |
| K2 both strata populated | ≥100 nodes, ≥15 events each | 131/20, 1218/271 | PASS |
| K3 metric not degenerate | ≥10 distinct values, ≤95% one side | — | PASS |
| **K4 advantage larger where scarce** | ≥ +0.05 | **+0.0093** | **FAIL** |
| K5 precise enough to mean anything | CI width ≤ 0.20 | 0.0707 | PASS |
| K6 permutation control null | CI contains 0 | yes | PASS |
| K7 holds across substrates? | — | — | UNTESTABLE-HERE |
| K8 DCM self-audit | — | — | EXCLUDED |

**K8 is excluded on principle:** the analysed outcome is a continuous AUC difference, and
Δ = V·I·C cannot fail on a continuous unbanded outcome. A gate that cannot fail is not
evidence, so it scores nothing rather than inflating the total.
