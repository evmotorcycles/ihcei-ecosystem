#!/usr/bin/env python3
"""
govphys_quadratic_prereg_test.py
================================
Pre-registered, falsifiable test of the quadratic governance hypothesis
    E = U * D^2     vs the linear constitutive relation     E = U * D
on real GitHub data, using an enablement-based two-hop D with a VIF gate.

>>> THIS DOCSTRING IS THE PRE-REGISTRATION. Do not edit thresholds or variable
>>> definitions after the first data fetch. At runtime the script prints a
>>> SHA-256 hash of this specification block; commit that hash (and
>>> PREREGISTRATION.md) BEFORE running, to lock the design.

UNIT OF ANALYSIS: one public GitHub repository.

OUTCOME  E  (measured, non-circular):
    E = 0 (failed)   if repo.archived == True
                     OR no push in > 24 months at query date
    E = 1 (survived) otherwise.
    Derived from repo lifecycle metadata; independent of D and tau_v.

ENCODING FIDELITY  D_enc in [0,1]  (the node's OWN output quality):
    mean TF-IDF (1-2 gram) cosine similarity of up to 100 recent commit
    messages to the locked OQM_REFERENCE corpus, x4 stretch, clipped [0,1].

ENABLEMENT / DECODING FIDELITY  D_dec in [0,1]  (measured on OTHERS):
    D_dec = mean(outsider_merge_rate, contribution_spread)
      outsider_merge_rate = merged PRs by non-core authors
                            / total PRs by non-core authors
        non-core := author_association in {CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR,
                                           FIRST_TIMER, MANNEQUIN, NONE}
      contribution_spread = 1 - Gini(contributions across contributors)
    Both measure how much the repo raises/distributes OTHERS' capacity to
    contribute -> structurally independent of D_enc, which is what gives the
    two-hop channel its chance at low VIF.

CAPACITY UTILITY  U = log(1 + n_contributors) * log(1 + n_commits_sampled)

ENFORCEMENT LATENCY  tau_v  (Third Law; reported SEPARATELY, never in D):
    mean(days created_at -> closed_at) over closed NON-PR issues, capped 365.
    If no measurable closed issue, tau_v IMPUTED = 30.0 and flagged.
    Imputed fractions are reported per group (failed vs survived).

SAMPLING (pre-registered queries; dedupe by full_name; seed = 42):
    S1 thriving : language:python stars:>1000 pushed:>2024-06-01
    S2 aging    : language:python stars:100..1000 pushed:2022-01-01..2023-12-31
    S3 at-risk  : language:python stars:10..100 pushed:<2022-01-01
    S4 failed   : language:python archived:true stars:>10
    Target ~250/stratum; require N_total >= 1000, N_fail >= 100.

VIF GATE (channel-intact requirement):
    VIF(D_enc, D_dec) = 1/(1 - r^2), r = Pearson(D_enc, D_dec).
    VIF >= 5 -> CHANNEL COLLAPSE: hops redundant, quadratic test INCONCLUSIVE.

ANALYSIS (logistic regression, AIC):
    PRIMARY (framework's literal claim); D scaled to [0,1] by empirical min-max:
        M_lin  : logit(E) = b0 + b1*(U*D_s)
        M_quad : logit(E) = b0 + b1*(U*D_s^2)
        dAIC = AIC(M_lin) - AIC(M_quad)        ( >0 favours quadratic )
        permutation null: permute D_s 1000x (seed 42) -> z-score of dAIC.
    SECONDARY (scale-robust curvature); D on natural [0,1]:
        M0: b0+b1U ; M1: +b2*D ; M2: +b3*D^2

DECISION RULE (pre-committed, BOTH directions; thresholds LOCKED):
    A verdict on the quadratic requires N_fail >= 100 AND VIF < 5.
    QUADRATIC SUPPORTED    iff dAIC > 10  AND permutation z > 3.
    QUADRATIC DISCONFIRMED  iff dAIC <= 0.
    INCONCLUSIVE           iff VIF >= 5, or 0 < dAIC <= 10, or N_fail < 100.
"""

import os, sys, time, math, json, hashlib, datetime, re
import numpy as np

import requests
from scipy.stats import mannwhitneyu
import statsmodels.api as sm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

np.seterr(all="ignore")
SEED = 42

