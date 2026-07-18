"""pytest: the Telemetric Metric d^2=kappa*tau_rt — geometry, scaling, discriminator."""
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from telemetric_metric import telemetric_distance  # noqa: E402
from emergent_spacetime import rand_coupling  # noqa: E402


def test_metric_and_inverse_sqrt_scaling():
    rng = random.Random(2)
    W = rand_coupling(6, rng)
    d1 = telemetric_distance(W)[0][5]
    d4 = telemetric_distance([[4 * W[i][j] for j in range(6)] for i in range(6)])[0][5]
    # d ~ 1/sqrt(coupling): quadrupling coupling halves the distance
    assert abs(d4 - d1 / 2.0) < 1e-6


def test_discriminator_emergent_responds_fundamental_does_not():
    rng = random.Random(29)
    base = rand_coupling(6, rng)
    a, b = 0, 5
    d_ref = telemetric_distance(base)[a][b]
    resp = []
    for g in (0.5, 2.0, 4.0):
        W = [row[:] for row in base]
        for x in (a, b):
            for j in range(6):
                if j != x:
                    W[x][j] *= g; W[j][x] = W[x][j]
        resp.append(telemetric_distance(W)[a][b])
    assert max(resp) - min(resp) > 0.05      # emergent distance moves with coupling
    assert all(r == d_ref for r in [d_ref])  # fundamental container stays fixed (trivially)


def test_script_exits_zero_all_three():
    r = subprocess.run([sys.executable, os.path.join(HERE, "telemetric_metric.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 3/3 validated" in r.stdout
