# Legislation & Judicial Coupling Tests — Result: INCONCLUSIVE (documented)

**Date:** 2026-07-08 · **Live API:** `api/bill-text.js` on Vercel `project-6q4gj`
(`https://project-6q4gj.vercel.app/api/bill-text`, Congress.gov key configured,
health `{"ok":true,"keyConfigured":true}`).

## What was run
Real U.S. bill full text was fetched through the deployed Congress.gov proxy and
scored with `legislation_coupling_test.py`. Sample (all returned usable text):

| Bill | Words | D_enc specificity (defs / xref / numeric / mandates per 1k) |
|---|--:|---|
| 117-hr-3684 (IIJA) | 429,089 | 1.56 / 8.83 / 17.30 / 10.61 |
| 117-hr-1 | 152,933 | 1.31 / 10.48 / 17.28 / 9.40 |
| 117-s-1605 (NDAA) | 384,209 | 0.95 / 8.22 / 17.03 / 7.27 |
| 117-hjres-100 | 708 | 1.41 / 11.30 / 5.65 / 4.24 |
| 118-hr-2 | 34,160 | 1.05 / 7.49 / 8.40 / 8.55 |
| 117-hr-3076 (Postal) | 11,517 | 2.43 / 10.42 / 10.94 / 12.50 |

D_enc (bill-text specificity) is measurable and varies across bills. The test
nonetheless returns **INCONCLUSIVE** — and this is the honest, pre-committed
verdict, not a failure to find an effect.

## Why INCONCLUSIVE (same obstacles for legislation and judicial)
1. **No independent second hop.** The corpus yields the statute's own words
   (D_enc) only. The decoding hop LISM requires — faithful *implementation by
   agencies* and *survival under judicial review*, measured on **other** actors —
   is simply not in the data. Without an independent D_dec the two-hop channel
   cannot be formed, so the quadratic is not identifiable.
2. **A within-text proxy collapses the channel.** Substituting an
   enforcement/penalty-term density computed from the same text gives
   VIF(D_enc, D_dec) ≈ 1.0 here (and would trend to collapse at scale) — it is
   not an independent hop; using it is circular with D_enc.
3. **No non-circular outcome.** Durable-enactment status (enacted AND not
   repealed/struck down) is not returned by the text endpoint; labelling bills
   from their own text would be circular.
4. **Underpowered.** N in this demonstration run is far below any decision
   threshold; even a full-Congress crawl would still fail obstacles 1–3.

The **judicial** variant (clause specificity vs independent enforcement capacity
vs adjudicated durability) is inconclusive for the same reason 1: the
independent enforcement-capacity hop is absent from the corpus.

## Reading
This is precisely the manuscript's "Unlocking the untested domains" position,
now demonstrated on **live** data rather than asserted: legislation and judicial
coupling remain formally untested because the field lacks *linked, independent
two-hop telemetry with a measured, non-circular outcome* — not because a null
was found. Resolving them needs a registered-report partnership with a data
holder (e.g. GAO/agency implementation records + court dockets linked to statute
text), exactly as the manuscript proposes. Reproduce with:

```
# fetch once (endpoint or Vercel MCP), then:
python legislation_coupling_test.py --bills-json legis_bills_raw.json
```
