# OpenAlex LISM — a pre-registered NULL, reported with full force

**One command:** `python3 openalex-lism/openalex_lism.py` · stdlib · offline · `$0`

This is the experiment that **failed its own pre-registration on real data — and that's the
point.** We locked a heavy-tail gate *before* seeing any data (spec
`175efac5f805f87989c249069b695b095d9a4c170bbc72205c7ed7f22df9233f`), ran it on a real
50-work random sample of OpenAlex, and the gate **was not met.** We did not move the goalposts.

> Data source: OpenAlex (open, keyless, CC0). The reproducible fixed-seed sample
> `api.openalex.org/works?sample=50&seed=42` was fetched by the user (OpenAlex is
> network-blocked from the analysis session but needs no credential) and frozen verbatim.

---

## What was pre-registered, and what happened

| gate (locked before data) | result on real data |
|---|---|
| **H1** citations heavy-tail: `mean > median AND p90/median ≥ 2.0` | **FAIL** — median = 0 |
| **H2** references heavy-tail: `mean > median AND p90/median ≥ 2.0` | **FAIL** — median = 0 |
| **H3** `E = U·D` coupling | untestable on a snapshot (as pre-registered) |

```
H1 citations : median 0   mean 3.32   p90 4    max 99   zeros 34/50 (68%)   → FAIL
H2 references: median 0   mean 5.96   p90 34   max 51   zeros 38/50 (76%)   → FAIL

PRE-REGISTERED OUTCOME:  NULL — the locked p90/median tail gate is NOT met.
```

## Why it failed — the honest reason (not a retune)

The gate failed **not because citations aren't concentrated, but because they're so
concentrated the median is literally 0.** In a *random full-population* OpenAlex sample,
**68% of works have never been cited** and **76% have no parsed references** — the long,
flat floor of the scholarly distribution. A `p90/median` ratio is **undefined when the
median is 0**, so the gate cannot be satisfied.

The gate was calibrated on **nonzero-median** cohorts (GitHub stars, HF likes), where the
typical item has *some* engagement. A zero-inflated population violates that assumption.
**That is a pre-registration mistake, surfaced honestly — the metric, not the phenomenon,
was ill-posed.** We report the null and leave the locked gate exactly as written.

## The concentration is real — it just isn't *this* metric (descriptive only)

For context, and explicitly **not** as a substitute gate: the concentration is in fact
*extreme.* The single top work holds **60% of all citations** in the sample (99 of 166).
The heavy tail is unmistakably there; the pre-registered ratio metric simply can't express
it on zero-inflated data. A *robust* future gate (e.g. top-decile share, or the ratio on
the nonzero subset) would capture it — but proposing that **after** seeing the data would be
exactly the goalpost-moving this repo refuses. It's logged as future work, not run here.

## Why this null is valuable

Every prior LISM cohort in this repo passed its gates; a framework that only ever confirms
itself isn't being tested. This is the **epistemic firewall working in public**: a locked
prediction met real data, the specific metric failed, and the failure is recorded — with the
diagnosis — instead of being quietly retuned into a win. The reproducibility test
(`test_openalex.py`) **locks the null in**: it asserts the gate is *not* met and that the
outcome is reported honestly, so the same documented null reproduces every run.

## Files

```
openalex-lism/
  prereg/openalex_prereg.json       spec (locked BEFORE data) — gate unchanged
  prereg/MANIFEST.sha256.json       spec + fixture hashes
  data/openalex_cohort_frozen.json  the real 50-work sample (frozen)
  openalex_lism.py                  runs the LOCKED gate; reports the null; no retune
  test_openalex.py                  locks the null in (asserts gate NOT met, honestly)
  results_openalex.json             emitted results
```

Layer-1, offline, `$0`. A pre-registered null, reported with full force.
