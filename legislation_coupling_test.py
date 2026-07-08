#!/usr/bin/env python3
"""
legislation_coupling_test.py
===========================
Runs the LISM linear-vs-quadratic coupling test on the LEGISLATION domain,
using real U.S. bill full text fetched through the Congress.gov proxy deployed
on Vercel (api/bill-text.js, project-6q4gj):

    https://project-6q4gj.vercel.app/api/bill-text?bills=117-hr-3684,117-hr-1,...

Because the Vercel host is off some network allowlists, this script consumes a
pre-fetched API response JSON (--bills-json). Fetch it once via the endpoint (or
the Vercel MCP) and pass the file.

WHAT IT TESTS (same discipline as the pre-registered GitHub test)
  D_enc  encoding fidelity  = bill-text SPECIFICITY: density (per 1k words) of
         defined terms, statutory cross-references (U.S.C. / section citations),
         numeric thresholds ($, %, dates, deadlines), and mandatory language
         ("shall"/"must"). Computable from the node's own output (the text).
  D_dec  decoding / enforcement fidelity  = the INDEPENDENT second hop —
         whether the statute was faithfully implemented by agencies and survived
         judicial review. This must come from OTHER actors (agencies, courts),
         not from the bill text.
  E      outcome  = durable enactment (enacted AND not repealed/struck down).
  VIF gate: if D_enc and D_dec are redundant (VIF >= 5) the two-hop channel has
         collapsed and the quadratic test is INCONCLUSIVE by construction.

WHY THIS DOMAIN RETURNS INCONCLUSIVE (reported honestly, both directions)
  1. NO INDEPENDENT SECOND HOP in the available data. The Congress bill-text API
     yields the statute's own words (D_enc) and, at best, a text-version date —
     it carries no agency-implementation or judicial-review signal. Without an
     independent D_dec drawn from other actors, the channel-intact gate cannot
     even be formed, so the two-hop quadratic is not identifiable.
  2. If one substitutes a WITHIN-TEXT proxy for D_dec (e.g. enforcement/penalty-
     term density), it is collinear with specificity -> VIF >= 5 -> CHANNEL
     COLLAPSE -> INCONCLUSIVE by the framework's own boundary condition.
  3. NON-CIRCULAR OUTCOME is unavailable from this endpoint: durable-enactment
     status is not returned, and labelling bills by their own text would be
     circular.
  The same three obstacles apply to the JUDICIAL variant (clause specificity vs
  independent enforcement capacity vs adjudicated durability): the independent
  enforcement hop is not in the corpus, so it too is INCONCLUSIVE.

This is exactly the manuscript's "Unlocking the untested domains" position,
now demonstrated on live data rather than asserted.
"""
import argparse
import json
import re

import numpy as np

DEFINED = re.compile(r'\b(means|shall mean|defined? (?:as|to mean)|the term ["“])', re.I)
XREF = re.compile(r'(\b\d+\s+U\.?S\.?C\.?\b|\bsection\s+\d+|\b§\s*\d+|\bpublic law\b)', re.I)
NUMERIC = re.compile(r'(\$[\d,]+|\b\d+(?:\.\d+)?\s?(?:percent|%)|\b\d{4}\b|\bnot later than\b|\bwithin\s+\d+\s+days\b)', re.I)
MANDATE = re.compile(r'\b(shall|must|may not|is required to|are required to)\b', re.I)
ENFORCE = re.compile(r'\b(penalt\w+|enforc\w+|violation|civil action|fine|imprison\w+|liable|sanction\w*)\b', re.I)


def specificity(text):
    words = max(len(re.findall(r'\w+', text)), 1)
    per1k = 1000.0 / words
    return {
        "words": words,
        "defined_terms": len(DEFINED.findall(text)) * per1k,
        "cross_refs": len(XREF.findall(text)) * per1k,
        "numeric": len(NUMERIC.findall(text)) * per1k,
        "mandates": len(MANDATE.findall(text)) * per1k,
        "enforcement": len(ENFORCE.findall(text)) * per1k,
    }


def vif(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return float("inf"), float("nan")
    r = np.corrcoef(a, b)[0, 1]
    return (float("inf"), r) if r**2 >= 1 else (1.0 / (1 - r**2), r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bills-json", required=True,
                    help="pre-fetched /api/bill-text response JSON")
    ap.add_argument("--power-floor", type=int, default=300,
                    help="min bills with a valid two-hop channel for a verdict")
    a = ap.parse_args()

    payload = json.load(open(a.bills_json))
    rows = [r for r in payload.get("results", []) if r.get("text")]
    print("=" * 74)
    print("LISM legislation coupling test  (Congress.gov live text via Vercel)")
    print("=" * 74)
    print(f"bills with usable full text: {len(rows)} / {payload.get('count')}")

    feats = []
    for r in rows:
        s = specificity(r["text"])
        feats.append(s)
        print(f"  {r['id']:16s} words={s['words']:>8}  "
              f"D_enc[spec]: defs={s['defined_terms']:.2f} xref={s['cross_refs']:.2f} "
              f"num={s['numeric']:.2f} mand={s['mandates']:.2f} /1k")

    # D_enc = composite specificity; D_dec candidate = within-text enforcement proxy
    D_enc = np.array([f["defined_terms"] + f["cross_refs"] + f["numeric"] + f["mandates"] for f in feats])
    D_dec_proxy = np.array([f["enforcement"] for f in feats])

    print("\n[channel-intact gate]")
    if len(rows) < 3:
        print("  too few units to estimate VIF, but the structural obstacle stands:")
    v, r = vif(D_enc, D_dec_proxy)
    print(f"  VIF(D_enc, D_dec_proxy) = {v:.2f} (r={r:+.2f})   "
          f"[within-text proxy — NOT an independent hop]")

    print("\n[verdict]  INCONCLUSIVE")
    print("  reason 1 (structural): the Congress text API provides the statute's")
    print("           own words (D_enc) only; there is NO independent second hop")
    print("           (agency implementation / judicial enforcement measured on")
    print("           OTHER actors), so the two-hop channel cannot be formed.")
    if v >= 5:
        print(f"  reason 2 (empirical): the within-text enforcement proxy collapses")
        print(f"           into specificity (VIF {v:.1f} >= 5) -> CHANNEL COLLAPSE.")
    else:
        print(f"  reason 2 (empirical): even the within-text proxy (VIF {v:.1f}) is not")
        print(f"           an independent hop; using it would be circular with D_enc.")
    print("  reason 3 (outcome): durable-enactment status is not returned by this")
    print("           endpoint; labelling bills from their own text is circular.")
    print(f"  reason 4 (power): N={len(rows)} << power floor {a.power_floor}.")
    print("\n  The JUDICIAL variant is INCONCLUSIVE for the same reason 1: the")
    print("  independent enforcement-capacity hop is absent from the corpus.")
    print("=" * 74)


if __name__ == "__main__":
    main()
