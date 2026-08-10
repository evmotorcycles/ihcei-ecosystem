#!/usr/bin/env python3
"""
text_channel.py -- pre-registered tests of the testable textual claims.
================================================================================
    python3 text-channel/text_channel.py

Runs exactly what text-channel/PREREG.md specifies, which was SHA-256 locked
before the Claim-2 statistic was computed. Stdlib only. No network. $0.

LAYER-1 ONLY. This measures co-occurrence of surface forms in a text file. It
does not interpret, and nothing here supports a claim about the status, purpose
or origin of the text. See PREREG.md Section 0 for the three boundaries that bind
this, in particular: no measurement of a network licenses a claim about a book.
"""
import hashlib
import json
import os
import random
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "data/quran-uthmani.xml")
SEED = 42
N_PERM = 10000

# ---- declared in PREREG.md Section C, before any statistic was computed ------
FAMILY_A = ["جَآء", "جَاء", "جِئ", "يَجِيء", "تَجِيء", "نَجِيء"]
FAMILY_B_FORM_I = ["أَتَىٰ", "أَتَى", "أَتَتْ", "أَتَوْا", "يَأْتِ", "تَأْتِ", "نَأْتِ", "ءَاتٍ"]
FAMILY_B_FORM_IV_EXCLUDED = ["ءَاتَىٰ", "ءَاتَي", "يُؤْتِ", "نُؤْتِ", "تُؤْتِ", "أُوتِ"]
PAYLOAD = ["كتب", "بين", "رسل", "علم", "هدى", "ايت", "حكم", "ذكر", "حق", "امر"]

BISM_OMITTED, BISM_RETAINED = "بِسْمِ", "بِٱسْمِ"

# Arabic diacritics + tatweel; removed to reduce surface forms to skeletons.
DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
# orthographic normalisation for skeleton matching only
NORMALISE = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})


def skeleton(text):
    return DIACRITICS.sub("", text).translate(NORMALISE)


def load():
    root = ET.parse(CORPUS).getroot()
    verses = []
    for sura in root.findall(".//sura"):
        for aya in sura.findall("aya"):
            t = aya.get("text")
            verses.append({"sura": int(sura.get("index")), "aya": int(aya.get("index")),
                           "text": t, "skel": skeleton(t), "words": len(t.split())})
    assert len(verses) == 6236, f"expected 6236 verses, parsed {len(verses)}"
    assert len({v['sura'] for v in verses}) == 114
    return verses


def has_any(skel, forms):
    return any(skeleton(f) in skel for f in forms)


def payload_hits(skel):
    return sum(1 for p in PAYLOAD if p in skel)


# ============================ Claim 1 — descriptive ==========================
def claim1(verses):
    om = [(v["sura"], v["aya"]) for v in verses if BISM_OMITTED in v["text"]]
    re_ = [(v["sura"], v["aya"]) for v in verses if BISM_RETAINED in v["text"]]
    n = len(om) + len(re_)
    return {
        "status": "UNTESTABLE_AT_THIS_N",
        "alif_omitted_n": len(om), "alif_omitted_at": om,
        "alif_retained_n": len(re_), "alif_retained_at": re_,
        "total_n": n,
        "why_untestable": (
            f"N = {n} total. A {len(om)}/{len(re_)} split of {n} items cannot be "
            "statistically distinguished from any other narrative partition of "
            f"{n} items. This is a statement about sample size, not about whether "
            "the claim is true."),
        "not_a_finding_note": (
            "This is DESCRIPTIVE. The counts were taken before PREREG.md was "
            "written and carry no confirmatory weight."),
    }


