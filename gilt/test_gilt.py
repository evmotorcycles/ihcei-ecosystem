"""pytest: the REAL GILT simulation reproduces its locked results + passes the gates.

This deliberately does NOT accept the fabricated constants from the circulated
bistable_irreducible_test.py -- it asserts the metrics computed by the real dynamics.
"""
import importlib.util
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

_HAS_NUMPY = importlib.util.find_spec("numpy") is not None


@pytest.mark.skipif(not _HAS_NUMPY, reason="GILT needs numpy")
def test_gilt_reproduces_and_passes_gates():
    sys.path.insert(0, HERE)
    import gilt_sim
    r = gilt_sim.run()
    # deterministic reproduction of the REAL metrics (RandomState(42), legacy generator)
    man = json.load(open(os.path.join(HERE, "prereg", "MANIFEST.sha256.json")))
    import hashlib
    rh = hashlib.sha256(json.dumps(r, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert rh == man["expected_results_sha256"]
    # the four pre-registered gates pass on the honest numbers
    assert 0.30 <= r["survival_rate"] <= 0.70          # G1 bistable tipping point
    assert r["static_auc"] <= 0.55                     # G2 static oracle near chance
    assert r["dynamic_auc"] >= 0.70                    # G3 tau_v predicts
    assert r["gain"] >= 0.15                           # G4 decisive dynamic gain


@pytest.mark.skipif(not _HAS_NUMPY, reason="GILT needs numpy")
def test_metrics_are_not_the_fabricated_constants():
    sys.path.insert(0, HERE)
    import gilt_sim
    r = gilt_sim.run()
    # the circulated fake script hard-coded these; the real run differs
    fabricated = {"survival_rate": 0.3772, "static_auc": 0.5348, "dynamic_auc": 0.7324, "gain": 0.1976}
    assert r != fabricated
