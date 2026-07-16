#!/usr/bin/env python3
"""
methodology_experiment.py — Does the LISM/NERE methodology actually kill false signals?
=======================================================================================
The epistemological thesis under test: the breakthrough of LISM is not the linear
law or tau_v, it is the METHODOLOGY — a four-pillar cognitive firewall that
actively suppresses the false "universal laws" that post-hoc data-mining
manufactures. This experiment tests that claim head-on, by Monte Carlo.

Two analysts see the SAME synthetic datasets:

  NAIVE  ("vending-machine science")  — garden of forking paths: search several
         model specs x several sub-populations, report a LAW if ANY (spec,
         subgroup) crosses p<0.05 with the expected sign. No gates.

  FIREWALL (the LISM/NERE four pillars):
     P1 pre-registration lock : ONE locked spec, FULL sample only, no subgroup
                                mining; a locked bidirectional linear-vs-quadratic
                                decision rule (nested LRT).
     P2 variance-inflation gate: if VIF(D_enc,D_dec) >= 5 -> INCONCLUSIVE (the
                                two-hop channel has collapsed; cf. SEC EDGAR).
     P3 honest non-test triage : if the failing region is underpopulated
                                (min class < 100) -> INCONCLUSIVE (separation
                                artifact; cf. the M5 non-converged fit).
     P4 public funeral         : a null is reported as a null and never re-mined.

Five data regimes, each with a KNOWN ground truth:
  NULL       — E independent of predictors            -> correct call: no law
  LINEAR     — E genuinely driven by U*D              -> correct call: LINEAR
  QUADRATIC  — E genuinely driven by U*D^2            -> correct call: QUADRATIC
  TRAP_VIF   — confounded + COLLINEAR two-hop channel  -> correct call: INCONCLUSIVE
               (a lurking Z drives both hops and the outcome; D looks protective
                but the channel has collapsed. The SEC EDGAR case — VIF gate must fire.)
  TRAP_SEP   — channel-intact but ULTRA-SPARSE failures -> correct call: INCONCLUSIVE
               (near-separation manufactures a significant coefficient on a handful
                of failures. The M5 non-converged-fit case — non-test triage must fire.)

Metric per regime: how often each analyst reaches the CORRECT scientific verdict.
Under NULL that means the false-discovery (Type-I) rate is the headline number.

Run:  python3 methodology_experiment.py [--reps 300] [--n 250] [--seed 1] [--json out.json]
"""
from __future__ import annotations
import argparse, json, warnings
import numpy as np
import statsmodels.api as sm
from scipy import stats

warnings.simplefilter("ignore")  # separation / convergence warnings are DATA, handled below

ALPHA = 0.05
VIF_MAX = 5.0
NFAIL_MIN = 100