# ── Locked OQM reference (pre-registered; do not modify) ─────────────────────
OQM_REFERENCE = [
    "The methodology is documented and independently verifiable.",
    "Added verification step before executing the main operation.",
    "Refactored with explicit error handling and rollback procedure.",
    "This change was reviewed against the specification document.",
    "Added tests that verify the expected behavior explicitly.",
    "All claims are falsifiable and the counter-case is documented.",
    "Options considered: A, B, C. Selected A because of the stated reason.",
    "Source reference verified against an independent source.",
    "Fix: closes issue with documented root cause and verification.",
    "Merged after code review, test pass, and documentation update.",
]

STRATA = {
    "S1_thriving": "language:python stars:>1000 pushed:>2024-06-01",
    "S2_aging":    "language:python stars:100..1000 pushed:2022-01-01..2023-12-31",
    "S3_at_risk":  "language:python stars:10..100 pushed:<2022-01-01",
    "S4_failed":   "language:python archived:true stars:>10",
}
PER_STRATUM = 250
NON_CORE = {"CONTRIBUTOR", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "MANNEQUIN", "NONE"}

# Decision thresholds (LOCKED)
T_DAIC_SUPPORT = 10.0
T_PERM_Z       = 3.0
T_VIF_MAX      = 5.0
T_MIN_FAIL     = 100
T_MIN_TOTAL    = 1000


def spec_hash() -> str:
    return hashlib.sha256(__doc__.encode()).hexdigest()


# ── GitHub client ────────────────────────────────────────────────────────────
class GH:
    BASE = "https://api.github.com"

    def __init__(self, token):
        self.s = requests.Session()
        self.s.headers.update({"Accept": "application/vnd.github+json"})
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url, params=None):
        for attempt in range(4):
            r = self.s.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 429):
                reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(2, reset - time.time()) + 2
                print(f"    rate-limited; sleeping {wait:.0f}s", flush=True)
                time.sleep(min(wait, 900))
                continue
            return r
        return r

    def search(self, query, n):
        out, page = [], 1
        while len(out) < n and page <= 10:
            r = self._get(f"{self.BASE}/search/repositories",
                          {"q": query, "sort": "stars", "order": "desc",
                           "per_page": 100, "page": page})
            items = r.json().get("items", []) if r.status_code == 200 else []
            if not items:
                break
            out.extend(items)
            page += 1
            time.sleep(2)
        return out[:n]

    def list(self, owner, name, path, params):
        r = self._get(f"{self.BASE}/repos/{owner}/{name}/{path}", params)
        d = r.json() if r.status_code == 200 else []
        return d if isinstance(d, list) else []


def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    return float((2 * np.sum((np.arange(1, n + 1)) * x) / (n * x.sum())) - (n + 1) / n)


def d_enc_tfidf(messages):
    msgs = [m.strip() for m in messages if m and m.strip()]
    if not msgs:
        return 0.0
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        M = vec.fit_transform(OQM_REFERENCE + msgs)
        ref = np.asarray(M[:len(OQM_REFERENCE)].mean(axis=0))
        sims = cosine_similarity(M[len(OQM_REFERENCE):], ref).ravel()
        return float(np.clip(np.mean(sims) * 4.0, 0.0, 1.0))
    except Exception:
        return 0.0


def d_dec_enablement(pulls, contributors):
    nc = [p for p in pulls if (p.get("author_association") or "NONE").upper() in NON_CORE]
    if nc:
        merged = sum(1 for p in nc if p.get("merged_at"))
        outsider_merge_rate = merged / len(nc)
    else:
        outsider_merge_rate = 0.0
    contribs = [c.get("contributions", 0) for c in contributors]
    spread = 1.0 - gini(contribs) if contribs else 0.0
    return float(np.clip(np.mean([outsider_merge_rate, spread]), 0.0, 1.0))


def compute_tau_v(issues):
    lat = []
    for it in issues:
        if it.get("pull_request"):           # exclude PRs (GH lists them as issues)
            continue
        c, z = it.get("created_at"), it.get("closed_at")
        if c and z and it.get("state") == "closed":
            try:
                t0 = datetime.datetime.fromisoformat(c.replace("Z", "+00:00"))
                t1 = datetime.datetime.fromisoformat(z.replace("Z", "+00:00"))
                lat.append(min(365.0, max(0.0, (t1 - t0).total_seconds() / 86400)))
            except Exception:
                pass
    if lat:
        return float(np.mean(lat)), False
    return 30.0, True                         # imputed, flagged


def failed(repo):
    if repo.get("archived"):
        return 0
    p = repo.get("pushed_at", "")
    if p:
        try:
            pushed = datetime.datetime.fromisoformat(p.replace("Z", "+00:00"))
            months = (datetime.datetime.now(datetime.timezone.utc) - pushed).days / 30.44
            if months > 24:
                return 0
        except Exception:
            pass
    return 1