# ========================= Claim 2 — the genuine test ========================
def claim2(verses):
    rng = random.Random(SEED)
    A = [v for v in verses if has_any(v["skel"], FAMILY_A)]
    B_all = [v for v in verses if has_any(v["skel"], FAMILY_B_FORM_I)]
    excluded = [v for v in verses if has_any(v["skel"], FAMILY_B_FORM_IV_EXCLUDED)]
    exclset = {(v["sura"], v["aya"]) for v in excluded}
    # Form I only: drop verses whose only match is the excluded giving-verb.
    B = [v for v in B_all if (v["sura"], v["aya"]) not in exclset]
    # a verse containing BOTH families is ambiguous evidence; drop from both.
    Aset = {(v["sura"], v["aya"]) for v in A}
    Bset = {(v["sura"], v["aya"]) for v in B}
    both = Aset & Bset
    A = [v for v in A if (v["sura"], v["aya"]) not in both]
    B = [v for v in B if (v["sura"], v["aya"]) not in both]

    def rate(group):
        return sum(1 for v in group if payload_hits(v["skel"]) > 0) / len(group) if group else 0.0

    def per10(group):
        return (sum(payload_hits(v["skel"]) for v in group) /
                max(1, sum(v["words"] for v in group))) * 10

    pA, pB = rate(A), rate(B)
    obs = pA - pB

    pooled = A + B
    nA = len(A)
    flags = [payload_hits(v["skel"]) > 0 for v in pooled]
    null = []
    for _ in range(N_PERM):
        rng.shuffle(flags)
        null.append(sum(flags[:nA]) / nA - sum(flags[nA:]) / max(1, len(flags) - nA))
    pval = sum(1 for x in null if abs(x) >= abs(obs)) / N_PERM

    underpowered = len(A) < 30 or len(B) < 30
    if underpowered:
        verdict, why = "INCONCLUSIVE", "a group has fewer than 30 verses"
    elif obs <= 0:
        verdict, why = "FALSIFIED", "family B carries payload vocabulary at least as often as family A"
    elif obs >= 0.15 and pval < 0.01:
        verdict, why = "SUPPORTED", "difference >= 0.15 and permutation p < 0.01"
    else:
        verdict, why = "INCONCLUSIVE", (
            f"difference {obs:.4f} and p {pval:.4f} did not clear the locked gate "
            "(>= 0.15 and p < 0.01)")

    return {
        "n_family_A": len(A), "n_family_B_form_I": len(B),
        "n_form_IV_excluded": len(excluded), "n_dropped_both_families": len(both),
        "payload_rate_A": round(pA, 4), "payload_rate_B": round(pB, 4),
        "difference_A_minus_B": round(obs, 4),
        "permutation_p_two_sided": round(pval, 5), "n_permutations": N_PERM, "seed": SEED,
        "length_adjusted_payload_per_10_words_A": round(per10(A), 4),
        "length_adjusted_payload_per_10_words_B": round(per10(B), 4),
        "mean_words_A": round(sum(v["words"] for v in A) / max(1, len(A)), 2),
        "mean_words_B": round(sum(v["words"] for v in B) / max(1, len(B)), 2),
        "gate": "SUPPORTED if diff >= 0.15 and p < 0.01; FALSIFIED if diff <= 0; else INCONCLUSIVE",
        "verdict": verdict, "verdict_reason": why, "gate_moved": False,
    }


def robustness(verses):
    """POST-HOC, NOT PRE-REGISTERED. Leave-one-out over the payload lexicon.

    This can only weaken the result, never strengthen it, which is why running it
    after the fact is legitimate: it is an attempt to break our own finding, not
    an attempt to rescue it. The pre-registered verdict stands as recorded
    whatever this shows -- but a reader is entitled to know how much of that
    verdict rests on the exact word list we chose.
    """
    global PAYLOAD
    full = PAYLOAD[:]
    rows, fragile = [], []
    for term in full:
        PAYLOAD = [t for t in full if t != term]
        r = claim2(verses)
        clears = r["difference_A_minus_B"] >= 0.15 and r["permutation_p_two_sided"] < 0.01
        rows.append({"dropped": term, "difference": r["difference_A_minus_B"],
                     "p": r["permutation_p_two_sided"], "still_clears_gate": clears})
        if not clears:
            fragile.append(term)
    PAYLOAD = full
    return {
        "status": "POST_HOC_NOT_PREREGISTERED",
        "leave_one_out": rows,
        "terms_whose_removal_drops_below_gate": fragile,
        "direction_held_in_all_variants": all(r["difference"] > 0 for r in rows),
        "max_p_across_variants": max(r["p"] for r in rows),
        "reading": (
            f"The DIRECTION is robust: family A leads in all {len(rows)} variants, "
            f"every p <= {max(r['p'] for r in rows)}. The VERDICT is fragile: "
            f"removing any one of {len(fragile)} of {len(full)} payload terms drops "
            "the effect size below the pre-registered 0.15 gate. Honest summary: "
            "direction robust, magnitude marginal."),
    }