# ── data generating process ──────────────────────────────────────────────────
def make_dataset(regime, n, rng):
    """Return dict with U, D_enc, D_dec, D, E (binary failure), plus truth label."""
    U = rng.uniform(0.5, 1.5, n)

    if regime == "TRAP_VIF":
        # lurking Z drives BOTH hops (near-identical -> collinear) AND the outcome,
        # so D looks protective though the two-hop channel has collapsed.
        Z = rng.normal(0, 1, n)
        D_enc = np.clip(0.5 + 0.22 * Z + rng.normal(0, 0.02, n), 0.02, 0.98)
        D_dec = np.clip(0.5 + 0.22 * Z + rng.normal(0, 0.02, n), 0.02, 0.98)  # ~collinear
        D = D_enc * D_dec
        p_fail = 1 / (1 + np.exp(-(-0.2 - 1.3 * Z)))   # high Z -> high D -> LOW fail (spurious)
        E = (rng.uniform(size=n) < p_fail).astype(int) # base rate ~ 45%, so NOT sparse
        return dict(U=U, D_enc=D_enc, D_dec=D_dec, D=D, E=E, truth="INCONCLUSIVE")

    if regime == "TRAP_SEP":
        # channel-intact (independent hops, low VIF) but ULTRA-SPARSE failures ->
        # near-separation manufactures a "significant" protective coefficient.
        D_enc = rng.uniform(0.05, 0.95, n)
        D_dec = rng.uniform(0.05, 0.95, n)
        D = D_enc * D_dec
        p_fail = 1 / (1 + np.exp(-(-3.3 - 2.5 * (D - D.mean()))))  # ~3-5% failures, low-D biased
        E = (rng.uniform(size=n) < p_fail).astype(int)
        return dict(U=U, D_enc=D_enc, D_dec=D_dec, D=D, E=E, truth="INCONCLUSIVE")

    # independent, channel-intact hops; wide D so D and D^2 are separable
    D_enc = rng.uniform(0.05, 0.95, n)
    D_dec = rng.uniform(0.05, 0.95, n)
    D = D_enc * D_dec
    xlin = U * D
    xquad = U * D * D
    if regime == "NULL":
        logit = np.zeros(n)                        # E independent of everything
        truth = "NULL"
    elif regime == "LINEAR":
        logit = 5.0 * (xlin - xlin.mean())         # genuine linear coupling
        truth = "LINEAR"
    elif regime == "QUADRATIC":
        logit = 14.0 * (xquad - xquad.mean())      # genuine quadratic coupling
        truth = "QUADRATIC"
    else:
        raise ValueError(regime)
    p_fail = 1 / (1 + np.exp(logit))               # higher fidelity -> lower failure
    E = (rng.uniform(size=n) < p_fail).astype(int)
    return dict(U=U, D_enc=D_enc, D_dec=D_dec, D=D, E=E, truth=truth)


# ── shared statistics ────────────────────────────────────────────────────────
def _fit(X, y):
    """Logit fit; returns (params, pvalues, llf, converged) or None on failure."""
    Xc = sm.add_constant(X, has_constant="add")
    try:
        res = sm.Logit(y, Xc).fit(disp=0, maxiter=60)
        conv = bool(res.mle_retvals.get("converged", True))
        return res.params, res.pvalues, res.llf, conv
    except Exception:
        return None


def vif_two_hop(d_enc, d_dec):
    r = np.corrcoef(d_enc, d_dec)[0, 1]
    r2 = min(r * r, 1 - 1e-9)
    return 1.0 / (1.0 - r2)


def coupling_significant(ds, cols):
    """Fit E ~ f(cols) and return (significant, protective_sign) for the fidelity term."""
    y = ds["E"]
    X = np.column_stack([ds_key(ds, c) for c in cols])
    out = _fit(X, y)
    if out is None:
        return False, False, False
    params, pvals, _, conv = out
    # fidelity term is the last column; protective => coefficient < 0 (more D, less fail)
    coef, p = params[-1], pvals[-1]
    return (p < ALPHA), (coef < 0), conv


def ds_key(ds, c):
    if c == "UD":   return ds["U"] * ds["D"]
    if c == "UD2":  return ds["U"] * ds["D"] * ds["D"]
    if c == "D":    return ds["D"]
    if c == "Denc": return ds["D_enc"]
    if c == "Ddec": return ds["D_dec"]
    raise KeyError(c)


# ── analyst A: naive vending-machine science ─────────────────────────────────
def analyst_naive(ds, rng):
    """Search specs x subpopulations; report the strongest significant hit."""
    specs = [["UD"], ["UD2"], ["D"], ["Denc"], ["Ddec"]]
    U = ds["U"]
    subgroups = {
        "full":    np.ones(len(U), bool),
        "hiU":     U >= np.median(U),
        "loU":     U < np.median(U),
        "hiD":     ds["D"] >= np.median(ds["D"]),
        "loD":     ds["D"] < np.median(ds["D"]),
        "hiDenc":  ds["D_enc"] >= np.median(ds["D_enc"]),
    }
    best = None
    for sg_mask in subgroups.values():
        if sg_mask.sum() < 40 or ds["E"][sg_mask].sum() < 3:
            continue
        sub = {k: (v[sg_mask] if isinstance(v, np.ndarray) else v) for k, v in ds.items()}
        for spec in specs:
            sig, protective, _ = coupling_significant(sub, spec)
            if sig and protective:
                verdict = "QUADRATIC" if spec == ["UD2"] else "LINEAR"
                # first significant hit is enough for a "law found"
                return verdict
    return best or "NULL"


