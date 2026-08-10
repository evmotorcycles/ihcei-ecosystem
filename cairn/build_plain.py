#!/usr/bin/env python3
"""build_plain.py -- render cairn/plain.html, the plain-language browser app.

The four tools are generated from the MEASURED results (results_ci.json), and the
claim-checker is the JS port of ei_llm.py, inlined. Nothing is fetched at run time:
the output is a single self-contained file that works from file:// with no server,
no account and no network.

    python3 cairn/build_plain.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ci = json.load(open(os.path.join(HERE, "results_ci.json")))
cal = ci["C1_calibration"]
engine = open(os.path.join(HERE, "ei_engine.js")).read()
readers = open(os.path.join(os.path.dirname(HERE), "readers/readers.js")).read()

# The permission list, in the words an ordinary person would use for it.
RULES = [
    {"glob": "projects/**", "plain": "Read anything in your projects folder",
     "allow": True, "limit": "—"},
    {"glob": "projects/drafts/**", "plain": "Change files in your drafts folder",
     "allow": True, "limit": "5 changes, then it must ask again"},
    {"glob": "contracts/**", "plain": "Read your contracts", "allow": True, "limit": "read only"},
    {"glob": "payroll/**", "plain": "Anything in payroll", "allow": False, "limit": "—"},
    {"glob": "*.env", "plain": "Files holding passwords and keys", "allow": False, "limit": "—"},
    {"glob": ".ssh/**", "plain": "Your login keys", "allow": False, "limit": "—"},
]

DATA = {
    "rules": RULES,
    "bins": [{"bin": b["bin"], "n": b["n"], "mean_conf": b["mean_conf"],
              "mean_truth": b["mean_truth"], "gap": b["gap"]}
             for b in cal["bins"] if b["n"]],
    "ece": cal["ece"],
    "cohort_n": ci["cohort_n"],
}

tpl = open(os.path.join(HERE, "plain_template.html")).read()
for key, val in [("{{ENGINE}}", engine), ("{{READERS}}", readers),
                 ("{{DATA}}", json.dumps(DATA, separators=(",", ":"))),
                 ("{{ece}}", str(cal["ece"])),
                 ("{{n}}", str(ci["cohort_n"])),
                 ("{{diag}}", cal["diagnosis"]),
                 ("{{cons}}", cal["user_consequence"])]:
    tpl = tpl.replace(key, val)

assert "{{" not in tpl, "unfilled placeholder left in plain.html"
out = os.path.join(HERE, "plain.html")
open(out, "w").write(tpl)
print("wrote plain.html  (%.1f KB) from measured results — self-contained, no network"
      % (len(tpl) / 1024))
