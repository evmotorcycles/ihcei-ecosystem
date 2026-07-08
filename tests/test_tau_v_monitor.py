"""
Tests for tau_v_monitor. Pure stdlib + pytest; no network, no heavy deps.

Strategy: synthesize event streams with KNOWN latency dynamics and assert the
monitor returns the honest verdict -- OK for a stable network, ALERT for one
whose enforcement latency is genuinely and sustainedly rising, WATCH for a
one-off spike, INSUFFICIENT_DATA when the history cannot calibrate a baseline.
"""
from datetime import datetime, timedelta, timezone

import pytest

from tau_v_monitor import (
    Event, assess, build_windows, percentile, theil_sen_slope, mann_kendall,
    from_records, from_github_issues,
)

UTC = timezone.utc
T0 = datetime(2025, 1, 1, tzinfo=UTC)
WIN = 30.0
N = 12


def make_stream(latency_by_window, *, opened_per_window=20, window_days=WIN, start=T0):
    """Build events: in window k, open `opened_per_window` items each closed
    after `latency_by_window[k]` days. Returns (events, now)."""
    events = []
    for k, lat in enumerate(latency_by_window):
        wstart = start + timedelta(days=k * window_days)
        for j in range(opened_per_window):
            opened = wstart + timedelta(days=(j / opened_per_window) * window_days * 0.5)
            events.append(Event(opened_at=opened, closed_at=opened + timedelta(days=lat)))
    now = start + timedelta(days=len(latency_by_window) * window_days)
    return events, now


# --------------------------- unit: statistics ------------------------------ #
def test_percentile_basic():
    assert percentile([], 95) is None
    assert percentile([5.0], 95) == 5.0
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)
    assert percentile([1, 2, 3, 4, 100], 95) == pytest.approx(80.8, abs=0.1)


def test_theil_sen_slope_monotone():
    assert theil_sen_slope([1, 2, 3, 4, 5]) == pytest.approx(1.0)
    assert theil_sen_slope([5, 4, 3, 2, 1]) == pytest.approx(-1.0)
    assert theil_sen_slope([3]) is None


def test_mann_kendall_directions():
    _, p_up, d_up = mann_kendall([1, 2, 3, 4, 5, 6, 7, 8])
    assert d_up == "increasing" and p_up < 0.05
    _, p_dn, d_dn = mann_kendall([8, 7, 6, 5, 4, 3, 2, 1])
    assert d_dn == "decreasing" and p_dn < 0.05
    _, _, d_flat = mann_kendall([5, 5, 5, 5, 5, 5])
    assert d_flat == "no trend"


# --------------------------- windowing ------------------------------------- #
def test_build_windows_shape_and_backlog():
    events, now = make_stream([10.0] * N)
    wins = build_windows(events, now=now, window_days=WIN, n_windows=N)
    assert len(wins) == N
    # chronological, oldest first
    assert wins[0].start < wins[-1].start
    # each window closed ~20 items at ~10-day latency
    populated = [w for w in wins if w.n_closed > 0]
    assert populated
    assert all(abs(w.tau_v_mean - 10.0) < 2.0 for w in populated)


def test_open_items_count_as_backlog():
    # items opened but never closed must inflate backlog + tail, not tau_v
    now = T0 + timedelta(days=N * WIN)
    events = [Event(opened_at=T0 + timedelta(days=5), closed_at=None) for _ in range(10)]
    wins = build_windows(events, now=now, window_days=WIN, n_windows=N)
    last = wins[-1]
    assert last.n_open_backlog == 10
    assert last.backlog_p95_age is not None and last.backlog_p95_age > 0


# --------------------------- verdicts -------------------------------------- #
def test_stable_network_is_ok():
    events, now = make_stream([12.0] * N)
    a = assess(events, now=now, window_days=WIN, n_windows=N)
    assert a.status == "OK", a.reasons


def test_sustained_rise_alerts():
    # latency climbs steadily 8 -> ~30 days across the series
    lat = [8 + 2.0 * k for k in range(N)]
    events, now = make_stream(lat)
    a = assess(events, now=now, window_days=WIN, n_windows=N)
    assert a.status == "ALERT", (a.status, a.reasons)
    assert a.trend_direction == "increasing"
    assert a.robust_z > 3.0


def test_one_off_spike_is_watch_not_alert():
    lat = [10.0] * N
    lat[-1] = 40.0  # single recent spike, no sustained trend
    events, now = make_stream(lat)
    a = assess(events, now=now, window_days=WIN, n_windows=N)
    assert a.status == "WATCH", (a.status, a.reasons)
    assert a.trend_direction != "increasing"


def test_insufficient_data():
    # only two windows have any closed items -> cannot calibrate baseline
    now = T0 + timedelta(days=N * WIN)
    events = [Event(opened_at=T0 + timedelta(days=k), closed_at=T0 + timedelta(days=k + 5))
              for k in range(2)]
    a = assess(events, now=now, window_days=WIN, n_windows=N)
    assert a.status == "INSUFFICIENT_DATA"


def test_disclaimer_always_present():
    events, now = make_stream([12.0] * N)
    a = assess(events, now=now)
    assert "correlational" in a.disclaimer.lower()
    assert "correlational" in a.as_dict()["disclaimer"].lower()


# --------------------------- adapters -------------------------------------- #
def test_from_records_parses_and_skips_open():
    recs = [
        {"opened_at": "2025-01-01T00:00:00Z", "closed_at": "2025-01-11T00:00:00Z"},
        {"opened_at": "2025-01-02", "closed_at": ""},          # still open
        {"opened_at": "", "closed_at": "2025-01-05"},           # no open -> skipped
    ]
    evs = from_records(recs)
    assert len(evs) == 2
    assert evs[0].latency_days() == pytest.approx(10.0)
    assert evs[1].closed_at is None


def test_from_github_issues_excludes_prs():
    issues = [
        {"created_at": "2025-01-01T00:00:00Z", "closed_at": "2025-01-06T00:00:00Z"},
        {"created_at": "2025-01-01T00:00:00Z", "closed_at": "2025-01-02T00:00:00Z",
         "pull_request": {"url": "x"}},  # a PR -> excluded
        {"created_at": "2025-01-03T00:00:00Z", "closed_at": None,
         "labels": [{"name": "bug"}]},
    ]
    evs = from_github_issues(issues)
    assert len(evs) == 2
    assert evs[1].category == "bug"


def test_cap_days_limits_latency():
    e = Event(opened_at=T0, closed_at=T0 + timedelta(days=1000))
    assert e.latency_days(cap_days=365.0) == 365.0
    assert e.latency_days() == pytest.approx(1000.0)
