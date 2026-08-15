#!/usr/bin/env python3
"""audit.py -- check a keel run from the outside, in Python and in Plumb.

    python3 keel/audit.py <ledger.json>
    python3 keel/audit.py --demo

The kernel is JavaScript. This is deliberately not: an auditor that shares the
kernel's code shares the kernel's blind spots, and would agree with it about a
mistake they both make. This reads the ledger the kernel produced, re-derives
the seals itself, and checks six obligations against the record rather than
against the running program.

The numeric half then goes through keel/run.plumb, which asks a different
question -- not "did the kernel behave" but "is this run governed at all, or
merely logged". Both legs of that have to be non-zero or the product is zero.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "plumb"))

ZERO = "0" * 64


def reseal(entry):
    body = {k: v for k, v in entry.items() if k != "seal"}
    return hashlib.sha256(json.dumps(body, separators=(",", ":")).encode()).hexdigest()


def check(entries):
    """Six obligations, checked against the record and not against the code."""
    out = {}

    # O1 -- every decision is written down, whatever it was.
    outcomes = [e.get("outcome") for e in entries]
    out["O1_every_decision_recorded"] = {
        "gate": "an admitted action is recorded exactly as loudly as a refused one",
        "admitted": outcomes.count("ADMITTED"), "held": outcomes.count("HELD"),
        "refused": outcomes.count("REFUSED"),
        "unnamed": sum(1 for o in outcomes if o not in ("ADMITTED", "HELD", "REFUSED")),
        "result": "HOLDS" if all(o in ("ADMITTED", "HELD", "REFUSED") for o in outcomes)
                  else "FAILS",
    }

    # O2 -- the chain. Re-derived here, not trusted from the kernel.
    broken, prev = None, ZERO
    for i, e in enumerate(entries):
        if e.get("prev") != prev or reseal(e) != e.get("seal"):
            broken = i
            break
        prev = e["seal"]
    out["O2_chain_intact"] = {
        "gate": "editing any past decision breaks every seal after it",
        "entries": len(entries), "broken_at": broken,
        "result": "HOLDS" if broken is None else "FAILS",
    }

    # O3 -- nothing is admitted without naming the rule that allowed it.
    ruleless = [e for e in entries if e.get("outcome") == "ADMITTED" and not e.get("rule")]
    out["O3_admissions_name_their_rule"] = {
        "gate": "no action is admitted by nobody in particular",
        "ruleless": len(ruleless),
        "result": "HOLDS" if not ruleless else "FAILS",
    }

    # O4 -- every refusal says why. A refusal with no reason is a dead end.
    silent = [e for e in entries if e.get("outcome") in ("REFUSED", "HELD") and not e.get("why")]
    out["O4_refusals_give_a_reason"] = {
        "gate": "a person can disagree with any stop, because it says what it was",
        "silent": len(silent),
        "result": "HOLDS" if not silent else "FAILS",
    }

    # O5 -- the escalation is not arbitrary.
    def expected(e):
        if e.get("outcome") == "REFUSED":
            return "STOP"
        if e.get("outcome") == "HELD":
            high = {"medical/health", "safety-critical", "financial", "legal/regulatory"}
            return "STOP" if set(e.get("domains") or []) & high else "BATCH"
        return "LEDGER"
    wrong = [e for e in entries if e.get("tier") != expected(e)]
    out["O5_escalation_follows_the_rule"] = {
        "gate": "what interrupts a person is decided by a rule, not by mood",
        "misfiled": len(wrong),
        "result": "HOLDS" if not wrong else "FAILS",
    }

    # O6 -- a count never travels without what it counted.
    held = [e for e in entries if e.get("outcome") == "HELD"]
    bare = [e for e in held if e.get("found") and not e.get("missing")]
    out["O6_counts_carry_their_handles"] = {
        "gate": "'3 of 5' must name which three, or the reader cannot check any of them",
        "held": len(held), "bare_counts": len(bare),
        "result": "HOLDS" if not bare else "FAILS",
    }

    out["verdict"] = "GOVERNED" if all(v["result"] == "HOLDS" for k, v in out.items()
                                       if k.startswith("O")) else "NOT GOVERNED"
    return out


def to_plumb_record(entries):
    """One record for keel/run.plumb. The two legs must not read the same column."""
    attempted = len(entries)
    sealed = sum(1 for e in entries if e.get("seal"))
    reasoned = sum(1 for e in entries if e.get("why") and e.get("outcome"))
    return {"actions": attempted, "attempted": attempted, "sealed": sealed,
            "reasoned": reasoned,
            # deleted before evaluation by the `blind` clauses -- present here on
            # purpose, so the blinding has something to actually remove
            "self_report": "this run was fine", "summary": "all good"}


def run_plumb(records):
    from plumb import parse, run                                    # noqa: PLC0415
    prog = parse(open(os.path.join(HERE, "run.plumb"), encoding="utf-8").read())
    return run(prog, records)


DEMO = os.path.join(HERE, "fixtures", "demo_ledger.json")


def main(argv):
    path = DEMO if ("--demo" in argv or len(argv) < 2) else argv[1]
    entries = json.load(open(path, encoding="utf-8"))
    report = check(entries)
    print(json.dumps(report, indent=2))
    print()
    for name, v in report.items():
        if name.startswith("O"):
            print(f"  {v['result']:<6} {name}")
    print(f"\n  {report['verdict']}")
    return 0 if report["verdict"] == "GOVERNED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
