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

    # C2 -- NO SILENT UPGRADE. Originally this locked an absence (no essentiality labels).
    # Labels were later genuinely committed (DEG2001 -> systematic ORFs), so the gap is
    # allowed to close -- but ONLY together with a reproducing result. The upgrade path is
    # gated on the actual numbers, so a cohort still cannot be promoted by assertion alone.
    c2 = r["C2_yeast_outcome_GAP"]
    if not c2["label_source_found"]:
        assert c2["candidates"] == []
        assert c2["status"] == "NOT_OFFLINE_REPRODUCIBLE"
    else:
        gc = json.load(open(os.path.join(HERE, "results_gapclosure.json")))
        assert c2["gap_closed"] is True, "labels committed but coupling never verified"
        assert gc["yeast_outcome_gap_closed"] is True
        y = gc["yeast"]
        assert y["N"] == 4825 and 1000 <= y["n_essential"] <= 1100
        assert y["vif"] < 1.10                                     # channel still intact
        assert y["cv_auc_linear"] > y["cv_auc_quadratic"]          # quadratic adds nothing
        # the published 'anti-predictive 0.47' must remain identified as a non-converged artifact
        assert y["multivariate_converged"] is False
        assert y["cv_auc_quadratic"] >= 0.55                       # above chance under a real fit
    assert c2["pass"] is True

    # C3 -- REAL but UNDERPOWERED: direction holds, and the power warning must persist.
    c3 = r["C3_github_tau_v_REAL_underpowered"]
    assert c3["N"] == 21 and c3["n_failed"] == 4 and c3["n_survived"] == 17
    assert c3["auc_tau_v_failed_vs_survived"] > 0.5
    assert c3["median_tau_v_failed"] > c3["median_tau_v_survived"]
    assert "UNDERPOWERED" in c3["power_warning"]                   # the caveat stays in the record
    assert c3["pass"] is True

    # C4 -- RECOVERED 2026-07-26. This gate was previously "the gap must stay open".
    # The real artifact was supplied and committed, so the honest gate is now
    # state-aware and has exactly two acceptable worlds -- while still FAILING in the
    # dangerous one (a 992-row file present that has NOT passed recomputation).
    c4 = r["C4_github_992_GAP"]
    assert c4["claimed_N"] == 992
    if not c4["found_992_row_artifact"]:
        assert c4["status"] == "NOT_OFFLINE_REPRODUCIBLE"
        assert c4["largest_committed_labelled_cohort"] == 21
    else:
        assert c4["recovery_verified"] is True, (
            "a 992-row cohort is committed but was not verified by recomputation")
        assert c4["largest_committed_labelled_cohort"] == 992
        assert c4["status"].startswith("REAL_REPRODUCIBLE")
        rec = json.load(open(os.path.join(HERE, "results_992_recovery.json")))
        assert rec["verified"] is True and not rec["checks_failed"]
        assert rec["n_fail"] == 750 and rec["n_surv"] == 242
        assert rec["verdict_recomputed"] == "QUADRATIC_DISCONFIRMED"
        # the real value, which the refused synthetic 'restoration' got wrong (-3.16)
        assert abs(rec["dAIC_recomputed"] - (-3.483)) < 0.02
    assert c4["pass"] is True

    # C5 -- SIMULATION: must stay labelled, and must claim no real-world evidence.
    c5 = r["C5_swarm_SIMULATION"]
    assert c5["self_declared_simulation"] is True
    assert c5["real_world_evidence"] is False
    assert c5["r2_linear"] >= c5["r2_quadratic"]
    assert c5["pass"] is True

    # C6 -- the ledger must stay ACCURATE. It previously required >= 1 open gap; both
    # gaps have since been closed the hard way (yeast labels committed; 992 recovered
    # and verified), so the invariant is now that nothing is quietly promoted.
    c6 = r["C6_integrity_ledger"]
    if "B_github_992" not in c6["not_offline_reproducible"]:
        assert c4["recovery_verified"] is True, \
            "the 992 cohort left the gap list without a verified recovery"
        assert "verified" in c6["ledger"]["B_github_992"]
    # A_yeast_4825_outcome_coupling may leave this list ONLY when genuinely closed
    # (labels committed AND the coupling verified by gap_closure.py).
    if "A_yeast_4825_outcome_coupling" not in c6["not_offline_reproducible"]:
        assert r["C2_yeast_outcome_GAP"]["gap_closed"] is True, \
            "yeast outcome coupling left the gap list without a verified closure"
    assert "D_digital_swarm" in c6["simulations"]
    assert "C_knowledge_793" in c6["simulations"]
    assert c6["pass"] is True

    assert "does NOT mean all cohort claims are supported" in r["meaning_of_pass"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
