#!/usr/bin/env python3
"""run_blueprint.py — Page Code's blueprint on projects an agent wrote.

    python3 page-code/run_blueprint.py

Offline, deterministic, no network. Predictions locked in prereg_blueprint.md
before any import graph was looked at.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

# page-code has a hyphen, so it is not an importable package name.
_spec = importlib.util.spec_from_file_location(
    "blueprint", os.path.join(HERE, "blueprint.py"))
bpmod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bpmod)

from keel.keel import survey, abstained   # noqa: E402

PREREG_SHA = "bf47c93de29edd2cb030a23a370d04ec9e9b7e9a25132a221c6dadc36e2f1fc9"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def slot(r):
    return {"status": r.status, "says": r.says, "detail": r.detail}


def audit_project(root, name):
    bp = bpmod.blueprint(root, name)
    s = survey(bp["project"])
    fi = bpmod.fan_in(bp)
    row = {
        "name": name,
        "counts": bp["counts"],
        "sole_routes": slot(s.sole_routes),
        "fan_in_top": fi[:8],
        "abstained": abstained(s),
    }
    if fi:
        hub = fi[0][0]
        cs = survey(bpmod.as_claim(bp, hub))
        row["hub"] = hub
        row["hub_fan_in"] = fi[0][1]
        row["counted_twice"] = slot(cs.counted_twice)
    return row


if __name__ == "__main__":
    got = sha(os.path.join(HERE, "prereg_blueprint.md"))
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited since it was locked\n"
                         f"  locked {PREREG_SHA}\n  now    {got}")

    out = {
        "this_repo": audit_project(ROOT, "this repository"),
        "ihcei_v3": audit_project(os.path.join(ROOT, "ihcei_v3"), "ihcei_v3"),
        "_boundary": {
            "understands_language": bpmod.UNDERSTANDS_LANGUAGE,
            "proves": bpmod.PROVES,
            "cannot": bpmod.CANNOT,
        },
        "_prereg": {"file": "page-code/prereg_blueprint.md", "sha256": got},
    }
    json.dump(out, open(os.path.join(HERE, "results_blueprint.json"), "w"),
              indent=1, sort_keys=True)

    for key in ("this_repo", "ihcei_v3"):
        r = out[key]
        c = r["counts"]
        print(f"\n══ {r['name']} ══")
        print(f"  files scanned {c['files_scanned']}  in graph "
              f"{c['files_in_graph']}  isolated {c['files_isolated']}  "
              f"edges {c['edges']}")
        print(f"  sole_routes   {r['sole_routes']['status']}  "
              f"{r['sole_routes']['says']}")
        d = r["sole_routes"]["detail"]
        if d:
            print(f"     pieces {d.get('pieces')}  single points: "
                  f"{d.get('single_points')}")
        print(f"  fan-in top    {r['fan_in_top'][:5]}")
        if "counted_twice" in r:
            ct = r["counted_twice"]
            print(f"  hub {r['hub']} (fan-in {r['hub_fan_in']})")
            print(f"  counted_twice {ct['status']}  "
                  f"each settles {ct['detail'].get('each_settles')}")
