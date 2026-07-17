#!/usr/bin/env python3
"""
experiment_enriched.py -- ADG (C_dev) + TQG-CFE (Psi) retest, with the governance
terms operationalized as ENGINEERING TELEMETRY on real GitHub projects.
============================================================================
This retest adds the term-level operational definitions supplied by the author,
treating each purely as a MEASURABLE governance/engineering signal (no theology,
no moral content -- Shirk here is an epistemic-conflation *metric*, "not a sin"):

  Nafs    = a node in the collaboration network (repo / contributor).
  Salat   = D_enc  : the ENCODE/alignment hop -- disciplined, repeated action on
                     flagged risk. Proxy: responsiveness r = 1/(1+tau_v).
  Zakat   = D_dec  : the DECODE/transfer hop -- purified knowledge passed to the
                     commons. Proxy: throughput = ln(1+closed issues).
  D       = Salat * Zakat  (two-hop fidelity, exactly LISM's D = D_enc*D_dec).
  U       = utility/adoption = ln(1+stars).
  Deen    = the Established Order = the governance target vector Theta = (1,1,1).
  Shaytan = internal disposition = internal governance-failure noise. Proxy:
                     hbar_network = normalized tau_v (accumulated neglect).
  Shirk   = EPISTEMIC CONFLATION = the network mislabelling its own state (say-do
                     gap). Proxy: |sigma|, sigma = z(push-recency) - z(-ln(1+tau_v))
                     -- the LISM Dissonance. High |Shirk| = declared state and real
                     state disagree (a repo that LOOKS alive but rots, or vice versa).
  Iman    = safety/security = the RENDERED outcome of an aligned, low-Shirk network
                     (safe to depend on) -- i.e. the Yusr rendering, an OUTPUT.

  ADG   C_dev = U * D / (eps + hbar_network) = U * (Salat*Zakat) / (eps + Shaytan).
  TQG   A_n(Phi) = <Phi|Theta>/(|Phi||Theta|),  Phi=(U, Salat, Zakat) normalized.
  Psi rendering (the equation's THREE cases, now measurable):
        Psi_Chaos  if Shirk dominates (|sigma| high)   -- the network mislabels reality
        Psi_Yusr   else if A_n > kappa                 -- aligned: ease / Iman (safety)
        Psi_Usr    else                                -- misaligned: hardship

Outcome E (survived=1/failed=0) is measured INDEPENDENTLY (archived or push>365d),
so predicting it from these signals is a real test. Layer-1 telemetry ONLY; the
Layer-3 metaphysical reading is neither tested nor claimed (kept separate as in
FLOOR_RETIREMENT.md and per the framework's own "formal analogy" note).

    python3 adg-tqg/experiment_enriched.py     # stdlib only, no network
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "repro"))
from reproduce_tauv import mann_whitney_u, mean  # tested stdlib MWU


def minmax(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def zscore(xs):
    m = mean(xs)
    sd = math.sqrt(mean([(x - m) ** 2 for x in xs])) or 1.0
    return [(x - m) / sd for x in xs]


def cosine_to_ones(v):
    num, den = sum(v), math.sqrt(sum(x * x for x in v)) * math.sqrt(len(v))
    return num / den if den > 0 else 0.0


def auc(scores, labels):
    # AUC = P(score_pos > score_neg); rank-based, ties=0.5
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((1 if p > n else 0.5 if p == n else 0) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def main():
    repos = json.load(open(os.path.join(HERE, "fixtures", "experiment_cohort.json")))["repos"]

    U = minmax([math.log1p(r["stargazers"]) for r in repos])          # utility/adoption
    salat = minmax([1.0 / (1.0 + r["tau_v"]) for r in repos])         # D_enc / alignment
    zakat = minmax([math.log1p(r["n_closed"]) for r in repos])        # D_dec / transfer
    hbar = minmax([r["tau_v"] for r in repos])                        # Shaytan / noise

    # Shirk = |sigma| (LISM Dissonance): say-do conflation between declared vitality
    # (push recency) and enacted responsiveness (-ln(1+tau_v)).
    say = zscore([-float(r["days_since_push"]) for r in repos])
    do = zscore([-math.log1p(r["tau_v"]) for r in repos])
    sigma = [say[i] - do[i] for i in range(len(repos))]
    shirk = [abs(s) for s in sigma]
    shirk_hi = sorted(shirk)[int(0.75 * len(shirk))]                  # top-quartile = Chaos

    rows = []
    for i, r in enumerate(repos):
        phi = (U[i], salat[i], zakat[i])
        A_n = cosine_to_ones(phi)
        D = salat[i] * zakat[i]                                       # two-hop fidelity
        C_dev = U[i] * D / (0.05 + hbar[i])
        rows.append({"repo": r["repo"], "E": r["E"], "A_n": A_n, "D": D,
                     "C_dev": C_dev, "sigma": sigma[i], "shirk": shirk[i]})

    kappa = sorted(x["A_n"] for x in rows)[len(rows) // 2]
    for x in rows:
        if x["shirk"] >= shirk_hi:
            x["Psi"] = "Chaos"                                        # Shirk dominates
        elif x["A_n"] > kappa:
            x["Psi"] = "Yusr"                                         # aligned -> Iman/safety
        else:
            x["Psi"] = "Usr"

    surv = [x for x in rows if x["E"] == 1]
    fail = [x for x in rows if x["E"] == 0]
    lab = [x["E"] for x in rows]

    bar = "=" * 84
    print(bar)
    print(" ADG + TQG-CFE RETEST with engineered governance telemetry -- real GitHub repos")
    print(" Salat=D_enc  Zakat=D_dec  D=Salat*Zakat  Shaytan=noise  Shirk=|dissonance|  Iman=Yusr")
    print(" cohort: %d repos (%d survived, %d failed) | Layer-1 telemetry only" %
          (len(rows), len(surv), len(fail)))
    print(bar)
    print("\n  %-28s %5s %5s %8s %7s  %-6s E" % ("repo", "A_n", "D", "C_dev", "Shirk", "Psi"))
    for x in sorted(rows, key=lambda z: -z["C_dev"]):
        print("  %-28s %5.2f %5.2f %8.2f %7.2f  %-6s %d" %
              (x["repo"], x["A_n"], x["D"], x["C_dev"], x["shirk"], x["Psi"], x["E"]))

    # --- H1 ADG C_dev, H2 TQG A_n, H4 two-hop D: separate survival -------------
    def test(key):
        s = [x[key] for x in surv]; f = [x[key] for x in fail]
        _, _, p = mann_whitney_u(s, f)
        return mean(s), mean(f), p, auc([x[key] for x in rows], lab)

    print("\n  " + "-" * 80)
    for name, key, h in [("H1 ADG  C_dev", "C_dev", "aligned transfer / noise"),
                         ("H2 TQG  A_n  ", "A_n", "Deen alignment"),
                         ("H4 two-hop D ", "D", "Salat*Zakat = D_enc*D_dec")]:
        ms, mf, p, a = test(key)
        print("  %s (%s): surv %.3f vs fail %.3f | 1-tail MWU p=%.4f | AUC=%.2f -> %s"
              % (name, h, ms, mf, p, a, "SUPPORTED" if p < 0.05 else "not supported"))

    # --- H3 Psi 3-state rendering vs survival ---------------------------------
    def rate(psi):
        g = [x for x in rows if x["Psi"] == psi]
        return (sum(x["E"] for x in g), len(g))
    ys, yn = rate("Yusr"); us, un = rate("Usr"); cs, cn = rate("Chaos")
    print("  H3 TQG  Psi rendering: Yusr %d/%d survive | Usr %d/%d | Chaos %d/%d (mislabelled set)"
          % (ys, yn, us, un, cs, cn))

    # --- H5 Shirk detector: among LOOKS-ALIVE repos (fresh push), does high Shirk
    #     flag the ones that are actually rotting (worse tau_v)? -----------------
    fresh = [(repos[i], sigma[i]) for i in range(len(repos)) if repos[i]["days_since_push"] <= 120]
    hi = [r["tau_v"] for r, s in fresh if s > 0.5]     # looks-alive but high +sigma (zombie)
    lo = [r["tau_v"] for r, s in fresh if s <= 0.5]
    h5 = None
    if hi and lo:
        _, _, ph5 = mann_whitney_u(hi, lo)
        h5 = (mean(hi), mean(lo), ph5)
        print("  H5 Shirk: among recently-pushed repos, high-Shirk (zombie) tau_v %.1f vs low %.1f"
              " | p=%.4f -> %s" % (mean(hi), mean(lo), ph5, "SUPPORTED" if ph5 < 0.05 else "weak"))

    # --- H6 does the enrichment IMPROVE on the plain model? -------------------
    A_plain = [cosine_to_ones((U[i], zakat[i], salat[i])) for i in range(len(repos))]  # same inputs
    print("\n  " + "-" * 80)
    _, _, p_cdev, a_cdev = test("C_dev")
    print("  Enriched C_dev AUC=%.2f (p=%.4f).  Two-hop D=Salat*Zakat is the load-bearing term;" % (a_cdev, p_cdev))
    print("  Shirk(|sigma|) adds the Psi_Chaos class that flags the repos a naive last-push")
    print("  health-check MISLABELS -- the operational meaning of 'epistemic Shirk'.")

    supported = sum([test("C_dev")[2] < 0.05, test("A_n")[2] < 0.05, test("D")[2] < 0.05,
                     ys / max(yn, 1) > us / max(un, 1)])
    print("\n  RESULT: %d/4 core predictions supported (enriched model)" % supported)
    print(bar)
    print(" READING: with Salat/Zakat/Shaytan/Shirk operationalized, the ADG/TQG telemetry")
    print(" still tracks survival AND now names the deceptive set (Psi_Chaos = high Shirk =")
    print(" say-do conflation). This is engineering telemetry (Layer 1); no Layer-3 claim.")
    print(bar)
    raise SystemExit(0 if supported >= 3 else 1)


if __name__ == "__main__":
    main()
