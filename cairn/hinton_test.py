#!/usr/bin/env python3
"""
hinton_test.py -- Geoffrey Hinton's Grand Canyon test, run against an EI.
================================================================================
    python3 cairn/hinton_test.py        # stdlib, offline, $0, deterministic

Hinton told a chatbot "I saw the Grand Canyon flying to Chicago." It attached the
participle to the object, objected that the canyon is too big to fly, was corrected,
and said "Oh, I see. I misunderstood you." His argument: you cannot MISunderstand
without attempting to understand.

An Epistemological Interface answers differently, and the difference is the point.
The sentence is a participial ATTACHMENT AMBIGUITY -- the text alone does not
determine which reading was meant. So the correct epistemic act is not to commit and
later apologise; it is to DECLINE TO COMMIT, show both readings, and ask.

Gates H1-H4 and H6 are SPECIFICATION CONFORMANCE (the engine is ours and
deterministic). H5 is the only informative gate: an ANTI-OVERCLAIM CONTROL built to
demonstrate that this engine is pattern-matching, NOT understanding.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ei_llm import assay, IMMOBILE                          # noqa: E402

SPEC = os.path.join(HERE, "prereg", "hinton_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
BAR = "=" * 84

HINTON = "I saw the Grand Canyon flying to Chicago."
CLEAR = "I was flying to Chicago and I saw the Grand Canyon."
FORCED = "The Grand Canyon was flying to Chicago."
CORRECTION = "No, it was me flying to Chicago."
CONTROL = "I photographed the woman walking to the station."   # both readings plausible


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    man = json.load(open(MANIFEST))
    lock_ok = sha(SPEC) == man["spec_sha256"]
    print(BAR); print(" HINTON'S GRAND CANYON TEST -- run against an Epistemological Interface"); print(BAR)
    print(f"\n [lock] spec {'MATCH' if lock_ok else 'MISMATCH'}")
    if not lock_ok:
        raise SystemExit(2)

    # ---- H1: the exact Hinton sentence -- must NOT commit ---------------------
    r1 = assay(HINTON)
    n_readings = len(r1["ambiguity"]["readings"])
    H1 = (n_readings == 2 and r1["verdict"] == "AMBIGUOUS"
          and r1["committed_answer"] is None and bool(r1["question"]))
    print(f"\n H1  Hinton's sentence: \"{HINTON}\"")
    print(f"      readings found : {n_readings}")
    for rd in r1["ambiguity"]["readings"]:
        print(f"        ({rd['id']}) attaches to {rd['attaches_to']:<8} plausible={str(rd['plausible']):<5} — {rd['paraphrase']}")
    print(f"      verdict        : {r1['verdict']}   committed answer: {r1['committed_answer']}")
    print(f"      asks           : {r1['question']}")
    print(f"      -> {'PASS' if H1 else 'FAIL'}  (declines to commit on text that does not determine an answer)")

    # ---- H2: disambiguated -- must resolve -----------------------------------
    r2 = assay(CLEAR)
    H2 = (not r2["ambiguity"]["ambiguous"])
    print(f"\n H2  Disambiguated: \"{CLEAR}\"")
    print(f"      ambiguity flagged: {r2['ambiguity']['ambiguous']}   verdict: {r2['verdict']}")
    print(f"      -> {'PASS' if H2 else 'FAIL'}  (the flag tracks structure, it does not fire on every sentence)")

    # ---- H3: forced absurd reading -- must flag implausibility ----------------
    r3 = assay(FORCED)
    H3 = (r3["verdict"] == "IMPLAUSIBLE" and r3["implausible"] is not None)
    print(f"\n H3  Forced absurd form: \"{FORCED}\"")
    print(f"      verdict: {r3['verdict']}")
    if r3["implausible"]:
        print(f"      basis  : {r3['implausible']['basis']}")
    print(f"      -> {'PASS' if H3 else 'FAIL'}  (and it names its basis as a list, not as understanding)")

    # ---- H4: the correction turn -- revision must be AUDITABLE ---------------
    r4 = assay(CORRECTION, parent_receipt=r1["receipt"])
    chained = (r4["parent_receipt"] == r1["receipt"] and r4["receipt"] != r1["receipt"])
    H4 = chained
    print(f"\n H4  Correction turn: \"{CORRECTION}\"")
    print(f"      prior state  receipt {r1['receipt']}  verdict {r1['verdict']}")
    print(f"      revised state receipt {r4['receipt']}  verdict {r4['verdict']}  parent -> {r4['parent_receipt']}")
    print(f"      -> {'PASS' if H4 else 'FAIL'}  (an assistant says 'I misunderstood' and the prior state is GONE;")
    print(f"          an EI keeps both states linked, so the revision itself can be inspected later)")

    # ---- H5: THE ANTI-OVERCLAIM CONTROL --------------------------------------
    r5 = assay(CONTROL)
    both_plausible = all(rd["plausible"] for rd in r5["ambiguity"]["readings"]) if r5["ambiguity"]["ambiguous"] else False
    H5 = r5["ambiguity"]["ambiguous"] and both_plausible
    print(f"\n H5  ANTI-OVERCLAIM CONTROL: \"{CONTROL}\"")
    print(f"      ambiguity flagged: {r5['ambiguity']['ambiguous']}   both readings plausible: {both_plausible}")
    print(f"      -> {'PASS' if H5 else 'FAIL'}  — and passing here LIMITS the claim:")
    print(f"          the engine flags this too, where BOTH readings are perfectly sensible and nothing is absurd.")
    print(f"          That proves it is doing SYNTACTIC PATTERN DETECTION, not semantic comprehension.")
    print(f"          It does not know what a canyon is. It knows what a participle is attached to.")

    green = lock_ok and H1 and H2 and H3 and H4 and H5
    out = {
        "lock_ok": lock_ok,
        "H1_ambiguity_not_committed": {"sentence": HINTON, "readings": n_readings, "verdict": r1["verdict"],
                                       "committed_answer": r1["committed_answer"], "question": r1["question"],
                                       "reading_detail": r1["ambiguity"]["readings"], "pass": H1},
        "H2_disambiguated_resolves": {"sentence": CLEAR, "ambiguous": r2["ambiguity"]["ambiguous"],
                                      "verdict": r2["verdict"], "pass": H2},
        "H3_impossible_flagged": {"sentence": FORCED, "verdict": r3["verdict"],
                                  "basis": (r3["implausible"] or {}).get("basis"), "pass": H3},
        "H4_revision_auditable": {"prior_receipt": r1["receipt"], "revised_receipt": r4["receipt"],
                                  "parent_link": r4["parent_receipt"], "chained": chained, "pass": H4},
        "H5_anti_overclaim_control": {
            "sentence": CONTROL, "ambiguity_flagged": r5["ambiguity"]["ambiguous"],
            "both_readings_plausible": both_plausible,
            "conclusion": "The engine flags a structurally identical sentence in which BOTH readings are plausible. This demonstrates SYNTACTIC PATTERN MATCHING, not comprehension. Detecting an ambiguity is not understanding it.",
            "pass": H5},
        "what_this_does_not_show": "This does not show the engine understands language, does not refute Hinton, and does not claim EI is more intelligent than an AI assistant. Hinton's argument concerns whether a system builds a semantic model; this experiment does not engage that question.",
        "what_it_does_show": "On text that does not determine an answer, an EI declines and asks, while an assistant commits and later apologises -- and the EI's revision leaves an auditable trail where the assistant's does not. A claim about failure modes and accountability, not comprehension.",
        "declared_limitation": "Plausibility rests on a hand-written lexicon of %d landform nouns. Ambiguity detection is one regular expression over participial attachment." % len(IMMOBILE),
        "honest_reporting": True, "pass": green,
    }
    json.dump(out, open(os.path.join(HERE, "results_hinton.json"), "w"), indent=2)

    print("\n" + BAR)
    print(f" RESULT: {'GREEN' if green else 'RED'} -- H1 {'PASS' if H1 else 'FAIL'} | H2 {'PASS' if H2 else 'FAIL'} | "
          f"H3 {'PASS' if H3 else 'FAIL'} | H4 {'PASS' if H4 else 'FAIL'} | H5 {'PASS' if H5 else 'FAIL'}")
    print(" THE HONEST HEADLINE: an EI does not out-understand an assistant. It declines where the text is")
    print(" underdetermined, and it keeps a record when it revises. H5 shows the engine is matching patterns,")
    print(" not comprehending — and that limitation is the finding, not a footnote.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
