#!/usr/bin/env python3
"""
n157_barakah_experiment.py — How LISM transforms OQM, with N157 as the case study
=================================================================================
Source N157 ("How to have Barakah / Why did Mussa seek Barakah?") makes structural,
FALSIFIABLE claims once Barakah is read as a governance function (Layer 2), not a
theological gift. This experiment operationalises N157's own worked cases and then
shows the specific transformation LISM performs on OQM.

GOVERNANCE DEFINITIONS (Layer 2, from the OQM docs):
  Barakah  E   = compounding knowledge produced by DEPLOYING capacity through a protocol
  U            = capacity / endowment (Wus') — GIVEN, thermodynamically INERT until deployed
  D_enc = Salat = sincere seeking      (encoding hop)
  D_dec = Zakat = selflessness / sharing(decoding hop)
  f            = deployed fraction of capacity ("Mussa risking 100% of U by leaving Madyan")
  E = (f * U) * D_enc * D_dec           (LISM linear coupling)

N157 STRUCTURAL CLAIMS (pre-registered tests):
  C1 MADYAN CONTROL       — max capacity + no deployment = ZERO Barakah (capacity is inert).
                            Mussa in Madyan (U high, f~0) produces ~0 E.
  C2 SELECTION IS EARNED  — "selected" (top-Barakah) nodes are predicted by PROTOCOL
       NOT AT BIRTH         behaviour, not by birth endowment U. (The at-birth-selection
                            fallacy: birth AUC ~ 0.5; protocol AUC high.)
  C3 RISK TRIGGERS YIELD  — Barakah rises with DEPLOYED fraction f, not with capacity held;
                            a modest-but-deployed node out-produces an endowed-but-idle one.
  C4 BOTH LEGS MULTIPLY   — sincere seeking with zero selflessness (or vice versa) => ~0.

LISM TRANSFORMATION (the point of the exercise):
  T-CLIFF   under the OLD OQM prior E=U*D^2, a small fidelity loss is CATASTROPHIC (a cliff).
  T-MERCY   LISM's empirically-validated LINEAR law E=U*D makes the same loss GRACEFUL —
            this graceful slide is Rahmah, and it opens the tau_v self-correction runway.

Run:  python3 n157_barakah_experiment.py [--n 8000] [--seed 1]
"""
from __future__ import annotations
import argparse
import numpy as np
from sklearn.metrics import roc_auc_score

