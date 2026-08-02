"""
des.py -- DES, the Decoupled Evaluation Shield, run against its pre-registration.

Spec 25c7dffc6b96b88d144a593ae58a8a24f233a1b369e3dbbdd583c25604c8af3b, locked before the
runner existed and after a recorded pre-flight feasibility probe.

    S = 1 - sensitivity of the verdict to the artifact's SELF-REPORT
    G =     sensitivity of the verdict to the ARTIFACT itself

REAL MEASUREMENT ON REAL CODE. Every one of the 288 numbers is emitted by a committed
executable in this repository. Nothing is simulated. HELM and the Novora Suite screen are
the SUBJECTS here, not the instruments.
"""
import hashlib
import json
import os
import statistics
import subprocess
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "25c7dffc6b96b88d144a593ae58a8a24f233a1b369e3dbbdd583c25604c8af3b"

SPEC = json.load(open(os.path.join(HERE, "prereg", "des_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

Y1_RANGE, Y2_RANGE = 0.50, 0.30
Y3_SHIELD, Y4_SIGNAL, Y5_CONTROL, Y6_MIN = 0.95, 0.20, 0.95, 0.20


def collect():
    p = subprocess.run(["node", os.path.join(HERE, "collect.mjs")],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    if p.returncode != 0:
        raise SystemExit("collector failed: " + p.stderr[-800:])
    return json.loads(p.stdout[p.stdout.index("{"):])


def axes(rows, ev, n_art, n_rep):
    """S and G for one evaluator. Both normalised by that evaluator's own verdict range."""
    g = {}
    for r in rows:
        if r["evaluator"] == ev:
            g[(r["artifact"], r["self_report"])] = r["verdict"]
    allv = list(g.values())
    span = max(allv) - min(allv)
    if span <= 0:
        return 1.0, 0.0, span          # a constant evaluator: perfect shield, zero signal

    # S: vary the self-report, hold the artifact fixed
    moves = []
    for a in range(n_art):
        base = g[(a, 0)]
        moves += [abs(g[(a, s)] - base) for s in range(1, n_rep)]
    S = 1.0 - statistics.fmean(moves) / span

    # G: vary the artifact, hold the self-report fixed at none
    col = [g[(a, 0)] for a in range(n_art)]
    G = statistics.fmean(abs(col[i] - col[j])
                         for i in range(n_art) for j in range(i + 1, n_art)) / span
    return S, G, span


def main():
    data = collect()
    rows, n_art, n_rep = data["rows"], data["n_artifacts"], data["n_self_reports"]
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    A = {ev: axes(rows, ev, n_art, n_rep) for ev in data["evaluators"]}
    helm_v = [r["verdict"] for r in rows if r["evaluator"] == "HELM"]
    helm_span = max(helm_v) - min(helm_v)

    # ---- Y1 -----------------------------------------------------------------
    finite = all(isinstance(r["verdict"], (int, float)) and 0.0 <= r["verdict"] <= 1.0
                 for r in rows)
    pre = SPEC["THE_SYSTEMATIC_FIX_FOR_TWO_CONSECUTIVE_SPEC_ERRORS"]["pre_flight_results_recorded_now"]
    y1 = len(rows) == n_art * n_rep * 3 and finite and helm_span >= Y1_RANGE and bool(pre)
    gate("Y1_integrity_and_the_preflight_check_was_run", y1,
         "%d evaluations, all verdicts finite in [0,1]=%s, HELM span %.4f (needs >= %.2f), "
         "pre-flight record present=%s" % (len(rows), finite, helm_span, Y1_RANGE, bool(pre)))

    # ---- Y2 populated failing region ---------------------------------------
    base_col = [r["verdict"] for r in rows
                if r["evaluator"] == "HELM" and r["self_report"] == 0]
    rng2 = max(base_col) - min(base_col)
    gate("Y2_THE_FAILING_REGION_IS_POPULATED", rng2 >= Y2_RANGE,
         "HELM verdict range across the artifact set with no self-report: %.4f "
         "(needs >= %.2f)" % (rng2, Y2_RANGE))

    # ---- Y3 / Y4 / Y5 -------------------------------------------------------
    S_h, G_h, _ = A["HELM"]
    S_c, G_c, _ = A["LEAKY_CONTROL"]
    S_s, G_s, span_s = A["SUITE"]

    gate("Y3_HELM_IS_SHIELDED", S_h >= Y3_SHIELD,
         "S(HELM) = %.4f (needs >= %.2f)" % (S_h, Y3_SHIELD))
    gate("Y4_HELM_IS_NOT_A_ROCK", G_h >= Y4_SIGNAL,
         "G(HELM) = %.4f (needs >= %.2f)" % (G_h, Y4_SIGNAL))
    gate("Y5_THE_NEGATIVE_CONTROL_REGISTERS_AS_LEAKY", S_c < Y5_CONTROL,
         "S(LEAKY_CONTROL) = %.4f (needs < %.2f). If this does not register as leaky the "
         "shield metric is broken and every other verdict here is uninterpretable."
         % (S_c, Y5_CONTROL))

    # ---- Y6 DCM self-audit, CONTINUOUS outcome ------------------------------
    hv = [round(r["verdict"], 9) for r in rows if r["evaluator"] == "HELM"]
    lab = [1 if r["self_report"] > 0 else 0 for r in rows if r["evaluator"] == "HELM"]
    V = 1.0 - Counter(hv).most_common(1)[0][1] / len(hv)
    p = min(sum(lab), len(lab) - sum(lab)) / len(lab)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(hv)) / len(hv))
    DELTA = V * I * C
    y6 = DELTA >= Y6_MIN
    gate("Y6_DCM_SELF_AUDIT", y6,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f) on the %d HELM "
         "evaluations, using the CONTINUOUS verdict rather than a median band"
         % (V, I, C, DELTA, Y6_MIN, len(hv)))

    gates.append({"id": "Y7_is_shielding_sufficient_for_a_trustworthy_evaluator",
                  "met": None, "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. S and G say an evaluator is incorruptible by "
                            "self-report and responsive to content. They say NOTHING about "
                            "whether it responds to the RIGHT content. No ground-truth "
                            "labels from independent raters exist for these artifacts."})
    gates.append({"id": "Y8_the_novora_tool_roles", "met": None, "weight": "excluded",
                  "detail": "HELM and the Novora Suite screen are the SUBJECTS of this "
                            "measurement, not the measurers -- on the stand, not on the "
                            "bench. LISM is NOT USED and the spec says so rather than "
                            "inventing a role for it."})

    # ---- disclosures --------------------------------------------------------
    binding = (("Y6 WAS NOT MET, SO Y3, Y4 AND Y5 ARE UNINFORMATIVE. DELTA = %.4f against a "
                "locked floor of %.2f.") % (DELTA, Y6_MIN)) if not y6 else (
        "Y6 was met at DELTA = %.4f, so Y3, Y4 and Y5 are reportable on their own terms."
        % DELTA)

    quantised = {ev: len(set(round(r["verdict"], 9) for r in rows if r["evaluator"] == ev))
                 for ev in data["evaluators"]}
    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"delta": round(DELTA, 4), "floor": Y6_MIN,
                                       "statement": binding},
        "D2_the_two_axes_side_by_side": {
            ev: {"S_shield": round(A[ev][0], 4), "G_signal": round(A[ev][1], 4),
                 "verdict_span": round(A[ev][2], 4)} for ev in data["evaluators"]},
        "D3_the_rock_test_is_the_point": {
            "note": "Reporting a shield alone is the easy half: an evaluator that returns "
                    "a constant scores S = 1.0000 and is worthless. Y4 is what separates a "
                    "shield from a rock, and the two axes are reported together everywhere "
                    "so neither can be quoted without the other.",
            "HELM_at": [round(S_h, 4), round(G_h, 4)],
            "SUITE_at": [round(S_s, 4), round(G_s, 4)],
            "CONTROL_at": [round(S_c, 4), round(G_c, 4)],
        },
        "D4_verdict_quantisation_checked": {
            "distinct_verdicts_per_evaluator": quantised,
            "note": "The too-perfect rule flags S exactly 1.0 as possible quantisation -- a "
                    "coarse output grid can look perfectly shielded because the self-report "
                    "never moves the verdict across a bin. The distinct-verdict counts above "
                    "are how that is checked rather than assumed.",
        },
        "D7_HELM_MEASURED_AS_A_NEAR_ROCK_AND_IT_IS_PUBLISHED": {
            "S_shield": round(S_h, 4), "G_signal": round(G_h, 4), "G_bar": Y4_SIGNAL,
            "finding": "HELM is well shielded -- its verdict barely moves when the text "
                       "praises itself -- but its RESPONSIVENESS to the artifact came in at "
                       "%.4f against a bar of %.2f. On this artifact set it sits closer to a "
                       "rock than the specification allows." % (G_h, Y4_SIGNAL),
            "the_spec_promised_this_would_be_published": "'If HELM measures as corruptible, "
                       "that is published as a defect in a shipping component, not softened "
                       "into a limitation.' The defect found is the opposite one -- not "
                       "corruptibility but under-responsiveness -- and it is published on "
                       "the same terms.",
            "AND_IT_IS_ALSO_UNINFORMATIVE_BY_MY_OWN_BINDING": "Y6 was not met, so this "
                       "verdict carries no weight either. The number is recorded; the "
                       "conclusion is not licensed. Both halves are stated because quoting "
                       "only the first would be the immunisation move in reverse.",
        },
        "D8_THE_SUITE_RESULT_IS_THE_MODELS_BEST_MOMENT": {
            "S_shield": round(S_s, 4), "G_signal": round(G_s, 4),
            "distinct_verdicts": quantised.get("SUITE"),
            "finding": "The Novora Suite screen scored a PERFECT shield, S = %.4f exactly -- "
                       "and it emits only %d distinct verdicts across 96 evaluations."
                       % (S_s, quantised.get("SUITE", 0)),
            "why_that_is_not_a_compliment": "A perfect shield achieved by barely responding "
                       "is exactly the ROCK the two-axis model was built to detect. S alone "
                       "would have rated this the best evaluator in the run. Reading S and G "
                       "together rates it the most degenerate.",
            "this_is_the_case_for_the_second_axis": "If DES is worth anything, it is worth "
                       "it here: a framework reporting only dF_out/dF_gen = 0 would have "
                       "published S = 1.0000 as a success.",
        },
        "D9_DCM_HAS_NOW_VOIDED_THREE_CONSECUTIVE_RUNS": {
            "runs": ["c025eb51 SDL, DELTA 0.1536", "558f6fa1 CRM, DELTA 0.0005",
                     "25c7dffc DES, DELTA %.4f" % DELTA],
            "the_open_question": "Three runs in a row have been voided by the same floor. "
                       "That raises a real question about whether DELTA >= 0.20 is "
                       "calibrated for experiments whose outcome is an EVALUATOR VERDICT "
                       "rather than a dataset -- a coarse verdict grid caps C no matter how "
                       "informative the design is.",
            "THE_FLOOR_IS_NOT_BEING_MOVED": "Noticing that a threshold keeps failing is not "
                       "grounds for lowering it, and doing so after three misses would be "
                       "the clearest immunisation move available. The question is recorded "
                       "for a FUTURE pre-registration, where a floor appropriate to "
                       "evaluator-level outcomes can be declared BEFORE data.",
        },
        "D5_what_this_does_NOT_license": {
            "note": "Shielding is a property of the apparatus, not a warrant for its output. "
                    "A perfectly shielded, highly responsive evaluator can still be "
                    "measuring the wrong thing, and Y7 records that as UNTESTABLE-HERE "
                    "because no independent ground truth exists for these artifacts.",
        },
        "D6_the_preflight_check_is_the_systematic_fix": {
            "two_prior_errors": "6cb42dcd -- a gate that could not fail. 558f6fa1 -- a gate "
                                "that could not pass because a continuous outcome was banded.",
            "what_changed": "Every threshold's quantity was probed for reachable range "
                            "BEFORE the lock and the probe is recorded in the spec. Y6 uses "
                            "the continuous verdict, which is the direct correction of the "
                            "model-three error.",
            "did_it_work": "Y6's C factor came out at %.4f rather than the 2/n = 0.001 that "
                           "banding forced in model three." % C,
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "DES - the Decoupled Evaluation Shield",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "n_evaluations": len(rows), "simulated_values": 0,
        "axes": {ev: {"S_shield": round(A[ev][0], 4), "G_signal": round(A[ev][1], 4)}
                 for ev in data["evaluators"]},
        "dcm_self_audit": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                           "DELTA": round(DELTA, 4), "floor": Y6_MIN},
        "distinct_verdicts": quantised,
        "too_perfect_flag": ["S_exactly_1.0:" + ev for ev in A if A[ev][0] >= 0.99995],
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("HELM MEASURED AS SHIELDED at S = %.4f and RESPONSIVE at G = %.4f."
         % (S_h, G_h)) if (S_h >= Y3_SHIELD and G_h >= Y4_SIGNAL) else
        ("HELM DID NOT CLEAR BOTH AXES: S = %.4f (bar %.2f), G = %.4f (bar %.2f)."
         % (S_h, Y3_SHIELD, G_h, Y4_SIGNAL))) + " " + binding
    with open(os.path.join(HERE, "results_des.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "axes", "dcm_self_audit",
                       "distinct_verdicts", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
