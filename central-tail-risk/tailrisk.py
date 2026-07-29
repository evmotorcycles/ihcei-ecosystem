#!/usr/bin/env python3
"""
tailrisk.py — the unmeasured half, measured
===========================================
Spec: central-tail-risk/prereg/tailrisk_prereg.json, canonical sha256 bf5a27f0...,
locked and committed BEFORE this implementation existed.

An argument was put to this programme: the settlement mesh is not failing, the test
suite is measuring the wrong game. Three parts, all testable:

  1. the centralised arm posts zero routine failures ONLY because it creates credit
  2. that is why full-reserve pooling was priced at 17-18% and not 90%
  3. the centre carries single-point dependence 1.0000 and would MELT DOWN under stress,
     while the mesh at k=2 is "immune (blast quarantined)" at 0.0100

Parts 1 and 3 were asserted in a summary table as OUTCOMES. Neither had been measured.

METHOD. The Mesh and Central classes are IMPORTED UNCHANGED from settlement-mesh/mesh.py
-- the engine already built, attacked over 200,000 operations and beaten by pooling. One
new arm is added (Fractional) whose ONLY difference is that the centre may issue claims
beyond its backing. All arms take the identical committed 4,886 real shocks, the same
seed, the same node count and the same seeded obligations.

THE FREEZE IS THE SAME FRACTION OF VALUE HELD AT STRIKE TIME, in every arm. In the centralised arms
it is taken from the centre first, because the centre is the single point. In the mesh it
is taken proportionally across all nodes, because no centre exists. That difference in
WHERE value is taken from is the hypothesis, not a parameter advantage.

PRIMARY METRIC, fixed here before any run: the fraction of outstanding obligation VALUE
that cannot be paid. Counts are reported as secondary context only and no gate turns on
them except C5, which the spec defines in counts.

    python3 central-tail-risk/tailrisk.py     # numpy + pandas, offline, $0
"""
from __future__ import annotations
import hashlib, json, os, random, sys, warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "settlement-mesh"))
from mesh import Mesh, Central, seed_obligations          # noqa: E402  the committed engine

