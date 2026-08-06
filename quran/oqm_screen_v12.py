"""
oqm_screen_v12.py -- the adversarial blind-spot audit.

Every previous version was built to test a claim. This one is built to find MY OWN
instrument's limits. Every counted gate PASSES BY CONFIRMING A DEFECT: there is no
configuration of this file in which the screen comes out looking competent at Arabic
morphology.

The headline, stated before any number: there is NO morphological analyser anywhere in
this codebase. Every root match in every version was made either by an enumerated
surface-form list curated by hand, ayah by ayah, or by substring contiguity on a lossy
consonant skeleton. The screen does not know Arabic. Where its answers were right,
they were right because a human checked each form.

Aborts if the spec hash has moved.
"""
import collections
import hashlib
import json
import os
import re

from qtext import defective, load_voc, normalise

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "58e4b34718cb56d6f976731c850c7a95d3224e7366d6a7ba0ba5984806413bab"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")
HAMZA = re.compile(r"[ءأإئؤ]")


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v12_prereg.json"),
                          encoding="utf-8"))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    if got != LOCKED:
        raise SystemExit("SPEC HASH MOVED %s != %s -- refusing to run" % (got, LOCKED))

    rows = load_voc(DATA)
    gates, not_met = [], []

    def gate(gid, ok, detail, weight="counted"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "counted" and not ok:
            not_met.append(gid)

    toks = set()
    for r in rows:
        toks.update(t for t in r["tokens"] if len(t) > 2)
    coll = collections.defaultdict(set)
    for t in toks:
        coll[defective(t)].add(t)
    multi = {k: v for k, v in coll.items() if len(v) > 1}
    rate = 100.0 * len(multi) / len(coll)
    worst = sorted(((len(v), k) for k, v in coll.items()), reverse=True)[:8]

    # -- K1 collision at scale ---------------------------------------------------
    qal_key = defective(normalise("قال"))
    aqall_key = defective(normalise("أقل"))
    gate("K1_DEFECTIVE_COLLIDES_UNRELATED_ROOTS_AT_SCALE",
         rate > 25.0 and qal_key == aqall_key,
         "%d of %d defective keys collapse more than one surface form = %.1f%%. Worst "
         "keys %s. The key %r merges ق-و-ل (قال, to say) with ق-ل-ل (أقل, fewer) -- two "
         "unrelated roots. PASSING THIS GATE MEANS THE DEFECT IS REAL."
         % (len(multi), len(coll), rate, [(k, n) for n, k in worst], qal_key))

    # -- K2 hollow roots ---------------------------------------------------------
    hollow = {w: defective(normalise(w))
              for w in ("قال", "يقول", "قل", "قيل", "قولوا")}
    gate("K2_WEAK_ROOTS_ARE_NOT_HANDLED",
         len(set(hollow.values())) == 1 and aqall_key in set(hollow.values()),
         "%s -- all five hollow-root forms reduce to one key, which LOOKS like correct "
         "grouping but is a collision: أقل (root ق-ل-ل) reduces to the same key. The "
         "medial radical is destroyed, so ق-و-ل and ق-ل-ل are indistinguishable."
         % hollow)

    # -- K3 geminate roots -------------------------------------------------------
    gem = {w: defective(normalise(w))
           for w in ("رد", "ردوا", "يرتد", "مردود", "ردت")}
    gate("K3_GEMINATE_ROOTS_ARE_SPLIT", len(set(gem.values())) > 2,
         "%s -> %d distinct keys for ONE root (ر-د-د). A matcher that splits a single "
         "root into several is unusable for the nested-interpretation work OQM "
         "requires, because the witnesses never meet."
         % (gem, len(set(gem.values()))))

    # -- K4 broken plurals -------------------------------------------------------
    bp = {}
    for a, b in (("كتاب", "كتب"), ("رسول", "رسل"), ("عالم", "علماء"), ("نبي", "نبيون")):
        bp["%s/%s" % (a, b)] = defective(normalise(a)) == defective(normalise(b))
    gate("K4_BROKEN_PLURALS_ARE_UNRELIABLE",
         any(bp.values()) and not all(bp.values()),
         "%s -- some merge, some do not. Unreliability is WORSE than uniform failure, "
         "because it looks like it works." % bp)

    # -- K5 the homograph class --------------------------------------------------
    byn = collections.defaultdict(set)
    for r in rows:
        for raw in r["raw"]:
            byn[normalise(raw)].add(bool(HAMZA.search(raw)))
    amb = sorted(k for k, v in byn.items() if len(v) > 1)
    gate("K5_THE_HOMOGRAPH_CLASS_IS_LARGER_THAN_THE_ONE_I_FOUND", len(amb) > 20,
         "%d normalised tokens collapse hamza-bearing and hamza-free raw forms, out of "
         "%d distinct tokens. Most are benign orthographic variants of ONE word -- but "
         "قري was in this class and was NOT benign, and I have audited NONE of the "
         "others. Sample: %s" % (len(amb), len(byn), amb[:14]))

    # -- K6 no analyser exists ---------------------------------------------------
    mechanisms = {
        "v1/v2 designation": "enumerated verb forms + uniform proclitic rule",
        "v3 f-s-h / j-l-s": "defective() contiguity + waṣla stem rule",
        "v4 four narratives": "defective() candidate generation + HAND adjudication",
        "v6 Bayt/Tafseel": "enumerated form sets per narrative",
        "v8/v9 collective": "enumerated bare-base and unit-form sets",
        "v10 Iqra": "v4's hand-adjudicated list + hamza disambiguator",
        "v11 YT169 table": "enumerated form sets per row",
    }
    gate("K6_NO_MORPHOLOGICAL_ANALYSER_EXISTS", True,
         "matching mechanism by version: %s. Not one is a morphological analyser. "
         "There is no root extractor, no pattern matcher, no lexicon, no morphological "
         "model anywhere in this codebase. The screen does not know Arabic."
         % mechanisms)

    # -- K7 the design lesson ----------------------------------------------------
    gate("K7_THE_ARCHITECTURE_THAT_SAVED_THE_RESULTS", True,
         "Where the screens OVER-generated candidates and then adjudicated EVERY "
         "candidate visibly -- v4, v9, v10, v11 -- the weakness of defective() was "
         "contained, because a human checked each form and the rejections were printed "
         "for audit. Where a rule was applied WITHOUT that adjudication it failed: v3's "
         "proclitic rule ate 27:8 بُورِكَ, and v8's bare-base test was applied outside "
         "its domain. Over-generate then adjudicate visibly is the only pattern here "
         "that survived contact with the corpus.")

    gate("K8_does_this_invalidate_the_prior_results", False,
         "No, and it must not be read that way. Each specific finding rested on a "
         "hand-checked form list or a printed adjudication: ع-ب-س is three not two, "
         "كِذَّاب has two maṣdar witnesses not one, قري collides two roots, shadda was "
         "being deleted, 27:8 was wrongly rejected, أَبَابِيل is a hapax. Those stand. "
         "What is invalidated is any impression of general morphological competence. "
         "There is none.", "excluded")
    gate("K9_could_this_be_fixed", False,
         "Yes, and stating the fix is part of the audit. It needs a real morphological "
         "resource -- a root-annotated Quranic corpus such as the Quranic Arabic "
         "Corpus, or a morphological analyser. Neither is present in this container and "
         "neither has been used. Until one is, every root claim this screen makes must "
         "rest on an enumerated, hand-checked, printed form list, and should be read "
         "as exactly that and nothing more.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "collision_rate_pct": round(rate, 1),
        "defective_keys": len(coll), "colliding_keys": len(multi),
        "worst_collisions": [{"key": k, "n_forms": n,
                              "sample": sorted(coll[k])[:6]} for n, k in worst],
        "hollow_root": hollow, "geminate_root": gem, "broken_plurals": bp,
        "hamza_homograph_tokens": len(amb),
        "matching_mechanisms": mechanisms,
        "headline": spec["THE_HEADLINE_FINDING_STATED_UP_FRONT"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s -- and every one of those gates PASSES BY CONFIRMING A DEFECT. The "
        "skepticism was justified. There is NO morphological analyser anywhere in this "
        "codebase: %.1f%% of consonant-skeleton keys collapse multiple surface forms, "
        "the key قل merges ق-و-ل with ق-ل-ل, hollow roots lose their medial radical, "
        "geminate roots split into %d keys, broken plurals merge unreliably, and %d "
        "hamza-homograph tokens sit unaudited -- the class قري came from. The screen "
        "does not know Arabic. Where it has been right it has been right because I "
        "curated and printed every surface form by hand. Its real contribution has "
        "been bookkeeping -- arithmetic and citation discipline over work done by "
        "people who do know the language -- and that is a far smaller claim than "
        "Al-Mīzān."
        % (res["score"], rate, len(set(gem.values())), len(amb)))

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v12.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "collision_rate_pct",
                       "worst_collisions", "hollow_root", "geminate_root",
                       "broken_plurals", "hamza_homograph_tokens",
                       "primary_verdict")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
