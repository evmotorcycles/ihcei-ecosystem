# IHCEI D-Floor Shadow-Mode Efficacy Pilot

**Novora Research Initiative — Open-Source Replication Package**

[![Pre-registered](https://img.shields.io/badge/pre--registered-SHA256%20locked-blue)](docs/PREREGISTRATION.md)
[![Pilot status](https://img.shields.io/badge/pilot-UNTESTED%20%E2%80%94%20awaiting%20channel-orange)](docs/FALSIFIABILITY_LEDGER.md)
[![Coupling prior](https://img.shields.io/badge/coupling%20prior-linear%20(3%2F3%20cohorts)-red)](docs/FALSIFIABILITY_LEDGER.md)

---

## What this repository is

This is the complete, auditable replication package for the **IHCEI Constitutional Kernel** and its pre-registered **Shadow-Mode Efficacy Pilot** — a prospective, blind-adjudicated study of whether enforcing a governance-fidelity floor (the D-floor) on a real institutional channel catches genuine governance failures at an acceptable false-positive rate.

**This repository contains a design, not a result.** The pilot harness is validated and the specification is cryptographically locked. No channel has been instrumented yet. No efficacy numbers exist. The deployment-readiness row is UNTESTED until the pilot runs on a real channel with real adverse events observed prospectively.

---

## Empirical status (honest accounting)

### Coupling cohorts — the descriptive question: does E couple to D linearly or quadratically?

| Domain | N | VIF | ΔAIC (lin − quad) | Verdict |
|---|---|---|---|---|
| Yeast interactome | 4,772 | 1.003 | −48.2 | **QUADRATIC DISCONFIRMED** |
| GitHub repositories | 992 | 1.02 | −3.48 | **QUADRATIC DISCONFIRMED** |
| Statutory domain (US Congress) | 365 | 1.002 | −10.03 | **QUADRATIC DISCONFIRMED** |

All three channel-intact cohorts favour linear coupling. The quadratic has been disconfirmed as a descriptive natural law across every domain where a valid channel-intact test was run.

### The pilot — the prescriptive question: does enforcing the D-floor help?

**Status: UNTESTED.** The pilot tests a different question from the coupling cohorts — whether a D-floor decision rule catches real failures at acceptable cost, regardless of which exponent describes the coupling. This is a classifier-validation question answered against ground truth, not an exponent question. The pilot is exponent-agnostic at the boundary (D → 0 collapses E under either U·D or U·D²). The coupling disconfirmation does not answer it.

---

## Repository structure

```
ihcei-pilot-oss/
├── README.md                          # this file
├── IHCEI_kernel.py                    # constitutional kernel (D/U/E scoring)
├── ihcei_pilot_harness.py             # pilot analysis pipeline (self-test passes)
├── docs/
│   ├── PREREGISTRATION.md             # locked pilot specification
│   ├── PREREGISTRATION_statutory.md   # locked statutory coupling pre-registration
│   └── FALSIFIABILITY_LEDGER.md       # full empirical record, updated after each test
├── data/
│   └── README_data.md                 # data provenance and replication instructions
├── tests/
│   └── test_harness_fixtures.py       # pytest suite — pipeline self-test
└── .github/
    └── workflows/
        └── ci.yml                     # runs harness self-test on every push
```

---

## How to run the harness self-test

```bash
pip install scikit-learn numpy
python ihcei_pilot_harness.py
```

Expected output: all three synthetic fixtures return correct verdicts
(EARNS ENFORCEMENT / DOES NOT EARN ENFORCEMENT / INCONCLUSIVE),
confirming the decision rule is genuinely two-directional before any real data arrives.

The SHA-256 printed by the harness is the **commit-before-window hash**.
It must be committed to `main` before any real channel data is examined.
If any specification parameter changes, the hash changes — making post-hoc
tuning cryptographically detectable.

---

## How to run the statutory coupling replication

```bash
# Requires: US Policy Agendas Project CSVs (see data/README_data.md)
python scripts/statutory_coupling_test.py
```

Expected output: ΔAIC = −10.03, VIF = 1.002, VERDICT: QUADRATIC DISCONFIRMED.

---

## How to start the prospective pilot on a real channel

1. Select a channel carrying governance communications (change-approval, disclosure sign-off, incident triage) with observable downstream outcomes (incident, rollback, enforcement action, audit finding).
2. Run the EGS gate: sample 50 items, confirm EGS ≥ 0.60.
3. Calibrate D_floor on a sealed development split (target FPR = 0.15).
4. Commit the SHA printed by `python ihcei_pilot_harness.py` to this repo before opening the window.
5. Run kernel in shadow mode for 6–12 months, collecting N_adverse ≥ 50 with outcome adjudication blind to D-scores.
6. Run `ihcei_pilot_harness.py` on the real data. Report whatever verdict it returns.

**The three possible verdicts are equally reportable.** DOES NOT EARN ENFORCEMENT is a legitimate outcome, not a failure. INCONCLUSIVE means extend the window. None of them are to be filled by assumption.

---

## Honesty constraints (permanent)

- The quadratic is an **engineering constraint**, not a discovered natural law. Three independent cohorts disconfirmed it descriptively. Enforcing it may still be useful; that is what the pilot tests.
- The pilot result (when it arrives) **cannot launder the coupling result**, and the coupling result cannot launder the pilot result. They are firewalled by design.
- Synthetic data outputs (`np.random.seed(42)`) are pipeline self-tests, not empirical findings, and are never reported as measurements of the world.
- Layer 3 ontological claims (Nafs, OQM, Quranic hermeneutics) carry no evidentiary weight in Layer 1. The empirical pipeline is indifferent to them.

---

## Citation

Mago, L. (2026). *IHCEI Constitutional Kernel: Pre-Registered Coupling Tests and Shadow-Mode Efficacy Pilot.* Novora Research Initiative. GitHub: `evmotorcycles/ihcei-ecosystem`.