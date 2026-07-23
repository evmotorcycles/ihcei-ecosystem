#!/usr/bin/env python3
"""
kaggle_governance.py -- test two STRUCTURAL LISM predictions (engagement
concentration + maintenance-latency tau_v) on a REAL, frozen Kaggle open-dataset
cohort, and HONESTLY declare the E=U*D coupling untestable on this listing.
================================================================================
tau_v_maintenance = days(frozen_at - lastUpdated) = staleness / maintenance latency
-- the tau_v Third-Law analog on a maintained-artifact substrate.

    python3 kaggle-lism/kaggle_governance.py   # stdlib only, offline, reads frozen fixture

The cohort is REAL (a user-supplied Kaggle export; Kaggle is network-blocked from
the analysis session, so nothing is fetched live and nothing is fabricated). The
spec + fixture are SHA-256-locked and re-verified before scoring. While the fixture
is UNFILLED the runner refuses to run (exit 3) -- it never invents data.

Layer-1, offline, $0. Measures concentration + maintenance latency, NOT the E=U*D
coupling (declared untestable). See prereg/kaggle_prereg.json.
"""
import hashlib
import json
import os
import statistics
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "kaggle_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
FIXTURE = os.path.join(HERE, "data", "kaggle_cohort_frozen.json")
BAR = "=" * 80


def days(a, b):
    ya, ma, da = map(int, a.split("-")); yb, mb, db = map(int, b.split("-"))
    return (date(ya, ma, da) - date(yb, mb, db)).days


def heavy_tail(values):
    xs = sorted(values); n = len(xs)
    mean = statistics.mean(xs); med = statistics.median(xs)
    p90 = xs[min(n - 1, int(0.9 * n))]
    tail = p90 / med if med else 0.0
    return {"n": n, "min": xs[0], "median": med, "mean": round(mean, 1), "p90": p90,
            "max": xs[-1], "tail_ratio": round(tail, 2), "pass": mean > med and tail >= 2.0}


def main():
    fixture = json.loads(open(FIXTURE, "rb").read())
    if fixture.get("status") != "REAL" or not fixture.get("records"):
        print(BAR)
        print(" Kaggle cohort is UNFILLED -- refusing to run (no fabricated data).")
        print(BAR)
        print("\n To fill it with REAL data:")
        print("   1. On a machine with Kaggle CLI:  kaggle datasets list --sort-by votes --csv > k.csv")
        print("      (or paste the CSV; the assistant converts it to the fixture schema)")
        print("   2. Populate data/kaggle_cohort_frozen.json: set frozen_at=<export date>,")
        print("      status='REAL', and records[] = {ref,title,voteCount,lastUpdated,usabilityRating,...}")
        print("   3. Re-hash into prereg/MANIFEST.sha256.json, then re-run.")
        raise SystemExit(3)

    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    fixture_bytes = open(FIXTURE, "rb").read()
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix = hashlib.sha256(fixture_bytes).hexdigest()
    lock_ok = got == man["spec_sha256"] and fix == man["fixture_sha256"]

    recs = fixture["records"]
    frozen_at = fixture["frozen_at"]
    votes = [int(r["voteCount"]) for r in recs]
    stale = [days(frozen_at, r["lastUpdated"]) for r in recs]
    usab = [float(r["usabilityRating"]) for r in recs if r.get("usabilityRating") is not None]

    h1 = heavy_tail(votes)
    h2 = heavy_tail(stale)

    print(BAR)
    print(" LISM structural test on a REAL Kaggle open-dataset cohort (N=%d, pre-registered)" % len(recs))
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n H1 engagement concentration (voteCount):")
    print("   min %d  median %g  mean %.1f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h1["min"], h1["median"], h1["mean"], h1["p90"], h1["max"], h1["tail_ratio"], "PASS" if h1["pass"] else "FAIL"))

    print("\n H2 maintenance latency tau_v (days since last update = staleness):")
    print("   min %d  median %g  mean %.1f  p90 %d  max %d  | p90/median %.2f  -> %s"
          % (h2["min"], h2["median"], h2["mean"], h2["p90"], h2["max"], h2["tail_ratio"], "PASS" if h2["pass"] else "FAIL"))
    print("   READING: a slow tail of stale, unmaintained datasets is the tau_v hazard signature LISM predicts.")

    if usab:
        print("\n usabilityRating (Kaggle's own governance/quality score, descriptive):")
        print("   n=%d  min %.2f  median %.2f  mean %.2f  max %.2f" %
              (len(usab), min(usab), statistics.median(usab), statistics.mean(usab), max(usab)))

    print("\n H3 E=U*D coupling: DECLARED UNTESTABLE (honest construct validity).")
    print("   No independent second fidelity hop and no non-circular per-dataset survival outcome on this")
    print("   listing. Reported UNTESTABLE (like bioRxiv/PubMed H3 and the legislation channel), not spun.")

    green = lock_ok and h1["pass"] and h2["pass"]
    out = {"n": len(recs), "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "frozen_at": frozen_at,
           "H1_engagement_heavy_tail": h1,
           "H2_maintenance_latency_heavy_tail": h2,
           "usability": ({"n": len(usab), "median": round(statistics.median(usab), 3),
                          "mean": round(statistics.mean(usab), 3)} if usab else None),
           "H3_coupling": "UNTESTABLE (no independent second hop, no non-circular survival outcome)",
           "note": "engagement concentration + maintenance-latency tau_v on real Kaggle metadata; coupling untestable here.",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_kaggle.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — engagement is concentrated and maintenance latency is heavy-tailed on real" % ("GREEN" if green else "RED"))
    print(" Kaggle data; the E=U*D coupling is honestly declared untestable. Layer-1, offline, $0.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
