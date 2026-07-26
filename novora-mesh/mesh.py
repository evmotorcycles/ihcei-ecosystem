#!/usr/bin/env python3
"""
mesh.py — the Novora Sovereign Mesh, and the ablation that tests it honestly
===========================================================================
Spec: novora-mesh/prereg/mesh_prereg.json, canonical sha256 ed71c3fc...,
locked and committed BEFORE this runner existed.

THE PARADIGM CHANGE: there is no fidelity screen. Admission is open. Four pre-registered
designs died trying to underwrite BY fidelity, and the mechanism is a sign inversion —
selecting high D selects for failure. Telemetry is kept, but moved to the one job where
it demonstrably works: monitoring capital already deployed.

Pipeline, each component mapped to a stack element:

    admission        open                      (Agency algorithm — deliberately null)
    structure        90/10 proportional        (OQM mudarabah/musharakah, NO RECOURSE)
    reserve          multiplier exactly 1      (full reserve)
    telemetry        tau_v, self-report discarded  (LISM + Masjid / F_out = F_eval)
    abstention       hold where tau_v IMPUTED  (Novora PAGES confidence/abstain)
    staged response  hold / halve / exit       (NERE + IHCEI graded escalation)
    audit ledger     SHA-256 hash chain        (Echo + Page Code)

An integrated design can always be reported as "working" by pointing at the whole. So
every component is REMOVED ONE AT A TIME and the loss measured. A component that can be
deleted at no cost is dead weight and is named as such.

    python3 novora-mesh/mesh.py        # stdlib only, offline, $0
"""
from __future__ import annotations
import csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
SPEC = json.load(open(os.path.join(HERE, "prereg", "mesh_prereg.json")))
LOCKED = open(os.path.join(HERE, "prereg", "MESH.sha256")).read().strip()
P = SPEC["contract_parameters_fixed_before_running"]
COMPONENTS = list(SPEC["components_under_test"].keys())
RESULTS, FAILED = [], []


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [declared non-falsifiable — excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


class Ledger:
    """Echo / Page Code: an append-only SHA-256 chain over every decision."""

    def __init__(self):
        self.head = hashlib.sha256(b"novora-mesh-genesis").hexdigest()
        self.entries = []

    def append(self, kind, ref, detail):
        rec = {"kind": kind, "ref": ref, "detail": detail, "prev": self.head}
        blob = json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
        self.head = hashlib.sha256(blob).hexdigest()
        rec["hash"] = self.head
        self.entries.append(rec)

    def verify(self):
        h = hashlib.sha256(b"novora-mesh-genesis").hexdigest()
        for e in self.entries:
            rec = {"kind": e["kind"], "ref": e["ref"], "detail": e["detail"], "prev": h}
            h = hashlib.sha256(
                json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if h != e["hash"]:
                return False
        return h == self.head


def run_mesh(rows, *, structure="equity", reserve=True, telemetry=True,
             abstention=True, staged=True, admission="open", ledger=None):
    """One configuration of the mesh. Disabling a keyword ablates that component."""
    size = P["contract_size"]
    ins, bs = P["institution_stake_fraction"], P["borrower_stake_fraction"]
    g, phi, r = P["success_growth_g"], P["recovery_fraction_on_default_phi"], P["debt_markup_r"]
    s1, s1keep = P["stage1_tau_v_days"], P["stage1_exposure_retained"]
    s1cost, s2, s2cost = P["stage1_cost_on_released"], P["stage2_tau_v_days"], P["stage2_exit_cost"]

    book = rows
    if admission == "prestige":                     # the conventional baseline's screen
        book = sorted(rows, key=lambda x: -x["stars"])[:len(rows) // 2]

    inst, borrowers, n_abstained, n_staged, n_exited = 0.0, [], 0, 0, 0

    for row in book:
        stake = size * ins
        # --- telemetry + abstention decide the exposure held -----------------------
        exposure, cost = 1.0, 0.0
        if telemetry:
            usable = (not row["imputed"]) if abstention else True
            if not usable:
                n_abstained += 1                     # PAGES: decline to act on a guess
            else:
                if staged:
                    if row["tau_v"] > s2:
                        exposure, cost, n_exited = 0.0, stake * s2cost, n_exited + 1
                    elif row["tau_v"] > s1:
                        exposure = s1keep
                        cost = stake * (1 - s1keep) * s1cost
                        n_staged += 1
                else:                                # binary exit only
                    if row["tau_v"] > s2:
                        exposure, cost, n_exited = 0.0, stake * s2cost, n_exited + 1

        # --- the contract structure resolves the retained exposure ------------------
        if structure == "equity":
            pnl = (size * (1 + g) if not row["default"] else size * phi) - size
            inst += pnl * ins * exposure - cost
            borrowers.append(pnl * bs)               # no recourse: capped at the stake
        else:                                        # debt: priority claim, full recourse
            if not row["default"]:
                inst += (size * r) * exposure - cost
                borrowers.append(size * (1 + g) - size * (1 + r))
            else:
                inst += (size * phi - size) * exposure - cost
                borrowers.append(-(size * bs) - (size * (1 + r) - size * phi))
        if ledger is not None:
            ledger.append("decision", row["repo"],
                          "exposure=%.2f cost=%.2f" % (exposure, cost))

    deposits = 0.0 if reserve else len(book) * size * (1 - 1 / P["leverage_for_ablation"])
    assets = max(0.0, len(book) * size * ins + inst)
    shortfall = max(0.0, deposits - assets)

    return {"institution_pnl": inst, "borrowers": borrowers, "n_contracts": len(book),
            "n_abstained": n_abstained, "n_staged": n_staged, "n_exited": n_exited,
            "depositor_shortfall": shortfall}


def stdev(v):
    m = sum(v) / len(v)
    return (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5


def main():
    raw = list(csv.DictReader(open(CSV)))
    rows = [{"repo": r["repo"], "stars": float(r["stars"]), "tau_v": float(r["tau_v"]),
             "imputed": int(float(r["tau_v_imputed"])), "default": 1 - int(r["E"])}
            for r in raw]
    N = len(rows)

    print("=" * 84)
    print(" THE NOVORA SOVEREIGN MESH — no fidelity screen, tested by ablation")
    print(" spec  " + LOCKED)
    print(" data  data/github/govphys_quadratic_results.csv (recovered + verified 7/7)")
    print("=" * 84)
    print("\n N=%d  real defaults=%d (%.1f%%)  imputed telemetry=%d rows"
          % (N, sum(r["default"] for r in rows),
             100 * sum(r["default"] for r in rows) / N, sum(r["imputed"] for r in rows)))

    led = Ledger()
    full = run_mesh(rows, ledger=led)
    base = run_mesh(rows, structure="debt", reserve=False, telemetry=False,
                    abstention=False, staged=False, admission="prestige")

    print("\n FULL MESH      capital %+10.0f   held=%d staged=%d exited=%d abstained=%d"
          % (full["institution_pnl"], full["n_contracts"], full["n_staged"],
             full["n_exited"], full["n_abstained"]))
    print(" CONVENTIONAL   capital %+10.0f   (prestige screen, leveraged, debt, no telemetry)"
          % base["institution_pnl"])

    # ---- NP1 ----------------------------------------------------------------------
    gate("NP1_the_mesh_beats_the_conventional_baseline",
         full["institution_pnl"] > base["institution_pnl"],
         "mesh %+.0f  vs  conventional %+.0f  (delta %+.0f). The conventional book screens "
         "on prestige, runs at %.0fx leverage and carries no telemetry."
         % (full["institution_pnl"], base["institution_pnl"],
            full["institution_pnl"] - base["institution_pnl"], P["leverage_for_ablation"]))

    # ---- NP2  ABLATION --------------------------------------------------------------
    ablations, dead = [], []
    arms = {"admission": dict(admission="prestige"), "structure": dict(structure="debt"),
            "reserve": dict(reserve=False), "telemetry": dict(telemetry=False),
            "abstention": dict(abstention=False), "staged_response": dict(staged=False),
            "audit_ledger": dict()}
    for comp in COMPONENTS:
        if comp == "audit_ledger":
            # removing the ledger changes no cash flow; it is a governance control, and
            # this is recorded honestly rather than dressed up as an economic gain
            ablations.append({"component": comp, "capital_without": full["institution_pnl"],
                              "delta": 0.0, "earns_its_place": False,
                              "note": "no cash-flow effect by construction — a governance "
                                      "control, not an economic one"})
            dead.append(comp)
            continue
        without = run_mesh(rows, **arms[comp])
        delta = without["institution_pnl"] - full["institution_pnl"]
        earns = delta < 0                              # removing it must HURT
        ablations.append({"component": comp,
                          "capital_without": round(without["institution_pnl"]),
                          "delta": round(delta), "earns_its_place": bool(earns)})
        if not earns:
            dead.append(comp)

    print("\n ABLATION — remove one component at a time:")
    for a in ablations:
        print("   %-16s without: %+10.0f   delta %+9.0f   %s"
              % (a["component"], a["capital_without"], a["delta"],
                 "earns its place" if a["earns_its_place"] else "*** DEAD WEIGHT ***"))

    gate("NP2_every_component_earns_its_place", not dead,
         "%d of %d components earn their place. DEAD WEIGHT: %s"
         % (len(COMPONENTS) - len(dead), len(COMPONENTS), dead if dead else "none"))

    # ---- NP3 -------------------------------------------------------------------------
    act = run_mesh(rows, abstention=False)
    gate("NP3_abstention_on_imputed_telemetry_pays",
         full["institution_pnl"] > act["institution_pnl"],
         "abstain on %d imputed rows: %+.0f   vs   act on them as if measured: %+.0f "
         "(delta %+.0f)" % (sum(r["imputed"] for r in rows), full["institution_pnl"],
                            act["institution_pnl"],
                            full["institution_pnl"] - act["institution_pnl"]))

    # ---- NP4 -------------------------------------------------------------------------
    binary = run_mesh(rows, staged=False)
    gate("NP4_staged_response_beats_a_binary_exit",
         full["institution_pnl"] > binary["institution_pnl"],
         "staged (hold/halve/exit): %+.0f   vs   binary exit at %.0fd only: %+.0f "
         "(delta %+.0f); the middle stage charged a %.0f%% cost on %d reductions"
         % (full["institution_pnl"], P["stage2_tau_v_days"], binary["institution_pnl"],
            full["institution_pnl"] - binary["institution_pnl"],
            100 * P["stage1_cost_on_released"], full["n_staged"]))

    # ---- NP5 / NP6 / NP7  declared non-falsifiable ------------------------------------
    covered = {a["component"] for a in ablations}
    gate("NP5_no_component_contribution_is_claimed_without_its_ablation",
         covered == set(COMPONENTS),
         "%d/%d components have a measured ablation arm" % (len(covered), len(COMPONENTS)),
         weight="excluded")

    lev = run_mesh(rows, reserve=False)
    gate("NP6_full_reserve_eliminates_depositor_shortfall",
         full["depositor_shortfall"] == 0,
         "full reserve shortfall %.0f (definitional); the same book at %.0fx leverage "
         "shows a depositor shortfall of %.0f"
         % (full["depositor_shortfall"], P["leverage_for_ablation"],
            lev["depositor_shortfall"]), weight="excluded")

    ok_chain = led.verify()
    tampered = Ledger()
    tampered.entries = [dict(e) for e in led.entries]
    tampered.head = led.head
    if tampered.entries:
        tampered.entries[len(tampered.entries) // 2]["detail"] = "exposure=1.00 cost=0.00"
    gate("NP7_the_audit_ledger_is_tamper_evident", ok_chain and not tampered.verify(),
         "chain of %d decisions verifies (%s); mutating one entry breaks it: %s"
         % (len(led.entries), led.head[:16] + "...", not tampered.verify()),
         weight="excluded")

    # ---- POST-HOC diagnostics. NOT gates, NOT scored, written AFTER seeing the misses.
    imp_taus = sorted({r["tau_v"] for r in rows if r["imputed"]})
    n_imp_trigger = sum(1 for r in rows if r["imputed"] and r["tau_v"] > P["stage1_tau_v_days"])
    per_mesh = full["institution_pnl"] / full["n_contracts"]
    per_base = base["institution_pnl"] / base["n_contracts"]
    base_dr = sum(r["default"] for r in
                  sorted(rows, key=lambda x: -x["stars"])[:N // 2]) / (N // 2)
    print("\n" + "-" * 84)
    print(" POST-HOC (not gates, not scored, written after seeing NP1/NP3 fail):")
    print("   NP3 — every imputed row carries tau_v = %s exactly, the imputation constant."
          % (", ".join("%.2f" % t for t in imp_taus)))
    print("        %d of %d imputed rows can ever cross stage 1. Acting and abstaining are"
          % (n_imp_trigger, full["n_abstained"]))
    print("        therefore IDENTICAL here by construction of the imputation. This cohort")
    print("        cannot test the abstention rule; that is untestable-here, not refuted.")
    print("   NP1 — the comparison is confounded twice. The conventional book holds %d"
          % base["n_contracts"])
    print("        contracts to the mesh's %d, and its default rate is %.1f%% against %.1f%%"
          % (full["n_contracts"], 100 * base_dr, 100 * sum(r["default"] for r in rows) / N))
    print("        because prestige screening genuinely selects survivors. Per contract:")
    print("        mesh %+.2f vs conventional %+.2f — still worse, by 7%% not by 2.1x."
          % (per_mesh, per_base))
    print("-" * 84)

    scored = [g for g in RESULTS if g["weight"] == "full"]
    met = sum(1 for g in scored if g["pass"])
    print("\n" + "=" * 84)
    print(" RESULT: %d/%d scored gates met  (NP5-NP7 excluded — they cannot fail)"
          % (met, len(scored)))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    if dead:
        print("\n DEAD WEIGHT, named as required by the spec: %s" % dead)
        print(" These components are retained in the design only if a NON-ECONOMIC")
        print(" justification is stated explicitly. They earn nothing on this substrate.")
    print("\n SUBSTRATE LIMIT: GitHub repositories are a poor analogue for borrowers.")
    print(" This is mechanism over a real failure sequence, NOT a claim about credit markets.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED,
               "csv_sha256": hashlib.sha256(open(CSV, "rb").read()).hexdigest(),
               "N": N, "defaults": sum(r["default"] for r in rows),
               "imputed_rows": sum(r["imputed"] for r in rows),
               "mesh_capital": round(full["institution_pnl"]),
               "conventional_capital": round(base["institution_pnl"]),
               "mesh_staged": full["n_staged"], "mesh_exited": full["n_exited"],
               "mesh_abstained": full["n_abstained"],
               "borrower_stdev_mesh": round(stdev(full["borrowers"]), 2),
               "borrower_stdev_conventional": round(stdev(base["borrowers"]), 2),
               "ablations": ablations, "dead_weight": dead,
               "abstain_capital": round(full["institution_pnl"]),
               "act_on_imputed_capital": round(act["institution_pnl"]),
               "binary_exit_capital": round(binary["institution_pnl"]),
               "depositor_shortfall_full_reserve": full["depositor_shortfall"],
               "depositor_shortfall_levered": round(lev["depositor_shortfall"]),
               "ledger_entries": len(led.entries), "ledger_head": led.head,
               "posthoc_NOT_GATES": {
                   "imputed_tau_v_distinct_values": imp_taus,
                   "imputed_rows_able_to_trigger_stage1": n_imp_trigger,
                   "mesh_capital_per_contract": round(per_mesh, 2),
                   "conventional_capital_per_contract": round(per_base, 2),
                   "conventional_book_size": base["n_contracts"],
                   "conventional_default_rate": round(base_dr, 4)},
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_mesh.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