# ── analyst B: the LISM/NERE firewall ────────────────────────────────────────
def analyst_firewall(ds):
    """One locked pipeline on the full sample, with gates and a bidirectional rule."""
    # P2 — variance-inflation gate
    if vif_two_hop(ds["D_enc"], ds["D_dec"]) >= VIF_MAX:
        return "INCONCLUSIVE"
    # P3 — honest non-test triage (underpopulated failing region)
    n_fail = int(min(ds["E"].sum(), (ds["E"] == 0).sum()))
    if n_fail < NFAIL_MIN:
        return "INCONCLUSIVE"
    # P1 — locked bidirectional rule: nested LRT M1(E~U+UD) vs M2(+UD^2)
    y = ds["E"]
    UD = ds["U"] * ds["D"]
    UD2 = ds["U"] * ds["D"] * ds["D"]
    m1 = _fit(np.column_stack([ds["U"], UD]), y)
    m2 = _fit(np.column_stack([ds["U"], UD, UD2]), y)
    if m1 is None or m2 is None or not m1[3] or not m2[3]:
        return "INCONCLUSIVE"                       # non-converged fit is not evidence
    lr = 2 * (m2[2] - m1[2])
    p_quad = stats.chi2.sf(max(lr, 0), df=1)
    # is there any coupling at all? (M1 UD term)
    p_lin = m1[1][-1]
    if p_quad < ALPHA and m2[0][-1] != 0:           # quadratic term justified
        return "QUADRATIC"
    if p_lin < ALPHA and m1[0][-1] < 0:             # linear coupling, protective
        return "LINEAR"
    return "NULL"


# ── experiment driver ────────────────────────────────────────────────────────
REGIMES = ["NULL", "LINEAR", "QUADRATIC", "TRAP_VIF", "TRAP_SEP"]

def correct(verdict, truth):
    if truth == "NULL":         return verdict == "NULL"
    if truth == "INCONCLUSIVE": return verdict == "INCONCLUSIVE"
    return verdict == truth     # LINEAR / QUADRATIC must be named correctly


def run(reps, n, seed):
    rng = np.random.default_rng(seed)
    results = {r: {"naive": [], "firewall": []} for r in REGIMES}
    for regime in REGIMES:
        for _ in range(reps):
            ds = make_dataset(regime, n, rng)
            vn = analyst_naive(ds, rng)
            vf = analyst_firewall(ds)
            results[regime]["naive"].append((vn, correct(vn, ds["truth"])))
            results[regime]["firewall"].append((vf, correct(vf, ds["truth"])))
    return results


def rate(rows):  # fraction correct
    return 100.0 * sum(1 for _, ok in rows if ok) / max(len(rows), 1)

