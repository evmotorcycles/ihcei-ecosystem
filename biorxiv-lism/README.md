# bioRxiv LISM — enforcement latency (τ_v) on real scientific publishing

**One command:** `python3 biorxiv-lism/biorxiv_tau_v.py` · stdlib only · offline · `$0`

This experiment measures the **LISM Third Law** — *enforcement latency* `τ_v` — on a
brand-new real substrate: the time it takes a **bioRxiv preprint** to reach **formal
journal publication**. It is pre-registered and SHA-256-locked *before* it runs.

```
τ_v  =  days( journal-publication-date  −  preprint-posted-date )
```

That is a direct, non-circular latency — exactly analogous to the GitHub issue-close
`τ_v` cohort already in this repo, but drawn from a completely different domain (science
communication instead of software governance).

---

## Where the data comes from (real, then frozen)

The cohort is **40 real published bioRxiv preprints** (posted Feb 1–15, 2024), fetched
live through the bioRxiv MCP connector (`search_published_preprints`) and then **frozen**
to `data/biorxiv_cohort_frozen.json` so the experiment is reproducible offline with no
network and no keys. Each record carries `doi`, `category`, `preprint_date`,
`published_date`, `journal`, and `n_authors` — all transcribed verbatim from the API.

The fixture and the pre-registration spec are hashed and locked in
`prereg/MANIFEST.sha256.json`. The runner re-verifies both hashes before it computes
anything; if either drifts, it refuses to run (exit 2).

| artifact | SHA-256 |
|---|---|
| `prereg/biorxiv_prereg.json` (spec) | `6189220846b10050b44992c1046919e4d71f2dc93cefeaa5e1d81ef1696c071e` |
| `data/biorxiv_cohort_frozen.json` (fixture) | `aa3600d10c0fe6cbe0eb5f1b90949f8c8cd742e2f42956f8acca351d638c7103` |

---

## What was pre-registered (three gates, fixed before running)

- **H1 — heavy upper tail (the hazard signature).** `τ_v` is right-skewed with a wide
  tail. *PASS if `mean > median` AND `p90/median ≥ 2.0`.*
- **H2 — field variation.** Publication latency differs across scientific fields.
  *PASS if `(max category median)/(min category median) ≥ 2.0`* among categories with n≥2.
- **H3 — coupling declared UNTESTABLE.** The two-hop `E = U·D` **survival** coupling is
  **not** cleanly instrumentable on this metadata (only the *published* subset is
  observed — there is no unpublished comparison group, no independent second fidelity
  hop, and no non-circular binary survival outcome). This is declared **untestable** and
  reported as such — exactly like the legislation/judicial channel elsewhere in this repo.
  **It is not spun into support for the coupling law.**

---

## Measured result (GREEN, honest)

```
τ_v = preprint → journal-publication latency (days), N=40:
   min 88   p10 109   MEDIAN 219   mean 358.4   p90 856   max 1458

H1 heavy tail : mean 358.4 > median 219 ✓   p90/median = 3.90 (≥2.0) ✓   → PASS
H2 field var  : ratio 4.76 (≥2.0)                                          → PASS
     cancer biology     median 701 d
     …
     biochemistry       median 147 d
H3 coupling   : DECLARED UNTESTABLE (published-only, no independent second hop,
                no non-circular survival outcome)
```

**Reading.** Most preprints publish within months, but a long upper tail lingers for
*years* — a mean nearly double the median, a p90 of 856 days, a max of 1,458. That wide
upper tail is the `τ_v` hazard signature LISM describes: latency concentrates in a slow
minority. And the delay is strongly field-dependent (cancer biology takes ~4.8× longer
than biochemistry). Both are *measured* properties of the latency law on a new substrate.

## What this does and does not claim

- ✅ It measures the **latency law** (`τ_v`, the Third Law) on real scientific publishing.
- ❌ It does **not** claim the `E = U·D` coupling on bioRxiv — that is declared untestable
  here (construct validity), and honestly reported, not forced.
- This is a **first, illustrative** `τ_v` measurement (N=40, one fortnight of 2024), not a
  powered epidemiology of publication delay. The validated LISM *coupling* cohorts remain
  yeast (N=4,825), GitHub (N=992), knowledge/StackExchange (N=793), and the digital swarm.

## Files

```
biorxiv-lism/
  prereg/biorxiv_prereg.json      pre-registration spec (locked)
  prereg/MANIFEST.sha256.json     spec + fixture hashes
  data/biorxiv_cohort_frozen.json 40 real published preprints (frozen)
  biorxiv_tau_v.py                the experiment (stdlib, offline)
  test_biorxiv.py                 pytest guard (locks + H1/H2/H3)
  results_biorxiv.json            emitted results
```

Run the guard: `python3 -m pytest biorxiv-lism/test_biorxiv.py -q` · or the whole stack:
`bash reproduce_all.sh`. Layer-1, offline, `$0`.
