"""pytest: the LISM_CircuitBreaker trips correctly, is deterministic, and matches
the repo's real Cohort D telemetry."""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from circuit_breaker import LISM_CircuitBreaker, simulate, _load_cohort_d_per_hop  # noqa: E402


def test_trips_when_cumulative_below_floor():
    cb = LISM_CircuitBreaker(d_min=0.5, tau_v=0)
    assert cb.step(0.9)["tripped"] is False        # 0.90 >= 0.5
    assert cb.step(0.9)["tripped"] is False         # 0.81 >= 0.5
    st = cb.step(0.5)                                # 0.405 < 0.5 -> trip
    assert st["tripped"] is True and st["trip_hop"] == 3


def test_does_not_trip_above_floor():
    cb = LISM_CircuitBreaker(d_min=0.1, tau_v=0)
    for _ in range(20):
        st = cb.step(0.99)                          # 0.99^20 ~ 0.82 > 0.1
    assert st["tripped"] is False


def test_tau_v_enforcement_latency_delays_trip():
    # with tau_v=2, the breaker tolerates 2 hops below the floor before tripping
    cb = LISM_CircuitBreaker(d_min=0.5, tau_v=2)
    cb.step(0.4)                                     # 0.4 < 0.5, below_since=1
    cb.step(0.9)                                     # 0.36 < 0.5, hop2 - 1 = 1 < 2
    st = cb.step(0.9)                                # 0.324 < 0.5, hop3 - 1 = 2 >= 2 -> trip
    assert st["tripped"] is True and st["trip_hop"] == 3


def test_once_tripped_further_steps_are_noops():
    cb = LISM_CircuitBreaker(d_min=0.9, tau_v=0)
    cb.step(0.8)                                     # trips immediately
    hops_at_trip = cb.hops
    cb.step(0.5); cb.step(0.5)
    assert cb.hops == hops_at_trip                   # halted; no further propagation


def test_validates_inputs():
    with pytest.raises(ValueError):
        LISM_CircuitBreaker(d_min=0)
    with pytest.raises(ValueError):
        LISM_CircuitBreaker(d_min=0.5, tau_v=-1)
    with pytest.raises(ValueError):
        LISM_CircuitBreaker(d_min=0.5).step(1.5)


def test_matches_real_cohort_d_and_prevents_zombie_hops():
    per_hop = _load_cohort_d_per_hop()
    r = simulate(per_hop, d_min=0.10, tau_v=0)
    assert r["n_hops"] >= 39
    assert r["trip_hop"] is not None and r["trip_hop"] < r["n_hops"]
    assert r["hops_prevented"] > 0                   # the breaker saves real work
    assert r["ungoverned_zombie_hops"] > 0           # there IS a zombie tail to prevent


def test_deterministic():
    per_hop = _load_cohort_d_per_hop()
    a = simulate(per_hop, 0.1); b = simulate(per_hop, 0.1)
    assert a == b
