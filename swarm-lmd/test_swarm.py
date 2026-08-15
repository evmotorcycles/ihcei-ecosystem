#!/usr/bin/env python3
"""Guards for the swarm re-run.

    python3 -m pytest -q swarm-lmd/test_swarm.py

The results this locks include one pre-registered prediction that FAILED and one
comparison that turned out to be uninformative. Both are kept exactly as they
came out.
"""
import csv
import hashlib
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_swarm.json"), encoding="utf-8"))
CSV = os.path.join(HERE, "data", "swarm_rows.csv")


def test_the_prereg_is_unchanged_since_it_was_locked():
    live = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json"), encoding="utf-8"))
    assert live == lock["prereg_sha256"]
    assert R["prereg_intact"] is True


def test_the_prereg_states_the_prior_arm_did_not_fully_pass():
    src = open(os.path.join(HERE, "PREREG.md"), encoding="utf-8").read()
    assert "coupling_confirmed: false" in src
    assert "does not assume otherwise" in src


def test_decay_with_depth_replicates():
    assert R["S1_decay_with_depth"]["result"] == "HOLDS"
    assert R["S1_decay_with_depth"]["rho"] <= -0.50


def test_the_lmd_link_was_predicted_and_it_FAILED():
    """S2 said effective resistance would predict fidelity at least as well as
    hop depth. It does not. The prediction was registered before the run and the
    failure is kept."""
    s2 = R["S2_resistance_predicts"]
    assert s2["result"] == "FAILS"
    assert abs(s2["rho_resistance"]) < abs(s2["rho_depth"])
    assert s2["better"] == "depth"


def test_the_uninformative_comparison_is_labelled_as_such():
    """adj r² ≈ 0.0003 must never be read as falsifying E = U·D."""
    assert R["S3_functional_form"]["adj_r2_linear"] < 0.01
    caveat = R["S3_caveat"]
    assert "UNINFORMATIVE" in caveat.upper()
    assert "never enters the fidelity recursion" in caveat.lower()


def test_the_diagnostic_shows_why():
    s5 = R["S5_what_capacity_does"]
    assert s5["result"] == "CONSISTENT"
    assert s5["rho_U_descendants"] > 0.15, "capacity should buy reach"
    assert abs(s5["rho_U_fidelity"]) < 0.15, "and should not predict received fidelity"


def test_revoking_the_root_cuts_off_everything():
    s4 = R["S4_revocation"]
    assert s4["result"] == "HOLDS"
    assert s4["cut_off"] == s4["of"]


# ------------------------------------------------------------- the dataset --
def test_the_dataset_exists_and_matches_its_recorded_hash():
    assert os.path.exists(CSV)
    sha = hashlib.sha256(open(CSV, "rb").read()).hexdigest()
    assert sha == R["dataset"]["sha256"], "the dataset changed without the results changing"


def test_the_dataset_says_on_its_face_that_it_is_simulated():
    first = open(CSV, encoding="utf-8").readline()
    assert first.startswith("#")
    assert "SIMULATED" in first
    assert "NOT about the world" in first
    assert R["dataset"]["kind"] == "SIMULATED"


def test_the_dataset_has_the_columns_the_analysis_used():
    with open(CSV, encoding="utf-8") as f:
        f.readline()
        rows = list(csv.DictReader(f))
    assert len(rows) == R["dataset"]["rows"] >= 5000
    for col in ("swarm", "J", "depth", "R_from_root", "U", "d_enc", "d_dec",
                "E_UDD", "fidelity"):
        assert col in rows[0]


def test_the_dataset_actually_spans_the_coupling_sweep():
    with open(CSV, encoding="utf-8") as f:
        f.readline()
        Js = {r["J"] for r in csv.DictReader(f)}
    assert len(Js) >= 10, "a dataset from a sweep should contain the sweep"
    assert min(float(j) for j in Js) < 0.1 and max(float(j) for j in Js) > 10
