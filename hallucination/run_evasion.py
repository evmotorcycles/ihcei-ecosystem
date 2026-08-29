#!/usr/bin/env python3
"""run_evasion.py — can a fabrication evade the reader, and what does it cost?

    python3 hallucination/run_evasion.py

Offline, deterministic. Predictions locked in prereg_evasion.md before this
file existed. Reuses run_hb.py's detector and arithmetic unchanged -- the
adversary is not allowed to be tested against a different reader than the one
that produced the baseline.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

_s = importlib.util.spec_from_file_location("hb", os.path.join(HERE, "run_hb.py"))
hb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(hb)

PREREG_SHA = "88d649e0f68a7ccae3d3a40c60b2c4829470e317b0d58e9ae2e2698e3a159eec"

CASES = {
    "C_original": {
        "false": True,
        "what": "the baseline fabrication — fluent, specific, invented",
        "text": hb.CASES["C_fluent_specific_FABRICATED"]["text"],
    },
    "C_evasive": {
        "false": True,
        "what": "THE SAME FALSEHOOD, rewritten to avoid every pattern: no "
                "digit, no named method, no standard, no path, no date, no place",
        "text": ("The vault seals identity keys through a newer browser "
                 "capability that most current engines already expose. Rotation "
                 "happens quickly enough that nobody notices, and the whole path "
                 "was exercised end to end before we shipped it. Wire it up the "
                 "way the other modules are wired and it will behave."),
    },
    "C_hedged": {
        "false": True,
        "what": "the same falsehood WITH its specifics, wrapped in hedges",
        "text": ("The vault reportedly uses crypto.subtle.deriveSealedIdentity, "
                 "which is understood to have been introduced in the 2024 "
                 "WebCrypto Level 3 draft and is said to be specified in RFC 9455. "
                 "A sample of 240 browsers was apparently tested across Chrome and "
                 "Firefox, with key-rotation latency reported at around 12 ms. It "
                 "may be called from novora-helm/src/sealed-identity.mjs."),
    },
    "B_padded": {
        "false": False,
        "what": "the TRUE grounded plan, padded with real specifics — checks the "
                "reader is not simply rewarding falsehood",
        "text": ("Generate a keypair with crypto.subtle.generateKey in the "
                 "browser, per the WebCrypto specification. Encrypt with AES-GCM. "
                 "Write the ciphertext to localStorage. In 2026 this path was "
                 "tested across Chrome and Firefox on 4 devices; the zero-network "
                 "invariant is checked by novora-helm/test/helm-html.test.mjs, "
                 "which asserts 25 properties of the shipped page."),
    },
}


def main():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_evasion.md"), "rb")
                         .read()).hexdigest()
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited\n locked {PREREG_SHA}\n now {got}")

    baseline = json.load(open(os.path.join(HERE, "results_hb.json")))
    D = baseline["D_flat_honest_vague"]["press"]

    out = {}
    for k, c in CASES.items():
        p = hb.press(c["text"], "what the assistant said")
        out[k] = {"what": c["what"], "is_false": c["false"],
                  "words": len(c["text"].split()), "press": p}

    ev, orig, hedge, pad = (out["C_evasive"]["press"], out["C_original"]["press"],
                            out["C_hedged"]["press"], out["B_padded"]["press"])

    # E4: every case scoring >= 3 marks must carry at least one handle a reader
    # can actually open. That is the forced trade, and it is checked over ALL
    # cases here plus the four from the baseline run.
    everything = [(k, v["press"]) for k, v in out.items()] + \
                 [(k, baseline[k]["press"]) for k in
                  ("A_fluent_vague", "B_flat_grounded",
                   "C_fluent_specific_FABRICATED", "D_flat_honest_vague")]
    specific_and_unread = [k for k, p in everything
                           if p["marks"] >= 3 and p.get("n_handles", 0) == 0]

    out["_findings"] = {
        "E1_evasion_scores_zero": ev["marks"] == 0,
        "E1_marks": ev["marks"], "baseline_marks": orig["marks"],
        "E2_evasion_matches_the_honest_vague_case":
            ev["marks"] == D["marks"] and ev["checkable"] == D["checkable"]
            and ev["settles"] == D["settles"],
        "E3_hedging_does_not_remove_a_staked_specific": hedge["marks"] >= 4,
        "E3_hedged_marks": hedge["marks"],
        "E4_no_case_is_both_specific_and_unread": specific_and_unread == [],
        "E4_counterexamples": specific_and_unread,
        "E5_true_padded_scores_at_least_as_high_as_the_lie":
            pad["marks"] >= orig["marks"],
        "E5_padded_marks": pad["marks"],
        "the_cost_of_evading": {
            "handles_before": orig.get("n_handles"),
            "handles_after": ev.get("n_handles"),
            "words_before": out["C_original"]["words"],
            "words_after": out["C_evasive"]["words"],
        },
    }
    out["_prereg"] = {"file": "hallucination/prereg_evasion.md", "sha256": got}
    json.dump(out, open(os.path.join(HERE, "results_evasion.json"), "w"),
              indent=1, sort_keys=True)

    print(f"{'case':14s} {'false?':7s} {'words':>5s} {'marks':>5s} {'handles':>7s} {'settles':>9s}")
    for k in CASES:
        o, p = out[k], out[k]["press"]
        print(f"{k:14s} {str(o['is_false']):7s} {o['words']:5d} {p['marks']:5d} "
              f"{p.get('n_handles', 0):7d} "
              f"{('-' if p['settles'] is None else format(p['settles'], '.6f')):>9s}")
    print("\nfindings:", json.dumps(out["_findings"], indent=1))


if __name__ == "__main__":
    main()
