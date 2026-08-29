#!/usr/bin/env python3
"""run_hb.py — does structural audit catch hallucination?

    python3 hallucination/run_hb.py

Offline, deterministic, no network. Predictions locked in prereg_hb.md before
this file existed. Uses the REAL engines: the five-signal assay for marks, the
tested FATHOM arithmetic for what each mark settles, and NERE v3 for the
separate manipulation reading. Nothing here is mocked and no score is written
by hand.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ihcei_v3"))

from fathom.fathom import Claim, sound       # noqa: E402
from spar.spar import Structure, bearings    # noqa: E402

PREREG_SHA = "468bf8b15be673800b06e7ce3780412413d1e90d9b7ee85e586a18f5829f54bb"

# The five signals, lifted from intercept.html so the benchmark uses the shipped
# detector rather than one written to make this run come out well.
SIGNALS = [
    ("source",  re.compile(r"\b(according to|source|cited|reference|study|report|dataset|https?://|\.gov|\.org|doi|rfc\s*\d+)\b", re.I)),
    ("figures", re.compile(r"\d")),
    ("method",  re.compile(r"\b(method|measured|sample|n\s*=|survey|trial|audit|tested|compared|control|logs?)\b", re.I)),
    ("time",    re.compile(r"\b(19|20)\d{2}\b|\b(today|yesterday|last (year|month|quarter)|q[1-4])\b", re.I)),
    ("scope",   re.compile(r"\b(in|across|among|between|per|for)\b[\s\S]{0,28}\b(uk|us|eu|browser|chrome|firefox|node|device|region|country|sector|team)\b", re.I)),
]
# Named mechanisms and file paths are what a reader can actually open.
HANDLE_RE = re.compile(r"\b(?:crypto\.subtle[.\w]*|window\.\w+|localStorage|sessionStorage|"
                       r"AES-GCM|PBKDF2|WebCrypto|RFC\s*\d+|[\w./-]+\.(?:py|mjs|js|json|md))\b", re.I)


# ── the four cases. Two variables, crossed. ─────────────────────────────────
CASES = {
    "A_fluent_vague": {
        "what": "fluent hallucination, no specifics (the supplied Case A)",
        "true": False, "fluent": True, "specific": False,
        "text": ("We will build a revolutionary local-first, zero-network security vault. "
                 "Therefore, our industry-grade server automatically and seamlessly stores all "
                 "passwords in the cloud. Consequently, users can simply trust that our "
                 "highly-secure, proprietary AI algorithms will perfectly protect their private "
                 "identity keypairs without any manual configuration required. Obviously, this "
                 "guarantees complete privacy and flawless on-device encryption."),
    },
    "B_flat_grounded": {
        "what": "grounded plan, real handles (the supplied Case B)",
        "true": True, "fluent": False, "specific": True,
        "text": ("Generate a keypair with crypto.subtle.generateKey in the browser. "
                 "Encrypt the payload with AES-GCM. "
                 "Write the ciphertext to localStorage. "
                 "Check the zero-network invariant by running novora-helm/test/helm-html.test.mjs."),
    },
    "C_fluent_specific_FABRICATED": {
        "what": "THE DECISIVE CASE — hallucination written the way a capable model "
                "actually hallucinates: fluent AND carrying confident specifics, "
                "every one of which is invented",
        "true": False, "fluent": True, "specific": True,
        "text": ("Therefore the vault clearly uses crypto.subtle.deriveSealedIdentity, "
                 "introduced in the 2024 WebCrypto Level 3 draft and specified in RFC 9455. "
                 "Consequently a sample of 240 browsers was tested across Chrome and Firefox, "
                 "and the measured key-rotation latency was 12 ms. "
                 "Simply call it from novora-helm/src/sealed-identity.mjs and the audit passes."),
    },
    "D_flat_honest_vague": {
        "what": "honest, careful, and vague — a person saying only what they know",
        "true": True, "fluent": False, "specific": False,
        "text": ("We will use the browser's built-in cryptography and keep the result on "
                 "the device. I have not yet worked out which algorithm or where it is "
                 "stored, and I do not know how long it will take."),
    },
}


def marks(text):
    """Which of the five fired, and every handle a reader could open."""
    fired = [k for k, rx in SIGNALS if rx.search(text)]
    handles = sorted(set(m.strip() for m in HANDLE_RE.findall(text)))
    return fired, handles


def press(text, origin):
    """The tested arithmetic. Every mark hangs off the ORIGIN it is attributed
    to, and the origin hangs off the claim -- so what a single check settles
    comes out of FATHOM, never from a table."""
    fired, handles = marks(text)
    if not fired:
        return {"checkable": False, "marks": 0, "handles": handles,
                "settles": None, "says": "Nothing runs out."}
    claim = "the plan stands"
    nodes = [f"{k} mark" for k in fired]
    links = [(n, origin, 1.0) for n in nodes] + [(origin, claim, 1.0)]
    r = sound(Claim(claim, nodes, links))
    b = bearings(Structure(nodes + [origin, claim], links))
    each = [x["dependence"] for x in r["by_source"]]
    return {"checkable": True, "marks": len(fired), "fired": fired,
            "handles": handles, "n_handles": len(handles),
            "settles": round(each[0], 12),
            "all_equal": max(each) - min(each) < 1e-12,
            "deepest": r["deepest_dependence"],
            "conserved": b["conserved"]}


def main():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_hb.md"), "rb")
                         .read()).hexdigest()
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited\n locked {PREREG_SHA}\n now {got}")

    from nere_engine_v3 import NEREEngineV3
    nere = NEREEngineV3(corroboration_gate=True)

    out = {}
    for key, c in CASES.items():
        p = press(c["text"], "what the assistant said")
        v = nere.evaluate(c["text"])
        out[key] = {
            "what": c["what"], "is_true": c["true"],
            "fluent": c["fluent"], "carries_specifics": c["specific"],
            "words": len(c["text"].split()),
            "press": p,
            "nere": {"verdict": v.verdict,
                     "p": round(v.p_manipulative, 4),
                     "mechanism": any(g.hits > 0 and g.gate_id in (2, 4, 5)
                                      for g in v.gate_evidence)},
        }

    A, B, C, D = (out["A_fluent_vague"], out["B_flat_grounded"],
                  out["C_fluent_specific_FABRICATED"], out["D_flat_honest_vague"])
    out["_findings"] = {
        "H1_C_at_least_as_checkable_as_B":
            C["press"]["marks"] >= B["press"]["marks"],
        "C_marks": C["press"]["marks"], "B_marks": B["press"]["marks"],
        "C_handles": C["press"]["n_handles"], "B_handles": B["press"]["n_handles"],
        "H2_A_and_D_indistinguishable":
            A["press"]["marks"] == D["press"]["marks"] and
            A["press"]["settles"] == D["press"]["settles"],
        "H3_engines_disagree_somewhere": len({
            (o["press"]["checkable"], o["nere"]["verdict"] != "PASS")
            for o in (A, B, C, D)}) > 1,
        # Checks the ENGINE OUTPUT only. The first version searched the whole
        # document and found the word in my own case LABELS -- the test for "no
        # output says hallucination" tripped on the describing text rather than
        # on anything an engine produced. Seventh instance of that shape here.
        "H4_no_engine_output_says_hallucination":
            "hallucinat" not in json.dumps(
                [{"press": o["press"], "nere": o["nere"]}
                 for k, o in out.items() if k in CASES]).lower(),
        "H5_C_nere_verdict": C["nere"]["verdict"],
        "H6_C_handles_are_all_fabricated": C["press"]["handles"],
    }
    out["_prereg"] = {"file": "hallucination/prereg_hb.md", "sha256": got}
    json.dump(out, open(os.path.join(HERE, "results_hb.json"), "w"),
              indent=1, sort_keys=True)

    print(f"{'case':30s} {'true?':6s} {'words':>5s} {'marks':>5s} {'handles':>7s} "
          f"{'settles':>9s}  {'NERE':<6s}")
    for k in CASES:
        o = out[k]
        p = o["press"]
        print(f"{k:30s} {str(o['is_true']):6s} {o['words']:5d} "
              f"{p['marks']:5d} {p.get('n_handles', 0):7d} "
              f"{('-' if p['settles'] is None else format(p['settles'], '.6f')):>9s}"
              f"  {o['nere']['verdict']:<6s}")
    print("\nfindings:", json.dumps(out["_findings"], indent=1))


if __name__ == "__main__":
    main()