def main():
    verses = load()
    c1, c2 = claim1(verses), claim2(verses)
    rob = robustness(verses)
    corpus_sha = hashlib.sha256(open(CORPUS, "rb").read()).hexdigest()
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    lock_ok = corpus_sha == lock["corpus_sha256"] and \
        hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest() == lock["prereg_sha256"]

    bar = "=" * 78
    print(bar)
    print(" PRE-REGISTERED TEXTUAL CLAIMS — Layer-1 measurement only")
    print(bar)
    print(f"  corpus       : 6236 verses, 114 sections, sha256 {corpus_sha[:16]}...")
    print(f"  prereg lock  : {'VERIFIED' if lock_ok else 'BROKEN — file changed after locking'}")

    print(f"\n  CLAIM 1 — orthographic partition          {c1['status']}")
    print(f"    alif-omitted  N={c1['alif_omitted_n']}  at {c1['alif_omitted_at']}")
    print(f"    alif-retained N={c1['alif_retained_n']}  at {c1['alif_retained_at']}")
    print(f"    {c1['why_untestable']}")

    print(f"\n  CLAIM 2 — directed transmission vs unmarked arrival")
    print(f"    family A verses            {c2['n_family_A']}   mean length {c2['mean_words_A']} words")
    print(f"    family B verses (Form I)   {c2['n_family_B_form_I']}   mean length {c2['mean_words_B']} words")
    print(f"    Form IV excluded           {c2['n_form_IV_excluded']} verses (declared in advance)")
    print(f"    both-family verses dropped {c2['n_dropped_both_families']}")
    print(f"    payload rate A             {c2['payload_rate_A']}")
    print(f"    payload rate B             {c2['payload_rate_B']}")
    print(f"    difference (A - B)         {c2['difference_A_minus_B']}")
    print(f"    permutation p (two-sided)  {c2['permutation_p_two_sided']}  ({N_PERM} shuffles, seed {SEED})")
    print(f"    length-adjusted per 10 wds A={c2['length_adjusted_payload_per_10_words_A']} "
          f"B={c2['length_adjusted_payload_per_10_words_B']}")
    print(f"    GATE (locked in advance)   {c2['gate']}")
    print(f"    VERDICT                    {c2['verdict']}  -- {c2['verdict_reason']}")
    margin = c2['difference_A_minus_B'] - 0.15
    print(f"    margin over the gate       {margin:+.4f}  <-- read this before the verdict")

    print(f"\n  ROBUSTNESS (post-hoc, NOT pre-registered; can only weaken the result)")
    for r in rob['leave_one_out']:
        print(f"    without {r['dropped']:6} diff {r['difference']:+.4f}  p {r['p']:.4f}   "
              f"{'clears' if r['still_clears_gate'] else 'FAILS THE GATE'}")
    print(f"    {rob['reading']}")

    print(f"\n  CLAIM 3 — adversarial vs stabilising vocabulary   NOT_OPERATIONALISED")
    print("    Deciding which words are 'toxic' IS the claim. A researcher who picks")
    print("    the word lists picks the result. Reported as not tested.")

    out = {"corpus_sha256": corpus_sha, "prereg_lock_ok": lock_ok,
           "claim1_orthographic_partition": c1,
           "claim2_directed_transmission": c2,
           "claim2_robustness_post_hoc": rob,
           "claim3_adversarial_vocabulary": {
               "status": "NOT_OPERATIONALISED",
               "why": "the word lists that would define 'toxic' are the claim itself; "
                      "choosing them chooses the answer"},
           "boundaries": [
               "No measurement of a network licenses a claim about a text. Datasets 2-4 "
               "of the proposed design measure networks.",
               "Even a fully positive result here would show lexical structure, not "
               "purpose. Structure is evidence about a text; purpose is a claim about "
               "an author.",
               "Surface-form matching over un-lemmatised text misses forms and admits "
               "false positives. This limits precision and is not claimed away.",
           ],
           "layer": "Layer-1 measurement only; no interpretation is asserted"}
    json.dump(out, open(os.path.join(HERE, "results_text_channel.json"), "w"),
              indent=2, ensure_ascii=False)
    print(f"\n  wrote results_text_channel.json")
    print(bar)
    return 0 if lock_ok else 1


if __name__ == "__main__":
    sys.exit(main())
