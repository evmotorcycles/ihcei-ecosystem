"""pytest guard for the Constitutional Agency Allocator (three telemetry laws, one allocator).

    python3 -m pytest agency-constitution/test_constitution.py -q

Locks in BOTH the confirmed improvements AND the honest negative result:
  * G1  the two-hop + independence + shield allocator strictly beats capacity, equal, AND
        the prior triage allocator (PR #105) on real GitHub and Hugging Face.
  * G2  the independence gate voids a self-certifying hoarder; real legs are independent (VIF ~ 1).
  * G3  folding Law 2 (enforcement latency) into the yield objective is FALSIFIED (dE < 0) --
        asserted so the null stays in the reproducible record and can't be silently flipped.
  * G4  the allocation is invariant to self-certified claims (variance == 0 == dF_out/dF_gen).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_constitutional_allocator():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "constitution.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_constitution.json")))
    assert r["lock_ok"] is True
    subs = {s["name"]: s for s in r["substrates"]}

    # G1 -- the recommended allocator beats EVERY baseline (naive AND the prior triage
    # allocator) on both real substrates. This is the confirmed improvement over PR #105.
    for name in ("GitHub", "HuggingFace"):
        s = subs[name]
        assert s["E_constitution"] > s["E_capacity"]
        assert s["E_constitution"] > s["E_equal"]
        assert s["E_constitution"] > s["E_triage_prior"]     # strictly beats the prior triage allocator
    assert r["G1_two_hop_beats_all_baselines"] is True

    # G2 -- independence gate: hoarder voided, real nodes pass, legs genuinely independent.
    assert r["G2_hoarder_rejected"] is True
    assert r["G2_real_nodes_pass"] is True
    assert r["G2_independence_gate"] is True
    assert r["G2_vif"]["GitHub"] < 1.10 and r["G2_vif"]["HuggingFace"] < 1.10   # VIF ~ 1

    # G3 -- the HONEST NEGATIVE, locked: folding Law 2 into the objective HURTS on real
    # GitHub data (dE < 0). Latency is retained as a separate safety-layer compass. This
    # assertion keeps the falsification permanently in the record (cf. openalex PR #100).
    assert r["G3_falsified"] is True
    assert r["G3_dE_throttle_github"] < 0
    assert subs["GitHub"]["E_throttle_in_objective"] < subs["GitHub"]["E_constitution"]

    # G4 -- decoupled shield: allocation invariant to self-certified claims -> variance 0.
    assert r["G4_variance"] == 0.0
    assert len(set(r["G4_E_by_claim"])) == 1
    assert r["G4_decoupled"] is True

    assert r["honest_reporting"] is True
    assert r["pass"] is True
