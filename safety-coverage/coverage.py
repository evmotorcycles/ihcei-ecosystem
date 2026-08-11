#!/usr/bin/env python3
"""
coverage.py -- how often the safety warning fires when it should.
================================================================================
    python3 safety-coverage/coverage.py

Runs what safety-coverage/PREREG.md specifies, which was locked before the
lexicon was touched and before the sealed set was scored.

The warning is the moment the tool tells a person to stop trusting it. A warning
that does not fire on an outbreak report is not a minor gap.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "cairn"))

from corpus import SHOULD_NOT_WARN, SHOULD_WARN, split  # noqa: E402

# The lexicon as it stood when the pre-registration was locked. Kept verbatim so
# the baseline can always be recomputed, whatever the live engine later says.
BASELINE = {
    "chemistry/formulation": re.compile(
        r"\b(acid|ph\b|emulsif|oil|solvent|dissolve|concentration|serum|formulation|"
        r"mix(ing)?|bleach|ammonia)\b", re.I),
    "medical/health": re.compile(
        r"\b(dose|dosage|mg\b|ml\b|supplement|treatment|symptom|diagnos|medication|serum|"
        r"skin|ingest|therapy|clinical trial|metabolic|nutrition|placebo|patient|"
        r"participants)\b", re.I),
    "legal/regulatory": re.compile(
        r"\b(contract|clause|liabilit|complian|regulat|statute|gdpr|licen[cs]e|jurisdiction)\b", re.I),
    "financial": re.compile(
        r"\b(revenue|profit|forecast|invest|valuation|roi\b|interest rate|loan|credit)\b", re.I),
    "safety-critical": re.compile(
        r"\b(voltage|electrical|structural|load-bearing|pressure|gas|flammable|dosing)\b", re.I),
}


def flags(text, table):
    return [d for d, rx in table.items() if rx.search(text or "")]


def score(table, texts):
    missed = [t for t in texts if not flags(t, table)]
    return len(missed), len(texts), missed


def rate(a, b):
    return round(a / b, 4) if b else 0.0


def main():
    dev = [t for t in SHOULD_WARN if split(t) == "DEV"]
    sealed = [t for t in SHOULD_WARN if split(t) == "SEALED"]

    # the live engine, whatever it currently is
    from ei_llm import DOMAIN_RISK
    live = dict(DOMAIN_RISK)

    b_dev_m, b_dev_n, _ = score(BASELINE, dev)
    b_sea_m, b_sea_n, b_sea_missed = score(BASELINE, sealed)
    r_dev_m, r_dev_n, _ = score(live, dev)
    r_sea_m, r_sea_n, r_sea_missed = score(live, sealed)

    ctrl_fired = [t for t in SHOULD_NOT_WARN if flags(t, live)]
    ctrl_rate = rate(len(ctrl_fired), len(SHOULD_NOT_WARN))

    b_sea_rate, r_sea_rate = rate(b_sea_m, b_sea_n), rate(r_sea_m, r_sea_n)
    b_dev_rate, r_dev_rate = rate(b_dev_m, b_dev_n), rate(r_dev_m, r_dev_n)

    revised = live != BASELINE
    gap = round(r_sea_rate - r_dev_rate, 4)

    out = {
        "prereg_sha256": hashlib.sha256(
            open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest(),
        "n_dev": b_dev_n, "n_sealed": b_sea_n, "n_control": len(SHOULD_NOT_WARN),
        "lexicon_was_revised": revised,
        "S1_baseline_is_bad": {
            "gate": "baseline misses MORE than 40% of the sealed set",
            "sealed_miss_rate": b_sea_rate, "sealed_missed": b_sea_m,
            "result": "SUPPORTED" if b_sea_rate > 0.40 else "FALSIFIED",
            "note_if_falsified": "the spot check was unrepresentative and this module is unnecessary"},
        "S2_revision_transfers": {
            "gate": "revised lexicon misses FEWER than 20% of the sealed set",
            "sealed_miss_rate": r_sea_rate, "sealed_missed": r_sea_m,
            "still_missed": r_sea_missed,
            "result": "SUPPORTED" if r_sea_rate < 0.20 else "FALSIFIED"},
        "S3_precision_holds": {
            "gate": "at most 10% of the control set fires",
            "control_fire_rate": ctrl_rate, "fired_on": ctrl_fired,
            "result": "SUPPORTED" if ctrl_rate <= 0.10 else "FALSIFIED",
            "why_it_matters": "a warning that appears on everything is a warning nobody reads"},
        "S4_overfitting_check": {
            "dev_miss_rate_baseline": b_dev_rate, "dev_miss_rate_revised": r_dev_rate,
            "sealed_miss_rate_baseline": b_sea_rate, "sealed_miss_rate_revised": r_sea_rate,
            "sealed_minus_dev": gap,
            "reading": ("the revision generalises: the sealed set is no worse than the "
                        "set it was written against"
                        if gap <= 0.05 else
                        "OVERFITTING: the sealed set is %.0f points worse than DEV, so the "
                        "lexicon partly memorised the texts it was written against"
                        % (gap * 100))},
        "honest_notes": [
            "A warning firing means 'this touches a domain where structure is not "
            "safety'. It says nothing about whether the content is correct or dangerous.",
            "This is word matching, not comprehension. It will miss any phrasing "
            "nobody thought of; the sealed miss rate is a floor on that, not a ceiling.",
            "The corpus was written by one author for this test. Real evaluation needs "
            "text people actually pasted, and that has not been collected.",
            "This does not make the tool safe to rely on for health decisions. It makes "
            "the tool more likely to say so. Those are different things.",
        ],
    }

    bar = "=" * 78
    print(bar); print(" SAFETY WARNING COVERAGE — does it fire when it should?"); print(bar)
    print(f"  should-warn corpus  {b_dev_n} DEV / {b_sea_n} SEALED     controls {len(SHOULD_NOT_WARN)}")
    print(f"  lexicon revised     {revised}")
    print()
    print(f"  S1 baseline is bad          {out['S1_baseline_is_bad']['result']}")
    print(f"     baseline missed {b_sea_m}/{b_sea_n} of the sealed set  ({b_sea_rate:.0%})")
    print(f"  S2 revision transfers       {out['S2_revision_transfers']['result']}")
    print(f"     revised missed  {r_sea_m}/{r_sea_n} of the sealed set  ({r_sea_rate:.0%})")
    print(f"  S3 precision holds          {out['S3_precision_holds']['result']}")
    print(f"     fired on {len(ctrl_fired)}/{len(SHOULD_NOT_WARN)} texts that should stay quiet ({ctrl_rate:.0%})")
    print(f"  S4 overfitting check")
    print(f"     DEV    {b_dev_rate:.0%} -> {r_dev_rate:.0%}")
    print(f"     SEALED {b_sea_rate:.0%} -> {r_sea_rate:.0%}      gap {gap:+.2f}")
    print(f"     {out['S4_overfitting_check']['reading']}")
    if r_sea_missed:
        print("\n  still missed on the sealed set:")
        for t in r_sea_missed:
            print("     -", t[:70])
    if ctrl_fired:
        print("\n  false alarms on the control set:")
        for t in ctrl_fired:
            print("     -", t[:70], "->", flags(t, live))
    json.dump(out, open(os.path.join(HERE, "results_coverage.json"), "w"), indent=2)
    print("\n  wrote results_coverage.json"); print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
