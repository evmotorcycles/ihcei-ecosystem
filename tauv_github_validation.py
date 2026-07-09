#!/usr/bin/env python3
"""
tauv_github_validation.py
========================
A thorough, live validation of the enforcement-latency sensor (tau_v) on a fresh,
independent set of GitHub repositories, fetched via api/gh-issues.js. Reproduces
the manuscript's Third Law logic on new data:

  tau_v(repo) = mean close latency (days, capped 365) of that repo's closed,
                non-PR issues.
  E (lifecycle): survived (1) if NOT archived AND pushed within 24 months;
                 failed (0) if archived OR no push in > 24 months.
  Test: is tau_v higher in failed repos than surviving ones? (Mann-Whitney, one-tailed)

Also exercises the shipped tau_v_monitor on each repo (trajectory/verdict), so the
same sensor code that would run in production is what is validated here.

Input: one or more gh-issues JSON responses (--json a.json b.json ...) or a
directory (--dir) of them.
"""
import argparse
import glob
import json
import os
from datetime import datetime, timezone

import numpy as np
from scipy.stats import mannwhitneyu

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tau_v_monitor import from_github_issues, assess  # noqa: E402

DAY = 86400.0
NOW = datetime.now(timezone.utc)


def parse_ts(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def repo_tau_v(issues, cap=365.0):
    lat = []
    for it in issues:
        o, c = parse_ts(it.get("created_at")), parse_ts(it.get("closed_at"))
        if o and c:
            d = max((c - o).total_seconds() / DAY, 0.0)
            lat.append(min(d, cap))
    return (float(np.mean(lat)), len(lat)) if lat else (float("nan"), 0)


def label_E(meta):
    pushed = parse_ts(meta.get("pushed_at"))
    stale = pushed is None or (NOW - pushed).days > 730
    return 0 if (meta.get("archived") or stale) else 1  # 0=failed, 1=survived


def load(paths):
    out = []
    for p in paths:
        raw = open(p).read()
        try:
            d = json.loads(json.loads(raw)["text"]) if raw.lstrip().startswith("{\"success") else json.loads(raw)
        except Exception:
            import re
            m = re.search(r'\{"repo".*\}', raw, re.DOTALL)
            d = json.loads(m.group(0))
        if "repo" in d:
            out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", nargs="*", default=[])
    ap.add_argument("--dir", default=None)
    a = ap.parse_args()
    paths = list(a.json)
    if a.dir:
        paths += sorted(glob.glob(os.path.join(a.dir, "*.json")))
    repos = load(paths)

    print("=" * 78)
    print("tau_v live validation on fresh GitHub repositories")
    print("=" * 78)
    rows = []
    for m in repos:
        tv, nclosed = repo_tau_v(m.get("issues", []))
        E = label_E(m)
        # exercise the shipped sensor too
        ev = from_github_issues([{"created_at": i["created_at"], "closed_at": i["closed_at"]}
                                 for i in m.get("issues", [])])
        verdict = assess(ev, window_days=30, n_windows=12).status if ev else "NO_DATA"
        rows.append((m["repo"], E, tv, nclosed, m.get("archived"), m.get("pushed_at", "")[:10], verdict))
        print(f"  {m['repo']:34s} E={'surv' if E else 'FAIL'}  "
              f"tau_v={tv:6.1f}d  n_closed={nclosed:4d}  archived={bool(m.get('archived'))}  "
              f"pushed={m.get('pushed_at','')[:10]}  monitor={verdict}")

    failed = [r[2] for r in rows if r[1] == 0 and np.isfinite(r[2])]
    surv = [r[2] for r in rows if r[1] == 1 and np.isfinite(r[2])]
    print("\n" + "-" * 78)
    print(f"repos: {len(rows)}  (failed={sum(1 for r in rows if r[1]==0)}, "
          f"survived={sum(1 for r in rows if r[1]==1)})")
    if failed and surv:
        mf, ms = np.mean(failed), np.mean(surv)
        try:
            _, p = mannwhitneyu(failed, surv, alternative="greater")
        except Exception:
            p = float("nan")
        print(f"mean tau_v  failed = {mf:.1f}d   survived = {ms:.1f}d   ratio = {mf/ms:.2f}x")
        print(f"Mann-Whitney one-tailed (failed > survived): p = {p:.4g}")
        print("-> " + ("DIRECTION CONFIRMED: failed repos close their own issues slower"
                       if mf > ms else "direction not reproduced on this sample"))
    else:
        print("need >=1 failed and >=1 survived repo with closed issues for the test")
    print("=" * 78)


if __name__ == "__main__":
    main()
