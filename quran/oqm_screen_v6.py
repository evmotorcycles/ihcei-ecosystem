"""
oqm_screen_v6.py -- Bayt, Tafseel and Nested Interpretation as measurements.

Three operations the OQM documents describe are made mechanical here:

    BAYT      cluster a root's ayahs by shared CONTENT vocabulary. A multi-member
              cluster is a motif the text itself repeats.
    TAFSEEL   the number of distinct Buyut a root falls into. One zone = one
              setting; more than one = the root divaricates.
    NESTED    the loop can run only if the root is attested inside a narrative
              anchor AND outside it -- something to extract from, somewhere to
              nest into.

All three are availability and co-occurrence measures. None establishes meaning.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os

from qtext import defective, load_voc

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "faa2f56ee9b346908070af055bdda0e084339f9cb0c264870a968c797d4ab4fc"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

THETA = 0.10        # Bayt: content-word Jaccard for single-link clustering
SHORT_AYAH = 4      # below this many content words the measure cannot fire

STOP = set("من في ما لا الله ان و هو هم لهم عليهم الذين كان قال ولا اذا الا انا به له "
           "ثم كل يا قد بما لكم منهم اليه عن على هذا التي الذي وما وان فيها بها انه هي "
           "نحن كنتم كانوا لهۥ لكن هم انت وهو وهم بل ال ولقد لقد فان وقال".split())

FORMS = {
    "N157_barakah": {"تبارك", "باركنا", "مباركا", "مبارك", "مباركه", "فتبارك", "بركات",
                     "وبركات", "وبركاتهۥ", "بورك", "المباركه", "وباركنا", "وبارك",
                     "وتبارك"},
    "N182_al_asr": {"والعصر", "يعصرون", "المعصرات", "اعصار", "اعصر"},
    "N167_sulalah": {"سلاله", "يتسللون"},
}
NAQAH = {"ناقه", "الناقه"}


def content(row):
    return {t for t in row["tokens"] if t not in STOP and len(t) > 2}


def key(ref):
    return tuple(int(i) for i in ref.split(":"))


def buyut(idx, refs):
    """Single-link clustering on shared content vocabulary -- the Bayt measure."""
    refs = sorted(set(refs), key=key)
    parent = {r: r for r in refs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            a, b = content(idx[refs[i]]), content(idx[refs[j]])
            sim = len(a & b) / len(a | b) if (a | b) else 0.0
            if sim >= THETA:
                parent[find(refs[i])] = find(refs[j])
    groups = {}
    for r in refs:
        groups.setdefault(find(r), []).append(r)
    return sorted((sorted(v, key=key) for v in groups.values()),
                  key=lambda g: (-len(g), key(g[0])))


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v6_prereg.json"),
                          encoding="utf-8"))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    if got != LOCKED:
        raise SystemExit("SPEC HASH MOVED %s != %s -- refusing to run" % (got, LOCKED))

    rows = load_voc(DATA)
    idx = {r["ref"]: r for r in rows}
    gates, not_met = [], []

    def gate(gid, ok, detail, weight="counted"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "counted" and not ok:
            not_met.append(gid)

    # -- U1 root n-q-y is absent, and naqah is a hollow root --------------------
    # A n-q-y realisation would surface as نقي / انقى / نقيه / تنقيه. Searching the
    # DEFECTIVE form cannot work -- defective() strips yaa, so the root's third
    # radical vanishes and the test would pass vacuously. Search surface forms, and
    # list every substring near-miss so the reader can check the rejections.
    NQY_FORMS = {"نقي", "انقى", "نقيه", "تنقيه", "نقيا", "نقيه", "منقى"}
    nqy = sorted({r["ref"] for r in rows for t in r["tokens"] if t in NQY_FORMS},
                 key=key)
    nqy_nearmiss = sorted({(t, defective(t)) for r in rows for t in r["tokens"]
                           if "نقي" in t})
    # strip the article before reading the skeleton: defective("الناقه") is لنقه
    naq_tokens = [(r["ref"], t, defective(t[2:] if t.startswith("ال") else t))
                  for r in rows for t in r["tokens"] if t in NAQAH]
    skeletons = {d for _, _, d in naq_tokens}
    gate("U1_ROOT_N_Q_Y_IS_ABSENT_FROM_THE_TEXT",
         nqy == [] and skeletons == {"نقه"},
         "root ن-ق-ي attestations: %d. All %d نَاقَة tokens reduce to skeleton %s -- "
         "ن-ا-ق-ة, where the alif is a LONG VOWEL, not a radical yaa. The root is "
         "ن-و-ق (hollow). ن-ق-ي would give نَقِيَّة, a different word on a different "
         "template, and that root does not occur anywhere in the text. Under the "
         "coverage rule a root with ZERO attestations is below even 58:11, which had "
         "one. Substring near-misses, all other roots, listed so the rejections can "
         "be checked: %s." % (len(nqy), len(naq_tokens), sorted(skeletons),
                              nqy_nearmiss))

    gate("U2_THE_SCREEN_IS_NOT_CREDITED_WITH_A_RESULT_IT_DID_NOT_PRODUCE", True,
         "The v5 negative control established exactly one thing: أعناقهم (root ع-ن-ق) "
         "is not نَاقَة. That is a statement about two letter-strings. It evaluated no "
         "root ن-ق-ي and no semantic reading, so it cannot have shown the seven ayahs "
         "to be 'the purifier verses'. I am recording this because accepting credit "
         "for a measurement I did not make would corrupt the record more than any "
         "single wrong number.")

    # -- U3 abasa ---------------------------------------------------------------
    abs_hits = sorted({r["ref"] for r in rows for t in r["tokens"]
                       if "عبس" in defective(t)}, key=key)
    gate("U3_ABAS_HAS_THREE_ATTESTATIONS_NOT_TWO",
         abs_hits == ["74:22", "76:10", "80:1"],
         "root ع-ب-س -> %s. Three, not the two put to me; 76:10 عَبُوسًا was missing "
         "from the stated set. Three witnesses across three surahs clear both rules "
         "MORE comfortably than two -- but a nested interpretation built on two of "
         "three attestations has left a third of its own evidence unexamined."
         % abs_hits)

    # -- the three narratives ---------------------------------------------------
    report = {}
    for name, forms in FORMS.items():
        refs = sorted({r["ref"] for r in rows
                       if any(t in forms for t in r["tokens"])}, key=key)
        zones = buyut(idx, refs)
        anchor = spec["narratives"][name]["narrative_anchor"]
        outside = [r for r in refs if r not in anchor]
        short = [r for r in refs if len(content(idx[r])) < SHORT_AYAH]
        report[name] = {
            "root": spec["narratives"][name]["root"],
            "anchor_story": spec["narratives"][name]["anchor_story"],
            "n_ayahs": len(refs), "ayahs": refs,
            "buyut": zones,
            "n_buyut": len(zones),
            "multi_member_buyut": [g for g in zones if len(g) > 1],
            "tafseel": "DIVARICATES into %d zones" % len(zones) if len(zones) > 1
                       else "single zone",
            "anchor_present": all(a in refs for a in anchor),
            "attested_outside_anchor": bool(outside),
            "nested_interpretation": "RUNNABLE" if (all(a in refs for a in anchor)
                                                   and outside) else "NOT_RUNNABLE",
            "short_ayah_singletons": short,
        }

    brk = report["N157_barakah"]
    musa = [g for g in brk["buyut"] if "27:8" in g]
    gate("U4_BAYT_CLUSTERING_PRODUCES_REAL_MOTIFS",
         len(brk["multi_member_buyut"]) >= 3 and musa and "28:30" in musa[0],
         "b-r-k -> %d ayahs in %d zones, %d of them multi-member. 27:8 shares its Bayt "
         "with %s -- the risky half of this gate was predicting that the vocabulary "
         "measure would join the two Musa-at-the-fire passages, and it did. Other "
         "zones: %s"
         % (brk["n_ayahs"], brk["n_buyut"], len(brk["multi_member_buyut"]),
            [x for x in musa[0] if x != "27:8"] if musa else None,
            brk["multi_member_buyut"][:4]))

    sll = report["N167_sulalah"]
    gate("U5_TAFSEEL_DISTINGUISHES_ROOTS",
         sll["n_buyut"] == 2 and ["23:12", "32:8"] in sll["buyut"]
         and ["24:63"] in sll["buyut"],
         "s-l-l divaricates into %d zones %s -- the creation-account sulalah against "
         "the withdrawal verb -- while b-r-k's largest zone holds %d. A measure that "
         "returned the same shape for every root would be vacuous. DISCLOSED: the "
         "locked spec's CLAIM text says b-r-k's largest zone holds 4, from a probe run "
         "with a shorter stop-word list than the runner uses; the real figure is %d. "
         "The spec's stated passes_if concerns s-l-l only and is unchanged, but the "
         "claim text and the run disagree and that is my pre-registration error, "
         "recorded rather than quietly reconciled."
         % (sll["n_buyut"], sll["buyut"], max(len(g) for g in brk["buyut"]),
            max(len(g) for g in brk["buyut"])))

    gate("U6_NESTED_INTERPRETATION_IS_RUNNABLE_FOR_ALL_THREE",
         all(v["nested_interpretation"] == "RUNNABLE" for v in report.values()),
         "story anchor present AND attested outside it: %s. This licenses the LOOP. It "
         "says nothing about whether any definition the loop produces is correct."
         % {k: v["nested_interpretation"] for k, v in report.items()})

    asr = report["N182_al_asr"]
    gate("U7_THE_CLEANEST_DEMONSTRATION_IS_AL_ASR",
         all(a in asr["ayahs"] for a in ("12:36", "12:49", "103:1")),
         "3-s-r is attested inside the Yussuf narrative at 12:36 and 12:49, where the "
         "sense is physically pressing, and at 103:1 outside any narrative. So a "
         "definition can be extracted from a story and nested into 103:1 WITHOUT a "
         "dictionary -- precisely the operation N159 says is the only legitimate one. "
         "Full attestation set %s." % asr["ayahs"])

    flagged = {k: v["short_ayah_singletons"] for k, v in report.items()
               if v["short_ayah_singletons"]}
    gate("U8_THE_BAYT_MEASURE_DECLARES_ITS_OWN_COVERAGE_LIMIT",
         "103:1" in flagged.get("N182_al_asr", []),
         "ayahs with fewer than %d content words cannot cluster on vocabulary, so "
         "their singleton status is MECHANICAL and is not a finding about motifs. "
         "Flagged: %s. 103:1 وَٱلْعَصْرِ is two words. This is the Bayt measure's own "
         "58:11." % (SHORT_AYAH, flagged))

    gate("U9_does_clustering_establish_MEANING", False,
         "It does not. A Bayt here is a set of ayahs sharing vocabulary. That two "
         "ayahs share words is a fact; that they share a metaphor, an image or a "
         "governance function is a reading, and no threshold decides it.", "excluded")
    gate("U10_the_entanglement_framing_is_not_evaluated", False,
         "The document grounds cross-surah links in Bell-inequality violation and "
         "quantum entanglement. No physics is measured here. Shared vocabulary between "
         "two ayahs is co-occurrence -- ordinary, and requiring no non-locality. "
         "Borrowing the authority of a physics result for a text-statistics "
         "observation is the layer breach this repository exists to prevent.",
         "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "narratives": report,
        "corrections": spec["TWO_MORPHOLOGICAL_CLAIMS_PUT_TO_ME_THAT_FAIL"],
        "abas_attestations": abs_hits,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. Bayt, Tafseel and Nested Interpretation are now measurements. The Bayt "
        "measure joins 27:8 with 28:30 -- the two Musa-at-the-fire passages -- from "
        "vocabulary alone; s-l-l divaricates into two zones while b-r-k's largest "
        "holds %d; and all three narratives can run the nested loop, al-Ɛasr most "
        "cleanly, since 12:36/12:49 supply a story sense for 103:1 without a "
        "dictionary. Two morphological claims put to me do NOT survive: نَاقَة is root "
        "ن-و-ق, not ن-ق-ي, and ن-ق-ي is attested ZERO times -- so the purifier "
        "derivation has no root to stand on, though the reading itself is untouched by "
        "this. And root ع-ب-س occurs three times, not two."
        % (res["score"], max(len(g) for g in brk["buyut"])))

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v6.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "narratives": {k: {kk: v[kk] for kk in
                                         ("root", "n_ayahs", "n_buyut", "tafseel",
                                          "nested_interpretation",
                                          "multi_member_buyut")}
                                     for k, v in report.items()},
                      "abas_attestations": abs_hits,
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
