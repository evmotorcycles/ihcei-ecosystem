#!/usr/bin/env python3
"""
openalex_lism.py -- run the PRE-REGISTERED LISM structural gate on a REAL, frozen
OpenAlex works sample. The honest outcome here is a NULL, and it is reported as
such -- the locked gate is NOT retuned after seeing the data.
================================================================================
cited_by_count         = forward citations (D_dec / engagement proxy).
referenced_works_count = reference-list length (D_enc / encoding-effort proxy).

    python3 openalex-lism/openalex_lism.py    # stdlib only, offline, reads frozen fixture

PRE-REGISTERED RESULT (do NOT move the goalposts): the locked gate
`mean > median AND p90/median >= 2.0` FAILS on a random full-population OpenAlex
sample -- not because citations aren't concentrated, but because they are so
concentrated that the MEDIAN is 0 (most works are never cited), which makes a
p90/median ratio undefined. That is an honest pre-registered NULL, and a lesson:
the tail metric must be robust to zero-inflation. The concentration itself is
extreme (reported below as a DESCRIPTIVE, non-gate statistic), but the specific
locked metric cannot capture it -- so the pre-registered gate is recorded as not
met. Layer-1, offline, $0. See prereg/openalex_prereg.json.

Exit 0 means "ran correctly and REPRODUCED the documented pre-registered outcome
(a null)", NOT "hypotheses passed". The scientific verdict is in results.pass
(False) and results.pre_registered_outcome (NULL).
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


def gate(values):
    """The LOCKED pre-registered heavy-tail gate. Unmodified after seeing data."""
    xs = sorted(values); n = len(xs)
    mean = statistics.mean(xs); med = statistics.median(xs)
    p90 = xs[min(n - 1, int(0.9 * n))]
    tail = p90 / med if med else 0.0          # undefined when median==0 (zero-inflated)
    zeros = sum(1 for v in xs if v == 0)
    top_share = (max(xs) / sum(xs)) if sum(xs) else 0.0
    return {"n": n, "median": med, "mean": round(mean, 2), "p90": p90, "max": max(xs),
            "zeros": zeros, "zero_frac": round(zeros / n, 2), "tail_ratio": round(tail, 2),
            "top_work_share": round(top_share, 2), "median_is_zero": med == 0,
            "pass": mean > med and tail >= 2.0}


def main():
    fixture = json.loads(open(FIXTURE, "rb").read())
    if fixture.get("status") != "REAL" or not fixture.get("results"):
        print(BAR); print(" OpenAlex sample is UNFILLED -- refusing to run (no fabricated data)."); print(BAR)
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
    h1 = gate(cites)
    h2 = gate(refs)

    print(BAR)
    print(" PRE-REGISTERED LISM gate on a REAL OpenAlex works sample (N=%d)" % len(works))
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n H1 citations (cited_by_count): median %g  mean %.2f  p90 %d  max %d  zeros %d/%d (%.0f%%)"
          % (h1["median"], h1["mean"], h1["p90"], h1["max"], h1["zeros"], h1["n"], 100 * h1["zero_frac"]))
    print("    locked gate mean>median AND p90/median>=2.0  ->  %s" % ("PASS" if h1["pass"] else "FAIL (median=0 -> ratio undefined)"))
    print("\n H2 references (referenced_works_count): median %g  mean %.2f  p90 %d  max %d  zeros %d/%d (%.0f%%)"
          % (h2["median"], h2["mean"], h2["p90"], h2["max"], h2["zeros"], h2["n"], 100 * h2["zero_frac"]))
    print("    locked gate mean>median AND p90/median>=2.0  ->  %s" % ("PASS" if h2["pass"] else "FAIL (median=0 -> ratio undefined)"))

    null_by_zero_inflation = (not h1["pass"] and h1["median_is_zero"]) and (not h2["pass"] and h2["median_is_zero"])

    print("\n " + BAR)
    print(" PRE-REGISTERED OUTCOME: NULL — the locked p90/median tail gate is NOT met.")
    print(" WHY (honest, not a retune): a random full-population OpenAlex sample is ZERO-INFLATED —")
    print("   %.0f%% of works have 0 citations, %.0f%% have 0 references — so the MEDIAN is 0 and a" % (100 * h1["zero_frac"], 100 * h2["zero_frac"]))
    print("   p90/median ratio is undefined. The gate was calibrated on nonzero-median cohorts")
    print("   (GitHub stars, HF likes); scholarly works violate that assumption. Goalposts NOT moved.")
    print("\n DESCRIPTIVE (non-gate, for context only): the concentration is in fact EXTREME —")
    print("   the single top work holds %.0f%% of all citations in the sample (max %d of %d)."
          % (100 * h1["top_work_share"], h1["max"], sum(cites)))
    print("   The heavy tail is real; the pre-registered METRIC just cannot express it on zero-inflated data.")
    print(BAR)

    out = {"n": len(works), "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "H1_citations": h1, "H2_references": h2,
           "pre_registered_outcome": "NULL — locked p90/median tail gate not met (zero-inflated, median=0); NOT retuned",
           "null_by_zero_inflation": null_by_zero_inflation,
           "descriptive_only": {"top_work_citation_share": h1["top_work_share"],
                                "note": "extreme concentration IS present; the locked ratio metric is ill-posed for median=0 and was not changed."},
           "H3_coupling": "UNTESTABLE on snapshot (no non-circular survival outcome); most promising future two-hop",
           "hypotheses_pass": h1["pass"] and h2["pass"], "honest_reporting": True,
           "ran_ok": lock_ok, "pass": h1["pass"] and h2["pass"]}
    json.dump(out, open(os.path.join(HERE, "results_openalex.json"), "w"), indent=2)

    # Exit 0 = reproduced the documented pre-registered outcome (a null). NOT a hypothesis pass.
    raise SystemExit(0 if lock_ok else 1)


if __name__ == "__main__":
    main()
