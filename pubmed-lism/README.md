# PubMed LISM — self-correction failure burden, and the honest limit on retraction latency

**One command:** `python3 pubmed-lism/pubmed_retraction.py` · stdlib only · offline · `$0`

This experiment tests two **structural** LISM predictions — *concentration* (heavy tail)
and *field-dependence* — on a new real biomedical-governance substrate: **PubMed
retractions**. It also does something the framework demands: it **declares up front that
the retraction *latency* τ_v is not cleanly measurable through this connector**, rather
than forcing a number.

> **Attribution.** Data from PubMed (U.S. National Library of Medicine).

---

## What is measured (and what is not)

For 8 biomedical fields over a fixed 2004–2023 publication window, we take two real
PubMed `total_count` values each — all papers (denominator) and retracted papers
(numerator) — and compute:

```
retraction_rate(field)  =  retracted_papers / total_papers
```

This is the **realized self-correction failure burden** of a field. Because it's a
*ratio*, it controls for how much a field publishes — a large field doesn't look worse
just for being large.

**Construct-validity firewall.** The retraction *rate* is a **failure burden**, not the
enforcement *latency* `τ_v` (days from publication to retraction). Those are different
observables, and this experiment measures only the first. See H3.

| artifact | SHA-256 |
|---|---|
| `prereg/pubmed_prereg.json` (spec) | `54d2114cfc796409210d9fc768faaf188e7a6916108ddb53a71b5a146fe74892` |
| `data/pubmed_cohort_frozen.json` (fixture) | `70b75ad503f2c158cad020c87c284183c893cf42d0fd35d1d5e85bdeeff7262f` |

The runner re-verifies both hashes before computing; if either drifts, it refuses to run.

---

## Result (GREEN, honest)

```
retraction rate per field (PubMed, 2004–2023), per 100k papers:
   Anesthesia               262 /   79,294    330.4
   Stem Cells               680 /  218,494    311.2
   Neoplasms              6,435 / 2,251,959   285.8
   Cardiovascular Dis.    1,926 / 1,525,045   126.3
   Nervous System Dis.    1,957 / 1,639,434   119.4
   Mental Disorders         645 /   895,683    72.0
   Immune System Dis.       620 /   865,164    71.7
   Communicable Dis.        165 /   329,618    50.1

H1 heavy tail (concentration): mean 170.8 > median 122.8 ✓   max/median 2.69 (≥2.0) ✓  → PASS
H2 field dependence          : max/min 6.60 (≥2.0)                                     → PASS
H3 retraction LATENCY (τ_v)  : DECLARED UNTESTABLE
```

**H1 — concentration (PASS).** A small number of fields carry a disproportionate share of
self-correction failures. The two highest, **anesthesia** and **stem cells**, are exactly
the fields history flags for large-scale research-fraud episodes — a real external-validity
check, not a fitted artifact. This is the heavy-tail concentration LISM predicts for hazard.

**H2 — field-dependence (PASS).** The rate spans 6.6× from the highest field to the lowest.

**H3 — the latency τ_v is UNTESTABLE here (declared, not spun).** The days-from-publication-
to-retraction latency — the quantity that would directly test the Third Law — **cannot be
computed non-circularly through this connector.** PubMed returns each article's *original*
publication date, but the paired *retraction* date is not reachable: the `Retraction of
Publication` notice records aren't retrievable, and related-article links are word-similarity,
not the notice. So we report the latency as **untestable** — exactly as the bioRxiv coupling
(H3) and the legislation/judicial channel were reported. No number is manufactured.

## What this does and does not claim

- ✅ Tests the **structural signature** (concentration + field-dependence) that LISM's hazard
  theory predicts, on a real self-correction substrate.
- ❌ Does **not** measure the τ_v retraction *latency* (declared untestable here).
- ❌ Makes **no** `E = U·D` coupling claim on this substrate.
- Illustrative (8 fields, one 20-year window), not a powered scientometric study. The τ_v
  *latency law* remains measured on GitHub and bioRxiv; the coupling cohorts remain
  yeast/GitHub/knowledge/swarm.

## Reproduce

The 16 live queries are recorded in the fixture's `_provenance` block (denominator
`<field>[MeSH Terms]`; numerator `Retracted Publication[Publication Type] AND <field>[MeSH
Terms]`, window 2004–2023). Anyone can re-issue them against PubMed to reproduce the counts;
the frozen snapshot makes the offline run deterministic.

```
python3 pubmed-lism/pubmed_retraction.py       # GREEN, N=8 fields
python3 -m pytest pubmed-lism/test_pubmed.py -q
bash reproduce_all.sh                           # whole stack
```

## Files

```
pubmed-lism/
  prereg/pubmed_prereg.json        pre-registration spec (locked)
  prereg/MANIFEST.sha256.json      spec + fixture hashes
  data/pubmed_cohort_frozen.json   real PubMed counts + the exact queries (frozen)
  pubmed_retraction.py             the experiment (stdlib, offline)
  test_pubmed.py                   pytest guard (locks + H1/H2/H3)
  results_pubmed.json              emitted results
```

Layer-1, offline, `$0`. Data from PubMed (U.S. National Library of Medicine).
