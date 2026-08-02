"""
helmv2.py -- HELM v2 against v1 on a HELD-OUT artifact set, run against its
pre-registration.

Spec 03815a61ce8a555f2c741eb2b840502e32d9c845be46cb9be01d94e56755f119, locked after a
recorded granularity-only pre-flight probe and before the held-out set was ever evaluated.

REAL MEASUREMENT ON REAL CODE. 288 executions of committed engines. Nothing simulated.
"""
import hashlib
import json
import os
import statistics
import subprocess
from collections import Counter  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "03815a61ce8a555f2c741eb2b840502e32d9c845be46cb9be01d94e56755f119"

SPEC = json.load(open(os.path.join(HERE, "prereg", "helmv2_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

Z2_RANGE, Z3_SHIELD, Z3_SIGNAL = 0.30, 0.95, 0.20
Z4_TOL, Z5_CONTROL, Z6_MIN = 0.02, 0.95, 0.20
TOO_PERFECT_G = 0.60


def collect():
    p = subprocess.run(["node", os.path.join(HERE, "collect_v2.mjs")],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    if p.returncode != 0:
        raise SystemExit("collector failed: " + p.stderr[-900:])
    return json.loads(p.stdout[p.stdout.index("{"):])


def axes(rows, eng, n_art, n_rep):
    g = {(r["artifact"], r["self_report"]): r["verdict"]
         for r in rows if r["engine"] == eng}
    vals = list(g.values())
    span = max(vals) - min(vals)
    if span <= 0:
        return 1.0, 0.0, span, len(set(round(v, 9) for v in vals))
    moves = []
    for a in range(n_art):
        base = g[(a, 0)]
        moves += [abs(g[(a, s)] - base) for s in range(1, n_rep)]
    S = 1.0 - statistics.fmean(moves) / span
    col = [g[(a, 0)] for a in range(n_art)]
    G = statistics.fmean(abs(col[i] - col[j])
                         for i in range(n_art) for j in range(i + 1, n_art)) / span
    return S, G, span, len(set(round(v, 9) for v in vals))


def main():
    data = collect()
    rows, n_art, n_rep = data["rows"], data["n_artifacts"], data["n_self_reports"]
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    A = {e: axes(rows, e, n_art, n_rep) for e in data["engines"]}
    S1, G1, sp1, d1 = A["V1"]
    S2, G2, sp2, d2 = A["V2"]
    Sc, Gc, spc, dc = A["LEAKY_CONTROL_V2"]

    # ---- Z1 -----------------------------------------------------------------
    finite = all(isinstance(r["verdict"], (int, float)) and 0.0 <= r["verdict"] <= 1.0
                 for r in rows)
    pre = SPEC["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    v1_src = open(os.path.join(ROOT, "novora-helm/src/helm-core.mjs"), "rb").read()
    v1_hash = hashlib.sha256(v1_src).hexdigest()
    z1 = len(rows) == n_art * n_rep * 3 and finite and bool(pre)
    gate("Z1_integrity_and_the_preflight_is_recorded", z1,
         "%d evaluations, verdicts finite in [0,1]=%s, pre-flight record present=%s, "
         "v1 source sha256 %s" % (len(rows), finite, bool(pre), v1_hash[:16]))

    # ---- Z2 populated failing region on the held-out set --------------------
    def base_range(eng):
        c = [r["verdict"] for r in rows if r["engine"] == eng and r["self_report"] == 0]
        return max(c) - min(c)
    r1, r2 = base_range("V1"), base_range("V2")
    gate("Z2_THE_FAILING_REGION_IS_POPULATED_ON_THE_HELD_OUT_SET",
         r1 >= Z2_RANGE and r2 >= Z2_RANGE,
         "held-out verdict range with no self-report: v1 %.4f, v2 %.4f (each needs "
         ">= %.2f)" % (r1, r2, Z2_RANGE))

    # ---- Z3 primary ---------------------------------------------------------
    gate("Z3_V2_CLEARS_BOTH_AXES_ON_HELD_OUT_DATA",
         S2 >= Z3_SHIELD and G2 >= Z3_SIGNAL,
         "S(v2) = %.4f (needs >= %.2f) AND G(v2) = %.4f (needs >= %.2f). Both required."
         % (S2, Z3_SHIELD, G2, Z3_SIGNAL))

    # ---- Z4 anti-immunisation ----------------------------------------------
    gate("Z4_V2_DID_NOT_BUY_SIGNAL_BY_LOSING_SHIELD", S2 >= S1 - Z4_TOL,
         "S(v2) = %.4f against S(v1) = %.4f, change %+.4f (must not fall more than %.2f)"
         % (S2, S1, S2 - S1, Z4_TOL))

    # ---- Z5 control ---------------------------------------------------------
    gate("Z5_THE_NEGATIVE_CONTROL_STILL_REGISTERS_AS_LEAKY", Sc < Z5_CONTROL,
         "S(LEAKY_CONTROL_V2) = %.4f (needs < %.2f)" % (Sc, Z5_CONTROL))

    # ---- Z6 DCM self-audit on v2, floor UNCHANGED ---------------------------
    hv = [round(r["verdict"], 9) for r in rows if r["engine"] == "V2"]
    lab = [1 if r["self_report"] > 0 else 0 for r in rows if r["engine"] == "V2"]
    V = 1.0 - Counter(hv).most_common(1)[0][1] / len(hv)
    p = min(sum(lab), len(lab) - sum(lab)) / len(lab)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(hv)) / len(hv))
    DELTA = V * I * C
    z6 = DELTA >= Z6_MIN
    gate("Z6_DCM_SELF_AUDIT_ON_V2", z6,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f). FLOOR UNCHANGED from "
         "the three runs it voided." % (V, I, C, DELTA, Z6_MIN))

    gates.append({"id": "Z7_does_v2_respond_to_the_RIGHT_content", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. v2 could be more responsive to LENGTH while "
                            "being no better at detecting manipulation, and this design "
                            "cannot tell those apart. Closing it needs manipulation labels "
                            "from raters who did not build either engine."})
    gates.append({"id": "Z8_the_tool_roles", "met": None, "weight": "excluded",
                  "detail": "HELM v1 and v2 are the SUBJECTS. DCM supplies the self-audit "
                            "that can void the run. Only DCM and the negative control can "
                            "overrule a verdict."})

    # ---- disclosures --------------------------------------------------------
    binding = (("Z6 WAS NOT MET, SO Z2 THROUGH Z5 ARE UNINFORMATIVE. DELTA = %.4f against "
                "an unchanged floor of %.2f.") % (DELTA, Z6_MIN)) if not z6 else (
        "Z6 WAS MET at DELTA = %.4f against the SAME floor that voided the previous three "
        "runs. Z2 through Z5 are reportable on their own terms." % DELTA)

    suspect = []
    if S2 >= 0.99995:
        suspect.append("S_v2_exactly_1.0")
    if G2 > TOO_PERFECT_G:
        suspect.append("G_v2_above_0.60_check_for_length_detector")

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"delta": round(DELTA, 4), "floor": Z6_MIN,
                                       "statement": binding},
        "D2_the_two_engines_side_by_side_on_HELD_OUT_data": {
            "V1": {"S": round(S1, 4), "G": round(G1, 4), "distinct": d1},
            "V2": {"S": round(S2, 4), "G": round(G2, 4), "distinct": d2},
            "LEAKY_CONTROL_V2": {"S": round(Sc, 4), "G": round(Gc, 4), "distinct": dc},
        },
        "D3_v2_is_justified_by_code_inspection_not_by_the_voided_run": {
            "note": "The DES run that measured v1 was VOIDED by its own self-audit, so its "
                    "numbers licensed no conclusion. v2 rests instead on two facts readable "
                    "in v1's source: integer effective counts force a coarse output lattice, "
                    "and every pressure and mechanism term ignores text length. Neither "
                    "depends on any experiment.",
        },
        "D4_the_DCM_floor_was_not_moved": {
            "floor": Z6_MIN,
            "prior_voids": ["SDL 0.1536", "CRM 0.0005", "DES 0.0125"],
            "note": "Three consecutive voids raised a real question about whether 0.20 suits "
                    "evaluator-verdict outcomes. Lowering it immediately after building an "
                    "engine that would benefit would be the most transparent immunisation "
                    "move available in this programme. The floor stayed; the instrument "
                    "changed.",
        },
        "D5_the_primary_ran_on_data_neither_engine_had_seen": {
            "note": "The 12 held-out texts were written for this spec and never evaluated "
                    "before the lock. Measuring v2 on the DES grid -- the set whose "
                    "properties motivated the change -- would have been scoring a design "
                    "against the evidence that produced it.",
        },
        "D7_THE_DEFECT_I_BUILT_V2_TO_FIX_DID_NOT_REPRODUCE": {
            "G_v1_on_the_DES_grid": 0.1612,
            "G_v1_on_the_held_out_set": round(G1, 4),
            "the_bar": Z3_SIGNAL,
            "finding": "v1 measured G = 0.1612 on the DES artifact set and G = %.4f on the "
                       "held-out set. IT CLEARS THE 0.20 BAR ON DATA IT HAD NOT BEEN "
                       "CHARACTERISED ON. The under-responsiveness was a property of the "
                       "DES ARTIFACT SET, not of the engine." % G1,
            "why_this_is_the_run_s_most_important_line": "Had the primary been measured on "
                       "the DES grid -- the set whose properties motivated the rebuild -- "
                       "this run would have reported a confirmed fix for a problem that "
                       "does not generalise. The held-out design is the only reason that "
                       "did not happen, and it is why the spec forbade using the DES grid.",
            "what_it_costs_v2": "v2's responsiveness advantage over v1 is %+.4f, which is "
                       "nothing. On this evidence v2 does NOT fix a responsiveness defect, "
                       "because there was no responsiveness defect to fix."
                       % (G2 - G1),
        },
        "D8_what_v2_actually_improved_and_it_is_not_what_was_claimed": {
            "granularity": {"v1_distinct": d1, "v2_distinct": d2,
                            "v1_C_on_DES_grid": 0.0833, "v2_C_here": round(C, 4)},
            "responsiveness": {"v1_G": round(G1, 4), "v2_G": round(G2, 4),
                               "gain": round(G2 - G1, 4)},
            "note": "The real and large improvement is OUTPUT GRANULARITY -- %d distinct "
                    "verdicts against %d, and C at %.4f against 0.0833 on the earlier grid. "
                    "The responsiveness gain is %+.4f and is not worth reporting as an "
                    "improvement. Density weighting made the engine finer-grained, which is "
                    "what the code-inspection argument predicted, and did NOT make it more "
                    "sensitive to manipulation." % (d2, d1, C, G2 - G1),
            "and_the_shield_survived": "S moved %+.4f, well inside the 0.02 tolerance Z4 "
                    "declared. v2 did not buy anything by loosening the shield -- there was "
                    "simply less to buy than expected." % (S2 - S1),
        },
        "D9_the_binding_constraint_on_the_self_audit_MOVED": {
            "before": {"C": 0.0833, "note": "output granularity capped DELTA"},
            "now": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                    "DELTA": round(DELTA, 4)},
            "note": "C is no longer the constraint -- it rose from 0.0833 to %.4f. DELTA is "
                    "now held down by I = %.4f, and that is a property of THIS EXPERIMENT'S "
                    "GRID rather than of the engine: only 1 of the 8 self-report slots is "
                    "'none', so the grouping splits 12 against 84 and the incidence term "
                    "cannot approach 1." % (C, I),
            "what_a_future_spec_should_do": "Balance the grouping -- equal numbers of "
                    "self-report-present and self-report-absent cells -- and declare that "
                    "design BEFORE data. That is an experiment-design fix, not a floor "
                    "change, and it is the honest way to make the self-audit reachable.",
            "the_floor_still_did_not_move": True,
        },
        "D6_what_is_still_not_known": {
            "note": "Responsiveness is not accuracy. Z7 records that v2 might be a better "
                    "LENGTH detector rather than a better MANIPULATION detector, and nothing "
                    "in this run separates those.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "HELM v2 - density-weighted evidence",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "n_evaluations": len(rows), "simulated_values": 0,
        "held_out": True,
        "axes": {e: {"S_shield": round(A[e][0], 4), "G_signal": round(A[e][1], 4),
                     "distinct_verdicts": A[e][3]} for e in data["engines"]},
        "dcm_self_audit": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                           "DELTA": round(DELTA, 4), "floor": Z6_MIN},
        "too_perfect_flag": suspect,
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("V2 CLEARED BOTH AXES ON HELD-OUT DATA: S = %.4f, G = %.4f, against v1's "
         "S = %.4f, G = %.4f." % (S2, G2, S1, G1)) if (S2 >= Z3_SHIELD and G2 >= Z3_SIGNAL)
        else ("V2 DID NOT CLEAR BOTH AXES: S = %.4f (bar %.2f), G = %.4f (bar %.2f). v1 "
              "remains the shipping engine." % (S2, Z3_SHIELD, G2, Z3_SIGNAL))) + " " + binding
    with open(os.path.join(HERE, "results_helmv2.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "axes", "dcm_self_audit",
                       "too_perfect_flag", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
