"""pytest: distance emerges as a metric from pure information (indirect: space not fundamental)."""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from emergent_spacetime import dx_matrix, rand_coupling  # noqa: E402


def test_emergent_distance_is_a_metric():
    rng = random.Random(3)
    for _ in range(20):
        W = rand_coupling(6, rng)
        dx = dx_matrix(W)
        n = len(dx)
        for i in range(n):
            assert abs(dx[i][i]) < 1e-9
            for j in range(n):
                assert abs(dx[i][j] - dx[j][i]) < 1e-9        # symmetric
                for k in range(n):
                    assert dx[i][k] <= dx[i][j] + dx[j][k] + 1e-9   # triangle


def test_coupling_contracts_distance():
    rng = random.Random(5)
    W = rand_coupling(6, rng)
    W2 = [[4 * W[i][j] for j in range(6)] for i in range(6)]
    m1 = sum(dx_matrix(W)[i][j] for i in range(6) for j in range(i + 1, 6))
    m2 = sum(dx_matrix(W2)[i][j] for i in range(6) for j in range(i + 1, 6))
    assert m2 < m1                                            # higher coupling -> shorter distances


def test_script_exits_zero_all_three():
    r = subprocess.run([sys.executable, os.path.join(HERE, "emergent_spacetime.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 3/3 supported" in r.stdout
