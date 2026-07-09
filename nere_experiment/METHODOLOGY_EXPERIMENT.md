# The Methodology Experiment — does the firewall actually kill false signals?

*Testing the epistemological thesis directly: that the civilizational contribution
of LISM/NERE is the **methodology** — a four-pillar cognitive firewall that
suppresses the false "universal laws" post-hoc data-mining manufactures. Three
components, all reproducible: (1) the shipped stack's own 60-test suite, (2) a
Monte Carlo that pits disciplined vs vending-machine analysis on data with known
ground truth, (3) NERE catching the rhetorical signature of the same failure.*

---

## Component 1 — the shipped stack is sound (60/60)

Baseline: the uploaded IHCEI v3.0 probabilistic stack passes its full suite.

```
python3 ihcei_stack/ihcei_v3/test_ihcei_nere_v3.py   ->   RESULT: 60 passed, 0 failed
```

This establishes the substrate: probabilistic floor `[0.01, 0.99]`, `E=U·D²` and
`D_min` **RETIRED_FULLY** and unreachable, calibrated channel priors, agency-
preserving middleware (holds, never mutates). The engine works; the question is
whether the *discipline it encodes* buys anything. Components 2–3 test that.

## Component 2 — the four pillars vs vending-machine science (Monte Carlo)

Two analysts see the **same** synthetic datasets. Ground truth is known, so we can
score who reaches the *correct scientific verdict*.

- **NAIVE** — garden of forking paths: search 5 model specs × 6 sub-populations,
  declare a LAW if *any* combination crosses p < 0.05 with the expected sign. No gates.
- **FIREWALL** — the four pillars: (P1) one locked spec on the full sample + a
  locked bidirectional linear-vs-quadratic rule (nested LRT); (P2) VIF gate → if
  the two hops are collinear (VIF ≥ 5), triage INCONCLUSIVE; (P3) non-test triage
  → if the failing region has < 100 events, triage INCONCLUSIVE; (P4) a null is
  reported as a null.

Five regimes, `reps = 400`, `n = 250`, `seed = 1`, α = 0.05:

| Regime | Ground truth | NAIVE correct | FIREWALL correct |
|---|---|--:|--:|
| NULL | no law | 76.0% | **92.0%** |
| LINEAR | E = U·D | 100.0% | **95.5%** |
| QUADRATIC | E = U·D² | 0.0% | **53.2%** |
| TRAP_VIF | inconclusive | 0.0%\* | **100.0%** |
| TRAP_SEP | inconclusive | 0.0%\* | **100.0%** |

\* NAIVE has no INCONCLUSIVE category at all — it *cannot* triage, which is the point.

### The headline: false-discovery rate (fabricating a law where none exists)

| Cohort | NAIVE | FIREWALL |
|---|--:|--:|
| Pure NULL | **24.0%** | 8.0% |
| TRAP_VIF (confounded + collinear — the *SEC EDGAR* case) | **100.0%** | **0.0%** |
| TRAP_SEP (sparse near-separation — the *M5 non-converged fit* case) | **35.5%** | **0.0%** |

*(nominal α = 5%.)*

**Reading it.**
- On a **pure null**, forking paths manufacture a "universal law" **1-in-4 times**.
  The firewall holds near nominal (8% — and that 8%, not 5%, is honest: the locked
  bidirectional rule runs *two* tests, linear-existence and the quadratic term).
- **TRAP_VIF is the decisive panel.** A lurking variable drives both hops and the
  outcome; D *looks* protective but the two-hop channel has collapsed. Naive is
  fooled **every single time (100%)**. The VIF gate catches it **every single time
  (0% fabrication)**. This is precisely why SEC EDGAR was excluded from the real
  sweep — and here the exclusion rule is shown working under controlled truth.
- **TRAP_SEP** reproduces the M5 artifact: a handful of failures near-separate the
  logit and manufacture a "significant" coefficient. Naive bites 36% of the time;
  non-test triage refuses inference and fabricates 0%.
- The firewall is **not merely conservative**: it recovers the *real* linear law
  96% of the time and correctly *names* the real quadratic 53% of the time
  (distinguishing U·D from U·D² is genuinely low-power — which is exactly why the
  linear-vs-quadratic question demanded this much discipline in the first place).
  Naive scores **0%** on naming the quadratic: forking paths grab the first
  significant spec and mislabel the mechanism.

> Same data. Same statistics. The *only* difference is the discipline — and the
> discipline is what separates signal from self-deception. That is the thesis,
> demonstrated rather than asserted.

## Component 3 — NERE catches the *rhetoric* of vending-machine science

The statistical firewall stops a false law from being *born*. NERE stops it from
*travelling*: it flags the language that pressures a reader to stop checking. Run
on the real uploaded engine, one manipulative vs disciplined phrasing per pillar:

| Pillar (rhetorical tell) | Manipulative | Disciplined |
|---|---|---|
| P1 · post-hoc HARKing ("proves it, don't verify") | **BLOCK** P=0.97 | PASS P=0.03 |
| P2 · ignoring collinearity ("both predict, confirmed") | **BLOCK** P=0.93 | PASS P=0.36 |
| P3 · separation over-read ("few failures, certainly real") | **WARN** P=0.48 | PASS P=0.05 |
| P4 · refusing the funeral ("experts agree, ignore the null") | **BLOCK** P=0.98 | PASS P=0.07 |

**4/4** manipulative phrasings flagged; **4/4** disciplined phrasings pass. Every
BLOCK still ships a correction pathway ("remove the authority claim, require a
verifiable source with an independent checking pathway") — NERE preserves the
reader's agency, it does not censor. It does not decide truth; it flags the exact
move — *stop checking* — that lets a fabricated law spread.

---

## What this establishes for review

The primary contribution LISM offers a *PNAS* / *Nature Human Behaviour* reviewer
is not one more coupling coefficient — it is a **disciplined, reproducible,
anti-circular template** whose value can now be *quantified*: it cuts null-cohort
false discovery from 24% → 8%, and confounded/degenerate-cohort false discovery
from 100%/36% → 0%, while still recovering real effects. The statistical firewall
and its rhetorical twin (NERE) are the same discipline at two altitudes — the
"cognitive firewall" made measurable.

## Reproducibility

```
python3 ihcei_stack/ihcei_v3/test_ihcei_nere_v3.py     # 60/60 stack suite
python3 methodology_experiment.py --reps 400 --seed 1  # four-pillar Monte Carlo
python3 nere_epistemic_demo.py                         # NERE rhetoric demo (4/4)
```
Deterministic under the given seed. `methodology_results.json` carries the summary
numbers cited above.
