#!/usr/bin/env python3
"""run_oss.py — the two runs registered in prereg_oss.md, offline.

    python3 oss-audit/run_oss.py

RUN A  the derivation structure of 24 trending open-weight models
RUN B  IHCEI's false-alarm rate on 20 ordinary Qwen/DeepSeek descriptions

No network. Both cohorts are frozen fixtures already in this repository. The
pre-registration was written and hashed before either run existed; the hash is
asserted by test_oss.py and printed below.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ihcei_v3"))

from spar.spar import Structure, bearings, single_points   # noqa: E402
from fathom.fathom import Claim, sound                     # noqa: E402

PREREG = os.path.join(ROOT, "oss-audit", "prereg_oss.md")
PREREG_SHA = "d8ea04f0f39a4ea9b79980fc8c2438e6767d4e5b4a639411a1ef32cf3d26c148"

out = {}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ═══════════════════════════════════════════════════════ RUN A — structure ═══
def run_a():
    path = os.path.join(ROOT, "hf-cohort", "data", "hf_cohort_frozen.json")
    models = json.load(open(path))["models"]

    # The declared derivation edges. `base_model` is what an uploader wrote in a
    # metadata field -- see NULL-1. An absent edge is an absent DECLARATION.
    derived = [(m["id"], m["base_model"]) for m in models if m.get("base_model")]

    # THE COLLISION. A name can be both a model in the cohort and the declared
    # base of another model. bearings() keys nodes by name, so without this the
    # two silently become one node and every number below is computed on a graph
    # nobody described. Found on this exact data while building press.js.
    ids = {m["id"] for m in models}
    bases = {b for _, b in derived}
    collisions = sorted(ids & bases)

    parts, seen = [], set()
    for n in [m["id"] for m in models] + [b for _, b in derived]:
        if n not in seen:
            seen.add(n)
            parts.append(n)
    links = [(mid, base, 1.0) for mid, base in derived]

    st = Structure(parts, links)
    b = bearings(st)
    sp = single_points(st)
    sp_names = [r["part"] for r in sp]

    # children per base
    kids = {}
    for mid, base in derived:
        kids.setdefault(base, []).append(mid)
    ranked = sorted(kids.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    # A5 -- the 1/m^2 law on a real shared base, measured by the same engine
    law = {}
    for base, children in ranked:
        m = len(children)
        if m < 1:
            continue
        claim = "the family stands"
        ls = [(c, base, 1.0) for c in children] + [(base, claim, 1.0)]
        r = sound(Claim(claim, children, ls))
        law[base] = {
            "m": m,
            "settles": [round(x["dependence"], 12) for x in r["by_source"]],
            "expected_one_over_m2": round(1.0 / (m * m), 12),
            "deepest_dependence": r["deepest_dependence"],
            "rests_on_one_thread": r["rests_on_one_thread"],
        }

    # A6 -- a derived model whose base vanishes has nothing left, because one
    # declared base is the whole of its declared support.
    no_second_support = [mid for mid, _ in derived]

    out["A"] = {
        "n_models": len(models),
        "n_declaring_a_base": len(derived),
        "pieces": b["pieces"],
        "parts_in_graph": len(parts),
        "links": len(links),
        "conserved": b["conserved"],
        "total_bearing": b["total"],
        "expected_total": b["expected_total"],
        "single_points": sp_names,
        "single_points_that_are_bases": sorted(set(sp_names) & bases),
        "collisions_model_and_base": collisions,
        "most_depended_base": ranked[0][0] if ranked else None,
        "most_depended_count": len(ranked[0][1]) if ranked else 0,
        "children_per_base": {k: len(v) for k, v in ranked},
        "law": law,
        "share_no_second_support": round(len(no_second_support) / len(models), 6),
    }


# ═══════════════════════════════════════════════════ RUN B — false alarms ═══
def run_b():
    from nere_engine_v3 import NEREEngineV3

    path = os.path.join(ROOT, "ei-dashboards", "data", "qwen_deepseek_frozen.json")
    repos = json.load(open(path))["repos"]
    texts = [(r["full_name"], (r.get("description") or "").strip())
             for r in repos]
    texts = [(n, t) for n, t in texts if t]

    off = NEREEngineV3(corroboration_gate=False)
    on = NEREEngineV3(corroboration_gate=True)

    rows = []
    for name, text in texts:
        vo, vn = off.evaluate(text), on.evaluate(text)
        rows.append({
            "repo": name,
            "chars": len(text),
            "gate_off": {"verdict": vo.verdict, "p": round(vo.p_manipulative, 4)},
            "gate_on": {"verdict": vn.verdict, "p": round(vn.p_manipulative, 4)},
            "changed": vo.verdict != vn.verdict,
            # a "mechanism" is a NAMED manipulation route, not a tone
            "mechanism": any(g.hits > 0 and g.gate_id in (2, 4, 5)
                             for g in vn.gate_evidence),
        })

    def tally(key):
        c = {"BLOCK": 0, "WARN": 0, "PASS": 0}
        for r in rows:
            c[r[key]["verdict"]] += 1
        return c

    out["B"] = {
        "n_with_text": len(rows),
        "n_repos": len(repos),
        "gate_off": tally("gate_off"),
        "gate_on": tally("gate_on"),
        "changed": sum(1 for r in rows if r["changed"]),
        "with_mechanism": sum(1 for r in rows if r["mechanism"]),
        "rows": rows,
    }


if __name__ == "__main__":
    got = sha(PREREG)
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited since it was locked\n"
                         f"  locked {PREREG_SHA}\n  now    {got}")
    run_a()
    run_b()
    out["_prereg"] = {"file": "oss-audit/prereg_oss.md", "sha256": got}
    out["_cohorts"] = {
        "hf": sha(os.path.join(ROOT, "hf-cohort", "data", "hf_cohort_frozen.json")),
        "qwen_deepseek": sha(os.path.join(
            ROOT, "ei-dashboards", "data", "qwen_deepseek_frozen.json")),
    }
    dest = os.path.join(ROOT, "oss-audit", "results_oss.json")
    json.dump(out, open(dest, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k != "B"}, indent=1)[:2600])
    print("\nRUN B:", json.dumps({k: v for k, v in out["B"].items()
                                  if k != "rows"}, indent=1))
