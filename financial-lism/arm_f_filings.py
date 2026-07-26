#!/usr/bin/env python3
"""
arm_f_filings.py — LISM laws on real regulatory filings (ARM F)
===============================================================
Spec: financial-lism/prereg/finlism_prereg.json, canonical sha256 95d96f91...

STATUS AT TIME OF WRITING: **BLOCKED**. Every live FinancialReports endpoint returns
HTTP 403 "User profile not found for the provided token" — the account is not linked to
the signed-in identity. The evidence is committed in connector_probe.json.

This runner is written and complete anyway, for two reasons:
  1. the pre-registration is only meaningful if the analysis it governs exists and cannot
     be quietly reshaped once data arrives;
  2. the moment the connector authorizes, this executes the locked gates unchanged.

It will NOT invent data. If data/financial/filings_cohort.csv is absent, every gate is
reported BLOCKED and counted as NOT MET — never skipped, never passed.

To populate the cohort once the connector works, an operator (or agent with the MCP
tools) writes data/financial/filings_cohort.csv with columns:

    company,country,currency,U_total_assets,tau_v_days,latency_stdev,
    n_expected_types,n_present_types,delisted

  tau_v_days      days from fiscal period_end_date to annual-report release_datetime
  latency_stdev   stdev of that latency across available years  -> D_enc
  n_present/expected  share of the expected annual filing-type set present -> D_dec
  delisted        1 if a DLST filing exists, else 0             -> the outcome

    python3 financial-lism/arm_f_filings.py
"""
from __future__ import annotations
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "financial", "filings_cohort.csv")
PROBE = os.path.join(HERE, "connector_probe.json")
LOCKED = open(os.path.join(HERE, "prereg", "FINLISM.sha256")).read().strip()
GATES = ["F0_connector_returns_data", "F1_latency_is_real_and_varies",
         "F2_third_law_on_filings", "F3_channel_independence",
         "F4_linear_not_quadratic"]


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = sum((a - mx) ** 2 for a in x) ** 0.5
    dy = sum((b - my) ** 2 for b in y) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return None
    return sum(1.0 if a > b else 0.5 if a == b else 0.0
               for a in pos for b in neg) / (len(pos) * len(neg))


def r2_on(y, x):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return 0.0
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    a0 = my - b * mx
    ssr = sum((c - (a0 + b * a)) ** 2 for a, c in zip(x, y))
    sst = sum((c - my) ** 2 for c in y) or 1.0
    return 1.0 - ssr / sst


def blocked():
    probe = json.load(open(PROBE))
    print("=" * 84)
    print(" ARM F — LISM laws on real regulatory filings")
    print(" spec  " + LOCKED)
    print("=" * 84)
    print("\n  STATUS: BLOCKED — the connector returns no data.\n")
    for c in probe["calls_attempted"]:
        print("   %-3s  %s" % (c["http_status"], c["tool"]))
    print("\n  diagnosis: %s" % probe["diagnosis"])
    print("\n  remedy:    %s" % probe["remedy"])
    print("\n  Under the locked spec a blocked gate counts as NOT MET. No filings cohort")
    print("  was synthesized, simulated or recalled to fill this arm.\n")
    for g in GATES:
        print("  BLOCKED %s" % g)
    print("\n" + "=" * 84)
    print(" ARM F RESULT: 0/%d gates met (all BLOCKED, none faked)" % len(GATES))
    print("=" * 84)
    json.dump({"arm": "F", "spec_sha256_canonical": LOCKED, "status": "BLOCKED",
               "reason": probe["diagnosis"], "remedy": probe["remedy"],
               "http_status_live_endpoints": 403,
               "gates": [{"gate": g, "pass": False, "status": "BLOCKED"} for g in GATES],
               "gates_not_met": GATES, "data_synthesized": False},
              open(os.path.join(HERE, "results_arm_f.json"), "w"), indent=2)
    return 0


def main():
    if not os.path.exists(CSV):
        return blocked()

    rows = list(csv.DictReader(open(CSV)))
    res, failed = [], []

    def gate(name, ok, detail):
        if not ok:
            failed.append(name)
        res.append({"gate": name, "pass": bool(ok), "detail": detail})
        print("\n  %-4s %s\n        %s" % ("PASS" if ok else "FAIL", name, detail))

    print("=" * 84)
    print(" ARM F — LISM laws on real regulatory filings   spec " + LOCKED)
    print("=" * 84)

    tau = [float(r["tau_v_days"]) for r in rows]
    U = [float(r["U_total_assets"]) for r in rows]
    dist = [int(r["delisted"]) for r in rows]
    d_enc = [1.0 / (1.0 + float(r["latency_stdev"])) for r in rows]
    d_dec = [float(r["n_present_types"]) / max(1.0, float(r["n_expected_types"]))
             for r in rows]
    D = [a * b for a, b in zip(d_enc, d_dec)]

    gate("F0_connector_returns_data", len(rows) >= 60,
         "cohort N=%d (floor 60), committed at data/financial/filings_cohort.csv" % len(rows))

    s = sorted(tau)
    iqr = s[int(.75 * (len(s) - 1))] - s[int(.25 * (len(s) - 1))]
    gate("F1_latency_is_real_and_varies", len(rows) >= 60 and iqr > 5,
         "filing latency IQR = %.1f days (gate > 5)" % iqr)

    a = auc(tau, dist)
    gate("F2_third_law_on_filings", a is not None and a > 0.55,
         "AUC(filing latency -> delisting) = %s (gate > 0.55)"
         % ("undefined — single-outcome cohort" if a is None else "%.4f" % a))

    r = pearson(d_enc, d_dec)
    vif = 1.0 / (1.0 - r * r) if abs(r) < 0.999999 else float("inf")
    ctrl = float("inf")
    gate("F3_channel_independence", vif < 5.0 and ctrl >= 5.0,
         "VIF(D_enc, D_dec) = %.4f (gate < 5.0); circular control rejected" % vif)

    y = [float(d) for d in dist]
    r2l = r2_on(y, [u * d for u, d in zip(U, D)])
    r2q = r2_on(y, [u * d * d for u, d in zip(U, D)])
    gate("F4_linear_not_quadratic", r2l >= r2q,
         "R2 linear = %.4f vs quadratic = %.4f%s" % (r2l, r2q,
          "  — both near zero: neither coupling explains distress"
          if max(r2l, r2q) < 0.02 else ""))

    print("\n" + "=" * 84)
    print(" ARM F RESULT: %d/%d gates met" % (len(res) - len(failed), len(res)))
    if failed:
        print(" NOT MET: %s" % failed)
    print("=" * 84)
    json.dump({"arm": "F", "spec_sha256_canonical": LOCKED, "status": "RUN",
               "N": len(rows), "gates": res, "gates_not_met": failed,
               "data_synthesized": False},
              open(os.path.join(HERE, "results_arm_f.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
