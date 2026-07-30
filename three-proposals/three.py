#!/usr/bin/env python3
"""
three.py — three proposals for Islamic banking, put on the same engine
=======================================================================
Spec: three-proposals/prereg/three_prereg.json, canonical sha256 0b2328c5...,
locked and committed BEFORE this implementation existed.

THE ARMS
  irfan       100% full reserve, every claim a participation note: on shortfall the
              claim absorbs loss proportionally and is EXTINGUISHED, no default event.
  alqudah_m3  asset-backed sale/lease + diminishing co-ownership on the FRACTIONAL
              substrate the position accepts as regulatory reality. Claims amortise;
              the institution's ownership share absorbs a PROPORTION of loss and the
              remainder survives as a recoverable claim.
  alqudah_m1  identical contracts at full reserve. REQUIRED CONTROL -- separates the
              contract design from the substrate it is constrained to.
  tworegister full reserve, fixed 25% containment / 75% recovery policy mix. NO routing
              model: routing was refuted at ed80430a and is not reinstated.

THE CONFOUND THIS SPEC EXISTS TO CONTROL. Continuous distribution of inflows measured
delta J = +194.5 last run -- two orders of magnitude above any structural component, and
larger than anything the three positions dispute. It is a named part of OUR proposal and
not of the other two. Giving it to our arm alone would win the comparison on a mechanism
the doctrinal argument is not even about. So it is an INDEPENDENT FACTOR: every arm runs
BOTH ways, and the architecture gates are scored with it OFF everywhere.

NO COMBINED OBJECTIVE. The previous run locked equal 0.5/0.5 weights and then found the
terms differed 90x in dynamic range. Every gate here names exactly one metric.

    python3 three-proposals/three.py     # numpy + pandas, offline, $0
"""
from __future__ import annotations
import hashlib, json, os, random, sys, warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = json.load(open(os.path.join(HERE, "prereg", "three_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "THREE.sha256")).read().strip()
P = SPEC["fixed_parameters"]
N = P["n_nodes"]
BASE = N * 100.0
RESULTS, FAILED = [], []


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


# =============================================================================
class Book:
    """One settlement engine, four contract regimes.

    regime per node:
      'participation'  loss extinguishes the claim entirely   (Irfan)
      'fixed'          loss leaves a recoverable residual      (recovery register)
      'coown'          loss extinguishes the institution's ownership SHARE only,
                       the remainder survives as recoverable; claims also amortise
    """

    def __init__(self, n, rng, regime, m=1.0, distribute=False, k=2,
                 own_share=0.5, amort=0.02, contribution=0.25, cap_multiple=3.0):
        self.n, self.rng = n, rng
        self.regime = np.asarray(regime, dtype=object)
        self.m = float(m)
        self.distribute = distribute
        self.k = max(1, k)
        self.own_share, self.amort = own_share, amort
        self.reserves = np.full(n, 100.0)
        self.pledged = np.zeros(n)
        self.obligations = np.zeros((n, n))
        self.promised = np.zeros(n)
        self.delivered = np.zeros(n)
        self.primary_failures = self.secondary_failures = 0
        self.hit = np.zeros(n, dtype=bool)

        self.cluster_of = np.arange(n) // self.k
        self.pools = np.zeros(int(self.cluster_of.max()) + 1)
        self.contributed = np.zeros(n)
        if self.k > 1:
            self.contributed = self.reserves * contribution
            self.reserves -= self.contributed
            for c in range(len(self.pools)):
                self.pools[c] = self.contributed[self.cluster_of == c].sum()
        self.cap_multiple = cap_multiple

    def unbacked(self):
        return max(0.0, float(self.obligations.sum()) - float(self.pledged.sum()))

    def issue(self, issuer, holder, amount):
        """Under leverage m, only amount/m of real backing is required."""
        if amount <= 0 or issuer == holder:
            return False
        need = amount / self.m
        if self.reserves[issuer] - self.pledged[issuer] < need - 1e-9:
            return False
        self.pledged[issuer] += need
        self.obligations[issuer, holder] += amount
        self.promised[holder] += amount
        return True

    def net(self):
        mutual = np.minimum(self.obligations, self.obligations.T)
        self.obligations -= mutual
        self.pledged = np.minimum(self.pledged, self.obligations.sum(axis=1))

    def draw(self, node, need):
        if self.k <= 1 or need <= 0:
            return 0.0
        c = self.cluster_of[node]
        allowed = max(0.0, min(need, self.pools[c],
                               self.contributed[node] * self.cap_multiple))
        self.pools[c] -= allowed
        self.reserves[node] += allowed
        return allowed

    def credit(self, node, amount):
        self.reserves[node] += amount
        if not self.distribute:
            return
        owed = self.obligations[node]
        tot = owed.sum()
        if tot > 1e-9:
            share = min(amount * 0.5, self.reserves[node])
            pay = share * (owed / tot)
            self.delivered += pay
            self.obligations[node] = np.maximum(0.0, owed - pay)
            self.reserves[node] -= pay.sum()
            self.pledged[node] = self.obligations[node].sum() / self.m

    def settle(self, node, shock_fraction):
        self.reserves[node] = max(0.0, self.reserves[node] * (1.0 - shock_fraction))
        reg = self.regime[node]

        if reg == "coown":
            # diminishing co-ownership: the client buys the institution down each period
            amortised = self.obligations[node] * self.amort
            payable = min(amortised.sum(), self.reserves[node])
            if payable > 1e-9:
                frac = payable / max(amortised.sum(), 1e-9)
                pay = amortised * frac
                self.delivered += pay
                self.obligations[node] -= pay
                self.reserves[node] -= payable
                self.pledged[node] = self.obligations[node].sum() / self.m

        owed_v = self.obligations[node]
        owed = owed_v.sum()
        if owed <= 1e-9:
            return True
        if owed / max(self.reserves[node], 1e-9) > 30.0:
            self.draw(node, max(0.0, owed - self.reserves[node]))

        owed_v = self.obligations[node]
        owed = owed_v.sum()
        if owed <= self.reserves[node] + 1e-9:
            self.delivered += owed_v
            self.reserves[node] -= owed
            self.obligations[node] = 0.0
            self.pledged[node] = 0.0
            return True

        pay = self.reserves[node] * (owed_v / max(owed, 1e-9))
        self.delivered += pay
        self.reserves[node] = 0.0
        residual = owed_v - pay
        was_hit = self.hit[node]

        if reg == "participation":
            self.obligations[node] = 0.0                       # fully extinguished
        elif reg == "coown":
            self.obligations[node] = residual * (1.0 - self.own_share)  # partial
        else:
            self.obligations[node] = residual                  # survives in full
        self.pledged[node] = self.obligations[node].sum() / self.m

        self.hit |= (residual > 1e-9)
        self.primary_failures += 1
        if was_hit:
            self.secondary_failures += 1
        return False

    def shortfall(self):
        return float(np.maximum(0.0, self.promised - self.delivered).sum())


# =============================================================================
def regime_for(arm):
    if arm == "irfan":
        return np.array(["participation"] * N, dtype=object)
    if arm.startswith("alqudah"):
        return np.array(["coown"] * N, dtype=object)
    r = np.array(["fixed"] * N, dtype=object)
    n_c = int(round(P["containment_share_two_register"] * N))
    r[:n_c] = "participation"                 # FIXED policy mix, no routing model
    return r


def run(arm, distribute, events):
    m = P["leverage_for_constrained_arm"] if arm == "alqudah_m3" else 1.0
    rng = random.Random(P["seed"])
    b = Book(N, rng, regime_for(arm), m=m, distribute=distribute, k=P["k_pool"],
             own_share=P["alqudah_institution_ownership_share"],
             amort=P["alqudah_amortisation_per_settlement"])
    for _ in range(1200):
        b.issue(rng.randrange(N), rng.randrange(N), rng.uniform(1.0, 20.0))
    b.net()
    for idx, (kind, val) in enumerate(events):
        b.issue(rng.randrange(N), rng.randrange(N), rng.uniform(1.0, 20.0))
        if kind == "D":
            b.settle(idx % N, float(val))
        else:
            b.credit(idx % N, float(val))
    return b


ARMS = ["irfan", "alqudah_m3", "alqudah_m1", "tworegister"]


def main():
    dpath = os.path.join(ROOT, "data", "colab-audit")
    man = json.load(open(os.path.join(dpath, "MANIFEST.json")))["sha256"]
    bf = os.path.join(dpath, "banking_dataset.xlsx")
    if hashlib.sha256(open(bf, "rb").read()).hexdigest() != man["banking_dataset.xlsx"]:
        print("ABORT: event source changed since it was committed")
        return 1
    bank = pd.read_excel(bf).dropna(subset=["Transaction Amount", "Account Balance"])
    bank = bank[bank["Account Balance"] > 0]
    events = [("D", min(1.0, float(r["Transaction Amount"]) / float(r["Account Balance"])))
              if r["Transaction Type"] == "Debit"
              else ("C", min(100.0, float(r["Transaction Amount"]) / 100.0))
              for _, r in bank.iterrows()]

    print("=" * 88)
    print(" THREE PROPOSALS FOR ISLAMIC BANKING — one engine, one event sequence")
    print(" spec  " + LOCKED)
    print(" events %d (committed, hash-pinned, both sides of the ledger)" % len(events))
    print("=" * 88)

    R = {}
    for d in (False, True):
        for a in ARMS:
            b = run(a, d, events)
            R[(a, d)] = {"shortfall": b.shortfall(), "secondary": b.secondary_failures,
                         "primary": b.primary_failures, "unbacked": b.unbacked(),
                         "promised": float(b.promised.sum())}

    for d in (False, True):
        print("\n  continuous distribution %s" % ("ON" if d else "OFF"))
        print("  %-14s %14s %12s %12s" % ("arm", "shortfall", "secondary", "unbacked"))
        for a in ARMS:
            v = R[(a, d)]
            print("  %-14s %14.1f %12d %12.1f"
                  % (a, v["shortfall"], v["secondary"], v["unbacked"]))

    OFF = {a: R[(a, False)] for a in ARMS}
    ON = {a: R[(a, True)] for a in ARMS}

    # ---- B1 substrate difference is real, not nominal --------------------------
    fr_ok = all(OFF[a]["unbacked"] < 1e-6 for a in ("irfan", "alqudah_m1", "tworegister"))
    frac_ok = OFF["alqudah_m3"]["unbacked"] > 0.01 * BASE
    gate("B1_the_full_reserve_arms_hold_the_invariant_and_the_constrained_arm_does_not",
         fr_ok and frac_ok,
         "unbacked claims — irfan %.1f  alqudah_m1 %.1f  tworegister %.1f  |  "
         "alqudah_m3 %.1f (needs > %.1f)"
         % (OFF["irfan"]["unbacked"], OFF["alqudah_m1"]["unbacked"],
            OFF["tworegister"]["unbacked"], OFF["alqudah_m3"]["unbacked"], 0.01 * BASE))

    # ---- B2 shortfall, distribution OFF everywhere -----------------------------
    tr, ir, aq = (OFF["tworegister"]["shortfall"], OFF["irfan"]["shortfall"],
                  OFF["alqudah_m3"]["shortfall"])
    gate("B2_architecture_comparison_on_SHORTFALL_with_distribution_OFF_everywhere",
         not (tr > ir and tr > aq),
         "shortfall — tworegister %.1f  vs  irfan %.1f  and  alqudah_m3 %.1f\n"
         "        (our arm must not be worse than BOTH; written so we can lose)"
         % (tr, ir, aq))

    # ---- B3 cascade, distribution OFF ------------------------------------------
    best_c = min(ARMS, key=lambda a: OFF[a]["secondary"])
    gate("B3_architecture_comparison_on_CASCADE_with_distribution_OFF_everywhere",
         best_c == "irfan",
         "secondary failures — " + "  ".join("%s %d" % (a, OFF[a]["secondary"])
                                             for a in ARMS)
         + "\n        fewest: %s (the contagion-control prediction says irfan)" % best_c)

    # ---- B4 PRIMARY: does the doctrinal difference survive distribution? --------
    s_off = [OFF[a]["shortfall"] for a in ARMS]
    s_on = [ON[a]["shortfall"] for a in ARMS]
    spread_off, spread_on = max(s_off) - min(s_off), max(s_on) - min(s_on)
    ratio = spread_on / max(spread_off, 1e-9)
    gate("B4_DOES_THE_DOCTRINAL_DIFFERENCE_SURVIVE_CONTINUOUS_DISTRIBUTION",
         ratio >= 0.25,
         ("spread between best and worst arm on shortfall:\n"
          "            distribution OFF  %12.1f\n"
          "            distribution ON   %12.1f\n"
          "        retained %.1f%% (needs >= 25%%)\n"
          "        *** A FAIL means a payment-timing rule none of the three positions "
          "names\n        dominates the dispute between them — including ours."
          % (spread_off, spread_on, 100 * ratio)))

    # ---- B5 is the substrate critique right? -----------------------------------
    a3, a1 = OFF["alqudah_m3"]["shortfall"], OFF["alqudah_m1"]["shortfall"]
    gate("B5_the_substrate_critique_is_correct_on_measurement",
         a3 >= 1.25 * a1,
         "identical contracts, different substrate: m=3 %.1f vs m=1 %.1f "
         "(needs m=3 >= %.1f)\n        ratio %.2fx — the practitioner critique says the "
         "substrate is what matters" % (a3, a1, 1.25 * a1, a3 / max(a1, 1e-9)))

    # ---- structural --------------------------------------------------------------
    gate("B6_identical_inputs_and_live_books",
         all(R[(a, d)]["promised"] > 0 for a in ARMS for d in (False, True)),
         "same %d events, seed %d, %d nodes; promised booked in every arm — "
         % (len(events), P["seed"], N)
         + "  ".join("%s %.0f" % (a, OFF[a]["promised"]) for a in ARMS),
         weight="excluded")
    gate("B7_no_arm_is_scored_on_a_metric_it_alone_defines", True,
         "every gate names ONE metric applied identically to all four arms; no combined\n"
         "        objective exists in this spec", weight="excluded")

    n_full = len([g for g in RESULTS if g["weight"] == "full"])
    out = {
        "spec_sha256_canonical": LOCKED, "n_events": len(events),
        "arms": ARMS,
        "distribution_off": {a: OFF[a] for a in ARMS},
        "distribution_on": {a: ON[a] for a in ARMS},
        "spread_off": spread_off, "spread_on": spread_on, "spread_retained": ratio,
        "fewest_cascades_arm": best_c,
        "alqudah_substrate_ratio": a3 / max(a1, 1e-9),
        "gates": RESULTS, "gates_not_met": FAILED,
        "score": "%d/%d" % (n_full - len(FAILED), n_full),
    }
    json.dump(out, open(os.path.join(HERE, "results_three.json"), "w"), indent=2)
    print("\n" + "=" * 88)
    print("  SCORE %s   not met: %s" % (out["score"], FAILED or "none"))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
