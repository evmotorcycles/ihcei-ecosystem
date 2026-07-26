"""
test_bank.py — locks the underwriting result INCLUDING its two failed predictions.

Prevents: (a) the spec being edited after locking, (b) the failed B1/B2 gates being
quietly rescued by widening the band or flipping the comparison, (c) the B3 portfolio
result being upgraded into a general claim it does not support.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "fbe085fcf4cc2a7f5b3bf386a7e81f1542cda6f6f826996ca75ef41162f0d62a"


def _canon(v):
    if v is None or not isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ",".join(_canon(x) for x in v) + "]"
    return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + _canon(v[k])
                          for k in sorted(v)) + "}"


def test_underwriting_reproduces_including_its_failures():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "underwriting_test.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_bank.json")))

    spec = json.load(open(os.path.join(HERE, "prereg", "bank_prereg.json")))
    assert hashlib.sha256(_canon(spec).encode()).hexdigest() == LOCKED, \
        "the pre-registered banking spec was edited after locking"
    assert r["spec_sha256_canonical"] == LOCKED

    assert r["N"] == 27 and r["defaults"] == 6

    # --- THE TWO FAILURES MUST STAY FAILURES -------------------------------------
    # B1: popularity slightly OUT-discriminated enforcement latency. The central
    # prediction was wrong and is recorded as wrong.
    assert "B1_tauv_beats_stars" in r["gates_not_met"], \
        "B1 was rescued -- popularity out-discriminated tau_v on this cohort; keep it recorded"
    assert r["auc_stars"] > r["auc_tau_v"], "the direction of the B1 miss was altered"
    assert abs(r["auc_tau_v"] - 0.7143) < 5e-3
    assert abs(r["auc_stars"] - 0.7381) < 5e-3

    # B2: popularity was NOT near-chance. "Prestige carries zero information about
    # survival" is refuted on this cohort and must not be re-asserted.
    assert "B2_popularity_is_near_chance" in r["gates_not_met"], \
        "B2 was rescued -- stars carried real signal (AUC 0.74); the near-chance claim is refuted"
    assert r["auc_stars"] > 0.70

    # --- WHAT SURVIVED, held to exactly what it showed ---------------------------
    p = r["portfolio"]
    assert p["sovereign_default_rate"] < p["conventional_default_rate"]
    assert abs(p["conventional_default_rate"] - 0.1538) < 5e-3
    assert abs(p["sovereign_default_rate"] - 0.0769) < 5e-3
    assert abs(r["spearman_stars_tauv"]) < 0.50          # genuinely two axes

    # the surviving claim is about the FUNDED BOOK, not about ranking power
    assert len(r["gates_not_met"]) == 2, \
        "the number of failed gates changed; the banking result is 2/4, not a clean win"
