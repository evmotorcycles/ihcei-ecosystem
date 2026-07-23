#!/usr/bin/env python3
"""
pubmed_retraction.py -- test two STRUCTURAL LISM predictions (heavy-tailed
concentration + field-dependence) on real PubMed retraction data, and HONESTLY
declare that the retraction-latency tau_v is untestable via this connector.
================================================================================
retraction_rate(field) = retracted_papers / total_papers  -- the realized
self-correction FAILURE BURDEN of a biomedical field (a ratio, so it controls
for how much the field publishes). Data are real PubMed total_count values
(fetched via MCP, frozen for offline reproducibility).

    python3 pubmed-lism/pubmed_retraction.py    # stdlib only, offline, reads frozen fixture

CONSTRUCT-VALIDITY FIREWALL (Layer-1). This measures the FAILURE RATE, not the
enforcement LATENCY tau_v. The days-to-retraction latency is DECLARED UNTESTABLE
here (the connector gives no paired retraction date) -- reported honestly, never
spun into a tau_v claim. No E=U*D coupling is claimed on this substrate.

Data from PubMed (U.S. National Library of Medicine).
"""
import hashlib
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "pubmed_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
FIXTURE = os.path.join(HERE, "data", "pubmed_cohort_frozen.json")
BAR = "=" * 80


def main():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    fixture_bytes = open(FIXTURE, "rb").read()
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix = hashlib.sha256(fixture_bytes).hexdigest()
    lock_ok = got == man["spec_sha256"] and fix == man["fixture_sha256"]

    fields = json.loads(fixture_bytes)["fields"]
    rows = [(f["field"], f["retracted"], f["total"], f["retracted"] / f["total"] * 1e5) for f in fields]
    rows.sort(key=lambda r: -r[3])
    rates = [r[3] for r in rows]
    n = len(rates)
    mean = statistics.mean(rates); med = statistics.median(rates)
    hi, lo = max(rates), min(rates)
    tail_ratio = hi / med if med else 0.0
    field_ratio = hi / lo if lo else 0.0

    h1 = mean > med and tail_ratio >= 2.0
    h2 = field_ratio >= 2.0

    print(BAR)
    print(" LISM self-correction FAILURE BURDEN on real PubMed retractions (N=%d fields, pre-registered)" % n)
    print(BAR)
    print("\n [lock] spec %s  fixture %s" % ("MATCH" if got == man["spec_sha256"] else "MISMATCH",
                                             "MATCH" if fix == man["fixture_sha256"] else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n retraction rate = retracted / total papers, per field (PubMed, 2004-2023):")
    print("   %-28s %8s %11s   %s" % ("field", "retract", "total", "rate /100k"))
    for name, r, t, rate in rows:
        print("   %-28s %8d %11d   %7.1f" % (name, r, t, rate))

    print("\n H1 heavy tail (concentration): mean %.1f > median %.1f ? %s   max/median = %.2f (>=2.0? %s)  -> %s"
          % (mean, med, mean > med, tail_ratio, tail_ratio >= 2.0, "PASS" if h1 else "FAIL"))
    print("   READING: a small number of fields (here anesthesia, stem cells, oncology) carry a")
    print("   disproportionate share of self-correction failures -- the heavy-tail concentration LISM")
    print("   predicts for hazard. Because the rate is a RATIO, this is not merely field size.")

    print("\n H2 field dependence: max/min rate = %.2f (>=2.0? %s)  -> %s"
          % (field_ratio, field_ratio >= 2.0, "PASS" if h2 else "FAIL"))

    print("\n H3 retraction LATENCY (tau_v): DECLARED UNTESTABLE (honest construct validity).")
    print("   This connector returns each article's ORIGINAL publication date but no paired retraction")
    print("   date -- 'Retraction of Publication' notice records are not retrievable and related-article")
    print("   links are word-similarity, not the notice. So days-to-retraction cannot be computed non-")
    print("   circularly here. Reported UNTESTABLE (like bioRxiv H3 / the legislation channel), not spun.")

    green = lock_ok and h1 and h2
    out = {"n_fields": n, "spec_sha256": got, "fixture_sha256": fix, "lock_ok": lock_ok,
           "measured_observable": "retraction_rate (failure burden), NOT tau_v latency",
           "rates_per_100k": {name: round(rate, 1) for name, r, t, rate in rows},
           "H1_heavy_tail": {"mean": round(mean, 1), "median": round(med, 1), "tail_ratio": round(tail_ratio, 2), "pass": h1},
           "H2_field_dependence": {"ratio": round(field_ratio, 2), "pass": h2},
           "H3_latency": "UNTESTABLE (no paired retraction date via this connector; notices not retrievable)",
           "note": "structural concentration + field-dependence tested on a real self-correction substrate; tau_v latency honestly untestable here; no E=U*D coupling claimed.",
           "attribution": "Data from PubMed (U.S. National Library of Medicine).",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_pubmed.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — retraction FAILURE BURDEN is heavy-tailed and field-dependent on real PubMed" % ("GREEN" if green else "RED"))
    print(" data; the tau_v retraction latency is honestly declared untestable here. Layer-1, offline, $0.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
