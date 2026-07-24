"""pytest guard for the biomedical OQM case study (four telemetry laws, real substrates).

    python3 -m pytest biomedical-agency/test_biomedical.py -q

Reads the FROZEN yeast feature fixture (derived from the committed real STRING v12 data by
build_yeast_features.py; not rebuilt here -- that needs networkx and ~85s). Locks the four
measured findings AND the epistemic firewall (measured layer separate from the interpretive
biomedical overlay). Nothing here is a clinical claim.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_biomedical_oqm_case_study():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "biomedical_oqm.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_biomedical.json")))
    assert r["lock_ok"] is True

    # B1 -- REAL yeast interactome: two fidelity hops independent (VIF ~ 1.00), collinear voided.
    b1 = r["B1_yeast_independence"]
    assert b1["N"] == 4825
    assert b1["VIF_real"] < 1.10
    assert abs(b1["VIF_real"] - 1.003) < 0.01          # reproduces the known value
    assert b1["collinear_rejected"] is True
    assert b1["B1"] is True

    # B2 -- REAL PubMed: retraction burden concentrated + dissonance flag fires.
    b2 = r["B2_pubmed_dissonance"]
    assert b2["top_field_retraction_share"] > b2["uniform_share"]
    assert len(b2["high_dissonance_fields"]) >= 1
    assert b2["B2"] is True

    # B3 -- REAL bioRxiv: self-correction latency heavy-tailed; survivor-only limit recorded.
    b3 = r["B3_biorxiv_latency"]
    assert b3["mean_days"] > b3["median_days"]
    assert b3["p90_over_p50"] > 2.0
    assert b3["survivor_only"] is True                 # the honest limit stays in the record
    assert b3["B3"] is True

    # B4 -- REAL bioinformatics GitHub: triage allocator beats naive (small-N caveat recorded).
    b4 = r["B4_github_triage"]
    assert b4["E_constitution"] >= b4["E_capacity"]
    assert b4["E_constitution"] >= b4["E_equal"]
    assert b4["N"] == 8
    assert b4["B4"] is True

    # the firewall must be present in the emitted record
    assert "not medical advice" in r["epistemic_firewall"].lower()
    assert r["honest_reporting"] is True
    assert r["pass"] is True
