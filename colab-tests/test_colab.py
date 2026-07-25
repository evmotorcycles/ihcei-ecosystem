"""pytest: the repo reproduces its OWN locked Colab hash (self-consistency), and the
verifier accepts the lock and rejects a bad hash."""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import colab_suite as cs  # noqa: E402


def test_suite_reproduces_locked_hash():
    spec = json.load(open(os.path.join(HERE, "prereg", "colab_prereg.json")))
    hv = cs.hashed_view(cs.run_all())
    digest = hashlib.sha256(cs.canonical(hv).encode()).hexdigest()
    assert digest == spec["expected_results_sha256"]
    assert hv == spec["expected_results"]


def test_stable_fields_are_as_pre_registered():
    hv = cs.hashed_view(cs.run_all())
    assert hv["T1_lmd_ring"] == {"slope": -0.5, "r2": 1.0}          # algebraic LMD signature
    assert hv["T2_lmd_metric"]["triangle_violations"] == 0          # metric axioms
    assert hv["T3_lism"]["linear_wins"] is True                     # E=U*D linear > quadratic
    assert hv["T4_swarm"]["decays"] is True                        # multi-hop decay
    assert hv["T5_echo"]["tamper_changes_root"] is True             # Echo tamper-evident
    assert hv["T6_tau_v"]["separates"] is True                     # tau_v separates failed/surv
    assert hv["T7_hoffman"]["fitness_final_share"] > 0.6            # FBT


def test_verifier_accepts_lock_and_rejects_bad_hash():
    good = subprocess.run([sys.executable, os.path.join(HERE, "verify_colab.py"),
                           json.load(open(os.path.join(HERE, "prereg", "colab_prereg.json")))["expected_results_sha256"]],
                          capture_output=True, text=True)
    assert good.returncode == 0 and "VERIFIED" in good.stdout
    bad = subprocess.run([sys.executable, os.path.join(HERE, "verify_colab.py"), "deadbeef" * 8],
                         capture_output=True, text=True)
    assert bad.returncode == 1 and "MISMATCH" in bad.stdout
