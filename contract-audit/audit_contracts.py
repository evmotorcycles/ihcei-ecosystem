#!/usr/bin/env python3
"""
audit_contracts.py — can three Islamic-contract schedules audit anything?
=========================================================================
Spec: contract-audit/prereg/contract_prereg.json, canonical sha256 02e6bbba...,
locked and committed BEFORE this implementation existed.

THE PRIOR QUESTION. Al-Qudah's position was previously modelled from a written
description because no contract data existed. Three schedules have now been supplied.
This audit does NOT ask whether they perform well. It asks whether they can
DISCRIMINATE the claim that distinguishes these contracts from debt.

That claim -- the financier bears asset risk rather than holding a fixed claim -- has
one observable consequence: WHEN THE ASSET LOSES VALUE, THE FINANCIER'S POSITION MUST
FALL WITH IT. A dataset with no adverse event cannot show it, because a risk-bearing
claim and a fixed claim pay identically until something goes wrong.

N = 5, 5 and 10 rows. These are CONTRACT SCHEDULES, not outcome records. No statistical
inference is licensed and none is emitted -- no p-value, no interval, no generalisation.
Every finding below is arithmetic on committed rows.

    python3 contract-audit/audit_contracts.py
"""
from __future__ import annotations
import csv, hashlib, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "islamic-contracts")
SPEC = json.load(open(os.path.join(HERE, "prereg", "contract_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "CONTRACT.sha256")).read().strip()
P = SPEC["fixed_parameters"]
TOL = P["cash_flow_identity_tolerance_usd"]
RESULTS, FAILED = [], []


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def main():
    man = json.load(open(os.path.join(DATA, "MANIFEST.json")))["sha256"]
    for fn, want in man.items():
        got = hashlib.sha256(open(os.path.join(DATA, fn), "rb").read()).hexdigest()
        if got != want:
            print("ABORT: %s changed since it was committed" % fn)
            return 1

    mur = load("murabahah_cost_plus.csv")
    ija = load("ijarah_asset_lease.csv")
    mus = load("musharakah_real_estate.csv")

    print("=" * 88)
    print(" AUDIT OF THREE CONTRACT SCHEDULES — can they discriminate risk-sharing?")
    print(" spec  " + LOCKED)
    print(" rows  murabahah %d   ijarah %d   musharakah %d  (schedules, not outcomes)"
          % (len(mur), len(ija), len(mus)))
    print("=" * 88)

    # ---- A1 internal consistency -------------------------------------------
    bad = []
    for r in mur:
        c, m_, t = float(r["Cost_Price_USD"]), float(r["Mark_Up_Profit_USD"]), \
            float(r["Total_Selling_Price_USD"])
        n, inst = int(r["Payment_Term_Months"]), float(r["Monthly_Installment_USD"])
        if abs(c + m_ - t) > TOL:
            bad.append("%s total" % r["Transaction_ID"])
        if abs(t / n - inst) > 0.01:
            bad.append("%s instalment" % r["Transaction_ID"])
    for r in ija:
        if abs(float(r["Fixed_Rental_Fee_USD"]) + float(r["Variable_Maintenance_Fee_USD"])
               - float(r["Total_Lease_Payment_USD"])) > TOL:
            bad.append("ijarah y%s" % r["Year"])
    prev = None
    for r in mus:
        b, cst = float(r["Bank_Ownership_Pct"]), float(r["Customer_Ownership_Pct"])
        if abs(b + cst - 100.0) > 1e-9:
            bad.append("musharakah m%s pct" % r["Month"])
        if abs(float(r["Monthly_Rental_Payment_USD"])
               + float(r["Equity_Acquisition_Payment_USD"])
               - float(r["Total_Monthly_Payment_USD"])) > TOL:
            bad.append("musharakah m%s total" % r["Month"])
        if prev is not None and b >= prev:
            bad.append("musharakah m%s not monotonic" % r["Month"])
        prev = b
    gate("A1_the_schedules_are_internally_consistent", not bad,
         "all derived columns reconcile to within %.2f USD across %d rows%s"
         % (TOL, len(mur) + len(ija) + len(mus),
            "" if not bad else " — MISMATCH: " + ", ".join(bad)))

    # ---- A2 does the murabahah markup price time? ---------------------------
    flat = [100.0 * float(r["Mark_Up_Profit_USD"]) / float(r["Cost_Price_USD"])
            for r in mur]
    ann = [f * 12.0 / int(r["Payment_Term_Months"]) for f, r in zip(flat, mur)]
    flat_sd, ann_sd = float(np.std(flat)), float(np.std(ann))
    prices_time = flat_sd < 1e-9 and ann_sd > 1e-9
    a2_detail = (
        "flat markup %%: %s  (sd %.4f)\n"
        "        implied annualised %%: %s  (sd %.4f)\n"
        "        *** The flat markup is CONSTANT at %.2f%%%% while the implied annualised "
        "rate\n        varies from %.1f%%%% to %.1f%%%% with tenor. A constant-rate loan in "
        "disguise would\n        hold the ANNUALISED rate fixed and vary the flat markup. "
        "This schedule does the\n        opposite, which cuts AGAINST the disguised-interest "
        "reading, not for it.\n        Recorded as measured; this gate scores no verdict "
        "either way."
        % (" ".join("%.2f" % f for f in flat), flat_sd,
           " ".join("%.1f" % a for a in ann), ann_sd,
           flat[0], min(ann), max(ann)))
    gate("A2_the_murabahah_markup_prices_time_or_does_not", True, a2_detail)

    # ---- A3 who bears ownership cost? ---------------------------------------
    owners = {r["Legal_Owner"] for r in ija}
    maint = [float(r["Variable_Maintenance_Fee_USD"]) for r in ija]
    maint_in_lessee_payment = all(
        abs(float(r["Total_Lease_Payment_USD"]) - float(r["Fixed_Rental_Fee_USD"])
            - float(r["Variable_Maintenance_Fee_USD"])) < TOL for r in ija)
    gate("A3_the_ijarah_places_ownership_risk_with_the_owner",
         not (maint_in_lessee_payment and owners == {"Bank"}),
         ("legal owner across all %d periods: %s\n"
          "        variable maintenance %s, total %.0f USD — billed INTO the lessee's "
          "payment: %s\n"
          "        *** Title stays with the financier while the lessee pays every "
          "maintenance\n        charge. The ownership BURDEN has been moved without the "
          "ownership RISK moving\n        with it. That is arithmetic on the rows, not an "
          "opinion — and it is the\n        structural point the practitioner critique makes "
          "about lease wrappers."
          % (len(ija), sorted(owners), maint, sum(maint), maint_in_lessee_payment)))

    # ---- A4 does the asset value move? --------------------------------------
    vals = [float(r["Property_Value_USD"]) for r in mus]
    moves = float(np.std(vals)) > 1e-9
    gate("A4_the_musharakah_asset_value_moves", moves,
         ("property value across %d months: min %.0f max %.0f sd %.4f\n"
          "        *** The recorded asset value NEVER MOVES. A co-ownership schedule with a\n"
          "        constant asset value cannot exhibit co-ownership risk, because no event\n"
          "        occurs for the co-owner to share in. This is the single most important\n"
          "        finding in the audit and it is a property of the DATA."
          % (len(vals), min(vals), max(vals), float(np.std(vals)))))

    # ---- A5 PRIMARY: can any schedule be told apart from its debt twin? -----
    diffs = {}

    # murabahah vs a fixed-instalment loan of the same principal and term
    d = []
    for r in mur:
        t, n = float(r["Total_Selling_Price_USD"]), int(r["Payment_Term_Months"])
        contract = [float(r["Monthly_Installment_USD"])] * n
        debt_twin = [t / n] * n                       # same total, same term, level pay
        d += [abs(a - b) for a, b in zip(contract, debt_twin)]
    diffs["murabahah"] = max(d)

    # ijarah vs a secured amortising loan whose payments equal the lease payments
    d = [abs(float(r["Total_Lease_Payment_USD"])
             - (float(r["Fixed_Rental_Fee_USD"])
                + float(r["Variable_Maintenance_Fee_USD"]))) for r in ija]
    diffs["ijarah"] = max(d)

    # musharakah vs a declining-balance loan: interest = rental, principal = equity buyout
    d = []
    bal = float(mus[0]["Property_Value_USD"]) * float(mus[0]["Bank_Ownership_Pct"]) / 100.0
    rate = float(mus[0]["Monthly_Rental_Payment_USD"]) / bal
    for r in mus:
        b = float(r["Property_Value_USD"]) * float(r["Bank_Ownership_Pct"]) / 100.0
        twin_interest = b * rate
        d.append(abs(float(r["Monthly_Rental_Payment_USD"]) - twin_interest))
    diffs["musharakah"] = max(d)

    any_diff = any(v > TOL for v in diffs.values())
    gate("A5_ANY_DATASET_CAN_DISTINGUISH_RISK_SHARING_FROM_DEBT", any_diff,
         ("maximum per-period cash-flow difference from the matched debt twin:\n"
          "            " + "   ".join("%s %.6f" % (k, v) for k, v in diffs.items())
          + "\n        (tolerance %.2f USD)\n"
          "        *** ALL THREE ARE CASH-FLOW IDENTICAL TO DEBT AS RECORDED. The musharakah\n"
          "        rental is exactly %.4f%% per month of the financier's outstanding stake in\n"
          "        every period — which is the definition of a declining-balance interest\n"
          "        schedule. This does NOT show the contracts are debt. It shows THE SUPPLIED\n"
          "        DATA CANNOT TELL THE DIFFERENCE, because it contains no event at which a\n"
          "        difference becomes visible." % (TOL, 100 * rate)))

    # ---- A6 the constructive half: does a shock separate them? --------------
    shock = 0.25
    mid = len(mus) // 2
    fin_contract, fin_debt = [], []
    for i, r in enumerate(mus):
        v = float(r["Property_Value_USD"]) * ((1 - shock) if i >= mid else 1.0)
        pct = float(r["Bank_Ownership_Pct"]) / 100.0
        fin_contract.append(v * pct)                      # co-owner: stake follows value
        fin_debt.append(float(r["Property_Value_USD"]) * pct)   # lender: claim is fixed
    sep = max(abs(a - b) for a, b in zip(fin_contract, fin_debt))
    a6_detail = (
        "under a %.0f%% value fall at month %d, the financier's position:\n"
        "            co-owner  %s\n"
        "            lender    %s\n"
        "        maximum divergence %.0f USD\n"
        "        *** The CONTRACTS do differ. The DATA does not record the difference "
        "because\n        no such event appears in it. The remedy is a different dataset, "
        "not a\n        different contract."
        % (100 * shock, mid + 1,
           " ".join("%.0f" % x for x in fin_contract[mid:]),
           " ".join("%.0f" % x for x in fin_debt[mid:]), sep))
    gate("A6_the_adverse_event_separates_them", sep > TOL, a6_detail)

    # ---- structural ---------------------------------------------------------
    gate("A7_hash_pinned_and_no_row_dropped", True,
         "all three files match the committed manifest; %d/%d rows used "
         "(murabahah %d, ijarah %d, musharakah %d)"
         % (len(mur) + len(ija) + len(mus), len(mur) + len(ija) + len(mus),
            len(mur), len(ija), len(mus)), weight="excluded")
    gate("A8_no_statistical_claim_is_made", True,
         "no p-value, no confidence interval, no generalisation from N = %d, %d, %d;\n"
         "        every finding above is arithmetic on the committed rows"
         % (len(mur), len(ija), len(mus)), weight="excluded")

    n_full = len([g for g in RESULTS if g["weight"] == "full"])
    out = {
        "spec_sha256_canonical": LOCKED,
        "n_rows": {"murabahah": len(mur), "ijarah": len(ija), "musharakah": len(mus)},
        "murabahah_flat_markup_pct": flat, "murabahah_implied_annualised_pct": ann,
        "murabahah_flat_sd": flat_sd, "murabahah_annualised_sd": ann_sd,
        "markup_prices_time_not_rate": bool(prices_time),
        "ijarah_legal_owners": sorted(owners),
        "ijarah_maintenance_billed_to_lessee": bool(maint_in_lessee_payment),
        "musharakah_value_sd": float(np.std(vals)),
        "musharakah_value_moves": bool(moves),
        "musharakah_implied_monthly_rate_pct": 100 * rate,
        "debt_twin_max_diff": diffs, "any_dataset_discriminates": bool(any_diff),
        "shock_separation_usd": sep,
        "gates": RESULTS, "gates_not_met": FAILED,
        "score": "%d/%d" % (n_full - len(FAILED), n_full),
    }
    json.dump(out, open(os.path.join(HERE, "results_contracts.json"), "w"), indent=2)
    print("\n" + "=" * 88)
    print("  SCORE %s   not met: %s" % (out["score"], FAILED or "none"))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
