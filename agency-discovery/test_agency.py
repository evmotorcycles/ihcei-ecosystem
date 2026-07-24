"""pytest guard for AlphaAgency -- the agency-allocation discovery pipeline.

    python3 -m pytest agency-discovery/test_agency.py -q

Asserts the pre-registered gates A1-A5 AND locks in the HONEST limitation: the
evolved simple policy is NOT near-optimal against a genuine strong reference
(the pre-registered 'oracle' turned out myopic). The real, verified results are
the decoupling (A3) and the load-bearing tau_v floor (A5); the discovered simple
policy is modest, and that is recorded, not hidden.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_alpha_agency():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "alpha_agency.py")], capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_agency.json")))
    assert r["lock_ok"] is True
    # A1 — beats every naive baseline
    assert r["A1_beats_naive"] is True
    m = r["means"]
    assert m["evolved"] > max(m["random"], m["equal"], m["greedy_capacity"], m["greedy_need"])
    # A2 — literal gate (vs the myopic 1-step greedy) passes; framed honestly, not as near-optimality
    assert r["A2_near_optimal"]["pass"] is True
    # A3 — F_out=F_eval: deterministic AND honest==lying (gap 0). The core trustworthiness result.
    assert r["A3_decoupling"]["deterministic"] is True
    assert r["A3_decoupling"]["honest_vs_lying_gap"] == 0
    assert r["A3_decoupling"]["pass"] is True
    # A4 — monotone ratchet
    assert r["A4_monotone"] is True
    # A5 — the tau_v collapse floor is load-bearing
    assert r["A5_tau_v_load_bearing"]["pass"] is True
    assert m["evolved"] > m["floor_blind"]
    # HONESTY LOCK: against a GENUINE strong reference, the evolved simple policy is NOT near-optimal.
    # This is asserted so the limitation stays in the reproducible record and can never be quietly dropped.
    assert m["strong_localsearch_ref_exploratory"] > m["evolved"]        # genuine optimum is well above
    assert r["near_optimal_vs_strong_ref"]["ratio"] < 0.8                # evolved reaches <80% of it
    assert "MYOPIC" in r["honest_note"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
