#!/usr/bin/env python3
"""
run.py -- execute the PRE-REGISTERED Telemetric Metric validation exactly as locked
in telemetric_prereg.json. Thresholds and parameters come ONLY from the frozen spec;
this runner cannot change them. Emits results.json for the audit orchestrator.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # physics-agency/
from telemetric_metric import endpoint_metric, endpoint_scaling, endpoint_discriminator

SPEC = os.path.join(HERE, "telemetric_prereg.json")


def main():
    spec = json.load(open(SPEC))
    P = spec["parameters"]
    n, kappa = P["n_nodes"], P["kappa"]

    # H1 -- metric validity
    m = endpoint_metric(n, P["n_random_networks"], P["metric_seed"], kappa)
    h1_pass = m["triangle_violations"] == 0

    # H2 -- predicted scaling
    s = endpoint_scaling(n, P["scaling_seed"], P["scaling_couplings"], kappa, tuple(P["probe_sites"]))
    hyp2 = next(h for h in spec["hypotheses"] if h["id"] == "H2")
    h2_pass = abs(s["slope"] - hyp2["target_slope"]) < hyp2["slope_tol"] and s["r2"] > hyp2["r2_min"]

    # H3 -- the discriminator (primary endpoint)
    d = endpoint_discriminator(n, P["discriminator_seed"], tuple(P["probe_sites"]),
                               P["discriminator_couplings"], kappa)
    hyp3 = next(h for h in spec["hypotheses"] if h["id"] == "H3")
    h3_pass = d["emergent_range"] > hyp3["emergent_range_min"] and d["null_range"] < hyp3["null_range_max"]

    results = {
        "engine": spec["engine"],
        "H1": {"triangle_violations": m["triangle_violations"], "checks": m["checks"], "pass": h1_pass},
        "H2": {"slope": round(s["slope"], 4), "r2": round(s["r2"], 5), "pass": h2_pass},
        "H3": {"emergent_range": round(d["emergent_range"], 4), "null_range": d["null_range"],
               "emergent": [round(x, 4) for x in d["emergent"]], "null_fixed": round(d["null_fixed"], 4),
               "pass": h3_pass, "primary": True},
        "n_pass": int(h1_pass) + int(h2_pass) + int(h3_pass),
        "verdict": "PASS" if (h1_pass and h2_pass and h3_pass) else "NULL",
    }
    out = os.path.join(HERE, "results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    # exit 0 whether PASS or NULL: reporting a null honestly is a valid outcome.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
