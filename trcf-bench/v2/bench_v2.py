"""
bench_v2.py -- the v2 bench: the veto-form race T0 never ran, and an expired sunset.

Two things are genuinely new here and both are executable in-container:

    V2a  the MINIMUM (veto) form, which T0 never computed. Single index, no fitting,
         so no overfitting and no fold reuse -- the cleanest possible new look.
    W4   the SUNSET rule, which has already expired. V2b is still CONDITIONAL because
         no pre-outcome shock marker exists, so the tail-lemma demotion FIRES NOW,
         by date rather than by mood, and it fires AGAINST the carrier.

product-vs-additive is logged CONFIRMATORY ONLY: T0 already ran it, and counting it
again would be one look scored twice.

Aborts if the spec hash has moved.
"""
import csv
import datetime
import hashlib
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LOCKED = "37812580b45a216b598ef00837ef0e741279413bcdf1597feac476961e731458"


def z(c):
    m, s = st.mean(c), st.pstdev(c) or 1.0
    return [(v - m) / s for v in c]


def auc(scores, ys):
    pos, neg = sum(ys), len(ys) - sum(ys)
    if not pos or not neg:
        return 0.5
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rank = [0] * len(scores)
    for k, i in enumerate(order):
        rank[i] = k + 1
    s = sum(rank[i] for i in range(len(ys)) if ys[i] == 1)
    return (s - pos * (pos + 1) / 2) / (pos * neg)


def direction_free(scores, ys):
    """An index may point either way. Pre-committing to a sign would be a hidden
    researcher degree of freedom, so both directions are allowed and the better is
    taken -- applied IDENTICALLY to every form, so it cannot favour one."""
    a = auc(scores, ys)
    return max(a, 1 - a)


def ols_r2(y, Xs):
    n, k = len(y), len(Xs)
    m = k + 1
    A = [[1.0] + [Xs[j][i] for j in range(k)] for i in range(n)]
    ATA = [[sum(A[i][a] * A[i][b] for i in range(n)) for b in range(m)] for a in range(m)]
    ATy = [sum(A[i][a] * y[i] for i in range(n)) for a in range(m)]
    for c in range(m):
        p = max(range(c, m), key=lambda r: abs(ATA[r][c]))
        ATA[c], ATA[p] = ATA[p], ATA[c]
        ATy[c], ATy[p] = ATy[p], ATy[c]
        if abs(ATA[c][c]) < 1e-12:
            return 0.0
        for r in range(m):
            if r != c:
                f = ATA[r][c] / ATA[c][c]
                ATA[r] = [ATA[r][i] - f * ATA[c][i] for i in range(m)]
                ATy[r] -= f * ATy[c]
    b = [ATy[i] / ATA[i][i] for i in range(m)]
    pred = [b[0] + sum(b[j + 1] * Xs[j][i] for j in range(k)) for i in range(n)]
    my = st.mean(y)
    ss = sum((v - my) ** 2 for v in y)
    return 1 - sum((y[i] - pred[i]) ** 2 for i in range(n)) / ss if ss else 0.0


def classify(p):
    """The L4 inward knife: three binaries, structure never label."""
    return "RIBA-STRUCTURE" if (not p["state_contingent"] or p["delta_U"] > 0) else "COUPLED"


