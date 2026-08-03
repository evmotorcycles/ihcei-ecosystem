"""
con.py -- is D one construct? Run against its pre-registration.

Spec b6a262ead56e56b532a3578185c6d505df45fbc9c58a5ba5864108bb194c53d8, locked before
rho(U_versions, months_since_release) -- the quantity the primary turns on -- was computed.

Two committed real files. Nothing simulated, no proxy substituted for a blocked quantity.
"""
import csv
import hashlib
import json
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "b6a262ead56e56b532a3578185c6d505df45fbc9c58a5ba5864108bb194c53d8"

SPEC = json.load(open(os.path.join(HERE, "prereg", "construct_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

N2_BAR, N4_DROP, N6_HI, N_PERM, SEED = 0.50, 0.20, 0.10, 2000, 20260803
PYPI_BASELINE_RHO_U_DENC = 0.5869   # recorded in the spec as a pre-lock observation


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    a, b = rank(x), rank(y)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    den = (sum((v - ma) ** 2 for v in a) * sum((v - mb) ** 2 for v in b)) ** 0.5
    return num / den if den else 0.0


def load():
    py = list(csv.DictReader(open(os.path.join(ROOT, "data", "pypi", "dep_graph_nodes.csv"))))
    gh = [r for r in csv.DictReader(
        open(os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")))
        if r["tau_v_imputed"].strip().lower() not in ("true", "1", "yes")]
    return py, gh


def main():
    py, gh = load()
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    def col(rows, k):
        return [float(r[k]) for r in rows]

    U_ver = col(py, "U_versions")
    months = col(py, "months_since_release")
    denc_py = col(py, "D_enc_release_hygiene")
    ddec_py = col(py, "D_dec_pin_clarity")
    U_gh = col(gh, "U")
    D_gh = col(gh, "D")

    # ---- N1 ------------------------------------------------------------------
    ok1 = (len(py) == 540 and len(gh) == 866
           and all(v == v for v in U_ver + months + denc_py + ddec_py + U_gh + D_gh))
    gate("N1_integrity", ok1,
         "PyPI n=%d, GitHub non-imputed n=%d, no NaN in any quantity used"
         % (len(py), len(gh)))

    # ---- N2 PRIMARY ----------------------------------------------------------
    rho_u_months = spearman(U_ver, months)
    n2 = abs(rho_u_months) >= N2_BAR
    gate("N2_PRIMARY_THE_PYPI_CORRELATION_IS_CONSTRUCTION_INDUCED", n2,
         "rho(U_versions, months_since_release) = %+.4f, |rho| = %.4f (needs >= %.2f). "
         "D_enc is defined as 1/(1 + months/12), so a strong coupling here means the "
         "PyPI rho(U, D_enc) of %+.4f follows from the DEFINITION rather than from a "
         "measured fidelity." % (rho_u_months, abs(rho_u_months), N2_BAR,
                                 PYPI_BASELINE_RHO_U_DENC))

    # ---- N3 the declared identity, EXCLUDED ----------------------------------
    rho_identity = spearman(denc_py, months)
    gates.append({"id": "N3_the_pypi_D_enc_identity", "met": None, "weight": "excluded",
                  "detail": "rho(D_enc_pypi, months_since_release) = %+.4f. Declared in "
                            "advance as an algebraic identity because D_enc = 1/(1+m/12) "
                            "is strictly decreasing in m. Verified, NOT scored: a quantity "
                            "that cannot come out otherwise is not evidence."
                            % rho_identity})

    # ---- N4 discriminating ---------------------------------------------------
    rho_timing_free = spearman(U_ver, ddec_py)
    drop = PYPI_BASELINE_RHO_U_DENC - abs(rho_timing_free)
    n4 = drop >= N4_DROP
    gate("N4_DISCRIMINATING_A_TIMING_FREE_D_enc_BREAKS_THE_PYPI_CORRELATION", n4,
         "substituting the only other committed fidelity column, D_dec_pin_clarity, which "
         "does not reference release timing: rho(U_versions, pin_clarity) = %+.4f. Drop "
         "from the %.4f baseline = %.4f (needs >= %.2f)."
         % (rho_timing_free, PYPI_BASELINE_RHO_U_DENC, drop, N4_DROP))

    # ---- N5 count vs intensity, disclosure gate ------------------------------
    age = [max(m, 1e-9) for m in months]
    U_int = [u / a for u, a in zip(U_ver, age)]
    rho_int = spearman(U_int, denc_py)
    gates.append({"id": "N5_THE_COUNT_VS_INTENSITY_RULE_APPLIED_TO_U", "met": None,
                  "weight": "excluded",
                  "detail": "U is a raw COUNT of versions. As an INTENSITY -- versions per "
                            "month of age -- rho(U_intensity, D_enc) = %+.4f against the "
                            "raw count's %+.4f. Reported whether or not it helps; no "
                            "threshold, this gate asserts disclosure."
                            % (rho_int, PYPI_BASELINE_RHO_U_DENC)})

    # ---- N6 permutation control ---------------------------------------------
    rng = random.Random(SEED)

    def perm_hi(x, y):
        vals = []
        for _ in range(N_PERM):
            s = list(y)
            rng.shuffle(s)
            vals.append(abs(spearman(x, s)))
        vals.sort()
        return vals[int(0.95 * N_PERM)]
    hi_py = perm_hi(U_ver, denc_py)
    hi_gh = perm_hi(U_gh, D_gh)
    n6 = hi_py <= N6_HI and hi_gh <= N6_HI
    gate("N6_THE_PERMUTATION_CONTROL", n6,
         "with D shuffled within substrate, the 95th percentile of |rho| over %d "
         "permutations is %.4f (PyPI) and %.4f (GitHub); both must be <= %.2f"
         % (N_PERM, hi_py, hi_gh, N6_HI))

    gates.append({"id": "N7_the_proposed_demand_normalisation", "met": None,
                  "weight": "excluded",
                  "detail": "BLOCKED. The committed GitHub cohort carries no inbound issue "
                            "or PR counts, so closed/total-inbound is not computable. No "
                            "proxy substituted. BLOCKED is not REFUTED: the mechanism may "
                            "well be right and simply cannot be tested from this file."})
    gates.append({"id": "N8_does_this_repair_D_for_cross_substrate_use", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Diagnosing why two numbers disagree does not "
                            "produce a construct that travels. Building one needs a single "
                            "formula computed the same way on both substrates, and the "
                            "committed files share no fidelity column."})

    suspect = []
    if abs(abs(rho_identity) - 1.0) < 1e-9:
        suspect.append("N3_identity_at_exactly_1.0_EXPECTED_and_declared_in_advance")

    verdict = ("THE PYPI HALF OF THE ALARM IS CONSTRUCTION-INDUCED. "
               if (n2 and n4) else
               "THE DEFINITIONAL EXPLANATION DID NOT HOLD. ")
    verdict += ("rho(U_versions, months_since_release) = %+.4f and a timing-free fidelity "
                "column gives rho = %+.4f against the timing-based %+.4f."
                % (rho_u_months, rho_timing_free, PYPI_BASELINE_RHO_U_DENC))

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Is D one construct?",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet, "simulated_values": 0,
        "measured": {
            "rho_U_versions_vs_months_since_release": round(rho_u_months, 4),
            "rho_D_enc_vs_months_IDENTITY": round(rho_identity, 4),
            "rho_U_versions_vs_pin_clarity_TIMING_FREE": round(rho_timing_free, 4),
            "rho_U_intensity_vs_D_enc": round(rho_int, 4),
            "pypi_baseline_rho_U_D_enc_from_spec": PYPI_BASELINE_RHO_U_DENC,
            "permutation_95th_abs_rho": {"pypi": round(hi_py, 4), "github": round(hi_gh, 4)},
        },
        "too_perfect_flag": suspect,
        "post_run_disclosures": {
            "D1_what_this_does_and_does_not_settle": {
                "settles": "Whether the PyPI half of the sign alarm follows from how D_enc "
                           "was defined there.",
                "does_NOT_settle": "The GitHub negative correlation, which no gate here "
                                   "touches. D is not repaired and E = U*D_enc*D_dec is not "
                                   "restored to universal standing.",
            },
            "D2_the_two_definitions_share_a_name_and_nothing_else": {
                "pypi_D_enc": "1.0 / (1.0 + months_since_release / 12.0) -- a recency decay",
                "github_D_enc": "mean TF-IDF cosine of commit messages to a fixed "
                                "methodology reference -- a text-similarity score",
                "note": "Comparing their correlations with U across substrates was "
                        "comparing two different quantities carrying one label. The remedy "
                        "is a rule about what may be compared, not a transformation applied "
                        "to either.",
            },
            "D3_the_proposed_demand_normalisation_is_BLOCKED_not_refuted": {
                "note": "No inbound issue or PR counts are committed for the GitHub cohort. "
                        "The mechanism may well be correct; this file cannot test it, and "
                        "no proxy was substituted.",
            },
            "D4_a_prediction_of_that_mechanism_already_failed_before_the_lock": {
                "note": "Queue congestion is a decode-side story, so the flip should sit in "
                        "D_dec. Both hops flip: PyPI D_enc +0.5869 / D_dec +0.3496 against "
                        "GitHub -0.2415 / -0.5154. Recorded as a pre-lock observation and "
                        "scored by nothing.",
            },
        },
        "primary_verdict": verdict,
    }
    with open(os.path.join(HERE, "results_con.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "measured",
                                          "too_perfect_flag", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
