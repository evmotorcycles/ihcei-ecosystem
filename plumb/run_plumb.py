#!/usr/bin/env python3
"""Run the pre-registered Plumb experiments and write plumb/results_plumb.json.

    python3 plumb/run_plumb.py

Cohort A (22 real Qwen/DeepSeek repos)  -- DESCRIPTIVE ONLY, see PREREG.md B.
Cohort B (28 real GitHub repos)         -- pre-registered out-of-sample, P5-P7.
Negative control                        -- must HALT (P2).
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plumb import parse, run  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "ei-dashboards/data/qwen_deepseek_frozen.json")
B = os.path.join(ROOT, "github-lism/data/github_cohort_frozen.json")
VENDOR = os.path.join(ROOT, "plumb/examples/vendor.plumb")
COLLAPSED = os.path.join(ROOT, "plumb/examples/collapsed.plumb")


def load(path):
    return json.load(open(path))["repos"]


def summarise(res):
    vs = res["verdicts"]
    return {
        "records": res["audit"]["records"],
        "supported": sum(1 for v in vs if v["verdict"] == "SUPPORTED"),
        "abstained": sum(1 for v in vs if v["verdict"] == "ABSTAIN"),
        "vif": res["audit"].get("vif"),
        "independent": res["audit"].get("independent"),
        "halted": res["audit"]["halted"],
        "blind_fields": res["audit"]["blind_fields"],
        "blind_values_stripped": res["audit"]["blind_values_stripped"],
    }


def main():
    src = open(VENDOR).read()
    a = summarise(run(parse(src), load(A)))
    b = summarise(run(parse(src), load(B)))
    neg = summarise(run(parse(open(COLLAPSED).read()), load(A)))

    b_abstain_rate = b["abstained"] / b["records"]
    out = {
        "_prereg_lock": json.load(open(os.path.join(ROOT, "plumb/prereg.lock.json"))),
        "_program_sha256": hashlib.sha256(open(VENDOR, "rb").read()).hexdigest(),
        "cohort_A_descriptive_only": a,
        "cohort_B_out_of_sample": b,
        "negative_control_expected_halt": neg,
        "prereg_outcomes": {
            "P5_independence_transfers": {
                "gate": "cohort B VIF finite and < 5.0",
                "measured": b["vif"],
                "result": "HOLDS" if isinstance(b["vif"], float) and b["vif"] < 5.0 else "FALSIFIED",
            },
            "P6_abstention_dominates": {
                "gate": "cohort B abstain rate >= 0.50 (informed by cohort A)",
                "measured": round(b_abstain_rate, 4),
                "result": "HOLDS" if b_abstain_rate >= 0.50 else "FALSIFIED",
            },
            "P7_no_silent_drop": {
                "gate": "supported + abstained == records",
                "measured": b["supported"] + b["abstained"],
                "result": "HOLDS" if b["supported"] + b["abstained"] == b["records"] else "FALSIFIED",
            },
        },
        "_honest_notes": [
            "Cohort A numbers are DESCRIPTIVE. They were measured before PREREG.md "
            "was written and carry no confirmatory weight.",
            "blind_values_stripped is 0 on cohort B because that cohort has no "
            "'description' or 'topics' columns at all. The blinding did not fail; "
            "there was nothing to blind. P1 is therefore tested on cohort A and on "
            "a synthetic poisoned record, NOT on cohort B.",
            "The high abstain rate on BOTH cohorts is a property of the "
            "1/(1+open_issues) transform saturating for large projects. It is not "
            "evidence that those projects are bad. The floor was not moved.",
            "Plumb checks structure, not truth. Q2 and Q5 of the five governance "
            "questions are not resolved here or anywhere in this repository.",
        ],
    }
    path = os.path.join(ROOT, "plumb/results_plumb.json")
    open(path, "w").write(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["prereg_outcomes"], indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
