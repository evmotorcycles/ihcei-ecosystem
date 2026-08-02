"""
probe.py -- PRE-FLIGHT FEASIBILITY PROBE, run BEFORE the specification was locked.

It runs the complete pipeline on TWO THROWAWAY RULES that are NOT among the eight the
experiment scores: rule 232 (majority vote, expected to be easy) and rule 62 (expected to
be harder). The question it answers is only whether the declared thresholds are physically
reachable by these quantities -- not what the answer will be.

Prior specs in this programme contained gates that could not be met by construction
(6cb42dcd's T2R could not fail, 558f6fa1's X6 could not pass). A probe recorded in the spec
before locking is the correction adopted in 25c7dffc, 03815a61 and 5576e524. This is the
fourth application.

NONE OF THE EIGHT SCORED RULES IS TOUCHED HERE.
"""
import json
import sys

from ca import run_rule

THROWAWAY = [232, 62]

out = {"probe": "complete pipeline on two THROWAWAY rules, neither of them scored",
       "rules": {}}
for r in THROWAWAY:
    d = run_rule(r)
    out["rules"][str(r)] = {"base_rate": round(d["base_rate"], 4),
                            "static_auc": round(d["static_auc"], 4),
                            "partial_auc": round(d["partial_auc"], 4),
                            "partial_minus_static": round(d["partial_auc"] - d["static_auc"], 4)}

s = [v["static_auc"] for v in out["rules"].values()]
out["IS_THE_0_75_BAR_REACHABLE"] = (
    "Highest static AUC seen on a throwaway rule is %.4f. A 0.75 bar for the SIMPLE arm is "
    "%s by this evidence." % (max(s), "reachable" if max(s) >= 0.75 else "NOT clearly reachable"))
out["IS_THE_0_60_BAR_REFUSABLE"] = (
    "Lowest static AUC seen on a throwaway rule is %.4f. A 0.60 ceiling for the COMPLEX arm "
    "is %s -- a predictor that always scored high would make the primary unfailable, and a "
    "predictor that always scored 0.5 would make it unearnable."
    % (min(s), "in range" if min(s) <= 0.60 else "NOT obviously in range"))
out["WHAT_WAS_DELIBERATELY_NOT_PROBED"] = (
    "None of the eight scored rules was evolved, featurised or fitted. The probe cannot "
    "tell us which way the primary will go.")
out["WHY_DCM_IS_EXCLUDED_AND_NOT_SCORED"] = (
    "DELTA = V*I*C is an admissibility check for CONCENTRATED or CATEGORICAL outcomes. The "
    "outcome here is cross-validated AUC -- continuous, unbanded and spread across cells -- "
    "so V and C both sit near 1 by construction and DELTA cannot fail. A gate that cannot "
    "fail is not evidence, so DCM is recorded as EXCLUDED with its reason rather than "
    "reported as a pass. The admissibility gates that CAN fail here are P2 (degenerate base "
    "rates) and P6 (the shuffled-label control).")

json.dump(out, sys.stdout, indent=2, sort_keys=True)
print()
