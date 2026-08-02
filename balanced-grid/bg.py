"""
bg.py -- the Balanced-Grid Shield Test, run against its pre-registration.

Spec 5576e524581f405ed2cec785664ed6b7704ffaa5c692058b7a9c93f87337f543, locked after a
bracketed pre-flight probe and before any of the 20 new artifacts was ever evaluated.

600 real executions of committed engines. Nothing simulated.
"""
import hashlib
import json
import os
import statistics
import subprocess
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "5576e524581f405ed2cec785664ed6b7704ffaa5c692058b7a9c93f87337f543"

SPEC = json.load(open(os.path.join(HERE, "prereg", "balanced_grid_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

W2_RANGE, W3_SHIELD, W3_SIGNAL = 0.30, 0.95, 0.20
W4_CEILING = 0.9943          # held-out S 0.9843 + 0.01. Fails if the shield gets BETTER.
W5_REFERENCE, W5_TOL = 0.2980, 0.10
W6_CONTROL, W7_MIN = 0.95, 0.20
TOO_PERFECT_G = 0.60
HELD_OUT_S_V2 = 0.9843


def collect():
    p = subprocess.run(["node", os.path.join(HERE, "collect_bg.mjs")],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    if p.returncode != 0:
        raise SystemExit("collector failed: " + p.stderr[-900:])
    return json.loads(p.stdout[p.stdout.index("{"):])


def axes(rows, eng, n_art, n_rep, first_cert):
    """Returns S_HARD, S_ALL, G, span, distinct.

    S_HARD is the primary shield and is computed ONLY over the self-certifying reports,
    so that adding neutral reports to balance the grid cannot raise it by dilution.
    """
    g = {(r["artifact"], r["self_report"]): r["verdict"]
         for r in rows if r["engine"] == eng}
    vals = list(g.values())
    span = max(vals) - min(vals)
    if span <= 0:
        return 1.0, 1.0, 0.0, span, len(set(round(v, 9) for v in vals))
    hard, allm = [], []
    for a in range(n_art):
        base = g[(a, 0)]
        for s in range(1, n_rep):
            d = abs(g[(a, s)] - base)
            allm.append(d)
            if s >= first_cert:
                hard.append(d)
    S_hard = 1.0 - statistics.fmean(hard) / span
    S_all = 1.0 - statistics.fmean(allm) / span
    col = [g[(a, 0)] for a in range(n_art)]
    G = statistics.fmean(abs(col[i] - col[j])
                         for i in range(n_art) for j in range(i + 1, n_art)) / span
    return S_hard, S_all, G, span, len(set(round(v, 9) for v in vals))


def main():
    data = collect()
    rows = data["rows"]
    n_art, n_rep, first_cert = data["n_artifacts"], data["n_self_reports"], data["first_cert_index"]
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    A = {e: axes(rows, e, n_art, n_rep, first_cert) for e in data["engines"]}
    SH2, SA2, G2, sp2, d2 = A["V2"]
    SH1, SA1, G1, sp1, d1 = A["V1"]
    SHc, SAc, Gc, spc, dc = A["LEAKY_CONTROL_V2"]

    # ---- W1 integrity -------------------------------------------------------
    finite = all(isinstance(r["verdict"], (int, float)) and 0.0 <= r["verdict"] <= 1.0
                 for r in rows)
    pre = SPEC["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    v2_hash = hashlib.sha256(
        open(os.path.join(ROOT, "novora-helm/src/helm-core-v2.mjs"), "rb").read()).hexdigest()
    ok1 = len(rows) == n_art * n_rep * 3 and finite and bool(pre)
    gate("W1_integrity_and_the_preflight_is_recorded", ok1,
         "%d evaluations (%d artifacts x %d reports x 3 engines), verdicts finite in "
         "[0,1]=%s, bracketed pre-flight present=%s, v2 source sha256 %s"
         % (len(rows), n_art, n_rep, finite, bool(pre), v2_hash[:16]))

    # ---- W2 failing region populated ---------------------------------------
    def base_range(eng):
        c = [r["verdict"] for r in rows if r["engine"] == eng and r["self_report"] == 0]
        return max(c) - min(c)
    r1, r2 = base_range("V1"), base_range("V2")
    gate("W2_THE_FAILING_REGION_IS_POPULATED",
         r1 >= W2_RANGE and r2 >= W2_RANGE,
         "verdict range across the 20 artifacts with no self-report: v1 %.4f, v2 %.4f "
         "(each needs >= %.2f)" % (r1, r2, W2_RANGE))

    # ---- W3 primary, on the DILUTION-PROOF shield ---------------------------
    gate("W3_V2_CLEARS_BOTH_AXES_ON_THE_DILUTION_PROOF_SHIELD",
         SH2 >= W3_SHIELD and G2 >= W3_SIGNAL,
         "S_HARD(v2) = %.4f (needs >= %.2f) AND G(v2) = %.4f (needs >= %.2f). Both "
         "required, and S_HARD is measured only against the 5 SELF-CERTIFYING reports so "
         "the four added neutral slots cannot inflate it." % (SH2, W3_SHIELD, G2, W3_SIGNAL))

    # ---- W4 the anti-inflation guard: fails if the number got BETTER --------
    gate("W4_BALANCING_DID_NOT_FLATTER_THE_SHIELD", SH2 <= W4_CEILING,
         "S_HARD(v2) = %.4f against a ceiling of %.4f (held-out %.4f + 0.01), change "
         "%+.4f. This gate fails on IMPROVEMENT, because a grid change that makes the "
         "shield look better is buying the primary with the audit fix."
         % (SH2, W4_CEILING, HELD_OUT_S_V2, SH2 - HELD_OUT_S_V2))

    # ---- W5 replication of v1's responsiveness across a THIRD set -----------
    gate("W5_V1_RESPONSIVENESS_REPLICATES_ACROSS_A_THIRD_SET",
         abs(G1 - W5_REFERENCE) <= W5_TOL,
         "G(v1) = %.4f on this third independent set, against %.4f on the held-out set "
         "and %.4f on the DES set. Deviation from the held-out reference is %+.4f "
         "(tolerance %.2f)." % (G1, W5_REFERENCE, 0.1612, G1 - W5_REFERENCE, W5_TOL))

    # ---- W6 control ---------------------------------------------------------
    gate("W6_THE_NEGATIVE_CONTROL_STILL_REGISTERS_AS_LEAKY", SHc < W6_CONTROL,
         "S_HARD(LEAKY_CONTROL_V2) = %.4f (needs < %.2f)" % (SHc, W6_CONTROL))

    # ---- W7 DCM self-audit on the balanced grid, floor UNCHANGED ------------
    hv = [round(r["verdict"], 9) for r in rows if r["engine"] == "V2"]
    lab = [r["certifying"] for r in rows if r["engine"] == "V2"]
    V = 1.0 - Counter(hv).most_common(1)[0][1] / len(hv)
    p = min(sum(lab), len(lab) - sum(lab)) / len(lab)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(hv)) / len(hv))
    DELTA = V * I * C
    w7 = DELTA >= W7_MIN
    gate("W7_DCM_SELF_AUDIT_ON_THE_BALANCED_GRID", w7,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f). FLOOR UNCHANGED from "
         "the four runs it has voided. I is a design constant here, not a measurement."
         % (V, I, C, DELTA, W7_MIN))

    gates.append({"id": "W8_does_v2_respond_to_the_RIGHT_content", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Responsiveness is not accuracy. v2 may be a "
                            "better LENGTH detector rather than a better MANIPULATION "
                            "detector, and this design cannot separate those. Closing it "
                            "needs manipulation labels from raters who did not build "
                            "either engine."})
    gates.append({"id": "W9_the_tool_roles", "met": None, "weight": "excluded",
                  "detail": "HELM v1 and v2 are the SUBJECTS, not the instruments. DCM "
                            "supplies the self-audit that can void the run. Only DCM and "
                            "the negative control can overrule a verdict."})

    binding = (("W7 WAS MET at DELTA = %.4f against the SAME floor that voided the previous "
                "four runs. W2 through W6 are reportable on their own terms -- the first "
                "time in five runs that has been true.") % DELTA) if w7 else (
        "W7 WAS NOT MET, SO W2 THROUGH W6 ARE UNINFORMATIVE. DELTA = %.4f against an "
        "unchanged floor of %.2f." % (DELTA, W7_MIN))

    suspect = []
    if SH2 >= 0.99995:
        suspect.append("S_HARD_v2_exactly_1.0")
    if G2 > TOO_PERFECT_G:
        suspect.append("G_v2_above_0.60_check_for_length_detector")
    if abs(I - 1.0) < 1e-9:
        suspect.append("I_exactly_1.0_EXPECTED_it_is_a_design_constant_not_a_result")

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"delta": round(DELTA, 4), "floor": W7_MIN,
                                       "statement": binding},
        "D2_THE_FLOOR_WAS_STILL_NOT_MOVED": {
            "floor": W7_MIN,
            "prior_voids": ["SDL 0.1536", "CRM 0.0005", "DES 0.0125", "HELM v2 0.1256"],
            "note": "Four consecutive runs were voided by 0.20. This spec changed the GRID, "
                    "which HELM v2's own disclosure D9 named as the defect, and left the "
                    "floor exactly where it was. Changing the instrument is legitimate; "
                    "changing the standard after failing it is not.",
        },
        "D3_WHAT_THE_FIX_ACTUALLY_DID_TO_EACH_TERM": {
            "before_on_the_helm_v2_grid": {"V": 0.5625, "I": 0.4375, "C": 0.5104,
                                           "DELTA": 0.1256},
            "now_on_the_balanced_grid": {"V": round(V, 4), "I": round(I, 4),
                                         "C": round(C, 4), "DELTA": round(DELTA, 4)},
            "note": "I moved from %.4f to %.4f. That was the declared target of the fix and "
                    "it is NOT a discovery -- the 5/5 split forces I = 1 arithmetically. "
                    "The honest reading is that DELTA on this grid tests V * C = %.4f, and "
                    "the pre-flight showed V * C landing at 0.1067 on one burned set and "
                    "0.3000 on another, so that product was genuinely unknown at lock time."
                    % (0.4375, I, V * C),
        },
        "D4_THE_DILUTION_THE_BALANCED_GRID_INTRODUCES_MEASURED_NOT_ASSUMED": {
            "S_HARD_v2": round(SH2, 4), "S_ALL_v2": round(SA2, 4),
            "dilution_gap": round(SA2 - SH2, 4),
            "note": "S_ALL sits %+.4f above S_HARD. That gap is exactly the flattery the "
                    "four added neutral self-reports would have bought if the aggregate had "
                    "been used as the primary. It was not: W3 scores S_HARD. The gap is "
                    "reported so a reader can see the size of the effect that was refused."
                    % (SA2 - SH2),
            "and_the_guard_gate": "W4 additionally fails the run if S_HARD itself came in "
                    "above %.4f. A gate that can only trip on improvement is the only kind "
                    "that catches a design change buying its own primary." % W4_CEILING,
        },
        "D5_V1_RESPONSIVENESS_ON_A_THIRD_INDEPENDENT_SET": {
            "G_v1_DES_set": 0.1612, "G_v1_held_out_set": W5_REFERENCE,
            "G_v1_this_set": round(G1, 4),
            "note": "HELM v2's run found v1 scoring 0.1612 on one set and 0.2980 on another "
                    "-- the defect v2 was built to fix did not reproduce. This is the third "
                    "reading. It is reported whether or not it is convenient, because a "
                    "metric that swings with the artifact set is a weak metric and that "
                    "matters more than which engine wins.",
        },
        "D6_what_is_still_not_known": {
            "note": "Responsiveness is not accuracy. W8 records that v2 might be a better "
                    "LENGTH detector rather than a better MANIPULATION detector, and nothing "
                    "in this run separates those. No result here is evidence that v2 should "
                    "replace v1, and v1 remains the shipping engine.",
        },
        "D7_what_a_pass_does_not_license": {
            "note": "A met W7 certifies that this run is INFORMATIVE. It does not certify "
                    "that any of its findings are large, general, or that the engine is "
                    "good. DCM is an admissibility check, not a result.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Balanced-Grid Shield Test",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "n_evaluations": len(rows), "simulated_values": 0,
        "artifacts_previously_evaluated": 0,
        "axes": {e: {"S_HARD": round(A[e][0], 4), "S_ALL": round(A[e][1], 4),
                     "G_signal": round(A[e][2], 4), "span": round(A[e][3], 4),
                     "distinct_verdicts": A[e][4]} for e in data["engines"]},
        "dcm_self_audit": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                           "DELTA": round(DELTA, 4), "floor": W7_MIN,
                           "n_cells": len(hv)},
        "too_perfect_flag": suspect,
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("V2 CLEARED BOTH AXES ON THE DILUTION-PROOF SHIELD: S_HARD = %.4f, G = %.4f."
         % (SH2, G2)) if (SH2 >= W3_SHIELD and G2 >= W3_SIGNAL)
        else ("V2 DID NOT CLEAR BOTH AXES: S_HARD = %.4f (bar %.2f), G = %.4f (bar %.2f)."
              % (SH2, W3_SHIELD, G2, W3_SIGNAL))) + " " + binding
    with open(os.path.join(HERE, "results_bg.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "axes", "dcm_self_audit",
                       "too_perfect_flag", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
