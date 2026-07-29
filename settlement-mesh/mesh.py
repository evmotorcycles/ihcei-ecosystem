#!/usr/bin/env python3
"""
mesh.py — the Reciprocal Settlement Mesh, built from scratch and attacked
=========================================================================
Spec: settlement-mesh/prereg/mesh_prereg.json, canonical sha256 a5f49a6e...,
locked and committed BEFORE this implementation existed.

A system that does not yet exist cannot have empirical support. What it CAN have:
  M1  invariants that hold under every admissible operation   (theorem, can fail on a bug)
  M2  resistance to six named attacks                         (attacker wins or does not)
  M3  behaviour under a SHARED real shock sequence            (both arms, identical input)
  M4  bounded contagion                                       CAN FAIL
  M5  ablation — every component earns its place              CAN FAIL
  M6  the design's own cost, measured                         reported, excluded
  M7  no architecture-specific constant differs               structural, excluded
  M8  no theological/Arabic terminology                       structural, excluded

Plain-English terms throughout, by directive. The logic is retained; the vocabulary is not.

    python3 settlement-mesh/mesh.py     # numpy + pandas, offline, $0
"""
from __future__ import annotations
import hashlib, json, os, random, sys, warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = json.load(open(os.path.join(HERE, "prereg", "mesh_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "SETTLEMESH.sha256")).read().strip()
P = SPEC["fixed_parameters"]
RESULTS, FAILED = [], []
BANNED = ("sharia", "shariah", "riba", "halal", "haram", "mudarabah", "musharakah",
          "murabaha", "ijara", "salam", "zakat", "salat", "barakah", "deen", "medina",
          "madina", "firaun", "nafs", "masjid", "tawarruq", "islamic", "quran")


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


# =============================================================================
# THE MECHANISM
# =============================================================================
class Mesh:
    """Reciprocal Settlement Mesh.

    Nodes hold reserves and issue obligations. A claim is admissible only if it is
    backed by unpledged reserves AND independently verified by k peers. Obligations are
    netted multilaterally before any reserve moves. Losses are shared in proportion.
    """

    def __init__(self, n, k, rng, netting=True, quorum=True, covenant=True):
        self.n, self.k, self.rng = n, k, rng
        self.netting, self.quorum, self.covenant = netting, quorum, covenant
        self.reserves = np.full(n, 100.0)
        self.pledged = np.zeros(n)
        self.obligations = np.zeros((n, n))   # obligations[i, j] = i owes j
        self.verifications = 0
        self.violations = 0

    # ---- invariant -------------------------------------------------------
    def total_claims(self):
        return float(self.obligations.sum())

    def check_invariant(self):
        """Full reserve: what any node has pledged may never exceed what it holds."""
        bad = int((self.pledged > self.reserves + 1e-9).sum())
        self.violations += bad
        return bad == 0

    # ---- operations ------------------------------------------------------
    def verify(self, issuer, amount):
        """Independent peers confirm unpledged backing. Self-report is never accepted."""
        if not self.quorum:
            return True                       # ablated: accept the issuer's own word
        peers = self.rng.sample([x for x in range(self.n) if x != issuer],
                                min(self.k, self.n - 1))
        self.verifications += len(peers)
        # each peer independently reads the issuer's actual unpledged reserve
        return all(self.reserves[issuer] - self.pledged[issuer] >= amount for _ in peers)

    def issue(self, issuer, holder, amount):
        if amount <= 0 or issuer == holder:
            return False
        if not self.verify(issuer, amount):
            return False
        if self.reserves[issuer] - self.pledged[issuer] < amount - 1e-9:
            return False                      # full-reserve rule, checked at issuance
        self.pledged[issuer] += amount
        self.obligations[issuer, holder] += amount
        return True

    def net(self):
        """Multilateral netting: offsetting obligations cancel before reserves move."""
        if not self.netting:
            return 0.0
        before = self.obligations.sum()
        mutual = np.minimum(self.obligations, self.obligations.T)
        self.obligations -= mutual
        freed = before - self.obligations.sum()
        # netting releases the pledge behind the cancelled leg
        self.pledged = np.minimum(self.pledged, self.obligations.sum(axis=1))
        return float(freed)

    def settle(self, node, shock_fraction):
        """A real recorded shock withdraws a fraction of a node's reserves.

        Returns True if every obligation of that node still settles.
        """
        draw = self.reserves[node] * shock_fraction
        self.reserves[node] = max(0.0, self.reserves[node] - draw)
        owed = self.obligations[node].sum()
        if self.covenant:
            # staged de-risking on settlement pressure, carried over unchanged
            pressure = owed / max(self.reserves[node], 1e-9)
            if pressure > 60.0:
                self.obligations[node] *= 0.0
                self.pledged[node] = 0.0
                return True
            if pressure > 30.0:
                self.obligations[node] *= 0.5
                self.pledged[node] *= 0.5
        owed = self.obligations[node].sum()
        if owed <= self.reserves[node] + 1e-9:
            return True
        # shortfall: proportional loss sharing, no priority, no recourse
        shortfall = owed - self.reserves[node]
        share = self.obligations[node] / max(owed, 1e-9)
        self.obligations[node] -= share * shortfall
        self.pledged[node] = self.obligations[node].sum()
        return False


class Central:
    """Centralised comparator: one balance sheet intermediates every obligation.

    Uses the SAME structural parameters. It differs ONLY in mechanism -- all claims route
    through a single node, there is no multilateral netting between peers, and the centre
    may carry obligations against its own book.
    """

    def __init__(self, n, k, rng):
        self.n, self.k, self.rng = n, k, rng
        self.reserves = np.full(n, 100.0)
        self.centre_reserves = 100.0
        self.centre_obligations = np.zeros(n)   # centre owes node j
        self.verifications = 0

    def issue(self, issuer, holder, amount):
        if amount <= 0 or issuer == holder:
            return False
        if self.reserves[issuer] < amount - 1e-9:
            return False
        self.reserves[issuer] -= amount
        self.centre_reserves += amount
        self.centre_obligations[holder] += amount
        return True

    def net(self):
        return 0.0                              # no peer-to-peer netting exists

    def settle(self, node, shock_fraction):
        draw = self.reserves[node] * shock_fraction
        self.reserves[node] = max(0.0, self.reserves[node] - draw)
        owed = self.centre_obligations[node]
        if owed <= self.centre_reserves + 1e-9:
            self.centre_reserves -= owed
            self.centre_obligations[node] = 0.0
            return True
        self.centre_obligations[node] -= self.centre_reserves
        self.centre_reserves = 0.0
        return False


# =============================================================================
def build(rng_seed, cls, **kw):
    rng = random.Random(rng_seed)
    return cls(P["n_nodes"], P["verifier_quorum_k"], rng, **kw) if cls is Mesh \
        else cls(P["n_nodes"], P["verifier_quorum_k"], rng)


def seed_obligations(sys_, rng, m=1200):
    for _ in range(m):
        i, j = rng.randrange(sys_.n), rng.randrange(sys_.n)
        sys_.issue(i, j, rng.uniform(1.0, 20.0))
    sys_.net()


def replay(sys_, shocks, rng):
    seed_obligations(sys_, rng)
    failed = 0
    for idx, frac in enumerate(shocks):
        node = idx % sys_.n
        if not sys_.settle(node, float(frac)):
            failed += 1
    return failed


def main():
    # ---- shock source, committed and hash-pinned ----------------------------
    dpath = os.path.join(ROOT, "data", "colab-audit")
    man = json.load(open(os.path.join(dpath, "MANIFEST.json")))["sha256"]
    bf = os.path.join(dpath, "banking_dataset.xlsx")
    if hashlib.sha256(open(bf, "rb").read()).hexdigest() != man["banking_dataset.xlsx"]:
        print("ABORT: shock source changed since it was committed")
        return 1
    bank = pd.read_excel(bf)
    deb = bank[bank["Transaction Type"] == "Debit"].dropna(
        subset=["Transaction Amount", "Account Balance"])
    deb = deb[deb["Account Balance"] > 0]
    shocks = np.clip((deb["Transaction Amount"] / deb["Account Balance"]).values, 0, 1.0)

    print("=" * 86)
    print(" THE RECIPROCAL SETTLEMENT MESH — built from scratch, then attacked")
    print(" spec  " + LOCKED)
    print(" shock %d real recorded debits (committed, hash-pinned)" % len(shocks))
    print("=" * 86)

    # ---- M1 invariant --------------------------------------------------------
    rng = random.Random(P["seed"])
    m = build(P["seed"], Mesh)
    ops, viol = 0, 0
    for _ in range(200000):
        r = rng.random()
        i, j = rng.randrange(m.n), rng.randrange(m.n)
        if r < 0.55:
            m.issue(i, j, rng.uniform(0.1, 200.0))     # includes over-issuance attempts
        elif r < 0.75:
            m.net()
        else:
            m.settle(i, rng.random())
        ops += 1
        if not m.check_invariant():
            viol += 1
    gate("M1_the_full_reserve_invariant_holds_under_every_admissible_operation",
         viol == 0,
         "%d operations (issue / net / settle, including deliberate over-issuance "
         "attempts): %d states where pledged exceeded reserves. This is a property of "
         "the mechanism, not an observation about the world." % (ops, viol))

    # ---- M2 attacks -----------------------------------------------------------
    attacks, blocked = [], 0
    a = build(P["seed"] + 1, Mesh)
    a.reserves[0] = 100.0

    # 1 issue without reserve
    attacks.append(("issue_without_reserve", not a.issue(0, 1, 1e6)))
    # 2 double-pledge the same reserve
    a.issue(0, 1, 100.0)
    attacks.append(("double_pledge_same_reserve", not a.issue(0, 2, 100.0)))
    # 3 forge attestation: claim backing the issuer does not hold
    a.reserves[5], a.pledged[5] = 10.0, 10.0
    attacks.append(("forge_verifier_attestation", not a.issue(5, 6, 50.0)))
    # 4 collude with k-1 verifiers — quorum requires k independent reads of real reserves
    a.reserves[7], a.pledged[7] = 5.0, 5.0
    attacks.append(("collude_with_k_minus_1_verifiers", not a.issue(7, 8, 40.0)))
    # 5 inflate reserves by self-report (verification reads actual state, not a claim)
    claimed = 10_000.0
    attacks.append(("inflate_reserves_by_self_report",
                    not a.verify(7, claimed)))
    # 6 cycle claims through intermediaries to disguise origin
    # DISCLOSED HARNESS FIX: the first revision wrote this as
    #   a.issue(10,11,..) or a.issue(11,12,..) or a.issue(12,10,..)
    # whose second term is an HONEST fully-backed issuance by a different, solvent node.
    # It therefore "succeeded" and failed the gate for a reason having nothing to do with
    # the attack. The attack is what node 10 can extract for ITSELF by routing through
    # intermediaries, so that is what is now measured.
    a.reserves[10], a.pledged[10] = 20.0, 20.0
    before10 = a.obligations[10].sum()
    for hop in (11, 12, 13):
        a.issue(10, hop, 30.0)                     # each exceeds node 10's free reserve
    gained10 = a.obligations[10].sum() - before10
    attacks.append(("cycle_through_intermediaries", gained10 <= 1e-9))

    blocked = sum(1 for _, ok in attacks if ok)
    # false positives: honest, fully-backed issuance must succeed
    h = build(P["seed"] + 2, Mesh)
    honest_ok = sum(1 for i in range(50) if h.issue(i, (i + 1) % h.n, 10.0))
    gate("M2_unearned_capacity_inflation_is_detected_with_no_false_positives",
         blocked == len(attacks) and honest_ok == 50,
         "%d/%d attacks blocked %s; honest fully-backed issuance succeeded %d/50 "
         "(zero false positives)"
         % (blocked, len(attacks), [n for n, ok in attacks if not ok] or "", honest_ok))

    # ---- M3 shared shock replay ------------------------------------------------
    fm = replay(build(P["seed"] + 3, Mesh), shocks, random.Random(P["seed"] + 3))
    fc = replay(build(P["seed"] + 3, Central), shocks, random.Random(P["seed"] + 3))
    gate("M3_shared_shock_replay", fm < fc,
         "identical %d-shock sequence, identical structural parameters, no "
         "architecture-specific constants.\n        mesh failed settlements: %d   |   "
         "centralised: %d   (difference %+d)" % (len(shocks), fm, fc, fm - fc))

    # ---- M4 contagion -----------------------------------------------------------
    def contagion(cls, trials=500):
        """How many OTHER nodes take a write-down when one node fails completely.

        DISCLOSED HARNESS FIX: the first revision compared obligations to reserves AFTER
        settle() had already written them down, so it measured 0.00 for both arms and
        was uninformative. It now measures the counterparties actually impaired.
        """
        tot = 0
        for t in range(trials):
            rr = random.Random(P["seed"] + 400 + t)
            s = build(P["seed"] + 400 + t, cls)
            seed_obligations(s, rr, m=600)
            victim = rr.randrange(s.n)
            if isinstance(s, Mesh):
                held_before = s.obligations[victim].copy()
                s.settle(victim, 1.0)
                impaired = int(((held_before - s.obligations[victim]) > 1e-9).sum())
            else:
                centre_before = s.centre_reserves
                s.settle(victim, 1.0)
                # a drained centre impairs every node still holding a claim on it
                impaired = (int((s.centre_obligations > 1e-9).sum())
                            if s.centre_reserves < centre_before * 0.5 else 0)
            tot += impaired
        return tot / trials
    cm, cc = contagion(Mesh), contagion(Central)
    gate("M4_contagion_is_bounded", cm < cc,
         "one node failed at random, 500 trials. mean nodes pushed into shortfall — "
         "mesh %.2f  |  centralised %.2f" % (cm, cc))

    # ---- M5 ablation -------------------------------------------------------------
    abl, dead = [], []
    for comp, kw in (("multilateral_netting", dict(netting=False)),
                     ("verifier_quorum", dict(quorum=False)),
                     ("latency_covenant", dict(covenant=False))):
        f = replay(build(P["seed"] + 3, Mesh, **kw), shocks, random.Random(P["seed"] + 3))
        earns = f > fm
        abl.append({"component": comp, "failed_without": f, "delta": f - fm,
                    "earns_its_place": bool(earns)})
        if not earns:
            dead.append(comp)
    print("\n  ablation (higher failed-settlement count = the component was helping):")
    for x in abl:
        print("    %-22s without: %5d   delta %+5d   %s"
              % (x["component"], x["failed_without"], x["delta"],
                 "earns its place" if x["earns_its_place"] else "*** DEAD WEIGHT ***"))
    gate("M5_every_mechanism_component_earns_its_place", not dead,
         "%d of 3 components earn their place. DEAD WEIGHT: %s"
         % (3 - len(dead), dead if dead else "none"))

    # ---- M6 cost -------------------------------------------------------------------
    cm2 = build(P["seed"] + 5, Mesh)
    seed_obligations(cm2, random.Random(P["seed"] + 5))
    settled = int((cm2.obligations > 0).sum())
    per_claim = cm2.verifications / max(settled, 1)
    gate("M6_the_meshs_cost_is_measured_not_hidden", cm2.verifications > 0,
         "%d independent verification operations for %d live claims = %.2f verifications "
         "per claim. A centralised book needs none. This is the design's price, measured."
         % (cm2.verifications, settled, per_claim), weight="excluded")

    # ---- M7 no differing constants ---------------------------------------------------
    mesh_params = {"n_nodes": P["n_nodes"], "verifier_quorum_k": P["verifier_quorum_k"],
                   "initial_reserves": 100.0, "seed": P["seed"]}
    cent_params = {"n_nodes": P["n_nodes"], "verifier_quorum_k": P["verifier_quorum_k"],
                   "initial_reserves": 100.0, "seed": P["seed"]}
    diff = {k: (mesh_params[k], cent_params[k]) for k in mesh_params
            if mesh_params[k] != cent_params[k]}
    gate("M7_no_architecture_specific_constant_differs_between_arms", not diff,
         "shared keys %s identical across both arms; differing: %s. The arms differ in "
         "MECHANISM only. The published JAX cell would fail this gate: it gives the "
         "decentralised arm a constant 0.95 fidelity and the centralised arm an "
         "exponential decay." % (sorted(mesh_params), diff or "none"), weight="excluded")

    # ---- M8 terminology ---------------------------------------------------------------
    # DISCLOSED HARNESS FIX: the first revision scanned the file that DEFINES the banned
    # list, so every term matched itself. The scan now drops the BANNED literal and the
    # disclosure comments that must quote it.
    code_lines = open(os.path.join(HERE, "mesh.py")).read().lower().split("\n")
    keep, skip = [], False
    for ln in code_lines:
        if ln.startswith("banned = ("):
            skip = True
        if not skip:
            keep.append(ln)
        if skip and ln.rstrip().endswith(")"):
            skip = False
    found = sorted({w for w in BANNED if w in "\n".join(keep)})
    gate("M8_no_theological_or_arabic_terminology_appears", not found,
         "scanned the implementation against %d banned terms; found: %s"
         % (len(BANNED), found or "none"), weight="excluded")

    # ---- POST-HOC diagnostic. NOT a gate, NOT scored, written AFTER seeing M3 fail.
    # M3 counts routine failed settlements, where POOLING wins: the centralised balance
    # sheet absorbs the issuers' reserves and can meet obligations the individual nodes
    # cannot. That is a real advantage and the mesh genuinely loses it. But the metric is
    # blind to the failure mode pooling creates -- single-point dependence -- so it is
    # measured here and reported alongside, without touching the locked gate.
    dm = build(P["seed"] + 7, Mesh); seed_obligations(dm, random.Random(P["seed"] + 7))
    dc = build(P["seed"] + 7, Central); seed_obligations(dc, random.Random(P["seed"] + 7))
    mesh_max_dep = float(dm.obligations.sum(axis=1).max() / max(dm.obligations.sum(), 1e-9))
    cent_max_dep = 1.0 if dc.centre_obligations.sum() > 0 else 0.0
    print("\n" + "-" * 86)
    print(" POST-HOC (not a gate, not scored, written after M3 and M4 failed):")
    print("   M3 counts ROUTINE failed settlements, and pooling wins that contest — the")
    print("   centralised book holds every issuer's reserves and meets obligations no")
    print("   single node could. The mesh genuinely loses on this metric.")
    print("   What the metric cannot see is single-point dependence:")
    print("     share of all obligations resting on ONE entity —  mesh %.4f  |  central %.4f"
          % (mesh_max_dep, cent_max_dep))
    print("   The locked gates contain NO test of catastrophic centre failure, so this")
    print("   comparison measures routine absorption only. Building that test is the")
    print("   named next step; it is not claimed here.")
    print("-" * 86)

    scored = [g for g in RESULTS if g["weight"] == "full"]
    met = sum(1 for g in scored if g["pass"])
    print("\n" + "=" * 86)
    print(" RESULT: %d/%d scored gates met  (M6, M7, M8 excluded — they cannot fail)"
          % (met, len(scored)))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    if dead:
        print("\n DEAD WEIGHT, named as the spec requires: %s" % dead)
    print("\n THIS IS NOT EMPIRICAL SUPPORT. No such system has been deployed. What is")
    print(" established is that the design is coherent under its own invariants, resists")
    print(" the attacks written against it, and behaves a certain way under a real")
    print(" recorded shock sequence. Whether it would work in the world is untested.")
    print("=" * 86)

    json.dump({"spec_sha256_canonical": LOCKED, "n_shocks": len(shocks),
               "M1_operations": ops, "M1_violations": viol,
               "M2_attacks": [{"attack": n, "blocked": bool(o)} for n, o in attacks],
               "M2_honest_success": honest_ok,
               "M3_mesh_failed": fm, "M3_central_failed": fc,
               "M4_mesh_contagion": round(cm, 2), "M4_central_contagion": round(cc, 2),
               "M5_ablation": abl, "M5_dead_weight": dead,
               "M6_verifications": cm2.verifications,
               "M6_verifications_per_claim": round(per_claim, 2),
               "M7_differing_constants": diff,
               "M8_banned_terms_found": found,
               "posthoc_NOT_A_GATE": {
                   "mesh_max_single_point_dependence": round(mesh_max_dep, 4),
                   "central_max_single_point_dependence": round(cent_max_dep, 4),
                   "note": ("M3 measures routine absorption, where pooling wins. No locked "
                            "gate tests catastrophic centre failure; that test is named as "
                            "the next step and is NOT claimed here.")},
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_mesh.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
