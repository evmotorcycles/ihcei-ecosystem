"""pytest guard for the knowledge-propagation experiment.

    python3 -m pytest knowledge-breakthroughs/test_knowledge.py -q

This guard locks the NEGATIVE results as hard as the positive ones. Passing here means the
pre-registered experiment reproduces EXACTLY as written -- including:
  K1  the FALSIFICATION of the central thesis (raw status predicts realized yield BETTER
      than fidelity-adjusted capacity on real HuggingFace and GitHub data),
  K2  the PARTIAL failure of the independence gate on GitHub (VIF 1.174 > the pre-registered
      1.10; the threshold was NOT moved),
  K3  capacity alone does not buy fidelity (confirmed),
  K4  prestige ranking is a different ordering from verified fidelity (confirmed),
  K5  the synthetic estimator control (explicitly carries no real-world evidence).
If anyone later "fixes" the null into a win, these assertions break loudly.
(Same discipline as openalex-lism PR #100 and the agency-constitution G3 falsification, PR #107.)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_knowledge_propagation_including_its_nulls():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "knowledge.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not reproduce:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_knowledge.json")))
    assert r["lock_ok"] is True

    # K1 -- THE FALSIFICATION, locked. The thesis was NOT supported: on both real substrates
    # raw status explains realized yield better than the fidelity-adjusted product.
    k1 = r["K1_fidelity_beats_status"]
    assert r["thesis_supported"] is False
    assert k1["falsified"] is True
    assert k1["pass"] is False
    assert k1["hf_rho_status_alone"] > k1["hf_rho_fidelity_adjusted"]
    assert k1["gh_rho_status_alone"] > k1["gh_rho_fidelity_adjusted"]

    # K2 -- the PARTIAL failure, locked with the ORIGINAL threshold (never moved).
    k2 = r["K2_independence"]
    assert k2["pre_registered_gate"] == 1.10
    assert k2["vif_hf"] < 1.10                       # HuggingFace channel intact
    assert k2["vif_github"] > 1.10                   # GitHub exceeds the gate as written
    assert k2["vif_github"] < 5.0                    # ...but is far below standard collinearity
    assert k2["circular_control_rejected"] is True   # self-certifying node still voided
    assert k2["partial"] is True
    assert k2["pass"] is False
    assert set(k2["untestable_single_leg"]) == {"bioRxiv", "PubMed"}

    # K3 -- CONFIRMED: raw capacity does not buy channel fidelity on either real substrate.
    k3 = r["K3_capacity_inert"]
    assert k3["pubmed_rho_size_vs_integrity"] <= 0.50
    assert k3["biorxiv_rho_team_vs_latency_fidelity"] <= 0.50
    assert k3["pubmed_N"] == 8 and k3["biorxiv_N"] == 40      # declared small-N / survivor-only
    assert k3["pass"] is True

    # K4 -- CONFIRMED: prestige ordering != verified-fidelity ordering; popular nodes below floor.
    k4 = r["K4_decoupled"]
    assert k4["hf_rankings_differ"] is True
    assert len(k4["hf_popular_but_below_floor"]) >= 1
    assert k4["pass"] is True

    # K5 -- the control must stay labelled synthetic and must claim no real-world evidence.
    k5 = r["K5_synthetic_control"]
    assert k5["fixture_is_synthetic"] is True
    assert k5["real_world_evidence"] is False
    assert k5["N"] == 793
    assert k5["vif"] < 1.10
    assert k5["pass"] is True

    assert r["reproduced_including_nulls"] is True
    assert r["honest_reporting"] is True
    assert r["pass"] is True
