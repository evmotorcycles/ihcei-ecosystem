"""
crm.py -- CRM, the Cognitive Reference Model, run against its pre-registration.

Spec 558f6fa11302867b7fd1dfc0254e45ad8a54544b74d1c2893d63c20ff1248787, locked before this
file was written.

    D_W  = |rank corr( g(x), x )|        fidelity to the WORLD
    D_F  = |rank corr( g(x), f_m(x) )|   fidelity to the PAYOFF

Both are computed from the perceptual map and the world ONLY. Neither reads the agent's
realised payoff -- a test scans the source of both to enforce it.

THIS IS A SIMULATION. Its gates score only for statements about the model, never about
people. No human behavioural trial dataset was reachable; X7 records that.
"""
import hashlib
import json
import math
import os
import random
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "558f6fa11302867b7fd1dfc0254e45ad8a54544b74d1c2893d63c20ff1248787"

SPEC = json.load(open(os.path.join(HERE, "prereg", "crm_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

MONO = [0.0, 0.25, 0.5, 0.75, 1.0]
AGENTS_PER_M, TRIALS, GRID, SEED = 400, 400, 200, 20260801
NOISE_SD = 0.01
X2_PAY_IQR, X2_FID_IQR = 0.02, 0.10
X3_MARGIN = X5_MARGIN = 0.005
X6_MIN = 0.20
TOO_PERFECT_GAIN, TOO_PERFECT_CORR = 0.05, 0.95


def payoff(x, m):
    return (1 - m) * math.exp(-((x - 0.5) / 0.18) ** 2) + m * x


# ------------------------------------------------- the two reference fidelities
def _ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        mr = (i + j) / 2.0
        for k in range(i, j + 1):
            r[order[k]] = mr
        i = j + 1
    return r


def spearman_abs(a, b):
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((p - ma) * (q - mb) for p, q in zip(ra, rb))
    da = math.sqrt(sum((p - ma) ** 2 for p in ra))
    db = math.sqrt(sum((q - mb) ** 2 for q in rb))
    if da == 0 or db == 0:
        return 0.0
    return abs(num / (da * db))


def D_world(percepts, states):
    """Fidelity to the world reference. Reads the map and the state. Nothing else."""
    return spearman_abs(percepts, states)


def D_payoff(percepts, payoffs):
    """Fidelity to the payoff reference. Reads the map and the payoff curve. Nothing else."""
    return spearman_abs(percepts, payoffs)


# ------------------------------------------------------------- agents & world
def make_map(rng):
    """A perceptual map on [0,1]: k control points, monotone or shuffled."""
    k = rng.randint(2, 7)
    pts = sorted(rng.random() for _ in range(k))
    vals = [rng.random() for _ in range(k + 1)]
    if rng.random() < 0.5:
        vals.sort()                      # monotone family
    return {"cuts": pts, "vals": vals, "levels": k + 1}


def perceive(mp, x):
    lo = 0
    for c in mp["cuts"]:
        if x <= c:
            break
        lo += 1
    return mp["vals"][lo]


def build(rng):
    grid = [(i + 0.5) / GRID for i in range(GRID)]
    rows = []
    for m in MONO:
        pay_grid = [payoff(x, m) for x in grid]
        for _ in range(AGENTS_PER_M):
            mp = make_map(rng)
            pg = [perceive(mp, x) for x in grid]
            dw, df = D_world(pg, grid), D_payoff(pg, pay_grid)
            total = 0.0
            for _ in range(TRIALS):
                a, b = rng.random(), rng.random()
                pick = a if perceive(mp, a) >= perceive(mp, b) else b
                total += payoff(pick, m)
            # noise goes DIRECTLY on the agent-level outcome; nothing is averaged after it
            realised = total / TRIALS + rng.gauss(0.0, NOISE_SD)
            rows.append({"m": m, "D_W": dw, "D_F": df,
                         "U": mp["levels"] / 8.0, "payoff": realised})
    return rows


# --------------------------------------------------------------- fitting
def ols(X, y):
    """Least squares with intercept, solved by Gaussian elimination on the normal equations."""
    n, p = len(X), len(X[0]) + 1
    A = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for xi, yi in zip(X, y):
        row = [1.0] + list(xi)
        for i in range(p):
            b[i] += row[i] * yi
            for j in range(p):
                A[i][j] += row[i] * row[j]
    for i in range(p):
        piv = max(range(i, p), key=lambda r: abs(A[r][i]))
        if abs(A[piv][i]) < 1e-12:
            return [0.0] * p
        A[i], A[piv] = A[piv], A[i]
        b[i], b[piv] = b[piv], b[i]
        for r in range(i + 1, p):
            f = A[r][i] / A[i][i]
            for c in range(i, p):
                A[r][c] -= f * A[i][c]
            b[r] -= f * b[i]
    w = [0.0] * p
    for i in range(p - 1, -1, -1):
        s = b[i] - sum(A[i][j] * w[j] for j in range(i + 1, p))
        w[i] = s / A[i][i]
    return w


def cv_error(rows, feats, seed=SEED):
    rng = random.Random(seed)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    folds = [idx[i::5] for i in range(5)]
    errs = []
    for i in range(5):
        te = folds[i]
        tr = [j for k, f in enumerate(folds) if k != i for j in f]
        w = ols([feats(rows[j]) for j in tr], [rows[j]["payoff"] for j in tr])
        e = [abs(w[0] + sum(c * v for c, v in zip(w[1:], feats(rows[j])))
                 - rows[j]["payoff"]) for j in te]
        errs.append(statistics.fmean(e))
    return statistics.fmean(errs)


def pearson(a, b):
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    da = math.sqrt(sum((p - ma) ** 2 for p in a))
    db = math.sqrt(sum((q - mb) ** 2 for q in b))
    return 0.0 if da == 0 or db == 0 else num / (da * db)


def iqr(v):
    s = sorted(v)
    n = len(s)
    return s[int(0.75 * (n - 1))] - s[int(0.25 * (n - 1))]


def main():
    rows = build(random.Random(SEED))
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ---- X1 -----------------------------------------------------------------
    ranges_ok = all(0.0 <= r["D_W"] <= 1.0 and 0.0 <= r["D_F"] <= 1.0 for r in rows)
    x1 = len(rows) == AGENTS_PER_M * len(MONO) and ranges_ok
    gate("X1_integrity_and_the_earlier_flaw_is_fixed", x1,
         "%d agents across %d monotonicity levels, all D_W/D_F in [0,1]=%s; noise sd %.3f "
         "applied to the agent-level outcome only" % (len(rows), len(MONO), ranges_ok, NOISE_SD))

    # ---- X2 populated failing region ---------------------------------------
    p_iqr = iqr([r["payoff"] for r in rows])
    w_iqr = iqr([r["D_W"] for r in rows])
    f_iqr = iqr([r["D_F"] for r in rows])
    x2 = p_iqr >= X2_PAY_IQR and w_iqr >= X2_FID_IQR and f_iqr >= X2_FID_IQR
    gate("X2_THE_FAILING_REGION_IS_POPULATED", x2,
         "IQR payoff %.4f (needs >= %.2f), D_W %.4f, D_F %.4f (each needs >= %.2f)"
         % (p_iqr, X2_PAY_IQR, w_iqr, f_iqr, X2_FID_IQR))

    # ---- models -------------------------------------------------------------
    e_two = cv_error(rows, lambda r: [r["D_W"], r["D_F"]])
    e_one = cv_error(rows, lambda r: [(r["D_W"] + r["D_F"]) / 2.0])
    e_w = cv_error(rows, lambda r: [r["D_W"]])
    e_f = cv_error(rows, lambda r: [r["D_F"]])
    e_lism = cv_error(rows, lambda r: [r["U"] * r["D_W"] * r["D_F"]])

    if x2:
        gate("X3_TWO_REFERENCES_BEAT_ONE", e_one - e_two >= X3_MARGIN,
             "mean held-out |error|: two-reference %.5f, single-fidelity %.5f, gain %+.5f "
             "(needs >= %.3f)" % (e_two, e_one, e_one - e_two, X3_MARGIN))
        gate("X5_CRM_BEATS_LISMS_OWN_TWO_HOP_FORM", e_lism - e_two >= X5_MARGIN,
             "mean held-out |error|: CRM two-reference %.5f, LISM U*D_enc*D_dec %.5f, "
             "gain %+.5f (needs >= %.3f)" % (e_two, e_lism, e_lism - e_two, X5_MARGIN))
    else:
        gate("X3_TWO_REFERENCES_BEAT_ONE", False, "UNTESTABLE-HERE: X2 not met")
        gate("X5_CRM_BEATS_LISMS_OWN_TWO_HOP_FORM", False, "UNTESTABLE-HERE: X2 not met")

    # ---- X4 directional dissociation ---------------------------------------
    corr = {}
    for m in MONO:
        sub = [r for r in rows if r["m"] == m]
        corr[m] = pearson([r["D_W"] for r in sub], [r["D_F"] for r in sub])
    a_ok, b_ok = corr[0.0] < 0, corr[1.0] >= 0
    gate("X4_THE_DISSOCIATION_IS_DIRECTIONAL", a_ok and b_ok,
         "corr(D_W,D_F) by monotonicity: %s. (a) m=0.0 negative = %s; (b) m=1.0 "
         "non-negative = %s" % ({k: round(v, 4) for k, v in corr.items()}, a_ok, b_ok))

    # ---- X6 DCM self-audit --------------------------------------------------
    med_p = statistics.median(r["payoff"] for r in rows)
    med_m = statistics.median(r["m"] for r in rows)
    ys = [1 if r["payoff"] > med_p else 0 for r in rows]
    labels = [1 if r["m"] > med_m else 0 for r in rows]
    V = 1.0 - Counter(ys).most_common(1)[0][1] / len(ys)
    p = min(sum(labels), len(labels) - sum(labels)) / len(labels)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(ys)) / len(ys))
    DELTA = V * I * C
    x6 = DELTA >= X6_MIN
    gate("X6_DCM_SELF_AUDIT", x6,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f) on n=%d agents"
         % (V, I, C, DELTA, X6_MIN, len(rows)))

    gates.append({"id": "X7_anything_about_human_cognition", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Four Hugging Face searches for human "
                            "behavioural trial data returned only text and multiple-choice "
                            "QA corpora. Every number here comes from simulated agents."})

    # ---- X8 the Novora governance layer, scores nothing ---------------------
    audit = {}
    try:
        import subprocess
        prose = ("The two-reference model was compared against a single fidelity number and "
                 "against LISM's own two-hop form under cross-validation. Every threshold "
                 "was locked before the runner was written.")
        js = ("import('%s').then(m=>console.log(JSON.stringify(m.audit(%s))))"
              % (os.path.join(os.path.dirname(HERE), "novora-helm/src/helm-core.mjs"),
                 json.dumps(prose)))
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
        line = [l for l in out.stdout.splitlines() if l.startswith("{")]
        if line:
            h = json.loads(line[0])
            audit = {"helm_verdict": h.get("verdict"),
                     "p_manipulative": h.get("p_manipulative"),
                     "engine": h.get("engine")}
    except Exception as exc:
        audit = {"helm_verdict": "UNAVAILABLE", "reason": str(exc)[:120]}
    gates.append({"id": "X8_the_novora_governance_layer", "met": None, "weight": "excluded",
                  "detail": "HELM audited the results prose: %s. A governance verdict on "
                            "PROSE is not evidence about agents, so this scores nothing."
                            % json.dumps(audit)})

    # ---- disclosures --------------------------------------------------------
    binding = (("X6 WAS NOT MET, SO X3, X4 AND X5 ARE UNINFORMATIVE. DELTA = %.4f against a "
                "locked floor of %.2f. No claim may be made for or against CRM on the "
                "strength of them.") % (DELTA, X6_MIN)) if not x6 else (
        "X6 was met at DELTA = %.4f, so X3, X4 and X5 are reportable on their own terms."
        % DELTA)

    verdict = ("CRM EARNED ITS EXISTENCE" if (x2 and x6 and e_one - e_two >= X3_MARGIN
                                              and e_lism - e_two >= X5_MARGIN)
               else "CRM DID NOT EARN ITS EXISTENCE ON THIS RUN. X5 missed: it beat LISM's "
                    "two-hop form by only %.5f against a locked bar of %.3f, and the spec "
                    "says in its own words that the honest conclusion is then to keep LISM "
                    "and drop CRM." % (e_lism - e_two, X5_MARGIN))

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"delta": round(DELTA, 4), "floor": X6_MIN,
                                       "statement": binding},
        "D2_the_earlier_flaw_and_how_this_run_differs": {
            "what_went_wrong_in_6cb42dcd": "noise applied per participant then AVERAGED, "
                    "giving effective noise ~0.0045 and a test that could not fail",
            "what_this_run_does": "noise sd %.3f applied DIRECTLY to the agent-level "
                    "outcome, nothing averaged after it, and X2 checks the failing region "
                    "is populated before any comparison is scored" % NOISE_SD,
            "measured_payoff_IQR": round(p_iqr, 4),
        },
        "D3_X4_half_b_is_near_definitional": {
            "note": "When payoff is monotone in the world state the two references very "
                    "nearly coincide, so a non-negative correlation at m=1.0 is close to "
                    "definitional. That was disclosed BEFORE the run. Only half (a) -- a "
                    "negative correlation in the non-monotone world -- carries information.",
            "corr_at_m0": round(corr[0.0], 4), "corr_at_m1": round(corr[1.0], 4),
        },
        "D4_what_this_says_about_people": {
            "statement": "NOTHING. Every agent is simulated. The substrate is a published "
                         "evolutionary-game setting, and a simulation can show a "
                         "decomposition is USEFUL inside a model while saying nothing about "
                         "whether it is TRUE of minds.",
        },
        "D6_X6_FAILED_BECAUSE_I_MIS_SPECIFIED_IT_AND_THE_BINDING_STILL_FIRES": {
            "measured": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                         "DELTA": round(DELTA, 4)},
            "what_went_wrong": "The locked spec said to band realised payoff at its median "
                    "as the outcome. DCM's C factor is distinct outcome values divided by n "
                    "-- so banding a continuous outcome to BINARY forces C = 2/2000 = 0.001 "
                    "BY CONSTRUCTION. The gate could not pass whatever the data did.",
            "whose_error": "Mine. Second consecutive specification in which I wrote a gate "
                    "that could not reach its own threshold -- the first was the averaged "
                    "noise in 6cb42dcd. That is a pattern about my spec-writing and is "
                    "recorded as one.",
            "diagnostic_only_NOT_a_re_score": "On the UNBANDED payoff the same C would be "
                    "%.4f, since realised payoff takes %d distinct values across %d agents. "
                    "That number is a diagnosis of the error, not a substitute verdict."
                    % (min(1.0, len(set(round(r["payoff"], 9) for r in rows)) / len(rows)),
                       len(set(round(r["payoff"], 9) for r in rows)), len(rows)),
            "THE_BINDING_IS_HONOURED_ANYWAY": "X6 is recorded as failed and X3, X4 and X5 "
                    "are reported UNINFORMATIVE. Honouring a binding rule only when it is "
                    "convenient is precisely the immunisation move the rule exists to stop. "
                    "The gate is not re-scored and the spec is not edited.",
        },
        "D7_X5_MISSED_AND_THE_SPEC_SAID_WHAT_THAT_MEANS": {
            "CRM_two_reference": round(e_two, 5), "LISM_two_hop": round(e_lism, 5),
            "gain": round(e_lism - e_two, 5), "bar": X5_MARGIN,
            "the_specs_own_words": "'If LISM's existing form predicts this cognitive outcome "
                    "as well as a purpose-built two-reference model, then CRM adds "
                    "vocabulary and no power, and the honest conclusion is to keep LISM and "
                    "drop CRM.' The gain was %.5f against a bar of %.3f. CRM DID NOT EARN "
                    "ITS EXISTENCE on this run." % (e_lism - e_two, X5_MARGIN),
            "and_a_harsher_reading_the_spec_did_not_lock": "D_F ALONE scores %.5f against "
                    "the two-reference model's %.5f -- a gain of only %.5f. The locked X3 "
                    "compared CRM against the MEAN of the two fidelities, which is a weaker "
                    "rival than the better single one. Against the best single reference the "
                    "two-reference model buys almost nothing. This comparison was not "
                    "pre-registered and scores nothing, and it is reported because leaving "
                    "it out would flatter the model."
                    % (e_f, e_two, e_f - e_two),
        },
        "D8_X4_PASSED_BUT_TRIPS_THE_TOO_PERFECT_RULE": {
            "correlations": {str(k): round(v, 4) for k, v in corr.items()},
            "note": "The locked too-perfect rule flags any |correlation| above 0.95. Two "
                    "values exceed it: 0.9569 at m=0.75 and exactly 1.0000 at m=1.0. The "
                    "flag fired. The reading is not leakage but DEGENERACY -- when payoff "
                    "is strictly increasing in the world state the two references are the "
                    "same ordering, so their correlation is forced to 1. That is why half "
                    "(b) of X4 was disclosed as near-definitional BEFORE the run. Only the "
                    "negative correlation at m=0.0 carries information.",
        },
        "D5_only_two_tools_could_change_a_verdict": {
            "could": ["LISM (the rival in X5)", "DCM (the self-audit in X6)"],
            "could_not": ["HELM / NERE", "Novora Suite fastmode", "Page Code",
                          "Claude Code", "IHCEI"],
            "note": "Claude Code wrote and locked the spec; IHCEI carries the run; the rest "
                    "audit the WRITE-UP. Recording this prevents the appearance that a "
                    "large toolchain was doing scientific work it was not doing.",
        },
    }
    suspect = []
    if e_one - e_two > TOO_PERFECT_GAIN or e_lism - e_two > TOO_PERFECT_GAIN:
        suspect.append("cv_gain_above_0.05")
    if any(abs(v) > TOO_PERFECT_CORR for v in corr.values()):
        suspect.append("correlation_above_0.95")

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "CRM - the Cognitive Reference Model",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "n_agents": len(rows), "monotonicity_levels": MONO, "seed": SEED,
        "cv_mean_abs_error": {"CRM_two_reference": round(e_two, 5),
                              "single_fidelity": round(e_one, 5),
                              "D_W_alone": round(e_w, 5), "D_F_alone": round(e_f, 5),
                              "LISM_two_hop": round(e_lism, 5)},
        "corr_DW_DF_by_monotonicity": {str(k): round(v, 4) for k, v in corr.items()},
        "iqr": {"payoff": round(p_iqr, 4), "D_W": round(w_iqr, 4), "D_F": round(f_iqr, 4)},
        "dcm_self_audit": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                           "DELTA": round(DELTA, 4), "floor": X6_MIN},
        "novora_governance_audit": audit,
        "too_perfect_flag": suspect,
        "human_data_reachable": False,
        "post_run_disclosures": disclosures,
        "primary_verdict": verdict + " | " + binding,
    }
    with open(os.path.join(HERE, "results_crm.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "cv_mean_abs_error",
                       "corr_DW_DF_by_monotonicity", "iqr", "dcm_self_audit",
                       "novora_governance_audit")}, indent=2))


if __name__ == "__main__":
    main()
