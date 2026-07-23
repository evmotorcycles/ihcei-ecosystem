"""pytest guard for the Deterministic Telemetry Equation (decoupling law).

    python3 -m pytest det-telemetry/test_det.py -q

Asserts the pre-registered gates D1-D5 on the deterministic FunSearch-style loop,
and independently re-checks the two EXACT predictions (evaluator determinism across
a fresh process, and honesty-decoupling gap == 0).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "funsearch_det.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    return json.load(open(os.path.join(HERE, "results_det.json")))


def test_gates_D1_to_D5():
    r = _run()
    assert r["lock_ok"] is True
    assert r["D1_evaluator_determinism"]["pass"] is True
    assert len(set(r["D1_evaluator_determinism"]["scores"])) == 1        # exact: variance 0
    assert r["D2_generator_variance"]["pass"] is True
    assert r["D3_honesty_decoupling"]["pass"] is True
    assert r["D3_honesty_decoupling"]["gap"] == 0                        # exact decoupling
    assert r["D3_honesty_decoupling"]["honest_true"] == r["D3_honesty_decoupling"]["lying_true"]
    assert r["D4_monotone_ratchet"]["pass"] is True
    assert r["D5_architecture_control"]["pass"] is True
    assert r["D5_architecture_control"]["self_verify_invalid"] is True   # self-verify fooled into invalid pick
    assert r["pass"] is True


def test_evaluator_is_deterministic_across_a_fresh_process():
    """Import the pure evaluator in a separate interpreter; the same candidate must
    score identically to the runner's -- determinism is not just within one run."""
    code = (
        "import sys; sys.path.insert(0, %r);"
        "import funsearch_det as f;"
        "probe = tuple(1 if i%%2==0 else 0 for i in range(len(f.ITEMS)));"
        "print(f.evaluate(probe))" % HERE
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    fresh = int(out.stdout.strip())
    r = _run()
    assert fresh == r["D1_evaluator_determinism"]["scores"][0]           # identical across processes
