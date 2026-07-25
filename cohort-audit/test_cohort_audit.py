"""pytest guard for the cohort integrity audit (Yeast 4825, GitHub 992, digital swarm).

    python3 -m pytest cohort-audit/test_cohort_audit.py -q

This guard locks the GAPS as hard as the positives. Passing means the audit reproduces
exactly as pre-registered, including:
  C1  yeast channel independence IS backed by committed real STRING v12 data,
  C2  the yeast OUTCOME-coupling claim is NOT offline-reproducible (no essentiality labels),
  C3  the real tau_v cohort holds its direction but is SEVERELY UNDERPOWERED (n_fail=4),
  C4  the N=992 GitHub cohort is NOT offline-reproducible (rows never committed),
  C5  the digital swarm is a SIMULATION carrying zero real-world evidence,
  C6  the ledger records >= 1 not-reproducible cohort (the audit does not whitewash itself).
If anyone later upgrades a cohort's status without committing the underlying data,
these assertions break loudly.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_cohort_integrity_audit_including_its_gaps():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "cohort_audit.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "audit did not reproduce:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_audit.json")))
    assert r["lock_ok"] is True

    # C1 -- REAL: yeast channel independence, traceable to the committed raw STRING file.
    c1 = r["C1_yeast_channel_REAL"]
    assert c1["N"] == 4825 and c1["n_edges"] == 70201
    assert c1["vif"] < 1.10 and abs(c1["vif"] - 1.003) < 0.01     # reproduces the reported value
    assert c1["collinear_control_rejected"] is True
    assert c1["raw_string_hash_matches_provenance"] is True        # features really derive from real data
    assert c1["pass"] is True

    # C2 -- GAP LOCKED: no committed gene-essentiality labels, so the outcome-coupling
    # result (delta AIC ~ -1805, AUC ~0.47) is NOT reproducible from this repository.
    c2 = r["C2_yeast_outcome_GAP"]
    assert c2["label_source_found"] is False
    assert c2["candidates"] == []
    assert c2["status"] == "NOT_OFFLINE_REPRODUCIBLE"
    assert c2["pass"] is True

    # C3 -- REAL but UNDERPOWERED: direction holds, and the power warning must persist.
    c3 = r["C3_github_tau_v_REAL_underpowered"]
    assert c3["N"] == 21 and c3["n_failed"] == 4 and c3["n_survived"] == 17
    assert c3["auc_tau_v_failed_vs_survived"] > 0.5
    assert c3["median_tau_v_failed"] > c3["median_tau_v_survived"]
    assert "UNDERPOWERED" in c3["power_warning"]                   # the caveat stays in the record
    assert c3["pass"] is True

    # C4 -- GAP LOCKED: the 992-row cohort is not committed; only a hash was ever stored.
    c4 = r["C4_github_992_GAP"]
    assert c4["claimed_N"] == 992
    assert c4["found_992_row_artifact"] is False
    assert c4["largest_committed_labelled_cohort"] == 21
    assert c4["status"] == "NOT_OFFLINE_REPRODUCIBLE"
    assert c4["pass"] is True

    # C5 -- SIMULATION: must stay labelled, and must claim no real-world evidence.
    c5 = r["C5_swarm_SIMULATION"]
    assert c5["self_declared_simulation"] is True
    assert c5["real_world_evidence"] is False
    assert c5["r2_linear"] >= c5["r2_quadratic"]
    assert c5["pass"] is True

    # C6 -- the ledger must keep at least one honest gap and both simulations.
    c6 = r["C6_integrity_ledger"]
    assert len(c6["not_offline_reproducible"]) >= 1
    assert "B_github_992" in c6["not_offline_reproducible"]
    assert "A_yeast_4825_outcome_coupling" in c6["not_offline_reproducible"]
    assert "D_digital_swarm" in c6["simulations"]
    assert "C_knowledge_793" in c6["simulations"]
    assert c6["pass"] is True

    assert "does NOT mean all cohort claims are supported" in r["meaning_of_pass"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
