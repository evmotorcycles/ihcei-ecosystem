"""pytest: the pre-registered Telemetric Metric run reproduces PASS against locked thresholds."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_locked_run_reproduces_pass():
    r = subprocess.run([sys.executable, os.path.join(HERE, "run.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results.json")))
    assert res["verdict"] == "PASS" and res["n_pass"] == 3
    assert res["H1"]["triangle_violations"] == 0
    assert abs(res["H2"]["slope"] + 0.5) < 0.02 and res["H2"]["r2"] > 0.999
    assert res["H3"]["emergent_range"] > 0.05 and res["H3"]["null_range"] < 1e-9


def test_spec_and_manifest_present():
    spec = json.load(open(os.path.join(HERE, "telemetric_prereg.json")))
    man = json.load(open(os.path.join(HERE, "MANIFEST.sha256.json")))
    assert len(man["canonical_sha256"]) == 64
    assert spec["hypotheses"][2]["id"] == "H3" and spec["hypotheses"][2].get("primary") is True
