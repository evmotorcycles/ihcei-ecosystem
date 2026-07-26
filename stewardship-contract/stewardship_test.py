#!/usr/bin/env python3
"""
stewardship_test.py — contract STRUCTURE over a real failure sequence
=====================================================================
Spec: stewardship-contract/prereg/stewardship_prereg.json, canonical sha256 8bac3099...,
locked and committed BEFORE this runner existed.

Selection is over. Four pre-registered runs failed at picking borrowers, and the reason is
now known: within a capacity tier the fidelity-outcome sign is INVERTED. So this tests
something orthogonal — given THE SAME borrowers and THE SAME real defaults, does the
contract structure change the outcome distribution?

  SC1  selection conceded mechanically      falsifiable:false, excluded from score
  SC2  borrower loss dispersion lower       CAN FAIL
  SC3  worst-case borrower loss bounded     supporting (no-recourse is definitional)
  SC4  risk-sharing COSTS the institution   CAN FAIL — the design's own price
  SC5  can it even stay solvent here?       CAN FAIL — genuinely at risk
  SC6  leverage threshold                   measured quantity, excluded from score
  SC7  tau_v as covenant, not screen        CAN FAIL — the signal's last chance

    python3 stewardship-contract/stewardship_test.py    # stdlib only, offline, $0
"""
from __future__ import annotations
import csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
SPEC = json.load(open(os.path.join(HERE, "prereg", "stewardship_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "STEWARDSHIP.sha256")).read().strip()
P = SPEC["contract_parameters_fixed_before_running"]
RESULTS, FAILED = [], []


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = {"full": "", "supporting": "   [supporting only]",
           "excluded": "   [construction/definitional — excluded from score]"}[weight]
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


def stdev(v):
    n = len(v)
    m = sum(v) / n
    return (sum((x - m) ** 2 for x in v) / n) ** 0.5


def run_debt(rows):
    """Priority claim. Yield insulated from outcome; shortfall pushed to the borrower."""
    size, r, phi = P["contract_size"], P["debt_markup_r"], P["recovery_fraction_on_default_phi"]
    g, bs = P["success_growth_g"], P["borrower_stake_fraction"]
    inst, borrowers = 0.0, []
    for row in rows:
        claim = size * (1 + r)
        if not row["default"]:
            proceeds = size * (1 + g)
            inst += claim - size                       # institution's net gain
            borrowers.append(proceeds - claim)         # borrower keeps the residual
        else:
            recovered = size * phi
            inst += recovered - size                   # institution's net loss
            # recourse: borrower loses their stake AND owes the shortfall
            borrowers.append(-(size * bs) - (claim - recovered))
    return inst, borrowers


def run_equity(rows):
    """Proportional co-ownership, no recourse. Loss shared in the same ratio as gain."""
    size, phi, g = P["contract_size"], P["recovery_fraction_on_default_phi"], P["success_growth_g"]
    bs, ins = P["borrower_stake_fraction"], P["institution_stake_fraction"]
    inst, borrowers = 0.0, []
    for row in rows:
        outcome = size * (1 + g) if not row["default"] else size * phi
        pnl = outcome - size                            # total project gain or loss
        inst += pnl * ins
        borrowers.append(pnl * bs)                      # liability ends at the stake
    return inst, borrowers


def run_covenant(rows):
    """SC7: exit on a latency breach, paying a real haircut on every trigger."""
    size, phi, g = P["contract_size"], P["recovery_fraction_on_default_phi"], P["success_growth_g"]
    ins = P["institution_stake_fraction"]
    thr, cut = P["covenant_tau_v_threshold_days"], P["covenant_exit_haircut"]
    inst, exits, exits_that_were_wrong = 0.0, 0, 0
    for row in rows:
        if row["tau_v"] > thr:
            exits += 1
            if not row["default"]:
                exits_that_were_wrong += 1
            inst += -(size * ins) * cut                 # pay the haircut, avoid the outcome
        else:
            pnl = (size * (1 + g) if not row["default"] else size * phi) - size
            inst += pnl * ins
    return inst, exits, exits_that_were_wrong


def main():
    raw = list(csv.DictReader(open(CSV)))
    rows = [{"tau_v": float(r["tau_v"]), "default": 1 - int(r["E"])} for r in raw]
    N = len(rows)
    nd = sum(r["default"] for r in rows)

    print("=" * 84)
    print(" THE STEWARDSHIP CONTRACT LAYER — structure, with selection held fixed")
    print(" spec  " + LOCKED)
    print(" data  data/github/govphys_quadratic_results.csv (recovered + verified 7/7)")
    print("=" * 84)
    print("\n N=%d  real defaults=%d (%.1f%%)  — the SAME borrowers enter both books"
          % (N, nd, 100 * nd / N))
    print(" contract %.0f | borrower stake %.0f%% | g=%.2f | recovery phi=%.2f | debt markup r=%.2f"
          % (P["contract_size"], 100 * P["borrower_stake_fraction"], P["success_growth_g"],
             P["recovery_fraction_on_default_phi"], P["debt_markup_r"]))

    debt_inst, debt_borrowers = run_debt(rows)
    eq_inst, eq_borrowers = run_equity(rows)

    # ---- SC1  honesty gate --------------------------------------------------------
    gate("SC1_selection_is_conceded_mechanically",
         len(debt_borrowers) == len(eq_borrowers) == N,
         "both books hold the identical %d borrowers and the identical %d real defaults; "
         "no fidelity quantity reorders, excludes or reweights anyone" % (N, nd),
         weight="excluded")

    # ---- SC2 ----------------------------------------------------------------------
    sd_d, sd_e = stdev(debt_borrowers), stdev(eq_borrowers)
    gate("SC2_borrower_loss_dispersion_is_lower_under_equity", sd_e < sd_d,
         "stdev of borrower net outcome:  debt %.2f  vs  equity %.2f  (ratio %.2fx)"
         % (sd_d, sd_e, sd_d / sd_e if sd_e else float("inf")))

    # ---- SC3 ----------------------------------------------------------------------
    gate("SC3_worst_case_borrower_loss_is_bounded", min(eq_borrowers) > min(debt_borrowers),
         "worst single borrower outcome:  debt %.2f  vs  equity %.2f  — under equity "
         "liability ends at the %.0f stake" % (min(debt_borrowers), min(eq_borrowers),
                                               P["contract_size"] * P["borrower_stake_fraction"]),
         weight="supporting")

    # ---- SC4  the design's own price ------------------------------------------------
    gate("SC4_risk_sharing_costs_the_institution_capital", eq_inst < debt_inst,
         "institution terminal P&L:  debt %+.0f  vs  equity %+.0f  (difference %+.0f).\n"
         "        A pass here is the design's PRICE, measured — not a win."
         % (debt_inst, eq_inst, eq_inst - debt_inst))

    # ---- SC5  solvency ---------------------------------------------------------------
    deployed = N * P["contract_size"] * P["institution_stake_fraction"]
    eq_capital = deployed + eq_inst
    gate("SC5_can_a_risk_sharing_institution_even_survive_this_population",
         eq_capital > 0,
         "deployed %.0f, terminal capital %.0f (%.1f%% of capital retained) over a "
         "%.1f%% default population" % (deployed, eq_capital,
                                        100 * eq_capital / deployed, 100 * nd / N))

    # ---- SC6  leverage threshold, measured -------------------------------------------
    # m is the leverage ratio assets/equity. Own capital C = book/m; the remainder of the
    # book is funded by depositor claims. m = 1 IS full reserve: no depositor is funding
    # the book at all, so no depositor can be short.
    # (Bug fix, disclosed: an earlier revision divided deposits by m, which made shortfall
    # FALL as leverage rose — backwards. This gate is excluded from the score, so no score
    # changes; only the reported quantity is corrected to match what the spec describes.)
    book = N * P["contract_size"]
    scan, first_insolvent = [], None
    for m in P["leverage_multipliers_scanned"]:
        own_capital = book / m
        deposits = book - own_capital
        assets = max(0.0, book + debt_inst)         # the book after its realised P&L
        shortfall = max(0.0, deposits - assets)
        scan.append({"multiplier": m, "own_capital": round(own_capital, 0),
                     "depositor_claims": round(deposits, 0),
                     "recoverable": round(assets, 0),
                     "depositor_shortfall": round(shortfall, 0)})
        if shortfall > 0 and first_insolvent is None:
            first_insolvent = m
    gate("SC6_full_reserve_bounds_systemic_shortfall", True,
         "leveraged DEBT institution first shows a depositor shortfall at multiplier %s; "
         "full-reserve equity issues no claim exceeding deposits so its shortfall is "
         "identically 0 — definitional, reported not scored.\n        scan: %s"
         % (first_insolvent if first_insolvent else "none in scanned range",
            ", ".join("m=%.0f short=%.0f" % (s["multiplier"], s["depositor_shortfall"])
                      for s in scan)), weight="excluded")

    # ---- SC7  the signal's last chance -----------------------------------------------
    cov_inst, exits, wrong = run_covenant(rows)
    gate("SC7_tau_v_as_a_covenant_trigger_rather_than_an_admission_gate",
         cov_inst > eq_inst,
         "covenant P&L %+.0f  vs  hold-everything baseline %+.0f  (gain %+.0f)\n"
         "        triggered on %d of %d contracts; %d of those exits were on borrowers who "
         "would NOT have defaulted (false positives, each charged the full %.0f%% haircut)"
         % (cov_inst, eq_inst, cov_inst - eq_inst, exits, N, wrong,
            100 * P["covenant_exit_haircut"]))

    # ---- POST-HOC diagnostic. NOT a gate, NOT scored, NOT pre-registered. -----------
    # SC4 predicted equity would cost the institution capital. It did not. This sweep
    # exists only to explain WHY, and to mark the boundary where the prediction would
    # have held. It was written AFTER seeing the result and must never be cited as
    # confirmation of anything.
    print("\n" + "-" * 84)
    print(" POST-HOC (not a gate, not scored, written after seeing SC4 fail):")
    print(" why did the priority claim lose to proportional participation?")
    sweep = []
    base_phi, base_r = P["recovery_fraction_on_default_phi"], P["debt_markup_r"]
    for phi in (0.2, 0.4, 0.6, 0.8, 0.95):
        P["recovery_fraction_on_default_phi"] = phi
        d, _ = run_debt(rows)
        e, _ = run_equity(rows)
        sweep.append({"recovery_phi": phi, "debt_pnl": round(d), "equity_pnl": round(e),
                      "debt_wins": bool(d > e)})
        print("   recovery phi=%.2f   debt %+8.0f   equity %+8.0f   -> %s"
              % (phi, d, e, "DEBT better" if d > e else "EQUITY better"))
    P["recovery_fraction_on_default_phi"], P["debt_markup_r"] = base_phi, base_r
    print(" Reading: a priority claim is only worth having if the asset can actually be")
    print(" recovered. At phi=0.40 the lender still eats 600 per failure while giving up")
    print(" all upside; proportional participation captures the 20%% gains on survivors.")
    print(" The debt structure overtakes equity only as recovery approaches certainty.")
    print("-" * 84)

    scored = [r for r in RESULTS if r["weight"] != "excluded"]
    met = sum(1 for r in scored if r["pass"])
    print("\n" + "=" * 84)
    print(" RESULT: %d/%d scored gates met  (SC1 and SC6 excluded — they cannot fail)"
          % (met, len(scored)))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    print("\n SUBSTRATE LIMIT, declared in the spec: GitHub repositories are a poor analogue")
    print(" for borrowers — no balance sheet, no collateral, no obligation to repay. These")
    print(" are statements about contract mechanics over a real failure sequence, NOT about")
    print(" credit markets.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED,
               "csv_sha256": hashlib.sha256(open(CSV, "rb").read()).hexdigest(),
               "N": N, "defaults": nd, "default_rate": round(nd / N, 4),
               "debt_institution_pnl": round(debt_inst, 2),
               "equity_institution_pnl": round(eq_inst, 2),
               "equity_terminal_capital": round(eq_capital, 2),
               "capital_retained_fraction": round(eq_capital / deployed, 4),
               "borrower_stdev_debt": round(sd_d, 2),
               "borrower_stdev_equity": round(sd_e, 2),
               "borrower_worst_debt": round(min(debt_borrowers), 2),
               "borrower_worst_equity": round(min(eq_borrowers), 2),
               "leverage_scan": scan, "first_insolvent_multiplier": first_insolvent,
               "covenant_pnl": round(cov_inst, 2), "covenant_exits": exits,
               "covenant_false_positive_exits": wrong,
               "posthoc_recovery_sweep_NOT_A_GATE": sweep,
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_stewardship.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
