"""pytest: the hardware coupler-sweep template predicts the -0.5 law and does NOT
fabricate a measurement."""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mock_willow_sweep as m  # noqa: E402
import random  # noqa: E402


def test_prediction_is_the_minus_half_law():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "physics-agency"))
    from emergent_spacetime import rand_coupling
    W = rand_coupling(6, random.Random(1))
    _, _, slope, r2 = m.predicted_sweep(W, pair=(0, 5))
    assert abs(slope - (-0.5)) < 1e-6      # analytic identity
    assert r2 > 0.9999


def test_measurement_hook_refuses_to_fabricate():
    # the honest template must NOT return a fake latency
    with pytest.raises(NotImplementedError):
        m.measure_scrambling_latency(0, 5, 1.0)


def test_predicted_distance_positive_and_symmetric():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "physics-agency"))
    from emergent_spacetime import rand_coupling
    W = rand_coupling(5, random.Random(2))
    d01 = m.predicted_distance(W, (0, 1))
    d10 = m.predicted_distance(W, (1, 0))
    assert d01 > 0 and abs(d01 - d10) < 1e-9
