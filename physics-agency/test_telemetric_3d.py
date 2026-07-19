"""pytest: the 3D coordinate-emergence sweep contracts monotonically with coupling."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def test_avg_distance_contracts_with_coupling():
    from telemetric_3d import coupling_sweep_averages
    sweep = coupling_sweep_averages([0.5, 1.0, 2.0, 5.0])
    avgs = [a for _, a in sweep]
    assert all(avgs[i] > avgs[i + 1] for i in range(len(avgs) - 1))   # strictly contracting
    # ~ 1/sqrt(coupling): quadrupling coupling roughly halves the average distance
    assert abs(sweep[2][1] - sweep[0][1] / 2.0) < 0.05                # coupling 2.0 vs 0.5
