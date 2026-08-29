#!/usr/bin/env python3
"""run_keel.py — KEEL against every real cohort this repository holds.

    python3 keel/run_keel.py

Offline, deterministic, no network. Predictions locked in prereg_keel.md
before this file existed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from keel.keel import survey, abstained, validate, Refused, Survey  # noqa: E402
from tau_v_monitor.core import Event                                # noqa: E402

PREREG_SHA = "5378d4ec236671e7fbc9c80c6ef17faecb6f2da0cee8c96f35e6519109978444"
out = {}
surveys = {}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ── cohort 1: the real HF derivation forest ─────────────────────────────────
def hf_project():
    models = json.load(open(os.path.join(
        ROOT, "hf-cohort", "data", "hf_cohort_frozen.json")))["models"]
    derived = [(m["id"], m["base_model"]) for m in models if m.get("base_model")]
    parts, seen = [], set()
    for n in [m["id"] for m in models] + [b for _, b in derived]:
        if n not in seen:
            seen.add(n)
            parts.append(n)
    return {"name": "open-weight model lineage (24 trending)",
            "parts": parts,
            "links": [(a, b, 1.0) for a, b in derived]}


# ── cohort 2: the four derivatives of one base, as a claim ──────────────────
def one_fibre_project():
    models = json.load(open(os.path.join(
        ROOT, "hf-cohort", "data", "hf_cohort_frozen.json")))["models"]
    hub = "Qwen/Qwen3.6-27B"
    kids = [m["id"] for m in models if m.get("base_model") == hub]
    claim = "this family of models is independently supported"
    links = [(k, hub, 1.0) for k in kids] + [(hub, claim, 1.0)]
    return {"name": "four derivatives, one base",
            "parts": kids + [hub, claim], "links": links,
            "conclusion": claim, "supports": kids}


# ── cohort 3: the same shape with genuinely separate origins ────────────────
def four_fibres_project():
    claim = "the estimate holds"
    sup = ["the 2026 filing", "the supplier quote",
           "the site measurement", "the council register"]
    origins = ["filing office", "supplier", "the site", "the council"]
    links = [(s, o, 1.0) for s, o in zip(sup, origins)] + \
            [(o, claim, 1.0) for o in origins]
    return {"name": "four supports, four origins",
            "parts": sup + origins + [claim], "links": links,
            "conclusion": claim, "supports": sup}


# ── cohort 4: 22 real Qwen/DeepSeek repositories under their orgs ───────────
def org_project():
    repos = json.load(open(os.path.join(
        ROOT, "ei-dashboards", "data", "qwen_deepseek_frozen.json")))["repos"]
    parts, links, seen = [], [], set()
    for r in repos:
        parts.append(r["full_name"])
        if r["org"] not in seen:
            seen.add(r["org"])
            parts.append(r["org"])
        links.append((r["full_name"], r["org"], 1.0))
    return {"name": "22 Qwen and DeepSeek repositories",
            "parts": parts, "links": links}


# ── cohort 5: an ordinary AI-assisted project plan ──────────────────────────
def assistant_plan_project():
    """The everyday case: a person asks an assistant for a plan and it comes
    back with four confident supports. Every one came from the same reply."""
    claim = "the launch plan is sound"
    sup = ["the cost figure", "the timeline", "the supplier list",
           "the compliance step"]
    links = [(s, "what the assistant said", 1.0) for s in sup] + \
            [("what the assistant said", claim, 1.0)]
    return {"name": "an AI-written launch plan",
            "parts": sup + ["what the assistant said", claim], "links": links,
            "conclusion": claim, "supports": sup}


# ── cohort 6: the tau_v cohort, to find out whether it can be fed at all ────
def tauv_project():
    d = json.load(open(os.path.join(ROOT, "repro", "tauv_cohort.json")))
    rows = d["repos"]
    # The cohort carries an AGGREGATE tau_v per repository, not the per-item
    # open/close timestamps assess() needs. Whether that means the reading
    # abstains is exactly prediction K5, so nothing is synthesised to avoid it.
    events = []
    parts = [r["repo"] for r in rows]
    return ({"name": "the tau_v repository cohort",
             "parts": parts, "links": [], "events": events},
            {"n_rows": len(rows), "has_per_item_timestamps": False,
             "fields": sorted(rows[0].keys())})


# ── cohort 7: SYNTHETIC rising latency — tests the engine, not the world ────
def synthetic_rising():
    now = datetime(2026, 8, 29)
    evs = []
    for w in range(12):
        lat = 5 + w * 4                       # 5 -> 49 days, monotone rise
        end = now - timedelta(days=(11 - w) * 30)
        for i in range(5):
            closed = end - timedelta(days=30 - (i + 1) * 5)
            evs.append(Event(opened_at=closed - timedelta(days=lat),
                             closed_at=closed))
    return {"name": "SYNTHETIC rising latency (engine test only)",
            "parts": ["one part"], "links": [], "events": evs, "now": now}


def record(key, project, extra=None):
    s = survey(project)
    surveys[key] = s
    # DEFECT, found by running this: the first version spread `detail` into the
    # same dict as `status`, and the latency detail carries its own `status`
    # key (OK/WATCH/ALERT). The nested one silently overwrote the readout's, so
    # a READ latency serialised as "ALERT" and the abstain count was wrong by
    # one. Same shape as the node-name collision in press.js: two different
    # things sharing a key, one of them vanishing without a word. The detail is
    # now nested rather than merged, so no future detail key can reach it.
    def slot(r):
        return {"status": r.status, "says": r.says, "detail": r.detail}

    row = {"name": s.name,
           "sole_routes": slot(s.sole_routes),
           "counted_twice": slot(s.counted_twice),
           "latency": slot(s.latency),
           "abstained": abstained(s)}
    if extra:
        row["_cohort"] = extra
    out[key] = row


if __name__ == "__main__":
    got = sha(os.path.join(HERE, "prereg_keel.md"))
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited since it was locked\n"
                         f"  locked {PREREG_SHA}\n  now    {got}")

    record("hf_lineage", hf_project())
    record("one_fibre", one_fibre_project())
    record("four_fibres", four_fibres_project())
    record("orgs", org_project())
    record("assistant_plan", assistant_plan_project())
    p, extra = tauv_project()
    record("tauv_cohort", p, extra)
    record("synthetic_rising", synthetic_rising())

    # ── the contract checks ────────────────────────────────────────────────
    contract = {}
    try:
        validate({"name": "x", "parts": ["a"], "stars": 104122})
        contract["L3_refuses_unaccepted_field"] = False
    except Refused as e:
        contract["L3_refuses_unaccepted_field"] = True
        contract["L3_message"] = str(e)[:120]
    try:
        validate({"name": "x", "parts": ["a"], "readouts": {}})
        contract["L6_refuses_its_own_output"] = False
    except Refused:
        contract["L6_refuses_its_own_output"] = True

    blob = json.dumps(out)
    contract["L9_no_fused_field"] = not any(
        w in blob for w in ("overall_score", "health_score", "combined",
                            "project_score", "total_score"))

    reads = sum(1 for r in out.values()
                for k in ("sole_routes", "counted_twice", "latency")
                if r[k]["status"] == "READ")
    total = len(out) * 3
    contract["readouts_total"] = total
    contract["readouts_read"] = reads
    contract["abstain_rate"] = round((total - reads) / total, 4)
    contract["latency_abstained_on_real_cohorts"] = all(
        out[k]["latency"]["status"] != "READ"
        for k in out if k != "synthetic_rising")
    contract["synthetic_latency_band"] = out["synthetic_rising"]["latency"]["detail"].get("status")

    out["_contract"] = contract
    out["_prereg"] = {"file": "keel/prereg_keel.md", "sha256": got}

    json.dump(out, open(os.path.join(HERE, "results_keel.json"), "w"),
              indent=1, sort_keys=True)

    print(json.dumps(contract, indent=1))
    print("\n── per cohort ──")
    for k, r in out.items():
        if k.startswith("_"):
            continue
        print(f"\n{k}  [{r['name']}]")
        for kind in ("sole_routes", "counted_twice", "latency"):
            print(f"   {kind:14s} {r[kind]['status']:9s} {r[kind]['says'][:76]}")
