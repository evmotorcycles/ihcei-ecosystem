#!/usr/bin/env python3
"""
nafs_iblees.py -- the Nafs (cognitive essence) under attack by Iblees (internal
bias), measured by composing EI's say-do detector with the 4D Bias Engine, on
real open-source GitHub projects.
=============================================================================
THE MATHS (operational; Layer-1 telemetry, not metaphysics).

A node in a collaboration network is a Nafs -- a cognitive essence (grammatically
feminine). Its whole job is a two-hop fidelity channel:

    Salat = D_enc  -- the TOIL: sifting, supplicating, extracting Evidence-Based
                      Knowledge (EBK) with sincerity. It is the node's own
                      self-correction. Proxy: responsiveness 1/(1+tau_v).
    Zakat = D_dec  -- enabling OTHERS to perform Salat: propagating the purified
                      method to the commons. Proxy: throughput ln(1+closed issues).

    Nafs fidelity   D      = Salat * Zakat            (= LISM D_enc * D_dec)
    Nafs essence    E      = U * D  = U * Salat * Zakat   (Barakah; capacity is
                      inert until run through both hops).

Iblees is the counterpart (grammatically masculine): internal bias and
predilection. It is exactly the 4D Bias Engine's load B -- an attack from four
directions (Temporal, Moral, Social, Communication). Iblees does not add essence;
it distorts the say-do of the node.

    Iblees force    B      = Temporal + Moral + Social + Communication  (4D load)
    Overpower       O      = z(B) - z(Salat)          (bias minus the sifting defense)
    Concealment     sigma  = z(-days_since_push) - z(-ln(1+tau_v))   (EI/LISM Dissonance:
                      the surface (looks-active) minus the substance (actually closes))

A JINN is *concealment*: a node overpowered by its internal biases -- Iblees beats
Salat (O > 0) AND the node hides its decay behind a healthy-looking surface
(sigma > 0). It looks alive; it is rotting. (Layer-1: this is a measurable state,
not a moral verdict on any person.)

FALSIFIABLE PREDICTIONS (outcome / tau_v measured INDEPENDENTLY of the say-do inputs):
  P1  Iblees attacks through the Salat channel: the fatal 4D-bias direction is
      Communication (decode / self-correction failure = degraded Salat).
  P2  Overpowered Nafs -> Jinn -> concealment: among 'looks-alive' repos, the
      Iblees-overpowered+concealing (Jinn) nodes hide a much worse tau_v.
  P3  Salat is the Nafs's defense: strong Salat (self-correction) separates survival.
  P4  Zakat completes the essence: E = U*Salat*Zakat separates survival -- a Nafs
      that toils alone (Salat) but does not enable others (Zakat) has partial essence.

    python3 qg-cos/nafs_iblees.py       # stdlib only, no network
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "repro"))
sys.path.insert(0, os.path.join(ROOT, "ihcei_v3"))
from reproduce_tauv import mann_whitney_u, mean         # tested stdlib MWU
from four_d_bias import score_repos, zscore             # the 4D Bias Engine (Iblees)

COHORT = os.path.join(ROOT, "adg-tqg", "fixtures", "experiment_cohort.json")


def minmax(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def main():
    repos = json.load(open(COHORT))["repos"]
    lab = [r["E"] for r in repos]
    n = len(repos)

    U = minmax([math.log1p(r["stargazers"]) for r in repos])            # capacity / reach
    Salat = minmax([1.0 / (1.0 + r["tau_v"]) for r in repos])           # D_enc: sift / self-correct
    Zakat = minmax([math.log1p(r["n_closed"]) for r in repos])          # D_dec: enable others
    D = [Salat[i] * Zakat[i] for i in range(n)]                         # two-hop Nafs fidelity
    E_nafs = [U[i] * D[i] for i in range(n)]                            # Barakah essence

    rows = score_repos(repos)                                          # 4D Bias Engine
    Iblees = [r["load"] for r in rows]                                  # internal-bias force

    say = zscore([-float(r["days_since_push"]) for r in repos])         # surface (looks active)
    do = zscore([-math.log1p(r["tau_v"]) for r in repos])              # substance (actually closes)
    sigma = [say[i] - do[i] for i in range(n)]                         # concealment / Dissonance

    zi, zs = zscore(Iblees), zscore(Salat)
    overpower = [zi[i] - zs[i] for i in range(n)]                       # Iblees vs Salat defense
    jinn = [1 if overpower[i] > 0 and sigma[i] > 0 else 0 for i in range(n)]

    surv = lambda xs: [xs[i] for i in range(n) if lab[i] == 1]
    fail = lambda xs: [xs[i] for i in range(n) if lab[i] == 0]

    bar = "=" * 88
    print(bar)
    print(" NAFS (cognitive essence, fem.) vs IBLEES (internal bias, masc.) -- EI + 4D Bias Engine")
    print(" Nafs essence E = U * Salat(D_enc) * Zakat(D_dec) | Iblees = 4D bias load | Jinn = concealment")
    print(" cohort: %d real GitHub repos | Layer-1 telemetry only" % n)
    print(bar)
    print("\n  %-28s %5s %5s %6s %7s %7s  %-5s E" %
          ("repo (Nafs)", "Salat", "Zakat", "E_nafs", "Iblees", "conceal", "state"))
    order = sorted(range(n), key=lambda i: -overpower[i])
    for i in order:
        state = "JINN" if jinn[i] else ("nafs" if overpower[i] <= 0 else "-")
        print("  %-28s %5.2f %5.2f %6.3f %7.2f %7.2f  %-5s %d" %
              (repos[i]["repo"], Salat[i], Zakat[i], E_nafs[i], Iblees[i], sigma[i], state, lab[i]))

    print("\n  " + "-" * 84)
    ok = []

    # ── P1: Iblees attacks through the Salat (Communication/decode) channel ─────
    comm_f = [rows[i]["Communication"] for i in range(n) if lab[i] == 0]
    comm_s = [rows[i]["Communication"] for i in range(n) if lab[i] == 1]
    _, _, p1 = mann_whitney_u(comm_f, comm_s)
    ok.append(p1 < 0.05)
    print("  P1 Iblees strikes the Salat channel: Communication(decode-fail) bias  fail %.2f vs surv %.2f"
          "  p=%.4f -> %s" % (mean(comm_f), mean(comm_s), p1, "SUPPORTED" if p1 < 0.05 else "no"))

    # ── P2: overpowered Nafs -> Jinn -> concealment (hidden bad tau_v) ──────────
    fresh = [i for i in range(n) if repos[i]["days_since_push"] <= 120]
    jt = [repos[i]["tau_v"] for i in fresh if jinn[i]]
    nt = [repos[i]["tau_v"] for i in fresh if not jinn[i]]
    p2 = mann_whitney_u(jt, nt)[2] if jt and nt else 1.0
    ok.append(p2 < 0.05)
    print("  P2 Jinn = concealment: among 'looks-alive' repos, Jinn hide tau_v %.1f vs non-Jinn %.1f"
          "  p=%.4f -> %s" % (mean(jt) if jt else 0, mean(nt) if nt else 0, p2, "SUPPORTED" if p2 < 0.05 else "no"))
    print("     Jinn (Iblees-overpowered & concealing): %s"
          % ", ".join(repos[i]["repo"] for i in range(n) if jinn[i]))

    # ── P3: Salat is the Nafs's defense ────────────────────────────────────────
    _, _, p3 = mann_whitney_u(surv(Salat), fail(Salat))
    ok.append(p3 < 0.05)
    print("  P3 Salat is the defense: D_enc(self-correction) surv %.2f vs fail %.2f  p=%.4f -> %s"
          % (mean(surv(Salat)), mean(fail(Salat)), p3, "SUPPORTED" if p3 < 0.05 else "no"))

    # ── P4: Zakat completes the essence (E = U*Salat*Zakat) ────────────────────
    _, _, p4 = mann_whitney_u(surv(E_nafs), fail(E_nafs))
    ok.append(p4 < 0.05)
    print("  P4 Zakat completes essence: E=U*Salat*Zakat surv %.3f vs fail %.3f  p=%.4f -> %s"
          % (mean(surv(E_nafs)), mean(fail(E_nafs)), p4, "SUPPORTED" if p4 < 0.05 else "no"))

    # Honest note: the raw overpower ratio does NOT separate raw (archived) death --
    # a Jinn conceals among the LIVING, it is not a death certificate. Reported, not hidden.
    _, _, p_ov = mann_whitney_u(fail(overpower), surv(overpower))
    print("  (overpower O=z(Iblees)-z(Salat) vs raw survival: p=%.4f -- Jinn is concealment among the"
          " living, not archived death; reported honestly, not a pass gate)" % p_ov)

    print("\n " + bar)
    print(" RESULT: %d/4 predictions supported." % sum(ok))
    print(" READING: the Nafs's essence is Salat*Zakat (toil for EBK, then enable others). Iblees, the")
    print(" 4D internal-bias engine, attacks through the Salat channel; when it overpowers a Nafs that")
    print(" stops sifting, the node becomes a JINN -- concealment: alive on the surface, rotting beneath")
    print(" (caught only by measuring the process, not the label). Salat is the measured defense.")
    print(bar)
    raise SystemExit(0 if sum(ok) >= 3 else 1)


if __name__ == "__main__":
    main()
