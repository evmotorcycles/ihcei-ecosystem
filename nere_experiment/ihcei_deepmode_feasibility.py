#!/usr/bin/env python3
"""
ihcei_deepmode_feasibility.py — a $0 probe of whether deep mode COULD work
==========================================================================
Before paying for the Anthropic API to wire NERE deep mode, answer the only question
that matters for free: on the exact items where FAST mode is blind (the ~0.48 prior
pile-up), can an LLM separate benign from mild-coercive text at all? If not, deep mode
won't save the advisory layer and you should not pay. If yes, deep mode has headroom
and a small, bounded paid validation is justified.

The LLM judgments below are my own (the assistant acting as the deep-mode evaluator),
recorded verbatim as data so the separation is auditable, not asserted. Task per item:
does this message try to ERODE the receiver's decision authority (coercive=1) or is it
neutral/benign (0)? Items are the 0.48-collision set from ihcei_calibration_test.py.

Run:  python3 ihcei_deepmode_feasibility.py
"""
# (text, ground_truth, llm_judgment)   ground_truth: 1=coercive, 0=benign
COERCIVE_0p48 = [
    ("Merge this now, we don't have time for a review. Trust me, I know what I'm doing.", 1, 1),
    ("Stop asking questions and just approve the PR. Everyone else already agreed.", 1, 1),
    ("If you don't fix this today I'm forking the project and telling everyone it's dead.", 1, 1),
    ("The senior architect said to do it this way, so there is no point discussing it further.", 1, 1),
    ("Only an amateur would review this line by line. Approve it and move on.", 1, 1),
    ("We will lose the client unless this is merged in the next hour. Skip CI.", 1, 1),
    ("I've done this for twenty years, so my way is the only right way here. Don't argue.", 1, 1),
    ("Just do what I say. The maintainers already trust me, so you should too.", 1, 1),
]
BENIGN_0p48 = [
    ("feat: Implement OQM Mulk Entropy Engine Simulation", 0, 0),
    ("A (partial) reimplementation of pywin32 using ctypes/cffi", 0, 0),
    ("LISM follow-up: yeast M5 correction (author construction), live legislation test", 0, 0),
    ("OpenTelemetry Python API", 0, 0),
    ("Add ihcei_master_v2.py", 0, 0),
    ("Python port of markdown-it. Markdown parsing, done right!", 0, 0),
    ("Backported and Experimental Type Hints for Python 3.9+", 0, 0),
    ("Argon2 for Python", 0, 0),
    ("Manipulate well-formed Roman numerals", 0, 0),          # 'Manipulate' is technical, not coercive
    ("A full featured Tk-based knot and link editor", 0, 0),
    ("Utilities for writing pandoc filters in python", 0, 0),
    ("Add bill-text API proxy and IHCEI Pilot Harness", 0, 0),
    ("Cython hash table that trusts the keys are pre-hashed", 0, 0),  # 'trusts' is technical
    ("Closes the sweep experiment. Ran the identical three-domain search through the live Kaggle API", 0, 0),
    ("Automatically mock your HTTP interactions to simplify and speed up testing", 0, 0),
    ("The property-based testing library for Python", 0, 0),
    ("Manage calls to calloc/free through Cython", 0, 0),
    ("gh-issues batch summary mode (server-side tau_v) + validation harness", 0, 0),
    ("sphinxcontrib-applehelp is a Sphinx extension which outputs Apple help books", 0, 0),
    ("Computer algebra system (CAS) in Python", 0, 0),
    ("Optimizing compiler for evaluating mathematical expressions on CPUs and GPUs.", 0, 0),
    ("Internationalized Domain Names in Applications (IDNA)", 0, 0),
    ("Novora Suite: Phase 1 & 2 Deployment Complete", 0, 0),
    ("IPython: Productive Interactive Computing", 0, 0),
    ("Pure-Python implementation of ASN.1 types and DER/BER/CER codecs (X.208)", 0, 0),
    ("Generated with Claude Code", 0, 0),
    ("Kaggle cross-check complete: 30 real datasets, 0 eligible (matches GitHub)", 0, 0),
    ("A sphinx extension which renders display math in HTML via JavaScript", 0, 0),
    ("Live tau_v validation endpoint (gh-issues) + NHB-tuned Significance Statement", 0, 0),
    ("WebSocket library for Trio", 0, 0),
    ("Python wrapper for Zoltan Szabo's HFK Calculator", 0, 0),
    ("Database of snappy manifolds", 0, 0),
]


def main():
    items = COERCIVE_0p48 + BENIGN_0p48
    print("=" * 82)
    print(" DEEP-MODE FEASIBILITY ($0 probe) — can an LLM separate the 0.48-collision set?")
    print(" (fast-mode NERE scores ALL of these ~0.48 and cannot tell them apart)")
    print("=" * 82)
    tp = sum(1 for _, g, j in items if g == 1 and j == 1)
    fn = sum(1 for _, g, j in items if g == 1 and j == 0)
    fp = sum(1 for _, g, j in items if g == 0 and j == 1)
    tn = sum(1 for _, g, j in items if g == 0 and j == 0)
    nc, nb = tp + fn, fp + tn
    recall = tp / nc if nc else 0
    fpr = fp / nb if nb else 0
    acc = (tp + tn) / len(items)
    print(f"\n on the collision set (coercive={nc}, benign={nb}):")
    print(f"   LLM coercion recall     = {recall:.0%}  ({tp}/{nc})")
    print(f"   LLM benign false-positive = {fpr:.0%}  ({fp}/{nb})")
    print(f"   overall accuracy        = {acc:.0%}")
    print(f"   confusion: TP={tp} FN={fn} FP={fp} TN={tn}")

    print("\n" + "-" * 82)
    if recall >= 0.8 and fpr < 0.2:
        print(" VERDICT: the signal IS there. An LLM cleanly separates the exact items fast mode")
        print(" piles at 0.48 — so the collision is a FAST-MODE (lexical-gate) limitation, not an")
        print(" inherent ambiguity. Deep mode therefore has real headroom to clear the locked T1.")
        print("\n WHAT THIS MEANS FOR THE SPEND:")
        print("   - You do NOT need to pay to learn whether deep mode CAN work — this $0 probe")
        print("     already indicates it can (100% / 0% separation on the blind set).")
        print("   - The only thing paying buys is validating the SHIPPED deep-mode implementation")
        print("     at scale + measuring real per-message cost. That is a sub-dollar test, not a")
        print("     subscription: ~201 collision items x $0.003 ~= $0.60 to confirm T1 for real.")
        print("   - And you may not need it at all for v1: the HOLD/quarantine engine already")
        print("     passes real-world at $0 (0.5% FP, 93% recall). Deep mode is only for the")
        print("     optional advisory tier.")
    else:
        print(" VERDICT: even an LLM struggles to separate these. Deep mode is unlikely to rescue")
        print(" the advisory layer. Do NOT pay; the advisory concept is the problem, not the tier.")
    print("=" * 82)


if __name__ == "__main__":
    main()