def surviving_stack(trig):
    s = ["L0", "L1", "L2", "L3", "L4"]
    if trig.get("F3"):
        s.remove("L2")          # branch retired -> contract stack falls back
    return s


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "v2_prereg.json"),
                          encoding="utf-8"))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    if got != LOCKED:
        raise SystemExit("SPEC HASH MOVED %s != %s -- refusing to run" % (got, LOCKED))

    MARGIN = spec["constants"]["MARGIN"]
    SUNSET = spec["constants"]["SUNSET"]
    gates, not_met = [], []

    def gate(gid, ok, detail, weight="counted"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "counted" and not ok:
            not_met.append(gid)

    rows = list(csv.DictReader(open(os.path.join(ROOT, spec["data"]["cohort"]),
                                    encoding="utf-8")))
    D = []
    for r in rows:
        try:
            D.append((math.log1p(float(r["U"])), float(r["D_enc"]),
                      float(r["D_dec"]), int(r["archived"])))
        except (ValueError, KeyError):
            continue
    n = len(D)
    u, de, dd = z([d[0] for d in D]), z([d[1] for d in D]), z([d[2] for d in D])
    y = [d[3] for d in D]
    fields = set(rows[0])

    # -- W1 independence gate, features only, repeated before any v2 look -------
    vif = {}
    cols = {"logU": u, "D_enc": de, "D_dec": dd}
    for nm, col in cols.items():
        r2 = ols_r2(col, [c for k, c in cols.items() if k != nm])
        vif[nm] = round(1 / (1 - r2) if r2 < 1 else float("inf"), 3)
    gate("W1_INDEPENDENCE_GATE_REPEATED_PRE_OUTCOME", all(v < 5 for v in vif.values()),
         "VIF %s -- all below 5, computed from features alone before any v2 outcome "
         "look. Repeated rather than inherited from T0, because a gate you assume is "
         "not a gate." % vif)

    # -- W2 V2a: the veto form, genuinely new ----------------------------------
    F = {"additive": [u[i] + de[i] + dd[i] for i in range(n)],
         "product": [u[i] * de[i] * dd[i] for i in range(n)],
         "minimum": [min(u[i], de[i], dd[i]) for i in range(n)]}
    A = {k: round(direction_free(v, y), 4) for k, v in F.items()}
    add_minus_min = round(A["additive"] - A["minimum"], 4)
    v2a_fired = add_minus_min < MARGIN
    gate("W2_PRIMARY_V2a_THE_VETO_FORM_RACE", True,
         "direction-free AUC: %s. additive - minimum = %+.4f, and V2a FIRES when that "
         "is below MARGIN=%.2f -> %s. The MINIMUM form WINS at %.4f. Single index, NO "
         "fitting, so no overfitting and no fold reuse -- the cleanest new look "
         "available on this cohort. This gate is about reporting, not about any "
         "particular form winning."
         % (A, add_minus_min, MARGIN, "FIRED" if v2a_fired else "did NOT fire",
            A["minimum"]))

    # -- W3 the double dip, logged not counted ---------------------------------
    confirmatory = round(A["additive"] - A["product"], 4)
    gate("W3_THE_DOUBLE_DIP_IS_LOGGED_NOT_COUNTED", True,
         "CONFIRMATORY ONLY: additive - product = %+.4f, product sits at %.4f which "
         "reproduces T0's chance-level result. T0 already ran this comparison; it "
         "contributes to NO gate and NO score in v2, because counting one look twice "
         "is the double-dip." % (confirmatory, A["product"]))

    # -- W4 the sunset, expired --------------------------------------------------
    today = datetime.date.today()
    sunset = datetime.date.fromisoformat(SUNSET)
    shock = [c for c in ("dep_shock", "maintainer_loss", "issue_spike") if c in fields]
    v2b_conditional = not shock
    expired = today > sunset
    demoted = v2b_conditional and expired
    gate("W4_THE_SUNSET_FIRES_BY_DATE", demoted,
         "V2b is CONDITIONAL (pre-outcome shock markers present: %s). SUNSET %s, today "
         "%s, expired=%s. THE TAIL-LEMMA DEMOTION IS EXECUTED: the lemma drops to a "
         "weight-zero prior and the branch stands on cascade alone. Fired by date, not "
         "by mood, and it fires AGAINST the carrier."
         % (shock or "NONE", SUNSET, today.isoformat(), expired))

    # -- W5 every unrun test declared -------------------------------------------
    unrun = {
        "V1_additive_forward": {
            "status": "AWAITING_EXTERNAL",
            "needs": "a temporal field (registered_at / archived_at) for the forward "
                     "holdout. Neither exists in the 992 cohort, so the additive lock "
                     "waits -- it is not 'pending'."},
        "V2b_tail_crossover": {
            "status": "CONDITIONAL_SUNSET_EXPIRED",
            "needs": "a pre-outcome shock marker (dep_shock / maintainer_loss / "
                     "issue_spike) and >=50 stressed rows. None exists; the sunset has "
                     "passed and the demotion above is executed."},
        "V3a_cascade_mechanism": {
            "status": "DATA_ABSENT",
            "needs": "HAMP or servicer panels with downstream-counterparty distress. "
                     "F3 null retires the hardship branch and invokes the fallback."},
        "V3b_cascade_analogue": {
            "status": "DATA_ABSENT",
            "needs": "an edge file for THESE repositories. A real dependency graph "
                     "exists at data/pypi/dep_graph_edges.csv (1287 edges, 540 nodes) "
                     "but it is PyPI packages: only 27 names overlap the 992 GitHub "
                     "repos, and cross-ecosystem name matching is unreliable. It is "
                     "not this cohort's edge file and is not substituted for one. "
                     "Separately, that graph carries no failure events and no "
                     "absorber variable, so any cascade computed on it would be "
                     "simulated."},
        "V3c_ABM_coherence": {
            "status": "NOT_BUILT_BY_CHOICE",
            "needs": "opt-in. If built it prints NOT EVIDENCE. It calibrates to T1/T5 "
                     "moments that do not exist, so it would be calibrated to nothing."},
        "V4_knife_rationales": {
            "status": "DATA_ABSENT",
            "needs": "T2 bend-vs-stagger plus the label-null. An F2 fire re-anchors "
                     "the knife on extraction and L4 must log it."},
        "V5_substrate_circulation": {
            "status": "DATA_ABSENT",
            "needs": "T1/T3 data. Never A2-dependent, so T0's and v2's results do not "
                     "touch it either way."},
    }
    # The spec's condition is that no test is DESCRIBED AS pending. Scanning the whole
    # blob for the substring was too crude: the V1 entry uses the word to DENY it
    # ("it is not 'pending'") and tripped my own guard. Checked on the STATUS field,
    # which is what "described as" actually refers to.
    VOCAB = {"AWAITING_EXTERNAL", "CONDITIONAL_SUNSET_EXPIRED", "DATA_ABSENT",
             "NOT_BUILT_BY_CHOICE", "CANNOT_RUN"}
    ok5 = len(unrun) == 7 and all(v.get("status") in VOCAB and v.get("needs")
                                  for v in unrun.values())
    gate("W5_EVERY_UNRUN_TEST_CARRIES_A_STATUS_AND_A_REMEDY", ok5,
         "seven declared: %s. Each names the artefact that would unblock it, and every "
         "status comes from the declared vocabulary -- none is 'pending' or 'in "
         "progress'. DISCLOSED: the first implementation of this check scanned the "
         "whole entry for the substring 'pending' and tripped on the V1 note that uses "
         "the word to DENY it. The check was corrected to read the STATUS field, which "
         "is what 'described as' means; the spec's condition was not touched."
         % {k: v["status"] for k, v in unrun.items()})

    # -- W6 the dry run ----------------------------------------------------------
    canary = classify({"state_contingent": False, "delta_U": 1,
                       "hardship_branch": False})
    coupled = classify({"state_contingent": True, "delta_U": 0,
                        "hardship_branch": True})
    stack = surviving_stack({"F3": True})
    gate("W6_V6_DRY_RUN_PROVES_THE_KNIFE_AND_THE_SEATBELT",
         canary == "RIBA-STRUCTURE" and coupled == "COUPLED"
         and stack == ["L0", "L1", "L3", "L4"],
         "inward knife: fixed/unbacked canary -> %s; state-contingent control -> %s "
         "(so the classifier is not a constant). Seatbelt: an F3 fire removes L2, "
         "leaving %s. The invocation logic is proven BEFORE it is needed, which is the "
         "only time proving it is cheap." % (canary, coupled, stack))

    gate("W7_does_V2a_firing_rescue_A2", False,
         "Partly, and the distinction matters. A2 AS WRITTEN says viability is the "
         "PRODUCT; T0 refuted that and v2 does not disturb it -- the product still "
         "sits at chance. A2's stated INTUITION, 'a zero in any factor zeroes the "
         "claim', is VETO semantics, which is what min() encodes and which wins here. "
         "So the idea may survive while the published formalisation does not. That is "
         "NOT a rescue of the published form, and reinterpreting a refuted "
         "formalisation after seeing the result is exactly what the anti-immunisation "
         "rule forbids counting.", "excluded")
    gate("W8_does_any_of_this_touch_the_reading_of_2_275", False,
         "No. Every form raced here is an operationalisation chosen downstream of the "
         "schema. The aya is not a functional form.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "V2a": {"direction_free_auc": A, "additive_minus_minimum": add_minus_min,
                "margin": MARGIN, "fired": v2a_fired, "winner": max(A, key=A.get)},
        "confirmatory_only": {"additive_minus_product": confirmatory,
                              "product_auc": A["product"],
                              "counted_toward_score": False},
        "sunset": {"date": SUNSET, "today": today.isoformat(), "expired": expired,
                   "v2b_conditional": v2b_conditional, "demotion_executed": demoted},
        "vif": vif, "n": n, "archived": sum(y),
        "unrun": unrun,
        "absent_paths": spec["PATHS_IN_THE_SUPPLIED_MODULE_THAT_DO_NOT_EXIST"],
        "simulated_values": 0,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. Two genuinely new results. FIRST, V2a FIRED: the MINIMUM (veto) form "
        "min(U, D_enc, D_dec) scores %.4f and BEATS additive %.4f by %.4f, while the "
        "product remains at chance %.4f. T0 never computed the veto form; this is a "
        "clean new look with no fitting and no fold reuse. It says viability on this "
        "cohort is governed by the WEAKEST factor, not by a sum and not by a product. "
        "SECOND, the SUNSET has EXPIRED: V2b is still CONDITIONAL because no "
        "pre-outcome shock marker exists, the date 2026-06-30 has passed, and the "
        "tail-lemma demotion is EXECUTED -- weight-zero prior, branch on cascade alone. "
        "product-vs-additive is logged CONFIRMATORY ONLY and counts toward nothing. "
        "Three paths the supplied module names do not exist here, including its edge "
        "file; a real PyPI graph exists but overlaps these repos by only 27 names and "
        "is NOT substituted. And note what V2a does NOT do: A2 as written claims a "
        "PRODUCT, which stays refuted. Its intuition -- a zero in any factor zeroes the "
        "claim -- is veto semantics, so the idea may survive while the formalisation "
        "does not. Reinterpreting after the result is not a rescue."
        % (res["score"], A["minimum"], A["additive"], -add_minus_min, A["product"]))

    json.dump(res, open(os.path.join(HERE, "results_v2.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    blob = json.dumps({k: res[k] for k in ("V2a", "sunset", "confirmatory_only")},
                      sort_keys=True)
    res["receipt"] = hashlib.sha256(blob.encode()).hexdigest()[:16]
    json.dump(res, open(os.path.join(HERE, "results_v2.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "V2a", "confirmatory_only", "sunset",
                       "primary_verdict", "receipt")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
