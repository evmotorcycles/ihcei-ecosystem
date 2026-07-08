"""
tau_v_monitor.core
==================
Domain-agnostic enforcement-latency (tau_v) early-warning core.

This operationalizes the *only* positive, deployable finding of the LISM
manuscript ("Information-Fidelity Coupling in Networks Is Linear, Not
Quadratic"): a network's responsiveness to its own flagged risks -- the mean
time it takes to close what it has itself flagged -- is a measured, monitorable
leading indicator of systemic failure.

Design commitments taken directly from the paper's Discussion, so this tool
does not over-claim what the data licensed:

  1. TRAJECTORY, NOT THRESHOLD. The informative quantity is a *sustained rise*
     and a *widening upper tail* (accumulating unresolved items), not any
     absolute number. Baseline latency varies with domain, team size and
     workflow, so we never ship a universal threshold. The failed/survived
     means from the paper (50.6 d vs 19.8 d) are specific to public GitHub
     repositories and are deliberately NOT hard-coded here.

  2. CALIBRATE LOCALLY. Alert levels are computed against the organization's
     *own* history (a robust baseline of earlier windows), never imported.

  3. ONE INPUT TO HUMAN REVIEW. The relationship is correlational and
     probabilistic. Every verdict carries that caveat; nothing here is an
     automated trigger for consequential action.

The core is intentionally stdlib-only (no numpy/pandas) so it can be
instrumented anywhere -- an issue tracker, a ticket queue, an
audit-finding-to-remediation log, an incident-to-resolution stream -- by
feeding it (opened_at, closed_at) pairs. See adapters.py for shaping helpers.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Iterable, Optional, Sequence

DAY = 86400.0

DISCLAIMER = (
    "tau_v is a correlational, probabilistic early-warning signal, not a "
    "deterministic oracle. Use as one input to human review; calibrate to your "
    "own history. Absolute day-counts are not transplantable thresholds."
)


# --------------------------------------------------------------------------- #
# Event model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Event:
    """One flagged item: an issue, ticket, audit finding, incident, defect.

    opened_at   : when the risk was flagged (required, tz-aware or naive-UTC).
    closed_at   : when it was resolved; None means still open (right-censored).
    category    : optional label (e.g. severity, control family) for slicing.
    """
    opened_at: datetime
    closed_at: Optional[datetime] = None
    category: Optional[str] = None

    def resolved(self) -> bool:
        return self.closed_at is not None

    def latency_days(self, cap_days: Optional[float] = None) -> Optional[float]:
        if self.closed_at is None:
            return None
        d = (self.closed_at - self.opened_at).total_seconds() / DAY
        d = max(d, 0.0)
        return min(d, cap_days) if cap_days else d


# --------------------------------------------------------------------------- #
# Per-window metrics
# --------------------------------------------------------------------------- #
@dataclass
class WindowMetric:
    start: datetime
    end: datetime
    n_closed: int
    n_open_backlog: int                 # items still open at window end
    tau_v_mean: Optional[float]         # mean close-latency of items CLOSED in window (days)
    tau_v_median: Optional[float]
    # The "widening upper tail" the paper emphasizes: P95 over the union of
    # closed-in-window latencies and still-open backlog ages. Captures risk
    # that is accumulating precisely because it is NOT being closed.
    tail_p95: Optional[float]
    backlog_p95_age: Optional[float]    # P95 age of still-open items (days)

    def as_dict(self) -> dict:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "n_closed": self.n_closed,
            "n_open_backlog": self.n_open_backlog,
            "tau_v_mean": _round(self.tau_v_mean),
            "tau_v_median": _round(self.tau_v_median),
            "tail_p95": _round(self.tail_p95),
            "backlog_p95_age": _round(self.backlog_p95_age),
        }


# --------------------------------------------------------------------------- #
# Small stdlib statistics (no numpy dependency)
# --------------------------------------------------------------------------- #
def percentile(xs: Sequence[float], q: float) -> Optional[float]:
    """Linear-interpolation percentile, q in [0,100]. None if empty."""
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return float(s[0])
    rank = (q / 100.0) * (len(s) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return float(s[lo])
    frac = rank - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def theil_sen_slope(ys: Sequence[float]) -> Optional[float]:
    """Robust slope (per index step) via median of pairwise slopes."""
    n = len(ys)
    if n < 2:
        return None
    slopes = [(ys[j] - ys[i]) / (j - i) for i in range(n) for j in range(i + 1, n)]
    return median(slopes) if slopes else None


def mann_kendall(ys: Sequence[float]) -> tuple[float, float, str]:
    """Mann-Kendall trend test with normal approximation and tie correction.

    Returns (S, p_two_sided, direction). direction in {"increasing",
    "decreasing", "no trend"}. Suited to short, possibly non-normal series.
    """
    n = len(ys)
    if n < 3:
        return 0.0, 1.0, "no trend"
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += _sign(ys[j] - ys[i])
    # variance with ties
    var = n * (n - 1) * (2 * n + 5)
    _, counts = _tie_groups(ys)
    for t in counts:
        var -= t * (t - 1) * (2 * t + 5)
    var /= 18.0
    if var <= 0:
        return float(s), 1.0, "no trend"
    if s > 0:
        z = (s - 1) / math.sqrt(var)
    elif s < 0:
        z = (s + 1) / math.sqrt(var)
    else:
        z = 0.0
    p = 2.0 * (1.0 - _norm_cdf(abs(z)))
    p = min(max(p, 0.0), 1.0)
    if p < 0.05 and s > 0:
        direction = "increasing"
    elif p < 0.05 and s < 0:
        direction = "decreasing"
    else:
        direction = "no trend"
    return float(s), p, direction


# --------------------------------------------------------------------------- #
# Windowing
# --------------------------------------------------------------------------- #
def build_windows(
    events: Iterable[Event],
    *,
    now: Optional[datetime] = None,
    window_days: float = 30.0,
    n_windows: int = 12,
    cap_days: Optional[float] = 365.0,
) -> list[WindowMetric]:
    """Bucket events into `n_windows` consecutive windows ending at `now`.

    tau_v for a window = latency of items *closed within that window*.
    Backlog for a window = items opened before the window end and not yet
    closed by the window end (right-censored age measured to window end).
    """
    evs = list(events)
    now = _coerce_now(now, evs)
    win = timedelta(days=window_days)
    windows: list[WindowMetric] = []
    for k in range(n_windows):
        end = now - k * win
        start = end - win
        closed_lat = [
            e.latency_days(cap_days)
            for e in evs
            if e.closed_at is not None and start <= e.closed_at < end
        ]
        closed_lat = [x for x in closed_lat if x is not None]
        open_ages = [
            min((end - e.opened_at).total_seconds() / DAY, cap_days or math.inf)
            for e in evs
            if e.opened_at < end and (e.closed_at is None or e.closed_at >= end)
        ]
        open_ages = [a for a in open_ages if a >= 0]
        tail_pool = closed_lat + open_ages
        windows.append(
            WindowMetric(
                start=start,
                end=end,
                n_closed=len(closed_lat),
                n_open_backlog=len(open_ages),
                tau_v_mean=(sum(closed_lat) / len(closed_lat)) if closed_lat else None,
                tau_v_median=median(closed_lat) if closed_lat else None,
                tail_p95=percentile(tail_pool, 95),
                backlog_p95_age=percentile(open_ages, 95),
            )
        )
    windows.reverse()  # chronological order, oldest first
    return windows


# --------------------------------------------------------------------------- #
# Verdict
# --------------------------------------------------------------------------- #
@dataclass
class Assessment:
    status: str                          # OK | WATCH | ALERT | INSUFFICIENT_DATA
    reasons: list[str] = field(default_factory=list)
    trend_direction: str = "no trend"
    trend_p: float = 1.0
    trend_slope_per_window: Optional[float] = None
    baseline_tau_v: Optional[float] = None
    current_tau_v: Optional[float] = None
    robust_z: Optional[float] = None     # (current - baseline_median) / baseline_IQR
    tail_ratio: Optional[float] = None   # current tail_p95 / baseline tail_p95
    windows: list[WindowMetric] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "reasons": self.reasons,
            "trend_direction": self.trend_direction,
            "trend_p": _round(self.trend_p, 4),
            "trend_slope_per_window": _round(self.trend_slope_per_window),
            "baseline_tau_v": _round(self.baseline_tau_v),
            "current_tau_v": _round(self.current_tau_v),
            "robust_z": _round(self.robust_z),
            "tail_ratio": _round(self.tail_ratio),
            "windows": [w.as_dict() for w in self.windows],
            "disclaimer": self.disclaimer,
        }


def assess(
    events: Iterable[Event],
    *,
    now: Optional[datetime] = None,
    window_days: float = 30.0,
    n_windows: int = 12,
    baseline_windows: int = 4,
    cap_days: Optional[float] = 365.0,
    robust_z_watch: float = 1.5,
    robust_z_alert: float = 3.0,
    tail_ratio_alert: float = 1.5,
    min_closed_per_window: int = 3,
) -> Assessment:
    """Assess whether enforcement latency is rising in a locally-calibrated way.

    ALERT  : a *significant* rising trend (Mann-Kendall p<0.05, increasing)
             AND the current level is elevated vs local baseline
             (robust_z >= robust_z_alert OR tail_ratio >= tail_ratio_alert).
    WATCH  : exactly one of {significant rise, elevated level} holds.
    OK     : neither.
    INSUFFICIENT_DATA : too few closed items to calibrate honestly.
    """
    windows = build_windows(
        events, now=now, window_days=window_days,
        n_windows=n_windows, cap_days=cap_days,
    )
    series = [w.tau_v_mean for w in windows]
    tails = [w.tail_p95 for w in windows]

    populated = [(w, s) for w, s in zip(windows, series)
                 if s is not None and w.n_closed >= min_closed_per_window]
    if len(populated) < max(baseline_windows + 1, 3):
        return Assessment(
            status="INSUFFICIENT_DATA",
            reasons=[
                f"Only {len(populated)} windows have >= {min_closed_per_window} "
                f"closed items; need >= {max(baseline_windows + 1, 3)} to "
                f"calibrate a local baseline. Widen window_days or extend history."
            ],
            windows=windows,
        )

    vals = [s for _, s in populated]
    base_vals = vals[:baseline_windows]
    current = vals[-1]
    base_median = median(base_vals)
    iqr = (percentile(base_vals, 75) or base_median) - (percentile(base_vals, 25) or base_median)
    iqr = iqr if iqr and iqr > 1e-9 else max(base_median * 0.5, 1e-6)
    robust_z = (current - base_median) / iqr

    base_tails = [t for _, t in zip(range(baseline_windows), tails) if t is not None][:baseline_windows]
    cur_tail = next((t for t in reversed(tails) if t is not None), None)
    tail_ratio = (cur_tail / median(base_tails)) if (cur_tail and base_tails and median(base_tails) > 0) else None

    _, p, direction = mann_kendall(vals)
    slope = theil_sen_slope(vals)

    rising = direction == "increasing"
    elevated_z = robust_z >= robust_z_alert
    elevated_tail = tail_ratio is not None and tail_ratio >= tail_ratio_alert
    elevated = elevated_z or elevated_tail
    watch_level = robust_z >= robust_z_watch

    reasons: list[str] = []
    if rising:
        reasons.append(
            f"Sustained rise in tau_v across windows (Mann-Kendall p={p:.3f}, "
            f"Theil-Sen slope={slope:+.2f} days/window)."
        )
    if elevated_z:
        reasons.append(
            f"Current tau_v {current:.1f}d is {robust_z:.1f} robust-SD above local "
            f"baseline median {base_median:.1f}d."
        )
    if elevated_tail:
        reasons.append(
            f"Upper tail (P95 unresolved age) is {tail_ratio:.2f}x the baseline "
            f"tail -- backlog of unaddressed items is widening."
        )

    if rising and elevated:
        status = "ALERT"
    elif rising or elevated or watch_level:
        status = "WATCH"
        if not reasons:
            reasons.append(
                f"Current tau_v {current:.1f}d is {robust_z:.1f} robust-SD above "
                f"baseline (watch level)."
            )
    else:
        status = "OK"
        reasons.append(
            f"tau_v stable near local baseline (current {current:.1f}d vs "
            f"baseline {base_median:.1f}d; no significant trend, p={p:.3f})."
        )

    return Assessment(
        status=status,
        reasons=reasons,
        trend_direction=direction,
        trend_p=p,
        trend_slope_per_window=slope,
        baseline_tau_v=base_median,
        current_tau_v=current,
        robust_z=robust_z,
        tail_ratio=tail_ratio,
        windows=windows,
    )


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _sign(x: float) -> int:
    return (x > 0) - (x < 0)


def _tie_groups(ys: Sequence[float]):
    seen: dict[float, int] = {}
    for y in ys:
        seen[y] = seen.get(y, 0) + 1
    return list(seen.keys()), [c for c in seen.values() if c > 1]


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _coerce_now(now: Optional[datetime], evs: Sequence[Event]) -> datetime:
    if now is not None:
        return now
    stamps = [e.closed_at for e in evs if e.closed_at] + [e.opened_at for e in evs]
    if not stamps:
        return datetime.now(timezone.utc)
    return max(stamps)


def _round(x, nd: int = 2):
    return round(x, nd) if isinstance(x, (int, float)) else x
