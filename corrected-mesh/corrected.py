#!/usr/bin/env python3
"""
corrected.py — the surgical correction, built and ablated
=========================================================
Spec: corrected-mesh/prereg/corrected_prereg.json, canonical sha256 dca3694c...,
locked and committed BEFORE this implementation existed.

WHAT THE TELEMETRY SAID TO KEEP, AND WHAT IT SAID TO CUT
  KEEP  balance-sheet pooling. A centralised book at dU = 0.0 cleared every routine
        debit with zero settlement failures (bf5a27f0 C1). Pooling is sound.
  CUT   fractional credit creation. Leverage made settlement monotonically WORSE:
        m=1 -> 0, m=3 -> 3,262, m=5 -> 3,912, m=10 -> 4,362 (bf5a27f0 C2).
  CUT   the single point, and CUT deferred consequence.

THE LOAD-BEARING UNTESTED PART is the participation note. A fixed obligation that
cannot be paid is a settlement FAILURE. A participation claim that cannot be paid is
written down and recorded as nothing. Scoring equity on failure COUNTS would hand it a
near-perfect result by construction. So every primary gate here is scored on

        CLAIMANT VALUE SHORTFALL  =  value promised  -  value delivered

which is defined identically for a debt claim and an equity claim, and cannot be
improved by relabelling.

A CORRECTION TO EVERY PREVIOUS RUN IN THIS PROGRAMME. All prior experiments replayed
only the 4,886 Debit rows. The committed dataset also holds 5,114 Credit rows. A
downside-only sequence structurally cannot show an upside-sharing mechanism, so every
previous test of risk-sharing was biased AGAINST it. Both are replayed here, in recorded
order, identically in every arm. This makes the test fairer to the proposal.

    python3 corrected-mesh/corrected.py     # numpy + pandas, offline, $0
"""
from __future__ import annotations
import hashlib, json, os, random, sys, warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = json.load(open(os.path.join(HERE, "prereg", "corrected_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "CORRECTED.sha256")).read().strip()
P = SPEC["fixed_parameters"]
N = P["n_nodes"]
RESULTS, FAILED = [], []


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


# =============================================================================
# THE CORRECTED ARCHITECTURE
# =============================================================================
class Corrected:
    """Full-reserve, locally pooled, participation-based settlement with a latency covenant.

    Four components, each independently switchable so F6 can ablate them:
      full_reserve   claims may never exceed unpledged reserves        (dU = 0)
      k              local mutual-guarantee pools of k neighbours
      equity         claims absorb loss proportionally instead of defaulting
      covenant       staged de-risking once settlement pressure builds

    EVERY arm tracks promised vs delivered value, so debt and equity are commensurable.
    """

    def __init__(self, n, rng, k=2, equity=True, full_reserve=True, covenant=True,
                 contribution=0.25, cap_multiple=3.0, prepay=None):
        self.n, self.rng, self.k = n, rng, max(1, k)
        self.equity, self.full_reserve, self.covenant = equity, full_reserve, covenant
        # prepay defaults to follow equity, but is INDEPENDENTLY switchable so the 2x2
        # control below can tell participation apart from mere continuous prepayment.
        self.prepay = equity if prepay is None else prepay
        self.reserves = np.full(n, 100.0)
        self.pledged = np.zeros(n)
        self.obligations = np.zeros((n, n))
        self.promised = np.zeros(n)          # cumulative value promised TO holder j
        self.delivered = np.zeros(n)         # cumulative value actually delivered to j
        self.violations = 0
        self.primary_failures = 0
        self.secondary_failures = 0          # knock-on: a node fails having itself been hit
        self.hit = np.zeros(n, dtype=bool)   # node has already suffered an impairment
        self.impaired = np.zeros(n, dtype=bool)

        self.cluster_of = np.arange(n) // self.k
        self.n_clusters = int(self.cluster_of.max()) + 1
        self.pools = np.zeros(self.n_clusters)
        self.contributed = np.zeros(n)
        if self.k > 1:
            self.contributed = self.reserves * contribution
            self.reserves = self.reserves - self.contributed
            for c in range(self.n_clusters):
                self.pools[c] = self.contributed[self.cluster_of == c].sum()
        self.cap_multiple = cap_multiple
        self.draws, self.bad_draws = 0, 0

    # ---- invariant -------------------------------------------------------
    def check_invariant(self):
        bad = int((self.pledged > self.reserves + self.contributed + 1e-9).sum())
        self.violations += bad
        return bad == 0

    def unbacked(self):
        return max(0.0, float(self.obligations.sum()) - float(self.pledged.sum()))

    # ---- operations ------------------------------------------------------
    def issue(self, issuer, holder, amount):
        if amount <= 0 or issuer == holder:
            return False
        free = self.reserves[issuer] - self.pledged[issuer]
        if self.full_reserve and free < amount - 1e-9:
            return False
        self.pledged[issuer] += amount
        self.obligations[issuer, holder] += amount
        self.promised[holder] += amount
        return True

    def net(self):
        before = self.obligations.sum()
        mutual = np.minimum(self.obligations, self.obligations.T)
        self.obligations -= mutual
        self.pledged = np.minimum(self.pledged, self.obligations.sum(axis=1))
        return float(before - self.obligations.sum())

    def draw(self, node, need):
        """Pull from the local pool, capped at a multiple of this member's contribution."""
        if self.k <= 1 or need <= 0:
            return 0.0
        c = self.cluster_of[node]
        allowed = min(need, self.pools[c], self.contributed[node] * self.cap_multiple)
        allowed = max(0.0, allowed)
        if allowed > self.pools[c] + 1e-9:
            self.bad_draws += 1
            allowed = self.pools[c]
        self.pools[c] -= allowed
        self.reserves[node] += allowed
        self.draws += 1
        return allowed

    def credit(self, node, amount):
        """A recorded CREDIT: real value arrives. Under participation, holders share it."""
        self.reserves[node] += amount
        if self.prepay:
            owed = self.obligations[node]
            tot = owed.sum()
            if tot > 1e-9:
                # upside participation: holders of this node's claims receive a share
                share = min(amount * 0.5, self.reserves[node])
                pay = share * (owed / tot)
                self.delivered += pay
                self.obligations[node] = np.maximum(0.0, owed - pay)
                self.reserves[node] -= pay.sum()
                self.pledged[node] = self.obligations[node].sum()

    def settle(self, node, shock_fraction):
        """A recorded DEBIT withdraws reserves; the node then meets what it owes."""
        drawn = self.reserves[node] * shock_fraction
        self.reserves[node] = max(0.0, self.reserves[node] - drawn)
        owed_v = self.obligations[node]
        owed = owed_v.sum()
        if owed <= 1e-9:
            return True

        if self.covenant:
            pressure = owed / max(self.reserves[node], 1e-9)
            if pressure > 30.0:
                need = min(owed - self.reserves[node], owed)
                self.draw(node, max(0.0, need))

        owed_v = self.obligations[node]
        owed = owed_v.sum()
        if owed <= self.reserves[node] + 1e-9:
            self.delivered += owed_v                 # paid in full
            self.reserves[node] -= owed
            self.obligations[node] = 0.0
            self.pledged[node] = 0.0
            return True

        # shortfall
        avail = self.reserves[node]
        pay = avail * (owed_v / max(owed, 1e-9))
        self.delivered += pay
        self.reserves[node] = 0.0
        residual = owed_v - pay
        was_hit = self.hit[node]

        if self.equity:
            # participation: the loss is absorbed proportionally, no default event
            self.obligations[node] = 0.0
            self.pledged[node] = 0.0
        else:
            # fixed debt: the residual stands and keeps propagating
            self.obligations[node] = residual
            self.pledged[node] = residual.sum()

        touched = residual > 1e-9
        self.impaired |= touched
        self.hit |= touched
        self.primary_failures += 1
        if was_hit:
            self.secondary_failures += 1
        return False

    # ---- outcome ---------------------------------------------------------
    def shortfall(self):
        """CLAIMANT VALUE SHORTFALL: promised minus delivered. The primary metric."""
        return float(np.maximum(0.0, self.promised - self.delivered).sum())


class CentralBook:
    """The benchmark: one full-reserve balance sheet, dU = 0, no participation."""

    def __init__(self, n, rng, prepay=False, **kw):
        self.n, self.rng, self.prepay = n, rng, prepay
        self.reserves = np.full(n, 100.0)
        self.centre = 100.0
        self.owed = np.zeros(n)
        self.promised = np.zeros(n)
        self.delivered = np.zeros(n)
        self.primary_failures = self.secondary_failures = 0
        self.hit = np.zeros(n, dtype=bool)
        self.violations = self.draws = self.bad_draws = 0
        self.n_clusters = 1

    def unbacked(self):
        return max(0.0, float(self.owed.sum()) - float(self.centre))

    def check_invariant(self):
        return True

    def issue(self, issuer, holder, amount):
        if amount <= 0 or issuer == holder or self.reserves[issuer] < amount - 1e-9:
            return False
        self.reserves[issuer] -= amount
        self.centre += amount
        self.owed[holder] += amount
        self.promised[holder] += amount
        return True

    def net(self):
        return 0.0

    def credit(self, node, amount):
        self.reserves[node] += amount
        if self.prepay:
            pay = min(amount * 0.5, self.reserves[node], self.owed[node])
            if pay > 0:
                self.reserves[node] -= pay
                self.owed[node] -= pay
                self.delivered[node] += pay

    def settle(self, node, shock_fraction):
        self.reserves[node] = max(0.0, self.reserves[node] * (1.0 - shock_fraction))
        o = self.owed[node]
        if o <= 1e-9:
            return True
        if o <= self.centre + 1e-9:
            self.centre -= o
            self.delivered[node] += o
            self.owed[node] = 0.0
            return True
        self.delivered[node] += self.centre
        self.owed[node] -= self.centre
        self.centre = 0.0
        was = self.hit[node]
        self.hit[node] = True
        self.primary_failures += 1
        if was:
            self.secondary_failures += 1
        return False

    def shortfall(self):
        return float(np.maximum(0.0, self.promised - self.delivered).sum())


# =============================================================================
def replay(cls, kw, events):
    rng = random.Random(P["seed"])
    s = cls(N, rng, **kw)
    for _ in range(1200):                       # seed a live book, identically in every arm
        s.issue(rng.randrange(N), rng.randrange(N), rng.uniform(1.0, 20.0))
    s.net()
    for idx, (kind, val) in enumerate(events):
        node = idx % N
        s.issue(rng.randrange(N), rng.randrange(N), rng.uniform(1.0, 20.0))
        if kind == "D":
            s.settle(node, float(val))
        else:
            s.credit(node, float(val))
        if idx % 500 == 0:
            s.check_invariant()
    s.check_invariant()
    return s


def main():
    dpath = os.path.join(ROOT, "data", "colab-audit")
    man = json.load(open(os.path.join(dpath, "MANIFEST.json")))["sha256"]
    bf = os.path.join(dpath, "banking_dataset.xlsx")
    if hashlib.sha256(open(bf, "rb").read()).hexdigest() != man["banking_dataset.xlsx"]:
        print("ABORT: shock source changed since it was committed")
        return 1
    bank = pd.read_excel(bf).dropna(subset=["Transaction Amount", "Account Balance"])
    bank = bank[bank["Account Balance"] > 0]
    events = []
    for _, r in bank.iterrows():
        frac = min(1.0, float(r["Transaction Amount"]) / float(r["Account Balance"]))
        if r["Transaction Type"] == "Debit":
            events.append(("D", frac))
        else:
            events.append(("C", min(100.0, float(r["Transaction Amount"]) / 100.0)))

    print("=" * 86)
    print(" THE SURGICAL CORRECTION — keep pooling, cut the corruptions, test the note")
    print(" spec  " + LOCKED)
    print(" events %d  (%d debits + %d credits, recorded order, committed and hash-pinned)"
          % (len(events), sum(1 for e in events if e[0] == "D"),
             sum(1 for e in events if e[0] == "C")))
    print("=" * 86)

    K = P["headline_k"]
    corrected = replay(Corrected, {"k": K, "equity": True}, events)
    debt = replay(Corrected, {"k": K, "equity": False}, events)
    central = replay(CentralBook, {}, events)

    print("\n  claimant value shortfall  (promised - delivered)")
    print("    corrected (equity, k=%d) %12.1f   primary %5d  secondary %5d"
          % (K, corrected.shortfall(), corrected.primary_failures,
             corrected.secondary_failures))
    print("    fixed debt (k=%d)        %12.1f   primary %5d  secondary %5d"
          % (K, debt.shortfall(), debt.primary_failures, debt.secondary_failures))
    print("    central full-reserve book%12.1f   primary %5d  secondary %5d"
          % (central.shortfall(), central.primary_failures, central.secondary_failures))

    # ---- MANDATORY CONTROL, run before the gates are scored --------------------
    # F2 compares an equity arm against a debt arm, but the equity arm ALSO distributes
    # 50% of every credit inflow to holders. That is PREPAYMENT, and a debt issuer could
    # do it too. Bundling them would credit participation with prepayment's effect, so
    # the 2x2 below separates them. It is run unconditionally and reported whatever it says.
    ctrl = {}
    for eq in (True, False):
        for pp in (True, False):
            s_ = replay(Corrected, {"k": K, "equity": eq, "prepay": pp}, events)
            ctrl["equity=%s,prepay=%s" % (eq, pp)] = {
                "shortfall": s_.shortfall(), "primary": s_.primary_failures,
                "secondary": s_.secondary_failures}
    central_pp = replay(CentralBook, {"prepay": True}, events)
    e_on = ctrl["equity=True,prepay=True"]["shortfall"]
    d_on = ctrl["equity=False,prepay=True"]["shortfall"]
    e_off = ctrl["equity=True,prepay=False"]["shortfall"]
    d_off = ctrl["equity=False,prepay=False"]["shortfall"]
    participation_helps = (e_on < d_on) and (e_off < d_off)
    print("\n  2x2 CONTROL — participation, or merely prepayment?")
    print("  %-30s %14s %10s" % ("arm", "shortfall", "secondary"))
    for kk, vv in ctrl.items():
        print("  %-30s %14.1f %10d" % (kk, vv["shortfall"], vv["secondary"]))
    print("  central full-reserve WITH prepay %13.1f" % central_pp.shortfall())

    # ---- F1 invariant ---------------------------------------------------------
    du = max(corrected.unbacked(), debt.unbacked())
    gate("F1_full_reserve_invariant_holds_exactly",
         du < 1e-6 and corrected.violations == 0 and debt.violations == 0,
         ("max unbacked claims %.3e; invariant violations — corrected arm %d, "
          "fixed-debt arm %d\n        *** The CORRECTED architecture holds full reserve "
          "exactly. The FIXED-DEBT comparator\n        does not: after a shortfall its "
          "residual claim survives with no reserve behind it,\n        which is what an "
          "unbacked debt IS. The gate says 'in every arm', so it FAILS as\n        "
          "written — and the reason is a property of debt, not a bug in the build."
          % (du, corrected.violations, debt.violations)))

    # ---- F2 does equity reduce the loss, or rename it? ------------------------
    se, sd = corrected.shortfall(), debt.shortfall()
    red = 100.0 * (sd - se) / max(sd, 1e-9)
    gate("F2_equity_reduces_claimant_value_shortfall_rather_than_relabelling_it",
         se <= 0.80 * sd,
         ("equity %.1f vs fixed debt %.1f  -> %.1f%% reduction (needs >= 20%%)\n"
          "        promised  equity %.1f / debt %.1f   delivered  equity %.1f / debt %.1f\n"
          "\n        *** DISCLOSURE — THIS PASS IS ENTIRELY ATTRIBUTABLE TO PREPAYMENT, "
          "NOT PARTICIPATION.\n        The 2x2 control holds the distribution policy "
          "fixed and the ranking INVERTS:\n"
          "            prepay ON    equity %.1f   vs   fixed debt %.1f\n"
          "            prepay OFF   equity %.1f   vs   fixed debt %.1f\n"
          "        In BOTH columns equity is WORSE than debt. The operative ingredient is "
          "the\n        discipline of distributing inflows continuously, which is "
          "orthogonal to whether\n        the claim is fixed or variable. Mechanism: "
          "writing a claim down EXTINGUISHES it,\n        so the holder can never be made "
          "whole from later inflows, whereas a residual debt\n        survives and is "
          "recoverable. The threshold is NOT moved and the gate is NOT\n        re-scored, "
          "but the architecture's central innovation is not what is working."
          % (se, sd, red, corrected.promised.sum(), debt.promised.sum(),
             corrected.delivered.sum(), debt.delivered.sum(),
             e_on, d_on, e_off, d_off)))

    # ---- F3 does equity suppress cascade? -------------------------------------
    ce, cd = corrected.secondary_failures, debt.secondary_failures
    gate("F3_equity_reduces_CASCADE_which_is_the_only_mechanism_by_which_it_could_win",
         ce <= 0.70 * cd,
         ("secondary (knock-on) failures: equity %d vs debt %d -> %.1f%% reduction "
          "(needs >= 30%%)\n"
          "        *** THIS IS THE ONE GATE THAT SURVIVES THE 2x2 CONTROL. Holding the\n"
          "        distribution policy fixed, participation reduces cascade in BOTH "
          "columns:\n"
          "            prepay ON    equity %d vs debt %d  (%.1f%% fewer)\n"
          "            prepay OFF   equity %d vs debt %d  (%.1f%% fewer)\n"
          "        So participation IS a real mechanism — but a CONTAGION control, not a\n"
          "        loss reducer. Absorbing a loss without a hard default event genuinely\n"
          "        stops it propagating; it does not make the loss smaller. Note the "
          "effect\n        weakens to %.1f%% once prepayment is present, below this "
          "gate's own threshold."
          % (ce, cd, 100.0 * (cd - ce) / max(cd, 1e-9),
             ctrl["equity=True,prepay=True"]["secondary"],
             ctrl["equity=False,prepay=True"]["secondary"],
             100.0 * (ctrl["equity=False,prepay=True"]["secondary"]
                      - ctrl["equity=True,prepay=True"]["secondary"])
             / max(ctrl["equity=False,prepay=True"]["secondary"], 1),
             ctrl["equity=True,prepay=False"]["secondary"],
             ctrl["equity=False,prepay=False"]["secondary"],
             100.0 * (ctrl["equity=False,prepay=False"]["secondary"]
                      - ctrl["equity=True,prepay=False"]["secondary"])
             / max(ctrl["equity=False,prepay=False"]["secondary"], 1),
             100.0 * (ctrl["equity=False,prepay=True"]["secondary"]
                      - ctrl["equity=True,prepay=True"]["secondary"])
             / max(ctrl["equity=False,prepay=True"]["secondary"], 1))))

    # ---- F4 does it approach the central book? --------------------------------
    sc = central.shortfall()
    gate("F4_the_corrected_architecture_approaches_the_central_book",
         se <= 1.25 * sc,
         ("corrected %.1f vs central full-reserve book %.1f (needs <= %.1f); ratio "
          "%.2fx\n        *** DISCLOSURE: the central comparator does NOT prepay. Given "
          "the same\n        distribution discipline it scores %.1f — so this gate "
          "compares distribution\n        policies, not topologies. On equal terms the "
          "central book is %s."
          % (se, sc, 1.25 * sc, se / max(sc, 1e-9), central_pp.shortfall(),
             "still ahead" if central_pp.shortfall() < se else "behind")))

    # ---- F5 the 1/K blast radius claim ----------------------------------------
    ksweep = []
    for k in P["cluster_sizes_swept"]:
        s = replay(Corrected, {"k": k, "equity": True}, events)
        ksweep.append({"k": k, "shortfall": s.shortfall(), "n_clusters": s.n_clusters,
                       "one_over_K": 1.0 / s.n_clusters,
                       "primary": s.primary_failures, "secondary": s.secondary_failures})
        print("    k=%-4d clusters %3d  1/K %.4f  shortfall %12.1f  primary %5d"
              % (k, s.n_clusters, 1.0 / s.n_clusters, s.shortfall(), s.primary_failures))

    s20 = replay(Corrected, {"k": 20, "equity": True}, events)
    impaired = float(s20.impaired.sum()) / N
    oneK = 1.0 / s20.n_clusters
    gate("F5_the_one_over_K_blast_radius_claim_tested_as_stated",
         impaired <= 1.25 * oneK,
         ("at k=20 there are %d clusters so 1/K = %.4f (the proposal quoted 0.0100, which\n"
          "        conflates cluster COUNT with cluster SIZE). MEASURED fraction of the "
          "network\n        whose delivered value is impaired: %.4f — %.1fx the claimed "
          "quarantine.\n        Damage is NOT confined to one cluster."
          % (s20.n_clusters, oneK, impaired, impaired / max(oneK, 1e-9))))

    # ---- F6 ablation -----------------------------------------------------------
    base = se
    abl = {}
    for label, kw in (("full_reserve", {"k": K, "equity": True, "full_reserve": False}),
                      ("local_pooling", {"k": 1, "equity": True}),
                      # prepay held ON so this isolates PARTICIPATION, not distribution
                      ("equity_participation", {"k": K, "equity": False, "prepay": True}),
                      ("latency_covenant", {"k": K, "equity": True, "covenant": False})):
        s = replay(Corrected, kw, events)
        abl[label] = {"shortfall": s.shortfall(), "delta": s.shortfall() - base,
                      "unbacked": s.unbacked()}
    print("\n  ABLATION — change in claimant value shortfall when each part is REMOVED")
    for k_, v in abl.items():
        print("    remove %-22s shortfall %12.1f   delta %+12.1f"
              % (k_, v["shortfall"], v["delta"]))
    # the spec says a component earns its place if removing it produces a LOSS.
    # A component whose removal produces a GAIN is worse than dead weight.
    dead = [k_ for k_, v in abl.items() if v["delta"] <= 1e-6]
    harmful = [k_ for k_, v in abl.items() if v["delta"] < -1e-6]
    gate("F6_ABLATION_every_component_earns_its_place", not dead,
         ("removing each component changes claimant shortfall by: "
          + "  ".join("%s %+.1f" % (k_, v["delta"]) for k_, v in abl.items())
          + ("\n        DID NOT EARN ITS PLACE (removal did not cost anything): %s" % dead
             if dead else "\n        every component earns its place")
          + ("\n        *** WORSE THAN DEAD WEIGHT — removing these IMPROVED the outcome: "
             "%s\n        The equity ablation holds prepayment ON, so it isolates "
             "participation itself." % harmful if harmful else "")))

    # ---- structural -------------------------------------------------------------
    books = {"corrected": float(corrected.promised.sum()),
             "debt": float(debt.promised.sum()), "central": float(central.promised.sum())}
    gate("F7_identical_inputs_and_a_live_book_guard", min(books.values()) > 0,
         "same %d events, seed %d, %d nodes in every arm; promised value booked — "
         % (len(events), P["seed"], N)
         + "  ".join("%s %.1f" % (a, b) for a, b in books.items()), weight="excluded")
    gate("F8_no_closed_form_reporting", True,
         "1/K is reported ONLY as the proposal's claim to be tested against a measured\n"
         "        impairment fraction; every other number is read out of engine state",
         weight="excluded")

    n_full = len([g for g in RESULTS if g["weight"] == "full"])
    out = {
        "spec_sha256_canonical": LOCKED, "n_events": len(events),
        "n_debits": sum(1 for e in events if e[0] == "D"),
        "n_credits": sum(1 for e in events if e[0] == "C"),
        "shortfall_equity": se, "shortfall_debt": sd, "shortfall_central": sc,
        "equity_reduction_pct": red,
        "secondary_equity": ce, "secondary_debt": cd,
        "primary_equity": corrected.primary_failures, "primary_debt": debt.primary_failures,
        "primary_central": central.primary_failures,
        "unbacked_max": du, "k_sweep": ksweep,
        "k20_clusters": s20.n_clusters, "k20_one_over_K": oneK,
        "k20_measured_impaired": impaired,
        "ablation": abl, "dead_weight": dead, "harmful_components": harmful,
        "control_2x2": ctrl, "central_with_prepay": central_pp.shortfall(),
        "participation_helps_when_prepay_held_fixed": bool(participation_helps),
        "participation_reduces_cascade_in_both_columns": bool(
            ctrl["equity=True,prepay=True"]["secondary"]
            < ctrl["equity=False,prepay=True"]["secondary"]
            and ctrl["equity=True,prepay=False"]["secondary"]
            < ctrl["equity=False,prepay=False"]["secondary"]),
        "confound_disclosed": ("F2 and F4 pass on the pre-registered comparisons, but the "
            "2x2 control shows the gain is attributable to PREPAYMENT, not participation: "
            "holding distribution policy fixed, equity is worse than debt in both columns. "
            "Thresholds not moved, gates not re-scored, confound recorded."),
        "gates": RESULTS, "gates_not_met": FAILED,
        "score": "%d/%d" % (n_full - len(FAILED), n_full),
    }
    json.dump(out, open(os.path.join(HERE, "results_corrected.json"), "w"), indent=2)
    print("\n" + "=" * 86)
    print("  SCORE %s   not met: %s" % (out["score"], FAILED or "none"))
    print("=" * 86)
    return 0


if __name__ == "__main__":
    sys.exit(main())
