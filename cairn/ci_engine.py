#!/usr/bin/env python3
"""
ci_engine.py -- Centric Intelligence: the layer that audits the auditor.
================================================================================
    python3 cairn/ci_engine.py        # stdlib, offline, $0, deterministic

*** ON THE NAME, HONESTLY ***
"Centric intelligence" is NOT a term we invented. It is an existing family --
human-centred AI, data-centric AI, target-centric intelligence analysis,
interaction-centred intelligence. We claim no novelty for the phrase. What is
specific here is the INSTANTIATION: three properties we can actually compute.

The EI layer (Assay) asks "how far does this text determine an answer?"
It does NOT ask two further questions, and CI does:

  C1 CALIBRATION       is the confidence it reports actually trustworthy?
  C2 OPTION-SPACE      did the interaction leave the human with more options?
  C3 SELF-VERIFIABILITY can the user check this WITHOUT the system?

A system whose confidence is uncorrelated with reality launders noise as
certainty. A system that reports uncertainty with no exit hands the user anxiety.
A system that cannot be independently checked cultivates dependence. CI measures
all three, and it OBSERVES ONLY -- it never adjusts an EI verdict (gate C4).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ei_llm import assay                                          # noqa: E402


# ---------------------------------------------------------------------------
# Ground truth is computed from the repository's STRUCTURED FIELDS, which the
# engine never sees. The engine sees only a natural-language sentence. This is
# what keeps calibration from being circular.
# ---------------------------------------------------------------------------
def structural_truth(repo):
    """Independent 0..1 quality signal from metadata the engine is not shown."""
    pts = 0.0
    if repo.get("license"):                       pts += 1          # legally reusable
    if len(repo.get("description") or "") >= 40:  pts += 1          # documented
    if repo.get("topics"):                        pts += 1          # categorised
    if not repo.get("archived"):                  pts += 1          # maintained
    denom = repo["forks"] + repo["open_issues"]
    if denom and (repo["forks"] / denom) >= 0.5:  pts += 1          # backlog under control
    return pts / 5.0


def describe(repo):
    """The sentence the engine is allowed to see. Deliberately free of the fields
    used for ground truth being stated as fields -- it is prose, as a user would type."""
    s = f"The project {repo['full_name']} has {repo['stars']} stars and {repo['forks']} forks"
    if repo.get("open_issues"):
        s += f" with {repo['open_issues']} open issues"
    if repo.get("description"):
        s += f". It is described as: {repo['description']}"
    if repo.get("pushed"):
        s += f". Last updated {repo['pushed']}."
    return s


def ece(pairs, bins=5):
    """Expected Calibration Error over equal-width bins. pairs = [(conf, truth)]."""
    if not pairs:
        return None, []
    tot, err, detail = len(pairs), 0.0, []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(c, t) for c, t in pairs if (c >= lo and (c < hi or (b == bins - 1 and c <= hi)))]
        if not sel:
            detail.append({"bin": f"{lo:.1f}-{hi:.1f}", "n": 0, "mean_conf": None, "mean_truth": None, "gap": None})
            continue
        mc = sum(c for c, _ in sel) / len(sel)
        mt = sum(t for _, t in sel) / len(sel)
        err += (len(sel) / tot) * abs(mc - mt)
        detail.append({"bin": f"{lo:.1f}-{hi:.1f}", "n": len(sel),
                       "mean_conf": round(mc, 3), "mean_truth": round(mt, 3), "gap": round(mc - mt, 3)})
    return err, detail


def ci_audit(repos, model="slate"):
    """Run the EI over each repo's description and audit the EI's own behaviour."""
    rows, pairs = [], []
    for r in repos:
        text = describe(r)
        a = assay(text, model=model)
        truth = structural_truth(r)
        conf = a["confidence"]
        has_next = bool(a.get("next_steps"))
        names_signals = bool(a.get("evidence")) and all("signal" in c for c in a["evidence"])
        if conf is not None:
            pairs.append((conf, truth))
        rows.append({
            "repo": r["full_name"], "verdict": a["verdict"], "confidence": conf,
            "structural_truth": round(truth, 3),
            "gap": (None if conf is None else round(conf - truth, 3)),
            "has_next_step": has_next, "names_signals": names_signals,
            "domain_flags": a.get("domain_flags", []), "receipt": a["receipt"],
        })
    e, detail = ece(pairs)
    band = ("well calibrated" if e is not None and e <= 0.15
            else "usable, gap disclosed" if e is not None and e <= 0.30
            else "POORLY CALIBRATED")
    return {
        "n": len(rows), "n_scored": len(pairs),
        "C1_ece": (None if e is None else round(e, 4)),
        "C1_band": band,
        "C1_bins": detail,
        "C2_option_space_fraction": round(sum(1 for x in rows if x["has_next_step"]) / len(rows), 3),
        "C3_self_verifiability_fraction": round(sum(1 for x in rows if x["names_signals"]) / len(rows), 3),
        "rows": rows,
        "limits": ("CI observes; it never adjusts an EI verdict. N is small. Ground truth is a "
                   "5-point structural proxy from metadata the engine never sees -- it is not "
                   "'real quality', and calling it that would be an overclaim."),
    }


if __name__ == "__main__":
    ROOT = os.path.dirname(HERE)
    repos = json.load(open(os.path.join(ROOT, "ei-dashboards/data/qwen_deepseek_frozen.json")))["repos"]
    print(json.dumps({k: v for k, v in ci_audit(repos).items() if k != "rows"}, indent=2))
