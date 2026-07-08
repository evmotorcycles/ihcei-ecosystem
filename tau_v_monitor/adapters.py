"""
tau_v_monitor.adapters
=======================
Shape real-world records into the domain-agnostic `Event` stream the core
consumes. Each adapter maps one domain's timestamps onto (opened_at,
closed_at, category). Add your own by returning a list[Event].

The three instantiations named in the LISM manuscript's Discussion:
  * software reliability : issue / defect open -> close  (GitHub issues here)
  * finance & audit      : audit finding raised -> remediated
  * clinical governance  : patient-safety report filed -> RCA closed
all reduce to the same (opened_at, closed_at) pair.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from typing import Iterable, Optional

from .core import Event


def _parse_ts(value) -> Optional[datetime]:
    """Parse ISO-8601 (incl. trailing 'Z') or common date forms; None if blank."""
    if value in (None, "", "null", "None"):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Unrecognized timestamp: {value!r}")
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def from_records(
    records: Iterable[dict],
    *,
    opened_key: str = "opened_at",
    closed_key: str = "closed_at",
    category_key: Optional[str] = "category",
) -> list[Event]:
    """Generic mapping from an iterable of dict rows to Events."""
    out: list[Event] = []
    for r in records:
        opened = _parse_ts(r.get(opened_key))
        if opened is None:
            continue  # an item with no open time cannot contribute latency
        out.append(
            Event(
                opened_at=opened,
                closed_at=_parse_ts(r.get(closed_key)),
                category=(r.get(category_key) if category_key else None),
            )
        )
    return out


def from_csv(
    path: str,
    *,
    opened_key: str = "opened_at",
    closed_key: str = "closed_at",
    category_key: Optional[str] = "category",
) -> list[Event]:
    with open(path, newline="", encoding="utf-8") as fh:
        return from_records(
            csv.DictReader(fh),
            opened_key=opened_key,
            closed_key=closed_key,
            category_key=category_key,
        )


def from_github_issues(issues: Iterable[dict]) -> list[Event]:
    """Map GitHub REST `GET /issues` payloads to Events.

    Excludes pull requests (which carry a 'pull_request' key) exactly as the
    manuscript's tau_v definition does ("closed non-pull-request issues").
    """
    out: list[Event] = []
    for it in issues:
        if it.get("pull_request"):
            continue
        opened = _parse_ts(it.get("created_at"))
        if opened is None:
            continue
        labels = it.get("labels") or []
        cat = None
        for lb in labels:
            name = lb.get("name") if isinstance(lb, dict) else lb
            if name and any(k in str(name).lower() for k in ("bug", "sev", "p0", "p1", "security")):
                cat = str(name)
                break
        out.append(Event(opened_at=opened, closed_at=_parse_ts(it.get("closed_at")), category=cat))
    return out
