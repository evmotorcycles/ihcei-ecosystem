"""pytest guard for the triage-first methodology on four real substrates.

    python3 -m pytest agency-substrates/test_substrates.py -q

Locks in BOTH the positives (HuggingFace, GitHub) AND the honest limits: PubMed is
construct-untestable (floor > invest cap -> rescue impossible, allocators tie) and
bioRxiv is a survivor-only null. LISM prioritizes nulls, so both are asserted so they
stay in the reproducible record.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_triage_methodology_on_real_substrates():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "substrates.py")], capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_substrates.json")))
    assert r["lock_ok"] is True
    subs = {s["name"]: s for s in r["substrates"]}

    # Positives: on HuggingFace and GitHub, triage-first strictly beats naive allocators.
    for name in ("HuggingFace", "GitHub"):
        s = subs[name]
        assert s["applicable"] and s["feasible"]
        assert s["T1"] is True                                   # rescue-gain > improve-gain
        assert s["T2"] is True
        assert s["E_triage"] > s["E_capacity"] and s["E_triage"] > s["E_equal"]

    # Honest limit 1 — PubMed: construct-untestable (floor > invest cap), allocators TIE.
    pm = subs["PubMed"]
    assert pm["applicable"] and pm["feasible"] is False
    assert pm["T1"] is True                                       # structural rescue-dominance still holds
    assert pm["E_triage"] == pm["E_capacity"]                     # the honest tie (rescue impossible)
    assert "PubMed" in r["untestable_substrates"]

    # Honest limit 2 — bioRxiv: survivor-only null, no collapsed nodes.
    assert r["biorxiv_below_floor"] == 0
    assert r["T4_biorxiv_null"] is True

    # F_out=F_eval on real data: verified fidelity, not self-reported popularity.
    assert r["T3_decoupling_real"] is True
    assert len(r["popular_but_below_floor"]) >= 1

    assert r["honest_reporting"] is True
    assert r["pass"] is True
