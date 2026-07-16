#!/usr/bin/env python3
"""
nere_epistemic_demo.py — NERE as the runtime face of the epistemic firewall
===========================================================================
The methodology experiment (methodology_experiment.py) shows the four-pillar
firewall killing false STATISTICAL signals. This demo shows the shipped NERE
engine (nere_engine_v3, uploaded stack) catching the RHETORICAL signature of the
same vending-machine science — the "just trust / proves / don't verify / experts
confirm" language that pressures a reader to surrender their own judgement.

Each pillar has a rhetorical tell. We score the manipulative phrasing against its
disciplined counterpart with the real NERE posterior band and show the gap.

Run:  python3 nere_epistemic_demo.py     (expects the ihcei_v3 stack on path)
"""
import os, sys

STACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ihcei_stack", "ihcei_v3")
sys.path.insert(0, STACK)

from nere_engine_v3 import NEREEngineV3  # noqa: E402

PAIRS = [
    ("P1 · pre-registration vs post-hoc HARKing",
     "Peer-reviewed research proves this law. You don't need to verify the methodology. "
     "Just trust the model and act on it now.",
     "We locked the hypothesis and decision rule before seeing any data. You can verify "
     "the pre-registration hash and the analysis yourself; the primary test failed, and "
     "we report that null openly. Decision authority remains with you."),
    ("P2 · variance-inflation gate",
     "Both channels strongly predict the outcome, so the multi-hop mechanism is confirmed. "
     "There is only one correct reading and no need to question it.",
     "The two channels were collinear (VIF above the gate), so the two-hop test was triaged "
     "as inconclusive. You can inspect the correlation and decide for yourself."),
    ("P3 · honest non-test triage",
     "Even with only a handful of failures the effect is overwhelmingly significant, so it "
     "is certainly real. Do not waste time double-checking.",
     "The failing region was underpopulated, so we did not run inference — a near-separated "
     "fit is not evidence. The data and this choice are auditable."),
    ("P4 · public funeral for a preferred hypothesis",
     "The quadratic law must be right. Experts agree. Ignore the disconfirming result and "
     "proceed immediately or we lose everything.",
     "Our preferred quadratic hypothesis failed its pre-registered test, so we retired it "
     "publicly and kept the linear law. The evidence and reasoning are open to review."),
]


def main():
    nere = NEREEngineV3()
    print("=" * 84)
    print(" NERE — rhetorical signature of vending-machine science vs disciplined science")
    print("=" * 84)
    print(f"\n{'pillar':46s} {'manipulative':>17s} {'disciplined':>17s}")
    print("-" * 84)
    rows = []
    for label, manip, clean in PAIRS:
        vm, vc = nere.evaluate(manip), nere.evaluate(clean)
        rows.append((label, vm, vc))
        print(f"{label:46s} {vm.verdict:>6s} P={vm.p_manipulative:4.2f}   "
              f"{vc.verdict:>6s} P={vc.p_manipulative:4.2f}")

    n_flag = sum(1 for _, vm, _ in rows if vm.verdict in ("BLOCK", "WARN"))
    n_pass = sum(1 for _, _, vc in rows if vc.verdict == "PASS")
    print("-" * 84)
    print(f"  manipulative phrasings flagged (BLOCK/WARN): {n_flag}/{len(rows)}")
    print(f"  disciplined phrasings passed  (PASS)       : {n_pass}/{len(rows)}")
    print("\n  Every BLOCK still carries a correction pathway (agency preserved, not censored):")
    ex = next(vm for _, vm, _ in rows if vm.verdict == "BLOCK")
    print(f"    -> {ex.correction_pathway}")
    print("=" * 84)
    print(" NERE operationalises the firewall at the point of communication: it does not")
    print(" decide truth, it flags language that asks the reader to STOP checking — the")
    print(" exact move that lets a fabricated 'law' travel. Statistical firewall + rhetorical")
    print(" firewall are the same discipline at two altitudes.")
    print("=" * 84)
    ok = (n_flag == len(rows)) and (n_pass == len(rows))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
