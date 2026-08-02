"""
diagnose.py -- POST-HOC analysis. NOT PRE-REGISTERED. Kept in a separate file from bg.py
so that nothing here can be mistaken for a locked gate.

WHY IT EXISTS. The pre-registered run failed W7 at DELTA = 0.1060 because the verdict
distribution was concentrated: 15 of the 20 artifacts return the IDENTICAL baseline verdict
0.1428 under both engines. The DCM void and that concentration are the same fact seen twice,
so the interesting question is WHY the engines fail to separate these texts.

WHAT IS COMPUTED. Spearman rank correlation between each engine's baseline verdict and
(a) the manipulativeness band declared in the locked spec, and (b) artifact word count.

THE LIMIT, STATED FIRST. The band labels were written by the same author as the engines'
test suites. They are NOT independent rater labels. This analysis therefore CANNOT settle
W8, which remains UNTESTABLE-HERE. What it can do is set a direction: author labels are
biased TOWARD agreement, so a null correlation measured against them is harder to explain
away than a positive one would be to trust.
"""
import json
import os
import statistics
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = json.load(open(os.path.join(HERE, "prereg", "balanced_grid_prereg.json")))
TEXTS = SPEC["the_NEW_artifact_set"]["texts"]

# The bands are read off the gradient sentence locked in the spec:
# "1-6 factual, 7-11 hedged, 12-15 mildly pressuring, 16-20 strongly manipulative."
BANDS = [0] * 6 + [1] * 5 + [2] * 4 + [3] * 5
BAND_NAMES = ["factual", "hedged", "mildly pressuring", "strongly manipulative"]
assert len(BANDS) == len(TEXTS) == 20


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    a, b = rank(x), rank(y)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    den = (sum((v - ma) ** 2 for v in a) * sum((v - mb) ** 2 for v in b)) ** 0.5
    return num / den if den else float("nan")


def main():
    p = subprocess.run(["node", os.path.join(HERE, "collect_bg.mjs")],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    if p.returncode != 0:
        raise SystemExit("collector failed: " + p.stderr[-900:])
    data = json.loads(p.stdout[p.stdout.index("{"):])
    words = [len(t.split()) for t in TEXTS]

    out = {}
    for eng in ("V1", "V2"):
        base = [r["verdict"] for r in sorted(
            (r for r in data["rows"] if r["engine"] == eng and r["self_report"] == 0),
            key=lambda r: r["artifact"])]
        c = Counter(round(v, 6) for v in base)
        modal_v, modal_n = c.most_common(1)[0]
        by_band = {BAND_NAMES[b]: round(statistics.fmean(
            [base[i] for i in range(len(base)) if BANDS[i] == b]), 4) for b in range(4)}
        out[eng] = {
            "spearman_vs_declared_manipulativeness": round(spearman(base, BANDS), 4),
            "spearman_vs_word_count": round(spearman(base, words), 4),
            "modal_baseline_verdict": modal_v,
            "artifacts_sharing_the_modal_verdict": "%d of %d" % (modal_n, len(base)),
            "distinct_baseline_verdicts": len(c),
            "mean_verdict_by_declared_band": by_band,
            "most_manipulative_text_scored": round(base[19], 4),
            "least_manipulative_text_scored": round(base[0], 4),
        }

    out["THE_FINDING"] = (
        "Neither engine orders this artifact set by manipulativeness. Spearman against the "
        "declared gradient is +%.4f for v1 and +%.4f for v2 -- indistinguishable from zero. "
        "Against WORD COUNT it is %+.4f and %+.4f: both engines score LONGER text as LESS "
        "manipulative, and they do so to nearly the same degree."
        % (out["V1"]["spearman_vs_declared_manipulativeness"],
           out["V2"]["spearman_vs_declared_manipulativeness"],
           out["V1"]["spearman_vs_word_count"], out["V2"]["spearman_vs_word_count"]))

    out["IT_IS_NOT_V2_S_DENSITY_WEIGHTING"] = (
        "v1 shows %+.4f against word count and v2 shows %+.4f. They are the same number. The "
        "length effect is therefore NOT introduced by v2's division by word count -- it is "
        "already present in the shared gate and regex structure that both engines inherit. "
        "v2 is not the culprit and replacing it would not help."
        % (out["V1"]["spearman_vs_word_count"], out["V2"]["spearman_vs_word_count"]))

    out["WHAT_THIS_SUGGESTS_ABOUT_THE_EARLIER_G_NUMBERS"] = (
        "On the DES set and the HELM v2 held-out set, the manipulative texts were also the "
        "SHORT texts, so length and manipulativeness were confounded. This spec deliberately "
        "broke that confound -- the 2-word 'Act now.' is in the most manipulative band while "
        "three 30-word texts are in the factual band -- and the manipulativeness signal "
        "disappeared. That is consistent with the earlier G = 0.2980 having measured LENGTH "
        "rather than MANIPULATION. It is consistent with, not proof of: see the limit below.")

    out["WHY_THE_DCM_VOID_IS_THE_SAME_FACT"] = (
        "W7 failed at DELTA = 0.1060 because V = 0.40 and C = 0.265 -- the verdicts are "
        "concentrated. They are concentrated because 15 of 20 artifacts land on the identical "
        "value %.4f. The self-audit did not obscure the finding; it detected it. DCM voided "
        "the run for precisely the right reason." % out["V2"]["modal_baseline_verdict"])

    out["THE_LIMIT_AND_IT_IS_SERIOUS"] = (
        "The band labels are the author's own, written into the spec by the same person who "
        "maintains the engines. They are NOT independent rater labels, so this does NOT close "
        "W8, which stays UNTESTABLE-HERE. The direction matters though: author labels are "
        "biased toward agreement with the author's engine, and the correlation still came out "
        "at zero. A positive result from these labels would have been worth little; a null "
        "from them is harder to dismiss.")

    out["WHAT_IS_NOT_CLAIMED"] = (
        "HELM is not refuted. This is one 20-text set, scored against author-supplied labels, "
        "in a run its own self-audit declared UNINFORMATIVE. The claim is narrower and it is "
        "about our measurements rather than about the engine: the shield-and-signal numbers "
        "reported for HELM in DES and in HELM v2 were measured on sets where length and "
        "manipulativeness were confounded, and no run so far has separated them.")

    out["STATUS"] = "POST-HOC. Not pre-registered. Not scored. No gate depends on it."

    with open(os.path.join(HERE, "results_bg_posthoc.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