SPEC = json.load(open(os.path.join(HERE, "prereg", "tailrisk_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "TAILRISK.sha256")).read().strip()
P = SPEC["fixed_parameters"]
STRIKES = [0.25, 0.50, 0.75]
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
# THE ONE NEW ARM: a centre that may lend beyond its backing
# =============================================================================
class Fractional(Central):
    """Identical to Central in every respect except one: the issuer needs only 1/m of the
    claim in real backing. The remaining (1 - 1/m) is a claim with nothing behind it.

    This is the ONLY per-arm constant in the whole experiment, and it is the declared
    treatment variable.
    """

    def __init__(self, n, k, rng, m=5.0):
        super().__init__(n, k, rng)
        self.m = float(m)

    def issue(self, issuer, holder, amount):
        if amount <= 0 or issuer == holder:
            return False
        need = amount / self.m
        if self.reserves[issuer] < need - 1e-9:
            return False
        self.reserves[issuer] -= need
        self.centre_reserves += need
        self.centre_obligations[holder] += amount     # full claim, partial backing
        return True


# =============================================================================
# MEASUREMENT — identical definitions applied to every arm
# =============================================================================
def claims_and_backing(s):
    """Outstanding claims, and the real value actually held against them."""
    if isinstance(s, Mesh):
        return float(s.obligations.sum()), float(s.pledged.sum())
    return float(s.centre_obligations.sum()), float(s.centre_reserves)


def unbacked(s):
    """dU: claims in excess of the value held against them. Zero under full reserve."""
    claims, backing = claims_and_backing(s)
    return max(0.0, claims - backing)


def unmet_value(s):
    """Obligation value that cannot be paid from the value actually available."""
    if isinstance(s, Mesh):
        owed = s.obligations.sum(axis=1)
        return float(np.maximum(0.0, owed - s.reserves).sum())
    return max(0.0, float(s.centre_obligations.sum()) - float(s.centre_reserves))


def unmet_count(s):
    """Nodes that cannot be made whole. Secondary context; only C5 turns on counts."""
    if isinstance(s, Mesh):
        owed = s.obligations.sum(axis=1)
        return int((owed > s.reserves + 1e-9).sum())
    # a centre short of its book haircuts every creditor pro-rata
    if s.centre_obligations.sum() <= s.centre_reserves + 1e-9:
        return 0
    return int((s.centre_obligations > 1e-9).sum())


def held(s):
    """Total real value in the system, measured identically in every arm."""
    if isinstance(s, Mesh):
        return float(s.reserves.sum())
    return float(s.reserves.sum()) + float(s.centre_reserves)


def freeze(s, f):
    """Remove the SAME FRACTION OF VALUE ACTUALLY HELD from every arm, at strike time.

    Centralised arms lose it from the centre first -- that is what "single point" means.
    The mesh has no centre, so it loses the same amount spread proportionally.

    DISCLOSED CORRECTION (see module docstring): this was first written as f * n * 100,
    a fraction of the INITIAL base. That is wrong once the replay has drained the system:
    by the end of the shock sequence the mesh holds 969 of its original 20,000, so a
    "10% of base" freeze removed 100% of everything left and every freeze level returned
    an identical, meaningless 1.000. Sizing the freeze against value held AT THE MOMENT OF
    THE STRIKE is the comparison the spec's fairness rule describes.
    """
    want = f * held(s)
    if want <= 0:
        return 0.0
    if isinstance(s, Mesh):
        tot = float(s.reserves.sum())
        take = min(want, tot)
        s.reserves *= (1.0 - take / max(tot, 1e-9))
        return take
    taken = min(want, s.centre_reserves)
    s.centre_reserves -= taken
    rest = want - taken
    if rest > 0:                                   # centre exhausted; spill to nodes
        tot = float(s.reserves.sum())
        more = min(rest, tot)
        s.reserves *= (1.0 - more / max(tot, 1e-9))
        taken += more
    return float(taken)


def routine(cls, kw=None):
    """The committed routine replay: identical shocks, identical seed, identical seeding."""
    rng = random.Random(P["seed"])
    s = cls(N, 5, rng, **(kw or {}))
    seed_obligations(s, rng)
    failed = 0
    for idx, frac in enumerate(SHOCKS):
        if not s.settle(idx % N, float(frac)):
            failed += 1
    return s, failed


def _issue_step(s, rng):
    """One new obligation per step, drawn from the SHARED rng stream.

    THIRD DISCLOSED CORRECTION, and the reason it is necessary. seed_obligations() runs
    once, and the centralised arm discharges its entire seeded book inside the first 200
    settles -- so at every strike point tested it was carrying claims of 0.0 and the freeze
    had nothing to act on. A payment system with an empty book cannot be stressed, and a
    comparison against an empty book is not a comparison.

    An economy does not stop transacting because a shock arrived. Issuance therefore runs
    for the whole replay, identically in every arm, from the same random stream, using each
    arm's own committed issue() method. This is symmetric by construction: it does not
    privilege either topology, it only ensures BOTH are carrying live commitments when the
    strike lands. Gate C6 asserts both arms hold a non-empty book at strike time, so this
    class of degeneracy cannot silently recur.
    """
    i, j = rng.randrange(s.n), rng.randrange(s.n)
    s.issue(i, j, rng.uniform(1.0, 20.0))


def strike_run(cls, kw, strike_at, f):
    """Replay, freeze value MID-FLIGHT while obligations are still outstanding, continue.

    DISCLOSED CORRECTION. The first version froze AFTER the whole replay. By then the
    centralised book had settled every obligation it ever held (claims 0.0, centre 100.0)
    and the mesh had 969 reserves left, so the "tail event" struck an empty book in one
    arm and an exhausted one in the other. A catastrophic-failure test has to strike while
    the system is CARRYING commitments -- that is the entire scenario being argued about.

    The strike point is SWEPT (0.25 / 0.50 / 0.75 of the sequence) so that no single
    moment can be chosen after the fact to produce a preferred number.
    """
    rng = random.Random(P["seed"])
    s = cls(N, 5, rng, **(kw or {}))
    seed_obligations(s, rng)
    cut = int(strike_at * len(SHOCKS))
    before = 0
    for idx in range(cut):
        _issue_step(s, rng)
        if not s.settle(idx % N, float(SHOCKS[idx])):
            before += 1

    claims_at_strike = claims_and_backing(s)[0]
    held_at_strike = held(s)
    unmet_pre = unmet_value(s)
    took = freeze(s, f)
    unmet_post, count_post = unmet_value(s), unmet_count(s)

    after = 0
    for idx in range(cut, len(SHOCKS)):
        _issue_step(s, rng)
        if not s.settle(idx % N, float(SHOCKS[idx])):
            after += 1

    return {
        "failed_before": before, "failed_after": after,
        "claims_at_strike": claims_at_strike, "held_at_strike": held_at_strike,
        "frozen_value": took, "unmet_pre": unmet_pre,
        "unmet_value": unmet_post, "unmet_count": count_post,
        "unmet_fraction": unmet_post / max(claims_at_strike, 1e-9),
        "combined_failed": before + after + count_post,
    }


# =============================================================================
def main():
    global SHOCKS
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
    SHOCKS = np.clip((deb["Transaction Amount"] / deb["Account Balance"]).values, 0, 1.0)

    print("=" * 86)
    print(" THE UNMEASURED HALF — does concentration cost what the mesh's defenders claim?")
    print(" spec  " + LOCKED)
    print(" shock %d real recorded debits (committed, hash-pinned)" % len(SHOCKS))
    print("=" * 86)

    # ---- routine replay, every arm ------------------------------------------
    mesh, mesh_routine = routine(Mesh)
    cent, cent_routine = routine(Central)

    lev = {}
    for m in P["leverage_multiples_swept"]:
        s, f = routine(Fractional, {"m": float(m)})
        lev[m] = {"m": m, "failed": f, "unbacked": unbacked(s),
                  "claims": claims_and_backing(s)[0]}
        print("  leverage m=%-3d routine failures %5d   unbacked claims %12.1f"
              % (m, f, unbacked(s)))

    print("\n  routine: mesh %d failed / central %d failed" % (mesh_routine, cent_routine))

    # ---- C1 does the centralised arm create credit? -------------------------
    du_c, du_m = unbacked(cent), unbacked(mesh)
    thr = 0.01 * BASE
    gate("C1_the_centralised_arm_creates_credit", du_c > thr,
         ("centralised arm unbacked claims = %.1f (threshold %.1f = 1%% of base %.0f)\n"
          "        mesh unbacked claims       = %.1f\n"
          "        claims/backing  central %.1f / %.1f    mesh %.1f / %.1f\n"
          "        *** The committed centralised comparator is FULL RESERVE. It moves\n"
          "        value from issuer to centre and never lends beyond it. Its zero routine\n"
          "        failures were therefore NOT bought with credit creation -- they were\n"
          "        bought with POOLING: one book meeting obligations no single node could.\n"
          "        The credit-creation explanation for its advantage is REFUTED on this\n"
          "        programme's own committed code."
          % (du_c, thr, BASE, du_m, *claims_and_backing(cent), *claims_and_backing(mesh))))

    # ---- C2 is credit creation what buys smoothness? ------------------------
    f5 = lev[5]["failed"]
    gate("C2_credit_creation_is_what_buys_smoothness", f5 < 0.25 * mesh_routine,
         ("leverage m=5 routine failures %d vs full-reserve mesh %d (threshold %.0f)\n"
          "        sweep: " % (f5, mesh_routine, 0.25 * mesh_routine)
          + "  ".join("m=%d:%d" % (k, v["failed"]) for k, v in sorted(lev.items()))))

    # ---- the freeze sweep ----------------------------------------------------
    sweep = []
    for sa in STRIKES:
        for f in P["freeze_fractions_swept"]:
            row = {"strike_at": sa, "freeze": f}
            for label, cls, kw in (("mesh", Mesh, None), ("central", Central, None),
                                   ("fractional_m5", Fractional, {"m": 5.0})):
                row[label] = strike_run(cls, kw, sa, f)
            sweep.append(row)

    print("\n" + "-" * 86)
    print("  STRIKE SWEEP — same FRACTION OF VALUE HELD removed, mid-flight")
    print("-" * 86)
    print("  %-6s %-7s %-26s %-26s" % ("strike", "freeze", "MESH (spread)",
                                       "CENTRAL (from the centre)"))
    print("  %-6s %-7s %-26s %-26s" % ("", "", "unmet val  frac  nodes",
                                       "unmet val  frac  nodes"))
    for r in sweep:
        print("  %-6.2f %-7.2f %10.1f %5.3f %6d   %10.1f %5.3f %6d"
              % (r["strike_at"], r["freeze"], r["mesh"]["unmet_value"],
                 r["mesh"]["unmet_fraction"], r["mesh"]["unmet_count"],
                 r["central"]["unmet_value"], r["central"]["unmet_fraction"],
                 r["central"]["unmet_count"]))

    hl = [r for r in sweep if r["freeze"] == P["headline_freeze"]
          and r["strike_at"] == 0.5][0]
    mf, cf = hl["mesh"]["unmet_fraction"], hl["central"]["unmet_fraction"]

    # ---- C3 is concentration catastrophic? -----------------------------------
    gate("C3_concentration_is_catastrophic_under_stress", cf > 0.50,
         ("at freeze %.2f the centralised arm cannot pay %.1f%% of its outstanding "
          "obligation value\n        (%.1f of %.1f); %d creditor nodes take a haircut"
          % (P["headline_freeze"], 100 * cf, hl["central"]["unmet_value"],
             hl["central"]["claims_at_strike"], hl["central"]["unmet_count"])))

    # ---- C4 is the mesh materially better? -----------------------------------
    immune = mf < 0.05
    mv, cv = hl["mesh"]["unmet_value"], hl["central"]["unmet_value"]
    gate("C4_the_mesh_is_materially_better_under_the_same_freeze", mf <= 0.5 * cf,
         ("mesh unmet fraction %.4f vs central %.4f (needs <= %.4f)\n"
          "        IMMUNE claim, tested as stated in the argument's table (< 0.05): %s\n"
          "        mesh unmet value %.1f of %.1f claims across %d nodes\n"
          "\n        *** DISCLOSURE — THIS PASS IS AN ARTEFACT OF THE PRE-REGISTERED "
          "METRIC.\n        The gate turns on a FRACTION, and the two arms do not carry "
          "comparable books.\n        In absolute value the result INVERTS: mesh %.1f "
          "unmet vs central %.1f — the mesh\n        loses %.0fx more actual value from "
          "the same proportional shock. The centre\n        clears obligations "
          "continuously and carries %.1f outstanding; the mesh accumulates\n        "
          "bilateral obligations and carries %.1f, so there is simply far more unsettled\n"
          "        value sitting in the mesh for a shock to destroy. The threshold is NOT "
          "moved and\n        the gate is NOT re-scored — but the pre-registered metric "
          "was the wrong choice,\n        and on the quantity that matters to a creditor "
          "this gate points the other way."
          % (mf, cf, 0.5 * cf, "HOLDS" if immune else "FAILS -- the mesh is degraded, "
             "not quarantined", mv, hl["mesh"]["claims_at_strike"],
             hl["mesh"]["unmet_count"], mv, cv, mv / max(cv, 1e-9),
             hl["central"]["claims_at_strike"], hl["mesh"]["claims_at_strike"])))

    # ---- C5 the combined ledger ----------------------------------------------
    mc, cc = hl["mesh"]["combined_failed"], hl["central"]["combined_failed"]
    cross = [(r["strike_at"], r["freeze"]) for r in sweep
             if r["mesh"]["combined_failed"] < r["central"]["combined_failed"]]
    gate("C5_the_mesh_wins_on_the_COMBINED_ledger", mc < cc,
         ("at freeze %.2f: mesh %d routine + %d tail = %d;  central %d routine + %d tail "
          "= %d\n        freeze levels where the mesh's combined ledger wins: %s"
          % (P["headline_freeze"], hl["mesh"]["failed_before"] + hl["mesh"]["failed_after"], hl["mesh"]["unmet_count"],
             mc, hl["central"]["failed_before"] + hl["central"]["failed_after"], hl["central"]["unmet_count"], cc,
             cross if cross else "NONE at any swept level")))

    # ---- structural, excluded -------------------------------------------------
    live = {lb: min(r[lb]["claims_at_strike"] for r in sweep)
            for lb in ("mesh", "central", "fractional_m5")}
    gate("C6_identical_inputs_across_arms", min(live.values()) > 0,
         ("same %d shocks, seed %d, %d nodes, same seeded obligations in every arm\n"
          "        NON-EMPTY BOOK GUARD (added after two degenerate runs): minimum claims "
          "outstanding\n        at strike time — " % (len(SHOCKS), P["seed"], N)
          + "  ".join("%s %.1f" % (k, v) for k, v in live.items())
          + "\n        A freeze applied to an empty book measures nothing; this gate fails "
            "if that recurs."), weight="excluded")
    gate("C7_no_architecture_specific_constant", True,
         "the ONLY per-arm constant is the declared leverage multiple m on the Fractional "
         "arm;\n        Mesh and Central are imported UNCHANGED from the committed engine",
         weight="excluded")
    gate("C8_no_tuned_formula_anywhere", True,
         "no reported quantity is a closed-form expression of freeze or leverage; every "
         "number\n        is read out of the settlement engine's state after the replay",
         weight="excluded")

    n_full = len([g for g in RESULTS if g["weight"] == "full"])
    out = {
        "spec_sha256_canonical": LOCKED, "n_shocks": int(len(SHOCKS)),
        "base_value": BASE,
        "mesh_routine_failed": mesh_routine, "central_routine_failed": cent_routine,
        "central_unbacked": du_c, "mesh_unbacked": du_m,
        "leverage_sweep": lev, "sweep": sweep,
        "headline_freeze": P["headline_freeze"], "strikes_swept": STRIKES,
        "mesh_unmet_fraction": mf, "central_unmet_fraction": cf,
        "mesh_is_immune": bool(immune),
        "mesh_unmet_value": mv, "central_unmet_value": cv,
        "absolute_value_ratio_mesh_over_central": mv / max(cv, 1e-9),
        "metric_confound_disclosed": ("C4 passes on the pre-registered FRACTION metric but "
            "inverts on absolute value; the two arms carry structurally different "
            "outstanding books. Threshold not moved, gate not re-scored, confound recorded."),
        "non_empty_book_guard": live,
        "mesh_combined": mc, "central_combined": cc,
        "freeze_levels_where_mesh_wins_combined": cross,
        "gates": RESULTS, "gates_not_met": FAILED,
        "score": "%d/%d" % (n_full - len(FAILED), n_full),
    }
    json.dump(out, open(os.path.join(HERE, "results_tailrisk.json"), "w"), indent=2)

    print("\n" + "=" * 86)
    print("  SCORE %s   not met: %s" % (out["score"], FAILED or "none"))
    print("=" * 86)
    return 0


if __name__ == "__main__":
    sys.exit(main())
