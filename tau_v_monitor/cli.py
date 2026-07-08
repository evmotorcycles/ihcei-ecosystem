"""
tau_v_monitor.cli
=================
Command-line entry point. Reads a CSV (or JSON array) of flagged items with
open/close timestamps and prints a locally-calibrated tau_v assessment.

    python -m tau_v_monitor --csv incidents.csv \
        --opened-key created_at --closed-key resolved_at \
        --window-days 30 --n-windows 12

    # GitHub issues JSON (array from GET /issues):
    python -m tau_v_monitor --github-json issues.json

Read-only, shadow-mode by construction: it only consumes timestamps.
"""
from __future__ import annotations

import argparse
import json
import sys

from .adapters import from_csv, from_github_issues, from_records
from .core import assess


def _load_json(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else data.get("items", [])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="tau_v_monitor",
        description="Locally-calibrated enforcement-latency (tau_v) early-warning monitor.",
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", help="CSV with opened/closed timestamp columns")
    src.add_argument("--json", help="JSON array of records with opened/closed keys")
    src.add_argument("--github-json", help="JSON array from GitHub GET /issues")

    ap.add_argument("--opened-key", default="opened_at")
    ap.add_argument("--closed-key", default="closed_at")
    ap.add_argument("--category-key", default="category")
    ap.add_argument("--window-days", type=float, default=30.0)
    ap.add_argument("--n-windows", type=int, default=12)
    ap.add_argument("--baseline-windows", type=int, default=4)
    ap.add_argument("--cap-days", type=float, default=365.0)
    ap.add_argument("--min-closed-per-window", type=int, default=3)
    ap.add_argument("--pretty", action="store_true", help="human-readable output")
    a = ap.parse_args(argv)

    if a.csv:
        events = from_csv(a.csv, opened_key=a.opened_key,
                          closed_key=a.closed_key, category_key=a.category_key)
    elif a.json:
        events = from_records(_load_json(a.json), opened_key=a.opened_key,
                              closed_key=a.closed_key, category_key=a.category_key)
    else:
        events = from_github_issues(_load_json(a.github_json))

    if not events:
        print(json.dumps({"status": "INSUFFICIENT_DATA",
                          "reasons": ["No usable events with an open timestamp."]}))
        return 2

    result = assess(
        events,
        window_days=a.window_days,
        n_windows=a.n_windows,
        baseline_windows=a.baseline_windows,
        cap_days=a.cap_days,
        min_closed_per_window=a.min_closed_per_window,
    )

    if a.pretty:
        _print_pretty(result, len(events))
    else:
        print(json.dumps(result.as_dict(), indent=2))
    # Exit code encodes severity for CI / cron use.
    return {"OK": 0, "WATCH": 0, "ALERT": 1, "INSUFFICIENT_DATA": 2}.get(result.status, 0)


def _print_pretty(r, n_events: int) -> None:
    bar = "=" * 68
    icon = {"OK": "OK   ", "WATCH": "WATCH", "ALERT": "ALERT", "INSUFFICIENT_DATA": "N/A  "}
    print(bar)
    print(f"  tau_v enforcement-latency monitor   [{icon.get(r.status, r.status)}]")
    print(bar)
    print(f"  events analyzed        : {n_events}")
    if r.current_tau_v is not None:
        print(f"  current tau_v (mean)   : {r.current_tau_v:.1f} days")
        print(f"  local baseline tau_v   : {r.baseline_tau_v:.1f} days")
        print(f"  robust z vs baseline   : {r.robust_z:+.2f}")
    if r.tail_ratio is not None:
        print(f"  upper-tail ratio (P95) : {r.tail_ratio:.2f}x baseline")
    print(f"  trend                  : {r.trend_direction} (Mann-Kendall p={r.trend_p:.3f})")
    print("  " + "-" * 66)
    for reason in r.reasons:
        print(f"  - {reason}")
    print("  " + "-" * 66)
    print(f"  NOTE: {r.disclaimer}")
    print(bar)


if __name__ == "__main__":
    sys.exit(main())