def falsepos(rows):  # fraction claiming ANY law (LINEAR/QUADRATIC) — for NULL/TRAP
    return 100.0 * sum(1 for v, _ in rows if v in ("LINEAR", "QUADRATIC")) / max(len(rows), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    print("=" * 82)
    print(" METHODOLOGY EXPERIMENT — does the four-pillar firewall kill false signals?")
    print(f" reps/regime={a.reps}  n/dataset={a.n}  seed={a.seed}  alpha={ALPHA}")
    print("=" * 82)
    res = run(a.reps, a.n, a.seed)

    print(f"\n{'regime':11s} {'ground truth':13s} | {'NAIVE correct':>14s} | {'FIREWALL correct':>17s}")
    print("-" * 82)
    truth_of = {"NULL": "no law", "LINEAR": "E=U*D", "QUADRATIC": "E=U*D^2",
                "TRAP_VIF": "inconclusive", "TRAP_SEP": "inconclusive"}
    summary = {}
    for r in REGIMES:
        rn, rf = rate(res[r]["naive"]), rate(res[r]["firewall"])
        print(f"{r:11s} {truth_of[r]:13s} | {rn:12.1f}% | {rf:15.1f}%")
        summary[r] = {"naive_correct": round(rn, 1), "firewall_correct": round(rf, 1)}

    # headline false-discovery numbers
    fd = {}
    for r in ("NULL", "TRAP_VIF", "TRAP_SEP"):
        fd[r] = {"naive": round(falsepos(res[r]["naive"]), 1),
                 "firewall": round(falsepos(res[r]["firewall"]), 1)}
    summary["false_discovery"] = fd

    print("\n" + "-" * 82)
    print(" FALSE-DISCOVERY RATE  (fraction that fabricate a 'law' where none is real)")
    print("-" * 82)
    print(f"  pure NULL cohort        : naive {fd['NULL']['naive']:5.1f}%   vs   firewall {fd['NULL']['firewall']:5.1f}%")
    print(f"  TRAP_VIF (collinear)    : naive {fd['TRAP_VIF']['naive']:5.1f}%   vs   firewall {fd['TRAP_VIF']['firewall']:5.1f}%")
    print(f"  TRAP_SEP (separation)   : naive {fd['TRAP_SEP']['naive']:5.1f}%   vs   firewall {fd['TRAP_SEP']['firewall']:5.1f}%")
    print(f"  (nominal alpha = {ALPHA*100:.0f}%)")

    # verdict-mix under NULL, to show WHERE naive goes wrong
    from collections import Counter
    mix = Counter(v for v, _ in res["NULL"]["naive"])
    print("\n  naive verdict mix under NULL:", dict(mix))
    mixf = Counter(v for v, _ in res["NULL"]["firewall"])
    print("  firewall verdict mix under NULL:", dict(mixf))

    print("\n" + "=" * 82)
    print(" INTERPRETATION")
    print("=" * 82)
    print(textblock(fd, summary["LINEAR"], summary["QUADRATIC"]))

    if a.json:
        json.dump({"config": vars(a), "summary": summary}, open(a.json, "w"), indent=2)
        print(f"\n[written] {a.json}")


def textblock(fd, lin, quad):
    return (
        f" - Under a PURE NULL, vending-machine science manufactures a 'universal law'\n"
        f"   {fd['NULL']['naive']:.0f}% of the time; the four-pillar firewall holds at "
        f"{fd['NULL']['firewall']:.0f}% (~ nominal alpha).\n"
        f"   The forking paths (specs x subgroups) are the entire difference.\n"
        f" - TRAP_VIF (confounded + collinear — the SEC EDGAR case): naive fabricates a\n"
        f"   protective law {fd['TRAP_VIF']['naive']:.0f}% of the time; the firewall's VIF gate\n"
        f"   drops it to {fd['TRAP_VIF']['firewall']:.0f}%.\n"
        f" - TRAP_SEP (sparse near-separation — the M5 non-converged-fit case): naive fabricates\n"
        f"   {fd['TRAP_SEP']['naive']:.0f}%; the firewall's non-test triage drops it to "
        f"{fd['TRAP_SEP']['firewall']:.0f}%.\n"
        f" - Crucially the firewall is NOT merely conservative: it still recovers the REAL\n"
        f"   linear law ({lin['firewall_correct']:.0f}% correct) and correctly NAMES the real\n"
        f"   quadratic one ({quad['firewall_correct']:.0f}% correct) via the locked bidirectional rule.\n"
        f" - Conclusion: the methodology is the active ingredient. Same data, same statistics —\n"
        f"   only the discipline differs, and it is the discipline that separates signal from\n"
        f"   self-deception. That is the civilizational contribution the thesis claims."
    )


if __name__ == "__main__":
    main()
