#!/usr/bin/env python3
"""build_desk.py -- render cairn/desk.html, the everyday-object GUI.

    python3 cairn/build_desk.py

Same audited engines as the console; different surface. The tools are named for
the physical object they resemble (a label, a valet key, a dashcam, a meter)
because that is what an ordinary person already understands. The component names
appear nowhere a user can see them.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ci = json.load(open(os.path.join(HERE, "results_ci.json")))
cal = ci["C1_calibration"]
engine = open(os.path.join(HERE, "ei_engine.js")).read()
readers = open(os.path.join(ROOT, "readers/readers.js")).read()

RULES = [
    {"glob": "projects/**", "plain": "Read anything in your projects folder", "allow": True, "limit": "—"},
    {"glob": "projects/drafts/**", "plain": "Change files in your drafts folder", "allow": True,
     "limit": "5 changes, then it asks again"},
    {"glob": "contracts/**", "plain": "Read your contracts", "allow": True, "limit": "reading only"},
    {"glob": "payroll/**", "plain": "Anything in payroll", "allow": False, "limit": "—"},
    {"glob": "*.env", "plain": "Files holding passwords and keys", "allow": False, "limit": "—"},
    {"glob": ".ssh/**", "plain": "Your login keys", "allow": False, "limit": "—"},
]
DATA = {"rules": RULES,
        "bins": [{"bin": b["bin"], "n": b["n"], "mean_conf": b["mean_conf"],
                  "mean_truth": b["mean_truth"], "gap": b["gap"]}
                 for b in cal["bins"] if b["n"]],
        "ece": cal["ece"], "cohort_n": ci["cohort_n"]}

tpl = open(os.path.join(HERE, "desk_template.html")).read()
for key, val in [("{{ENGINE}}", engine), ("{{READERS}}", readers),
                 ("{{DATA}}", json.dumps(DATA, separators=(",", ":"))),
                 ("{{ece}}", str(cal["ece"])), ("{{n}}", str(ci["cohort_n"]))]:
    tpl = tpl.replace(key, val)
assert "{{" not in tpl, "unfilled placeholder left in desk.html"
open(os.path.join(HERE, "desk.html"), "w").write(tpl)
print("wrote desk.html  (%.1f KB) — everyday-object GUI, self-contained" % (len(tpl) / 1024))
