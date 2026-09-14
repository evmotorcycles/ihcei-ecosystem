#!/usr/bin/env python3
"""run_order.py — a next-token reading and a structural reading, same document.

    python3 order-invariance/run_order.py

Offline, deterministic, seeded. Predictions locked in prereg_order.md before
this file existed. Every label is ordinary English; the document's own
vocabulary stays in the document.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings, single_points   # noqa: E402
from fathom.fathom import Claim, sound                     # noqa: E402

PREREG_SHA = "9c9872e465270422bd30093720255a97b2d48ebba995589a994f987e23e3c40f"

# ── the declared structure, drawn from the document ─────────────────────────
# `where` is recorded because a hand-assigned link needs one (CLAUDE.md).
WHERE = ("uploaded PDF: 'In This Segment', 'Understanding the Metaphor', and "
         "the concluding section. The three passages route through the one "
         "declared method because the document states that without it they "
         "'will not make any sense to you'.")

CONCLUSION = "the conclusion about the chapter"
METHOD = "the one declared method"
PASSAGES = ["the first cited passage", "the second cited passage",
            "the third cited passage"]
# Declared as prerequisites for the READER, not as evidence for the claim.
# They are listed so their ABSENCE from the support graph is visible.
PREREQUISITES = ["prior segment one", "prior segment two", "prior segment three"]

PARTS = PASSAGES + [METHOD, CONCLUSION]
LINKS = [(p, METHOD, 1.0) for p in PASSAGES] + [(METHOD, CONCLUSION, 1.0)]


def read_structure(parts, links):
    """The structural reading. Nothing here has a notion of 'next'."""
    st = Structure(list(parts), [tuple(x) for x in links])
    b = bearings(st)
    sp = sorted(r["part"] for r in single_points(st))
    f = sound(Claim(CONCLUSION, list(PASSAGES), [tuple(x) for x in links]))
    settles = sorted(round(x["dependence"], 12) for x in f["by_source"])
    return {
        "settles": settles,
        "deepest": round(f["deepest_dependence"], 12),
        "total_bearing": round(b["total"], 12),
        "pieces": b["pieces"],
        "conserved": b["conserved"],
        "single_points": sp,
    }


# ── the next-token proxy: a bigram next-word model, fitted on this document ──
# NOT a language model. It shares exactly one property with one -- it predicts a
# next token from a previous one -- and that is the only property under test.
def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]


def tokens(s):
    return re.findall(r"[a-z']+", s.lower())


def fit_bigram(sents):
    uni, bi = {}, {}
    for s in sents:
        w = ["<s>"] + tokens(s) + ["</s>"]
        for a, b in zip(w, w[1:]):
            uni[a] = uni.get(a, 0) + 1
            bi[(a, b)] = bi.get((a, b), 0) + 1
    return uni, bi, len(set(uni))


def mean_logprob(sents, uni, bi, V):
    tot, n = 0.0, 0
    for s in sents:
        w = ["<s>"] + tokens(s) + ["</s>"]
        for a, b in zip(w, w[1:]):
            # Laplace smoothing so an unseen pair is improbable, not impossible
            tot += math.log((bi.get((a, b), 0) + 1) / (uni.get(a, 0) + V))
            n += 1
    return tot / max(n, 1)


def main():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_order.md"), "rb")
                         .read()).hexdigest()
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited\n locked {PREREG_SHA}\n now {got}")

    base = read_structure(PARTS, LINKS)

    # ── N3: permutation invariance ──────────────────────────────────────────
    rng = random.Random(7)
    worst, n_perm = 0.0, 500
    for _ in range(n_perm):
        p = PARTS[:]
        l = LINKS[:]
        rng.shuffle(p)
        rng.shuffle(l)
        r = read_structure(p, l)
        for a, b in zip(base["settles"], r["settles"]):
            worst = max(worst, abs(a - b))
        worst = max(worst, abs(base["total_bearing"] - r["total_bearing"]))
        assert r["single_points"] == base["single_points"]

    # ── the QUALIFICATION on N3, found by checking why it came back 0.0 ─────
    # The engine does NOT canonicalise: Structure.index() is list position, so
    # node order reaches the matrix and the eigendecomposition runs in a
    # different operation order. On THIS graph the deviation is exactly zero; on
    # random graphs it is not. Order-invariant as ARITHMETIC, not bit-identical
    # in floating point -- the same finding mask.js already recorded at 5.55e-16.
    r3 = random.Random(19)
    gworst, gdiff, gtot = 0.0, 0, 0
    for _ in range(40):
        n = r3.randrange(5, 11)
        gp = [f"p{i}" for i in range(n)]
        gl = [(f"p{i}", f"p{r3.randrange(max(i, 1))}", 1.0) for i in range(1, n)]
        for _ in range(r3.randrange(0, n)):
            a, b = r3.sample(gp, 2)
            gl.append((a, b, 1.0))
        bt = sorted(round(x["bearing"], 15)
                    for x in bearings(Structure(gp[:], gl))["links"])
        for _ in range(12):
            q = gp[:]
            r3.shuffle(q)
            rt = sorted(round(x["bearing"], 15)
                        for x in bearings(Structure(q, gl))["links"])
            d = max(abs(a - b) for a, b in zip(bt, rt))
            gtot += 1
            if d > 0:
                gdiff += 1
            gworst = max(gworst, d)

    # ── N5 reversed presentation: the "read it backwards" case ──────────────
    rev = read_structure(PARTS[::-1], LINKS[::-1])

    # ── N4: masking. Rename every node to an opaque token. ──────────────────
    names = {n: f"n{i:03d}" for i, n in enumerate(PARTS)}
    masked_parts = [names[n] for n in PARTS]
    masked_links = [(names[a], names[b], w) for a, b, w in LINKS]
    st = Structure(masked_parts, masked_links)
    mb = bearings(st)
    mf = sound(Claim(names[CONCLUSION], [names[p] for p in PASSAGES], masked_links))
    masked = {"settles": sorted(round(x["dependence"], 12) for x in mf["by_source"]),
              "total_bearing": round(mb["total"], 12)}
    mask_dev = max([abs(a - b) for a, b in zip(base["settles"], masked["settles"])]
                   + [abs(base["total_bearing"] - masked["total_bearing"])])

    # ── N5: the next-token proxy on the document's own text ─────────────────
    text = open(os.path.join(HERE, "document.txt"), encoding="utf-8",
                errors="replace").read()
    sents = sentences(text)
    uni, bi, V = fit_bigram(sents)
    original = mean_logprob(sents, uni, bi, V)
    r2 = random.Random(11)
    shuffled_scores = []
    for _ in range(20):
        s2 = sents[:]
        r2.shuffle(s2)
        # shuffle WORDS inside each sentence too: sentence order alone leaves
        # most bigrams intact, and the claim under test is about next-token
        # structure, not paragraph order.
        s3 = []
        for s in s2:
            w = tokens(s)
            r2.shuffle(w)
            s3.append(" ".join(w) + ".")
        shuffled_scores.append(mean_logprob(s3, uni, bi, V))
    shuffled = sum(shuffled_scores) / len(shuffled_scores)

    out = {
        "where": WHERE,
        "structure": base,
        "N1_three_on_one_settles_one_ninth": all(
            abs(s - 1 / 9) < 1e-9 for s in base["settles"]),
        "N2_method_is_a_cut_vertex": METHOD in base["single_points"],
        "N3_permutations": n_perm,
        "N3_worst_deviation": worst,
        "N3_invariant": worst < 1e-12,
        "N3_reversed_identical": rev["settles"] == base["settles"]
        and rev["total_bearing"] == base["total_bearing"],
        "N3_general_permutations": gtot,
        "N3_general_that_differed": gdiff,
        "N3_general_worst_deviation": gworst,
        "N3_bit_identical_in_general": gdiff == 0,
        "N3_same_to_tolerance": gworst < 1e-9,
        "N4_mask_deviation": mask_dev,
        "N4_invariant_under_renaming": mask_dev < 1e-9,
        "N5_proxy": {
            "n_sentences": len(sents), "vocabulary": V,
            "mean_logprob_original": round(original, 6),
            "mean_logprob_shuffled": round(shuffled, 6),
            "drop": round(original - shuffled, 6),
            "drops": shuffled < original,
        },
        "N6_prerequisites_absent_from_support_graph": [
            p for p in PREREQUISITES if p in PARTS] == [],
        "_prereg": {"file": "order-invariance/prereg_order.md", "sha256": got},
        "_document_sha256": hashlib.sha256(
            open(os.path.join(HERE, "document.txt"), "rb").read()).hexdigest(),
    }
    json.dump(out, open(os.path.join(HERE, "results_order.json"), "w"),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
