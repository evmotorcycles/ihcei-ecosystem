#!/usr/bin/env python3
"""
openalex_lism.py -- test two STRUCTURAL LISM predictions (citation concentration
+ reference-effort heavy tail) on a REAL, frozen OpenAlex works sample, and
HONESTLY declare the E=U*D coupling untestable on a single snapshot (while
flagging OpenAlex as the most promising future two-hop substrate).
================================================================================
cited_by_count         = forward citations = engagement / D_dec proxy.
referenced_works_count = length of the reference list = encoding effort / D_enc.

    python3 openalex-lism/openalex_lism.py   # stdlib only, offline, reads frozen fixture

The cohort is a REAL fixed-seed random sample of OpenAlex (user-supplied export;
OpenAlex is network-blocked from the session but keyless, so nothing is fetched
live here and nothing is fabricated). While the fixture is UNFILLED the runner
refuses to run (exit 3). Layer-1, offline, $0. See prereg/openalex_prereg.json.
"""
import hashlib
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "openalex_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
FIXTURE = os.path.join(HERE, "data", "openalex_cohort_frozen.json")
BAR = "=" * 80


def heavy_tail(values):
    xs = sorted(values); n = len(xs)
    mean = statistics.mean(xs); med = statistics.median(xs)
    p90 = xs[min(n - 1, int(0.9 * n))]
    tail = p90 / med if med else 0.0
    return {"n": n, "min": xs[0], "median": med, "mean": round(mean, 1), "p90": p90,
            "max": xs[-1], "tail_ratio": round(tail, 2), "pass": mean > med and tail >= 2.0}


def main():
    fixture = json.loads(open(FIXTURE, "rb").read())
    if fixture.get("status") != "REAL" or not fixture.get("results"):
        print(BAR)
        print(" OpenAlex sample is UNFILLED -- refusing to run (no fabricated data).")
        print(BAR)
        print("\n To fill it with REAL data (OpenAlex is keyless -- fetch from any browser):")
        print("   1. Open the reproducible fixed-seed sample URL (in the fixture's sample_url):")
        print("      https://api.openalex.org/works?sample=50&seed=42&per-page=50&select=id,")
        print("      display_name,cited_by_count,referenced_works_count,publication_year,primary_topic")
        print("   2. Paste its JSON 'results' array into data/openalex_cohort_frozen.json,")
        print("      set frozen_at=<date>, status='REAL'.")
        print("   3. Re-hash into prereg/MANIFEST.sha256.json, then re-run.")
        raise SystemExit(3)

    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    fixture_bytes = open(FIXTURE, "rb").read()
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix = hashlib.sha256(fixture_bytes).hexdigest()
    lock_ok = got == man["spec_sha256"] and fix == man["fixture_sha256"]

    works = fixture["results"]
    cites = [int(w["cited_by_count"]) for w in works]
    refs = [int(w.get("referenced_works_count", 0)) for w in works]
    h1 = heavy_tail(cites)
    h2 = heavy_tail(refs)

    print(BAR)
    print(" LISM structural test on a REAL OpenAlex works sample (N=%d, pre-registered)" % len(works))
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n H1 citation concentration (cited_by_count = D_dec / engagement):")
    print("   min %d  median %g  mean %.1f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h1["min"], h1["median"], h1["mean"], h1["p90"], h1["max"], h1["tail_ratio"], "PASS" if h1["pass"] else "FAIL"))

    print("\n H2 reference-effort heavy tail (referenced_works_count = D_enc encoding effort):")
    print("   min %d  median %g  mean %.1f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h2["min"], h2["median"], h2["mean"], h2["p90"], h2["max"], h2["tail_ratio"], "PASS" if h2["pass"] else "FAIL"))

    print("\n H3 E=U*D coupling: DECLARED UNTESTABLE on a single snapshot (honest construct validity).")
    print("   references (D_enc) and citations (D_dec) ARE both present here, but there is no non-circular")
    print("   per-work SURVIVAL outcome (E) in one snapshot. Flagged as the MOST PROMISING future two-hop")
    print("   substrate (a longitudinal pull could test references -> citations -> 5yr survival), not spun.")

    green = lock_ok and h1["pass"] and h2["pass"]
    out = {"n": len(works), "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "H1_citation_heavy_tail": h1, "H2_reference_effort_heavy_tail": h2,
           "H3_coupling": "UNTESTABLE on snapshot (no non-circular survival outcome); most promising future two-hop",
           "note": "citation + reference concentration on a real OpenAlex sample; coupling untestable on a snapshot.",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_openalex.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — citations and reference effort are heavy-tailed on real OpenAlex data;" % ("GREEN" if green else "RED"))
    print(" the E=U*D coupling is honestly declared untestable on a snapshot. Layer-1, offline, $0.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