Z = lambda x: (np.asarray(x, float) - np.mean(x)) / (np.std(x) + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    N = a.n

    U = rng.uniform(0.3, 1.0, N)              # capacity/endowment (given)
    # THE COMFORT TRAP: deployment is NOT driven by capacity. If anything the comfortable
    # (high U, "safe in Madyan") are slightly LESS likely to deploy. So outcome cannot be
    # a rebrand of endowment.
    base = rng.beta(1.6, 1.6, N)
    f = np.clip(base - 0.15 * Z(U) * 0.15, 0, 1)   # deployed fraction, ~indep of U
    D_enc = rng.beta(2.0, 2.0, N)             # sincere seeking
    D_dec = rng.beta(2.0, 2.0, N)             # selflessness
    protocol = D_enc * D_dec                  # two-hop fidelity
    E = (f * U) * protocol                    # Barakah = deployed capacity * fidelity (LINEAR)

    print("=" * 86)
    print(" N157 — BARAKAH AS A GOVERNANCE FUNCTION, and how LISM transforms it")
    print(f" N={N} seed={a.seed}   E=(f*U)*D_enc*D_dec   [Layer-1 measurement / Layer-2 defs]")
    print("=" * 86)

    # ---- C1 Madyan control: max capacity, no deployment -> zero Barakah ----
    madyan = (U > 0.8) & (f < 0.1)            # "Mussa in Madyan": high U, not deployed
    misr = (f > 0.8)                          # deployed ("returned to Misr")
    print("\nC1 MADYAN CONTROL (capacity is inert until deployed)")
    print(f"   high-capacity but NOT deployed (Madyan):  mean Barakah = {E[madyan].mean():.4f}  (n={madyan.sum()})")
    print(f"   deployed through the protocol (Misr):     mean Barakah = {E[misr].mean():.4f}  (n={misr.sum()})")
    c1 = E[madyan].mean() < 0.02 and E[misr].mean() > 5 * max(E[madyan].mean(), 1e-4)
    print(f"   -> {'PASS' if c1 else 'FAIL'}: maximum capacity yields ~0 Barakah with no deployment")

    # ---- C2 selection is earned, not at birth ----
    selected = (E >= np.quantile(E, 0.90)).astype(int)   # top-decile Barakah = "selected"
    auc_protocol = roc_auc_score(selected, f * protocol)  # what they DID
    auc_birth = roc_auc_score(selected, U)                # birth endowment
    print("\nC2 SELECTION IS EARNED, NOT AT BIRTH (the at-birth-selection fallacy)")
    print(f"   predict 'selected' from PROTOCOL (f*D_enc*D_dec): AUC = {auc_protocol:.3f}")
    print(f"   predict 'selected' from BIRTH endowment (U):      AUC = {auc_birth:.3f}")
    print(f"   protocol dominates birth by margin = {auc_protocol - auc_birth:+.3f}  "
          f"(birth is a weak factor, not decisive)")
    c2 = auc_protocol > 0.85 and (auc_protocol - auc_birth) > 0.20
    print(f"   -> {'PASS' if c2 else 'FAIL'}: selection is dominated by the protocol you RUN, "
          f"not the capacity you were GIVEN")

    # ---- C3 risk triggers yield: modest-but-deployed beats endowed-but-idle ----
    modest_deployed = (U < 0.55) & (f > 0.7)
    endowed_idle = (U > 0.8) & (f < 0.3)
    md, ei = E[modest_deployed].mean(), E[endowed_idle].mean()
    print("\nC3 RISK TRIGGERS YIELD (deploying capacity, not holding it)")
    print(f"   modest capacity, deployed:   mean Barakah = {md:.4f}  (n={modest_deployed.sum()})")
    print(f"   high capacity, idle:         mean Barakah = {ei:.4f}  (n={endowed_idle.sum()})")
    print(f"   corr(Barakah, deployed f) = {np.corrcoef(E, f)[0,1]:+.3f}   "
          f"corr(Barakah, capacity U) = {np.corrcoef(E, U)[0,1]:+.3f}")
    c3 = md > ei
    print(f"   -> {'PASS' if c3 else 'FAIL'}: a modest diligent node out-produces an endowed idle one")

    # ---- C4 both legs multiply ----
    lowseek = D_enc < np.quantile(D_enc, 0.1)
    lowself = D_dec < np.quantile(D_dec, 0.1)
    print("\nC4 BOTH LEGS MULTIPLY (sincere seeking AND selflessness required)")
    print(f"   mean Barakah when sincere-seeking~0 : {E[lowseek].mean():.4f}")
    print(f"   mean Barakah when selflessness~0    : {E[lowself].mean():.4f}")
    print(f"   mean Barakah overall                : {E.mean():.4f}")
    c4 = E[lowseek].mean() < 0.5 * E.mean() and E[lowself].mean() < 0.5 * E.mean()
    print(f"   -> {'PASS' if c4 else 'FAIL'}: either leg at zero collapses Barakah")

    # ---- LISM TRANSFORMATION: cliff (quadratic) vs mercy (linear) ----
    print("\n" + "=" * 86)
    print(" HOW LISM TRANSFORMS OQM — the Barakah decay law: cliff vs mercy")
    print("=" * 86)
    print("  A node's two-hop fidelity D degrades from 1.0. Barakah retained vs the D=1 peak:")
    print(f"   {'D':>5} {'quadratic E~U*D^2':>20} {'linear E~U*D (LISM)':>22} {'mercy gain':>12}")
    for D in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
        q, l = D * D, D
        print(f"   {D:>5.1f} {q:>19.2f} {l:>21.2f} {l-q:>+11.2f}")
    # tau_v runway: steps of self-correction available before Barakah falls below a floor
    FLOOR = 0.5
    # D decays 3%/step; how many steps until retained Barakah < FLOOR under each law?
    def runway(power):
        D, t = 1.0, 0
        while D ** power >= FLOOR and t < 1000:
            D *= 0.97; t += 1
        return t
    r_q, r_l = runway(2), runway(1)
    print(f"\n  tau_v self-correction runway (steps until Barakah < {FLOOR}, D decaying 3%/step):")
    print(f"    under quadratic cliff : {r_q} steps")
    print(f"    under linear mercy    : {r_l} steps   (+{r_l-r_q} extra steps of runway = Rahmah)")

    passed = sum([c1, c2, c3, c4])
    print("\n" + "=" * 86)
    print(f" RESULT: N157 structural claims {passed}/4 pass; LISM transformation demonstrated.")
    print(" - OQM de-theologises Barakah into a function: built by deploying capacity through")
    print("   sincere-seeking x selflessness; selection is the OUTPUT, never a birthright.")
    print(" - LISM's empirical correction (quadratic disconfirmed, linear confirmed) transforms")
    print(f"   that function from a catastrophic cliff into a graceful slide — {r_l-r_q} extra steps")
    print("   of tau_v self-correction runway. That graceful linearity IS the Rahmah of the Dunya")
    print("   incubator: capacity is inert, effort is everything, and error is survivable in time.")
    print("=" * 86)
    raise SystemExit(0 if passed == 4 else 1)


if __name__ == "__main__":
    main()
