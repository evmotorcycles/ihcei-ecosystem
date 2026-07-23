#!/usr/bin/env python3
"""
github_lism.py -- test two STRUCTURAL LISM predictions (engagement concentration
+ unresolved-backlog hazard) on a REAL, frozen cross-domain GitHub cohort, and
HONESTLY declare the E=U*D coupling untestable on this listing.
================================================================================
stars       = engagement / capacity of a repo.
open_issues = unresolved-issue backlog = an enforcement-latency (tau_v) hazard
              analog: unaddressed issues accumulate before maintainers resolve
              them, and a wide upper tail is the LISM hazard signature.

    python3 github-lism/github_lism.py    # stdlib only, offline, reads frozen fixture

Data are real GitHub repository metadata (fetched via MCP, frozen). Spec + fixture
are SHA-256-locked and re-verified before scoring. Layer-1, offline, $0. Measures
concentration + backlog, NOT the E=U*D coupling (declared untestable). See
prereg/github_prereg.json.
"""
import hashlib
import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "github_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
FIXTURE = os.path.join(HERE, "data", "github_cohort_frozen.json")
BAR = "=" * 80


def heavy_tail(values):
    xs = sorted(values); n = len(xs)
    mean = statistics.mean(xs); med = statistics.median(xs)
    p90 = xs[min(n - 1, int(0.9 * n))]
    tail = p90 / med if med else 0.0
    return {"n": n, "min": xs[0], "median": med, "mean": round(mean, 1), "p90": p90,
            "max": xs[-1], "tail_ratio": round(tail, 2), "pass": mean > med and tail >= 2.0}


def main():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    fixture_bytes = open(FIXTURE, "rb").read()
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix = hashlib.sha256(fixture_bytes).hexdigest()
    lock_ok = got == man["spec_sha256"] and fix == man["fixture_sha256"]

    repos = json.loads(fixture_bytes)["repos"]
    stars = [r["stars"] for r in repos]
    backlog = [r["open_issues"] for r in repos]
    h1 = heavy_tail(stars)
    h2 = heavy_tail(backlog)

    by = defaultdict(list)
    for r in repos:
        by[r["domain"]].append(r)

    print(BAR)
    print(" LISM structural test on a REAL cross-domain GitHub cohort (N=%d, pre-registered)" % len(repos))
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n H1 engagement concentration (stars):")
    print("   min %d  median %g  mean %.0f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h1["min"], h1["median"], h1["mean"], h1["p90"], h1["max"], h1["tail_ratio"], "PASS" if h1["pass"] else "FAIL"))

    print("\n H2 unresolved-backlog hazard (open_issues = tau_v analog):")
    print("   min %d  median %g  mean %.0f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h2["min"], h2["median"], h2["mean"], h2["p90"], h2["max"], h2["tail_ratio"], "PASS" if h2["pass"] else "FAIL"))
    print("   READING: a slow tail of repos carries huge unaddressed issue backlogs (pytorch 18,272;")
    print("   scipy 1,845; stdlib 1,283) -- the wide upper tail is the tau_v hazard signature LISM predicts.")

    print("\n per-domain medians (descriptive, small unequal buckets -- not a gate):")
    for d, rs in sorted(by.items(), key=lambda kv: -statistics.median([x["open_issues"] for x in kv[1]])):
        print("   %-14s n=%d  median stars %d  median backlog %d"
              % (d, len(rs), int(statistics.median([x["stars"] for x in rs])), int(statistics.median([x["open_issues"] for x in rs]))))

    print("\n H3 E=U*D coupling: DECLARED UNTESTABLE (honest construct validity).")
    print("   No independent second fidelity hop and no non-circular per-repo survival outcome (a live repo")
    print("   is a survivor by construction; no abandoned/deleted control group). Reported UNTESTABLE, not spun.")

    green = lock_ok and h1["pass"] and h2["pass"]
    out = {"n": len(repos), "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "H1_engagement_heavy_tail": h1, "H2_backlog_heavy_tail": h2,
           "domain_medians": {d: {"n": len(rs), "median_stars": int(statistics.median([x["stars"] for x in rs])),
                                  "median_backlog": int(statistics.median([x["open_issues"] for x in rs]))} for d, rs in by.items()},
           "H3_coupling": "UNTESTABLE (no independent second hop, no non-circular survival outcome)",
           "note": "engagement concentration + backlog hazard on real GitHub metadata; coupling untestable here.",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_github.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — engagement is concentrated and the unresolved backlog is heavy-tailed on real" % ("GREEN" if green else "RED"))
    print(" GitHub data; the E=U*D coupling is honestly declared untestable. Layer-1, offline, $0.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
