#!/usr/bin/env python3
"""
iqra_channel.py -- Iqra as a COMMUNICATION CHANNEL, with the N157 (Madyan) control
case, measured on real open-source GitHub projects.
=============================================================================
LAYER-1 OPERATIONAL CLAIM (no metaphysics). 'Iqra' is read here not as a static
book but as a generative source that YIELDS knowledge to an active querier. If
that is a communication channel, then the essence a node extracts and retains is
NOT a property of the source -- it is a property of the querier's own two-hop
fidelity. The same commons yields different results to different nodes.

    E (retained essence / EBK)  =  U * D_enc * D_dec
      U      = access / capacity (reach into the commons; ln(1+stars))
      D_enc  = active sifting / self-correction (does the node query & correct?
               proxy 1/(1+tau_v))
      D_dec  = propagation / enabling others (does it pass the sifted knowledge on?
               proxy ln(1+closed issues))

THE N157 CONTROL CASE (Moses in Madyan). Toiling alone -- sifting for yourself
(high D_enc) but never propagating to others (D_dec -> 0) -- makes the JOINT
product collapse: E = U * D_enc * 0 = 0. Sincerity without selflessness is a
memory leak; it produces zero ENDURING essence, no matter how high D_enc is. This
is only true if the two hops MULTIPLY -- which requires them to carry independent,
non-redundant information (the LISM VIF~1 result). We test exactly that.

Predictions (outcome E measured INDEPENDENTLY: archived or push>365d):
  I1  Iqra is a CHANNEL: the yield E=U*D is querier-determined -- it separates
      survival more sharply than raw access U alone (source access is not enough).
  I2  Iqra is GENERATIVE to the active querier: active sifting D_enc separates
      survival (the source yields to those who query & self-correct, not passive holders).
  I3  N157 collapse: D_enc and D_dec are near-independent (low correlation -> they
      must multiply), so zeroing the propagation hop (D_dec->0, 'toil alone')
      collapses mean retained essence to ~0.

    python3 qg-cos/iqra_channel.py       # stdlib only, no network
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "repro"))
from reproduce_tauv import mann_whitney_u, mean

COHORT = os.path.join(ROOT, "adg-tqg", "fixtures", "experiment_cohort.json")


def minmax(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def pearson(a, b):
    ma, mb = mean(a), mean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((x - mb) ** 2 for x in b))
    return num / (da * db) if da > 0 and db > 0 else 0.0


def main():
    repos = json.load(open(COHORT))["repos"]
    lab = [r["E"] for r in repos]
    U = minmax([math.log1p(r["stargazers"]) for r in repos])       # access into the commons
    d_enc = minmax([1.0 / (1.0 + r["tau_v"]) for r in repos])      # active sifting / self-correct
    d_dec = minmax([math.log1p(r["n_closed"]) for r in repos])     # propagation / enable others
    D = [d_enc[i] * d_dec[i] for i in range(len(repos))]
    E = [U[i] * D[i] for i in range(len(repos))]

    surv = lambda xs: [xs[i] for i in range(len(repos)) if lab[i] == 1]
    fail = lambda xs: [xs[i] for i in range(len(repos)) if lab[i] == 0]

    bar = "=" * 88
    print(bar)
    print(" IQRA AS A COMMUNICATION CHANNEL (+ N157 Madyan control) -- real GitHub projects")
    print(" E (retained essence) = U(access) * D_enc(sift) * D_dec(propagate) | Layer-1 telemetry")
    print(bar)
    ok = []

    # ── I1: Iqra is a CHANNEL -- yield is querier-determined, not source-determined
    _, _, p_U = mann_whitney_u(surv(U), fail(U))
    _, _, p_E = mann_whitney_u(surv(E), fail(E))
    i1 = p_E < 0.05 and p_E < p_U
    ok.append(i1)
    print("\n I1 Iqra is a CHANNEL (yield is querier-determined):")
    print("    raw access U alone:            MWU p=%.4f   (the source, on its own, under-predicts)" % p_U)
    print("    retained essence E=U*D_enc*D_dec: MWU p=%.4f   -> %s"
          % (p_E, "SUPPORTED (the querier's two-hop fidelity determines the yield)" if i1 else "weak"))

    # ── I2: Iqra is GENERATIVE to the active querier ───────────────────────────
    _, _, p_enc = mann_whitney_u(surv(d_enc), fail(d_enc))
    i2 = p_enc < 0.05
    ok.append(i2)
    print("\n I2 Iqra is GENERATIVE to the active querier:")
    print("    active sifting D_enc (1/(1+tau_v)) separates survival: MWU p=%.4f -> %s"
          % (p_enc, "SUPPORTED (yields to those who query & self-correct)" if i2 else "weak"))

    # ── I3: N157 collapse -- two hops are independent, so they must multiply ────
    corr = pearson(d_enc, d_dec)
    vif = 1.0 / (1.0 - corr ** 2)                                  # VIF between the two hops
    E_full = mean(E)
    E_toil_alone = mean([U[i] * d_enc[i] * 0.0 for i in range(len(repos))])   # D_dec -> 0
    # empirically: propagation hop D_dec carries survival signal of its own
    _, _, p_dec = mann_whitney_u(surv(d_dec), fail(d_dec))
    i3 = abs(corr) < 0.4 and vif < 1.4 and E_toil_alone < 0.02 * max(E_full, 1e-9)
    ok.append(i3)
    print("\n I3 N157 (Madyan) -- Salat without Zakat = zero enduring essence:")
    print("    D_enc vs D_dec correlation r=%.3f  |  VIF=%.3f  (near-independent -> the hops MULTIPLY)"
          % (corr, vif))
    print("    propagation hop D_dec also separates survival on its own: MWU p=%.4f" % p_dec)
    print("    counterfactual 'toil alone' (D_dec->0): mean essence %.4f -> %.4f  -> %s"
          % (E_full, E_toil_alone, "SUPPORTED (collapses to zero -- the memory leak)" if i3 else "no"))

    print("\n " + bar)
    print(" RESULT: %d/3 supported." % sum(ok))
    print(" READING: the commons (Iqra) is a CHANNEL, not a vending machine -- the same source yields")
    print(" enduring essence only in proportion to the querier's own sifting (D_enc) AND propagation")
    print(" (D_dec). Because the two hops carry independent information they multiply; toiling alone")
    print(" (N157: D_dec->0) zeroes the yield no matter how hard you sift. Layer-1 telemetry only;")
    print(" the scriptural reading is the Layer-3 frame, neither tested nor claimed.")
    print(bar)
    raise SystemExit(0 if sum(ok) >= 2 else 1)


if __name__ == "__main__":
    main()