def aic_logit(y, X):
    X = sm.add_constant(X, has_constant="add")
    try:
        m = sm.Logit(y, X).fit(disp=0, maxiter=200)
        return float(m.aic), float(m.llf)
    except Exception:
        return float("nan"), float("nan")


def run(token, out_csv, out_json):
    print("=" * 68)
    print("GovPhys Quadratic Pre-Registered Test  |  E=U*D vs E=U*D^2")
    print(f"Spec SHA-256: {spec_hash()}")
    print("=" * 68, flush=True)
    gh = GH(token)

    # ── fetch ──
    repos, seen = [], set()
    for sname, q in STRATA.items():
        print(f"[fetch] {sname}: {q}", flush=True)
        for r in gh.search(q, PER_STRATUM):
            fn = r.get("full_name")
            if fn and fn not in seen:
                seen.add(fn)
                r["_stratum"] = sname
                repos.append(r)
    print(f"[fetch] {len(repos)} unique repositories", flush=True)

    rows = []
    for i, repo in enumerate(repos):
        owner = repo["owner"]["login"]; name = repo["name"]
        if i % 25 == 0:
            print(f"  metrics {i}/{len(repos)} ({len(rows)} ok)", flush=True)
        try:
            commits = gh.list(owner, name, "commits", {"per_page": 100})
            pulls   = gh.list(owner, name, "pulls", {"state": "all", "per_page": 100})
            issues  = gh.list(owner, name, "issues", {"state": "closed", "per_page": 100})
            contrib = gh.list(owner, name, "contributors", {"per_page": 100, "anon": "false"})
            msgs = [c.get("commit", {}).get("message", "") for c in commits if c.get("commit")]
            tau, imputed = compute_tau_v(issues)
            D_enc = d_enc_tfidf(msgs)
            D_dec = d_dec_enablement(pulls, contrib)
            U = math.log1p(max(len(contrib), 1)) * math.log1p(max(len(commits), 1))
            rows.append({
                "repo": f"{owner}/{name}", "stratum": repo["_stratum"],
                "E": failed(repo), "U": U, "D_enc": D_enc, "D_dec": D_dec,
                "D": D_enc * D_dec, "tau_v": tau, "tau_v_imputed": int(imputed),
                "stars": repo.get("stargazers_count", 0),
                "archived": int(bool(repo.get("archived"))),
            })
        except Exception:
            pass
        time.sleep(0.7)

    import csv
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"[save] per-repo data -> {out_csv}  (N={len(rows)})", flush=True)

    E   = np.array([r["E"] for r in rows])
    U   = np.array([r["U"] for r in rows], float)
    Den = np.array([r["D_enc"] for r in rows], float)
    Dde = np.array([r["D_dec"] for r in rows], float)
    D   = np.array([r["D"] for r in rows], float)
    n_fail = int((1 - E).sum()); n_surv = int(E.sum())

    # ── VIF gate ──
    r_pear = float(np.corrcoef(Den, Dde)[0, 1]) if len(rows) > 2 else 0.0
    vif = 1.0 / (1.0 - r_pear ** 2) if abs(r_pear) < 0.9999 else float("inf")

    # ── PRIMARY: framework forms with min-max scaled D ──
    rng = D.max() - D.min()
    Ds = (D - D.min()) / rng if rng > 0 else D * 0
    aic_lin, _  = aic_logit(E, (U * Ds).reshape(-1, 1))
    aic_quad, _ = aic_logit(E, (U * Ds ** 2).reshape(-1, 1))
    dAIC = aic_lin - aic_quad

    rng_obj = np.random.default_rng(SEED)
    null = []
    for _ in range(1000):
        Dp = rng_obj.permutation(Ds)
        al, _ = aic_logit(E, (U * Dp).reshape(-1, 1))
        aq, _ = aic_logit(E, (U * Dp ** 2).reshape(-1, 1))
        if np.isfinite(al) and np.isfinite(aq):
            null.append(al - aq)
    perm_z = float((dAIC - np.mean(null)) / max(np.std(null), 1e-6)) if null else 0.0

    # ── SECONDARY: scale-robust nested curvature ──
    a0, _ = aic_logit(E, U.reshape(-1, 1))
    a1, _ = aic_logit(E, np.column_stack([U, D]))
    a2, _ = aic_logit(E, np.column_stack([U, D, D ** 2]))

    # ── Third Law (separate), with imputation accounting ──
    tau = np.array([r["tau_v"] for r in rows], float)
    imp = np.array([r["tau_v_imputed"] for r in rows])
    tf, ts = tau[E == 0], tau[E == 1]
    def mw(a, b, alt):
        try: return float(mannwhitneyu(a, b, alternative=alt).pvalue)
        except Exception: return float("nan")
    p_one_all = mw(tf, ts, "greater"); p_two_all = mw(tf, ts, "two-sided")
    m = imp == 0
    tf_m, ts_m = tau[(E == 0) & m], tau[(E == 1) & m]
    p_one_meas = mw(tf_m, ts_m, "greater")
    imp_fail = float(imp[E == 0].mean()) if n_fail else 0.0
    imp_surv = float(imp[E == 1].mean()) if n_surv else 0.0

    # ── verdict (LOCKED rule) ──
    gate_ok = (n_fail >= T_MIN_FAIL) and (vif < T_VIF_MAX)
    if not gate_ok:
        verdict = "INCONCLUSIVE"
        why = (f"gate not met (N_fail={n_fail}>={T_MIN_FAIL}? VIF={vif:.2f}<{T_VIF_MAX}?)")
    elif dAIC > T_DAIC_SUPPORT and perm_z > T_PERM_Z:
        verdict = "QUADRATIC_SUPPORTED"; why = f"dAIC={dAIC:.2f}>10 and z={perm_z:.2f}>3"
    elif dAIC <= 0:
        verdict = "QUADRATIC_DISCONFIRMED"; why = f"dAIC={dAIC:.2f}<=0 (linear >= quadratic)"
    else:
        verdict = "INCONCLUSIVE"; why = f"weak: 0<dAIC={dAIC:.2f}<=10 or z={perm_z:.2f}<=3"

    summary = {
        "spec_sha256": spec_hash(), "seed": SEED,
        "n_total": len(rows), "n_fail": n_fail, "n_surv": n_surv,
        "pearson_Denc_Ddec": round(r_pear, 4), "VIF": round(vif, 4),
        "primary_aic_lin": round(aic_lin, 3), "primary_aic_quad": round(aic_quad, 3),
        "primary_dAIC_quad_minus_lin": round(dAIC, 3), "permutation_z": round(perm_z, 3),
        "secondary_aic_null": round(a0, 3), "secondary_aic_lin": round(a1, 3),
        "secondary_aic_quad": round(a2, 3),
        "secondary_dAIC_quad_vs_lin": round(a1 - a2, 3),
        "thirdlaw_tau_fail_mean": round(float(np.mean(tf)) if len(tf) else 0, 2),
        "thirdlaw_tau_surv_mean": round(float(np.mean(ts)) if len(ts) else 0, 2),
        "thirdlaw_p_one_tailed_all": round(p_one_all, 4),
        "thirdlaw_p_two_tailed_all": round(p_two_all, 4),
        "thirdlaw_p_one_tailed_measured_only": round(p_one_meas, 4),
        "thirdlaw_imputed_frac_failed": round(imp_fail, 3),
        "thirdlaw_imputed_frac_survived": round(imp_surv, 3),
        "VERDICT": verdict, "verdict_reason": why,
    }
    cert = "GOVPHYS-QUAD-" + hashlib.sha256(
        (spec_hash() + json.dumps(summary, sort_keys=True)).encode()).hexdigest()[:12].upper()
    summary["certificate_id"] = cert
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 68)
    print(f"N={len(rows)}  fail={n_fail}  surv={n_surv}")
    print(f"VIF(D_enc,D_dec)={vif:.2f}  (gate <{T_VIF_MAX})   r={r_pear:+.3f}")
    print(f"PRIMARY dAIC(quad-lin)={dAIC:+.2f}  perm z={perm_z:+.2f}")
    print(f"SECONDARY nested dAIC(quad-lin)={a1 - a2:+.2f}")
    print(f"Third Law: tau_fail={summary['thirdlaw_tau_fail_mean']} "
          f"tau_surv={summary['thirdlaw_tau_surv_mean']} "
          f"p1(all)={p_one_all:.4f} p1(measured)={p_one_meas:.4f} "
          f"imputed fail/surv={imp_fail:.2f}/{imp_surv:.2f}")
    print(f"\nVERDICT: {verdict}  ({why})")
    print(f"Certificate: {cert}")
    print(f"Summary -> {out_json}")
    print("=" * 68, flush=True)
    return summary


if __name__ == "__main__":
    tok = os.environ.get("GITHUB_TOKEN", "")
    if not tok:
        print("Set GITHUB_TOKEN (a PAT with public_repo scope is recommended for volume).")
        sys.exit(1)
    run(tok, "govphys_quadratic_results.csv", "govphys_quadratic_summary.json")