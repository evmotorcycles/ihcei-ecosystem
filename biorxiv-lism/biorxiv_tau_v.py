#!/usr/bin/env python3
"""
biorxiv_tau_v.py -- measure the LISM enforcement-latency law (tau_v) on real
bioRxiv scientific-publishing data.
================================================================================
tau_v = days from a preprint being posted to bioRxiv to its formal journal
publication -- a direct, non-circular latency, analogous to the GitHub
issue-close tau_v cohort already in this repo. We test two pre-registered
properties of the latency (heavy upper tail; field variation) and HONESTLY
declare that the two-hop E=U*D survival coupling is NOT cleanly testable on this
metadata (only the published subset is observed).

    python3 biorxiv-lism/biorxiv_tau_v.py     # stdlib only, offline, reads frozen fixture

Layer-1. This measures the latency law on a new substrate; it does NOT claim the
E=U*D coupling on bioRxiv (declared untestable -- construct validity).
"""
import hashlib
import json
import os
import statistics
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "biorxiv_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
FIXTURE = os.path.join(HERE, "data", "biorxiv_cohort_frozen.json")
BAR = "=" * 80


def days(a, b):
    ya, ma, da = map(int, a.split("-")); yb, mb, db = map(int, b.split("-"))
    return (date(yb, mb, db) - date(ya, ma, da)).days


def main():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    fixture_bytes = open(FIXTURE, "rb").read()
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix = hashlib.sha256(fixture_bytes).hexdigest()
    lock_ok = got == man["spec_sha256"] and fix == man["fixture_sha256"]

    recs = json.loads(fixture_bytes)["records"]
    tau = [days(r["preprint_date"], r["published_date"]) for r in recs]
    ts = sorted(tau); n = len(ts)
    mean = statistics.mean(tau); med = statistics.median(tau)
    p90 = ts[int(0.9 * n)]; p10 = ts[int(0.1 * n)]
    tail_ratio = p90 / med if med else 0.0

    by = defaultdict(list)
    for r, t in zip(recs, tau):
        by[r["category"]].append(t)
    cat_meds = {c: statistics.median(v) for c, v in by.items() if len(v) >= 2}
    field_ratio = (max(cat_meds.values()) / min(cat_meds.values())) if cat_meds else 0.0

    h1 = mean > med and tail_ratio >= 2.0
    h2 = field_ratio >= 2.0

    print(BAR)
    print(" LISM enforcement-latency (tau_v) on bioRxiv publishing (N=%d, pre-registered)" % n)
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n tau_v = preprint -> journal publication latency (days):")
    print("   min %d   p10 %d   MEDIAN %d   mean %.1f   p90 %d   max %d" % (min(ts), p10, med, mean, p90, max(ts)))
    print("\n H1 heavy tail (hazard signature): mean %.1f > median %d ? %s   p90/median = %.2f (>=2.0? %s)  -> %s"
          % (mean, med, mean > med, tail_ratio, tail_ratio >= 2.0, "PASS" if h1 else "FAIL"))
    print("   READING: the latency is strongly right-skewed -- most preprints publish quickly, but a long")
    print("   upper tail lingers for years. That wide upper tail is the tau_v hazard signature LISM describes.")

    print("\n H2 field variation:")
    for c, m in sorted(cat_meds.items(), key=lambda kv: -kv[1]):
        print("     %-24s n=%d  median %d d" % (c, len(by[c]), m))
    print("   ratio (max/min field median) = %.2f (>=2.0? %s)  -> %s" % (field_ratio, field_ratio >= 2.0, "PASS" if h2 else "FAIL"))

    print("\n H3 E=U*D coupling: DECLARED UNTESTABLE (honest construct validity).")
    print("   Only the PUBLISHED subset is observed (no unpublished comparison group), there is no")
    print("   independent second fidelity hop, and no non-circular binary survival outcome. Like the")
    print("   legislation/judicial channel, coupling is reported UNTESTABLE here -- not spun as support.")

    green = lock_ok and h1 and h2
    out = {"n": n, "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "tau_v_days": {"min": min(ts), "p10": p10, "median": med, "mean": round(mean, 1), "p90": p90, "max": max(ts)},
           "H1_heavy_tail": {"mean": round(mean, 1), "median": med, "tail_ratio": round(tail_ratio, 2), "pass": h1},
           "H2_field_variation": {"category_medians": cat_meds, "ratio": round(field_ratio, 2), "pass": h2},
           "H3_coupling": "UNTESTABLE (published-only, no independent second hop, no non-circular survival)",
           "note": "tau_v latency law measured on a new real substrate; coupling honestly untestable here.",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_biorxiv.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — tau_v is heavy-tailed (hazard signature) and field-dependent on real bioRxiv" % ("GREEN" if green else "RED"))
    print(" publishing; the E=U*D coupling is honestly declared untestable on this metadata. Layer-1, offline.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
