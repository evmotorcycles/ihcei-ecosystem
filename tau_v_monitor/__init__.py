"""
tau_v_monitor -- enforcement-latency early-warning monitor.

Operationalizes the positive, deployable finding of the LISM manuscript:
a sustained rise and widening upper tail in the time a network takes to close
its own flagged risks is a locally-calibrated leading indicator of collapse.

Quick start:
    from tau_v_monitor import Event, assess
    a = assess(events, window_days=30, n_windows=12)
    print(a.status, a.reasons)
"""
from .core import (
    Event,
    WindowMetric,
    Assessment,
    assess,
    build_windows,
    percentile,
    theil_sen_slope,
    mann_kendall,
    DISCLAIMER,
)
from .adapters import from_records, from_csv, from_github_issues

__all__ = [
    "Event", "WindowMetric", "Assessment", "assess", "build_windows",
    "percentile", "theil_sen_slope", "mann_kendall", "DISCLAIMER",
    "from_records", "from_csv", "from_github_issues",
]
__version__ = "0.1.0"
