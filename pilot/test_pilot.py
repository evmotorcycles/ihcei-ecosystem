"""pytest wrapper for the 90-day shadow-mode tau_v pilot on real OSS repos."""
import json
import os
from datetime import datetime, timezone

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tau_v_monitor import from_github_issues, assess  # noqa: E402

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "fixtures", "pilot_raw_issues.json")))


def _assess(repo):
    r = next(x for x in DATA["repos"] if x["repo"] == repo)
    ev = from_github_issues(
        [{"created_at": i["created_at"], "closed_at": i["closed_at"]} for i in r["issues"]]
    )
    return assess(ev, now=NOW, window_days=90, n_windows=16, min_closed_per_window=3)


def test_healthy_repo_reads_ok():
    assert _assess("pallets/flask").status == "OK"


def test_maintenance_repo_is_flagged():
    a = _assess("moment/moment")
    assert a.status in ("WATCH", "ALERT")


def test_flag_is_locally_calibrated_elevation():
    a = _assess("moment/moment")
    assert a.robust_z is not None and a.robust_z >= 3.0


def test_baselines_are_repo_specific():
    # No transplanted threshold: each repo calibrates to its own history.
    assert _assess("pallets/flask").baseline_tau_v != _assess("moment/moment").baseline_tau_v
