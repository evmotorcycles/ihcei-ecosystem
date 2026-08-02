"""
screen.py -- the MECHANICAL rule screen for spec v2. Run before v2 was locked.

WHY IT EXISTS. Spec 0de17fc4 declared four SIMPLE rules chosen by hand: 4, 108, 132, 160.
Rule 160 drives the centre cell to a CONSTANT 0 by step 60, so its AUC is undefined and the
ablation P4's pre-registered quantity -- the mean across all four -- does not exist. Rule 4
also came in at base rate 0.1375, outside the [0.20, 0.80] admissibility band the same spec
declared. That is a defect in my rule selection, not in the method.

WHAT THIS SCREEN MAY AND MAY NOT LOOK AT. It computes the CENTRE-CELL BASE RATE and nothing
else. It does NOT featurise, does NOT fit, and does NOT compute AUC for any candidate. Base
rate is the admissibility criterion P2 already declared BEFORE any data, so screening on it
is applying a pre-registered rule rather than selecting on the outcome.

THE SELECTION IS MECHANICAL. Candidate pool fixed below from published Wolfram class 1 and
class 2 assignments. Admit every candidate whose base rate lies in [0.20, 0.80]. Take the
FOUR LOWEST RULE NUMBERS among them. There is no discretion at any step.
"""
import json
import sys

import numpy as np

from ca import evolve, initial_conditions, N_INIT, HORIZON, SEED

# Published Wolfram class 1 and class 2 rule numbers. Fixed before running the screen.
CANDIDATES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 23, 24, 27, 28, 29,
    32, 33, 34, 35, 36, 37, 38, 40, 42, 43, 44, 46, 50, 51, 56, 57, 58, 62, 72,
    73, 74, 76, 77, 78, 94, 104, 108, 128, 130, 132, 134, 136, 138, 140, 142, 152,
    154, 156, 160, 162, 164, 168, 170, 172, 178, 184, 200, 204, 232, 250, 254, 255,
]
BAND = (0.20, 0.80)
TAKE = 4


def base_rate(rule):
    rng = np.random.default_rng(SEED + rule)
    states = initial_conditions(N_INIT, rng)
    col = np.array([evolve(rule, states[i], HORIZON)[HORIZON - 1] for i in range(N_INIT)])
    return float(col.mean())


rates = {r: base_rate(r) for r in CANDIDATES}
admitted = sorted(r for r in CANDIDATES if BAND[0] <= rates[r] <= BAND[1])
chosen = admitted[:TAKE]

out = {
    "what_was_computed": "centre-cell base rate at step %d only. No AUC, no features, no "
                         "model fitted for any candidate." % HORIZON,
    "n_candidates": len(CANDIDATES),
    "admissibility_band": list(BAND),
    "n_admitted": len(admitted),
    "admitted_rules": admitted,
    "CHOSEN_the_four_lowest_admitted": chosen,
    "chosen_base_rates": {str(r): round(rates[r], 4) for r in chosen},
    "rules_from_v1_that_the_screen_rejects": {
        "160": round(rates[160], 4), "4": round(rates[4], 4),
        "note": "Rule 160's centre cell is CONSTANT, which is why v1's ablation could not be "
                "computed. Rule 4 sits outside the band that v1's own P2 declared.",
    },
    "v1_simple_rules_that_survive_the_screen":
        [r for r in (4, 108, 132, 160) if r in admitted],
    "WHY_THIS_IS_NOT_SELECTING_ON_THE_OUTCOME":
        "Base rate is the admissibility criterion spec 0de17fc4 declared at P2 before any "
        "data existed. AUC -- the actual outcome -- was never computed for any candidate "
        "during this screen. The choice rule is 'four lowest admitted rule numbers', which "
        "leaves no room for judgement.",
}
json.dump(out, sys.stdout, indent=2, sort_keys=True)
print()
