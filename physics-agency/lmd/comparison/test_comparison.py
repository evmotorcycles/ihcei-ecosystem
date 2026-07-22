"""pytest: the LMD-vs-four-theories comparison runs and reports honest verdicts."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_comparison_runs_and_is_honest():
    r = subprocess.run([sys.executable, os.path.join(HERE, "compare_theories.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_comparison.json")))
    # Experiment A: Van Raamsdonk pinch-off reproduced
    a = res["experiment_A_van_raamsdonk"]
    assert a["diverges"] is True and a["more_links_shrink_distance"] is True
    assert a["inverse_sqrt_law"] is True
    # Experiment B: it is a genuine metric
    assert res["experiment_B_metric"]["violations"] == 0
    # scorecard covers all four theories with explicit verdicts (incl. honest nulls)
    verdicts = " ".join(s["verdict"] for s in res["scorecard"]).upper()
    assert "SILENT" in verdicts and "NOT COMPARABLE" in verdicts and "COMPARABLE" in verdicts
    assert len(res["scorecard"]) == 4
    # the false-collaboration claim is explicitly disclaimed
    assert "no google collaboration" in res["disclaimer"].lower()
    assert res["pass"] is True
