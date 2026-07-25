#!/usr/bin/env python3
"""
det_cohorts.py -- the empirical cohorts of the DETERMINISTIC laws (D>=Dmin,
F_out=F_eval), tested on real binary hard gates across four substrates.
================================================================================
Just as the LINEAR law E=U*D has yeast / GitHub-992 / knowledge / swarm, the
DETERMINISTIC threshold law D>=Dmin has these real cohorts -- every one a BINARY
hard gate (a candidate clears the bar or it does not):

  * GitHub      merge gate (CI + review)          survival = merged / (merged+closed_unmerged)
  * PubMed      integrity gate (not-retracted)    survival = 1 - retracted / total
  * HuggingFace eval-evidence gate                survival = frac reporting benchmark eval_results
  * bioRxiv     publication gate                  survivor-only -> pass-rate UNTESTABLE

    python3 deterministic-cohorts/det_cohorts.py     # stdlib only, offline, $0

Reads the ALREADY-FROZEN fixtures from the other modules (hash-pinned here). The
survivals span strict (HF) to lax-failure (PubMed) because D_min is a real,
gate-specific bar, not a universal constant. Layer-1, offline, $0. Pre-registered
gates DG1-DG4 (see prereg/det_cohorts_prereg.json). The two-regime interpretation
(Duniya linear incubator; Aakhirah deterministic terminal gate) is Layer-3, kept
separate from these measured binary-gate survivals.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "prereg", "det_cohorts_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
BAR = "=" * 80

FIX = {
    "github": os.path.join(ROOT, "two-regime", "data", "github_pr_survival_frozen.json"),
    "pubmed": os.path.join(ROOT, "pubmed-lism", "data", "pubmed_cohort_frozen.json"),
    "hf": os.path.join(ROOT, "hf-media", "data", "hf_media_cohort_frozen.json"),
    "biorxiv": os.path.join(ROOT, "biorxiv-lism", "data", "biorxiv_cohort_frozen.json"),
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix_hashes = {k: sha(v) for k, v in FIX.items()}
    lock_ok = spec_hash == man["spec_sha256"] and all(fix_hashes[k] == man["fixture_sha256"][k] for k in FIX)

    # ---- GitHub merge gate (binary: merged vs closed-unmerged) -------------- #
    gh = json.loads(open(FIX["github"], "rb").read())["repos"]
    gh_gates = [(r["full_name"], r["merged"], r["closed_unmerged"],
                 r["merged"] / (r["merged"] + r["closed_unmerged"])) for r in gh]
    gh_s = sum(s for *_, s in gh_gates) / len(gh_gates)

    # ---- PubMed integrity gate (binary: not-retracted vs retracted) --------- #
    pm = json.loads(open(FIX["pubmed"], "rb").read())["fields"]
    tot = sum(f["total"] for f in pm); ret = sum(f["retracted"] for f in pm)
    pm_s = 1 - ret / tot

    # ---- HuggingFace eval-evidence gate (binary: eval_results true/false) ---- #
    hf = json.loads(open(FIX["hf"], "rb").read())["models"]
    hf_pass = sum(1 for m in hf if m.get("eval_results")); hf_n = len(hf)
    hf_s = hf_pass / hf_n

    # ---- bioRxiv publication gate: survivor-only ---------------------------- #
    br = json.loads(open(FIX["biorxiv"], "rb").read())["records"]
    br_all_published = all("published_date" in r for r in br)

    measurable = {"github": gh_s, "pubmed": pm_s, "huggingface": hf_s}

    # ---- pre-registered gates ---------------------------------------------- #
    dg1 = (all(isinstance(r["merged"], int) and isinstance(r["closed_unmerged"], int) for r in gh)
           and all(isinstance(f["total"], int) and isinstance(f["retracted"], int) for f in pm)
           and all(isinstance(m.get("eval_results"), bool) for m in hf))
    dg2 = all(0 < s < 1 for s in measurable.values())
    spread = max(measurable.values()) / min(measurable.values())
    dg3 = spread >= 3.0
    dg4 = br_all_published  # survivor-only confirmed -> pass-rate untestable

    print(BAR)
    print(" EMPIRICAL COHORTS OF THE DETERMINISTIC LAW  D>=Dmin  (binary hard gates)")
    print(BAR)
    print("\n [lock] spec %s   fixtures %s" % ("MATCH" if spec_hash == man["spec_sha256"] else "MISMATCH",
          "MATCH" if all(fix_hashes[k] == man["fixture_sha256"][k] for k in FIX) else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    print("\n GitHub merge gate (CI + review):")
    for name, mg, cu, s in gh_gates:
        print("   %-24s merged %6d  unmerged %5d   s = %.3f" % (name, mg, cu, s))
    print("   mean survival = %.3f" % gh_s)
    print("\n PubMed integrity gate (not-retracted, pooled N=%d): %d retracted -> s = %.5f" % (tot, ret, pm_s))
    print(" HuggingFace eval-evidence gate: %d/%d report benchmark eval_results -> s = %.3f" % (hf_pass, hf_n, hf_s))
    print(" bioRxiv publication gate: %d records, all published (survivor-only) -> pass-rate UNTESTABLE" % len(br))

    print("\n DG1 gates are binary/deterministic (integer pass/fail counts) -> %s" % ("PASS" if dg1 else "FAIL"))
    print(" DG2 every measurable gate is a genuine filter (0<s<1)          -> %s" % ("PASS" if dg2 else "FAIL"))
    print(" DG3 D_min is a real bar (survival spread %.1fx >= 3)            -> %s" % (spread, "PASS" if dg3 else "FAIL"))
    print("     strict HF eval-gate %.3f ... lax-failure PubMed %.5f" % (hf_s, pm_s))
    print(" DG4 bioRxiv publication pass-rate DECLARED UNTESTABLE (survivor-only) -> %s" % ("PASS" if dg4 else "FAIL"))

    green = lock_ok and dg1 and dg2 and dg3 and dg4
    out = {"spec_sha256": spec_hash, "fixture_sha256": fix_hashes, "lock_ok": lock_ok,
           "github_merge_gate": {"mean_survival": round(gh_s, 4), "repos": [{"repo": n, "s": round(s, 4)} for n, *_, s in gh_gates]},
           "pubmed_integrity_gate": {"pooled_n": tot, "retracted": ret, "survival": round(pm_s, 5)},
           "hf_eval_gate": {"pass": hf_pass, "n": hf_n, "survival": round(hf_s, 4)},
           "biorxiv_publication_gate": "survivor-only -> pass-rate UNTESTABLE",
           "DG1_binary": dg1, "DG2_genuine_filter": dg2, "DG3_Dmin_spread": {"spread": round(spread, 2), "pass": dg3},
           "DG4_biorxiv_untestable": dg4,
           "note": "the deterministic threshold law D>=Dmin has real binary-gate cohorts on GitHub/PubMed/HF; bioRxiv survivor-only; D_min is gate-specific.",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_det_cohorts.json"), "w"), indent=2)

    print("\n" + BAR)
    print(" RESULT: %s — the deterministic threshold law D>=Dmin has real binary-gate cohorts across" % ("GREEN" if green else "RED"))
    print(" GitHub / PubMed / HuggingFace; bioRxiv honestly survivor-only. D_min is gate-specific, not universal.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
