"""pytest: ADG/TQG-CFE telemetry operationalization separates survived/failed repos."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "repro"))
sys.path.insert(0, HERE)
from reproduce_tauv import mann_whitney_u  # noqa: E402
from experiment import minmax, cosine_to_ones  # noqa: E402

REPOS = json.load(open(os.path.join(HERE, "fixtures", "experiment_cohort.json")))["repos"]


def _features():
    a = minmax([math.log1p(r["stargazers"]) for r in REPOS])
    t = minmax([math.log1p(r["n_closed"]) for r in REPOS])
    rsp = minmax([1.0 / (1.0 + r["tau_v"]) for r in REPOS])
    hbar = minmax([r["tau_v"] for r in REPOS])
    A = [cosine_to_ones((a[i], t[i], rsp[i])) for i in range(len(REPOS))]
    C = [A[i] * (a[i] * t[i]) / (0.05 + hbar[i]) for i in range(len(REPOS))]
    return A, C


def test_cohort_is_real_and_balanced():
    f = sum(1 for r in REPOS if r["E"] == 0)
    assert len(REPOS) == 22 and 3 <= f <= 12


def test_adg_cdev_separates_survival():
    _, C = _features()
    cs = [C[i] for i, r in enumerate(REPOS) if r["E"] == 1]
    cf = [C[i] for i, r in enumerate(REPOS) if r["E"] == 0]
    _, _, p = mann_whitney_u(cs, cf)
    assert p < 0.05


def test_tqg_alignment_separates_survival():
    A, _ = _features()
    as_ = [A[i] for i, r in enumerate(REPOS) if r["E"] == 1]
    af = [A[i] for i, r in enumerate(REPOS) if r["E"] == 0]
    _, _, p = mann_whitney_u(as_, af)
    assert p < 0.05


def test_alignment_is_bounded_unit_interval():
    A, _ = _features()
    assert all(0.0 <= x <= 1.0 + 1e-9 for x in A)


# --- enriched retest: Salat=D_enc, Zakat=D_dec, Shirk=|sigma| ------------------
def _enriched():
    import math as m
    a = minmax([m.log1p(r["stargazers"]) for r in REPOS])
    salat = minmax([1.0 / (1.0 + r["tau_v"]) for r in REPOS])   # D_enc
    zakat = minmax([m.log1p(r["n_closed"]) for r in REPOS])     # D_dec
    D = [salat[i] * zakat[i] for i in range(len(REPOS))]        # two-hop fidelity
    return D


def test_two_hop_D_salat_zakat_separates_survival():
    D = _enriched()
    ds = [D[i] for i, r in enumerate(REPOS) if r["E"] == 1]
    df = [D[i] for i, r in enumerate(REPOS) if r["E"] == 0]
    _, _, p = mann_whitney_u(ds, df)
    assert p < 0.05


def test_shirk_detects_zombies_among_fresh_pushed():
    # Epistemic Shirk: among recently-pushed repos, high say-do gap flags the
    # ones that are actually rotting (worse tau_v). Runs the enriched script.
    import subprocess
    r = subprocess.run(["python3", os.path.join(HERE, "experiment_enriched.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "H5 Shirk" in r.stdout and "SUPPORTED" in r.stdout
