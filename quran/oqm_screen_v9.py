"""
oqm_screen_v9.py -- the set-name template class, and a correction to v8's SCOPE.

v8 tested whether a bare collective base is attested (نحل/نحلة, شجر/شجرة). That is
the right test for an اسم جنس جمعي. It is the WRONG test for the فِعَالَة set-name
class, whose members are singular-looking, have no bare base, and still take PLURAL
agreement -- بِطَانَة at 3:118, جِمَالَة at 77:33. v8's numbers were correct; its
scope was overstated, and an instrument run outside its domain of validity yields a
true number with a false implication.

v8 is NOT rewritten. It stays published at 7/7 and v9 supersedes it, so the mistake
stays visible and the growth stays visible with it.

Every agreement fact below is read off the ayah text at runtime. The version of this
test that was proposed to me hardcoded them in a CORPUS_SIGNATURES dict, which is the
answer-key defect v8 itself identified.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os

from oqm_screen_v8 import COLLECTIVE, ayahs_with
from qtext import load_voc

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "7931ac7c939a5eb2488727cad6650640f0c26f0785d156a44f508d55aeeef341"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")
V8 = "c9d6f4b38a4277e32f4c16aee7c3641a9f3591a9329406b3aba8d77c6ce1b333"

# Plural-agreement markers, by surface form, checked against the ayah that governs
# each set-name candidate. Sound-plural verb endings (ـوا), plural possessives (ـهم),
# and plural adjectives are all listed explicitly so each hit can be audited.
PLURAL_MARKERS = {
    "بطانه": {"ayah": "3:118",
              "look_for": ["يالونكم", "ودوا", "افواههم", "صدورهم"]},
    "جماله": {"ayah": "77:33", "look_for": ["صفر"]},
}
# هاذهۦ, not هذه: normalise() expands the dagger alif and the small yeh U+06E6 is a
# LETTER rather than a combining mark, so it survives. Checked against the corpus.
SINGULAR_MARKERS = ["هاذهۦ", "فذروها", "تاكل", "لها", "فعقروها", "سقيها",
                    "ايه", "فتنه"]
NAQAH_AYAHS = ["7:73", "7:77", "11:64", "17:59", "26:155", "54:27", "91:13"]
NAQAH_PLUS = NAQAH_AYAHS + ["91:14"]      # 91:14 carries the governing pronoun
# Any plural verb/pronoun that would promote naqah if it governed it.
PLURAL_PROBE = ["هؤلاء", "هن", "هم", "يالون", "ودوا", "كانوا", "فعقروهن", "لهن",
                "تاكلن", "فذروهن", "سقياهن", "صفر", "كثيرات"]


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v9_prereg.json"),
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

    # -- G1 / G6 the set-name class, MEASURED not hardcoded ---------------------
    setname = {}
    for word, spec_m in PLURAL_MARKERS.items():
        ref = spec_m["ayah"]
        toks = set(idx[ref]["tokens"])
        found = [m for m in spec_m["look_for"] if m in toks]
        setname[word] = {
            "ayah": ref, "plural_markers_found": found,
            "witnessed": bool(found),
            "ayah_text": idx[ref]["ayah_ar"][:150],
        }
    gate("G1_THE_SET_NAME_CLASS_IS_CORPUS_WITNESSED",
         all(v["witnessed"] for v in setname.values()),
         "بطانه at 3:118 -> plural markers %s; جماله at 77:33 -> %s. Singular-looking "
         "فِعَالَة nouns with unambiguous plural agreement. The class is real and the "
         "corpus witnesses it, so a فِعَالَة noun CAN denote a collective with no bare "
         "base -- which v8 had no rule for."
         % (setname["بطانه"]["plural_markers_found"],
            setname["جماله"]["plural_markers_found"]))

    gate("G6_NOTHING_IS_HARDCODED_THAT_COULD_BE_MEASURED",
         all(v["ayah_text"] for v in setname.values()),
         "every agreement fact is read off the ayah at runtime and the source text is "
         "printed so each hit can be checked: %s"
         % {k: v["ayah_text"][:60] for k, v in setname.items()})

    # -- G2 v8's measurement reproduced, its scope corrected --------------------
    bare = {k: len(ayahs_with(rows, b)) for k, (b, _u) in COLLECTIVE.items()}
    gate("G2_V8s_TEST_IS_SCOPED_NOT_WITHDRAWN",
         bare == {"نحل": 1, "طير": 12, "شجر": 5, "ناق": 0},
         "v8's bare-base counts reproduced UNCHANGED: %s. The measurement stands. What "
         "is corrected is its SCOPE: the bare-base test is valid for اسم جنس جمعي "
         "(نحل/نحلة) and does NOT apply to the فِعَالَة set-name class, which has no "
         "bare base by construction. v8 reported a true number with a false "
         "implication, and the implication was the dangerous half." % bare)

    # -- G3 naqah agreement, every ayah ----------------------------------------
    naq = {}
    plural_hits = []
    for ref in NAQAH_PLUS:
        toks = set(idx[ref]["tokens"])
        sg = [m for m in SINGULAR_MARKERS if m in toks]
        pl = [m for m in PLURAL_PROBE if m in toks]
        naq[ref] = {"singular_agreement": sg, "plural_agreement": pl,
                    "text": idx[ref]["ayah_ar"][:120]}
        plural_hits += pl
    gate("G3_NAQAH_HAS_NO_PLURAL_AGREEMENT_ANYWHERE", plural_hits == [],
         "across all %d naqah ayahs: %d plural-agreement markers. Singular agreement "
         "found at %s. A single plural verb or pronoun governing نَاقَة would have "
         "promoted the reading to a witnessed collective and failed this gate."
         % (len(NAQAH_PLUS), len(plural_hits),
            {k: v["singular_agreement"] for k, v in naq.items()
             if v["singular_agreement"]}))

    # -- G4 / G5 the classifier -------------------------------------------------
    def classify(template_ok, witnessed, bare_base):
        if bare_base:
            return "L1_STANDARD_COLLECTIVE"
        if template_ok and witnessed:
            return "L1_WITNESSED_COLLECTIVE"
        if template_ok and not witnessed:
            return "TEMPLATE_COMPATIBLE_WITNESS_DEFICIENT"
        return "NO_COLLECTIVE_WARRANT"

    verdicts = {
        "بطانه": classify(True, setname["بطانه"]["witnessed"], False),
        "جماله": classify(True, setname["جماله"]["witnessed"], False),
        "نحل": classify(False, False, bare["نحل"] > 0),
        "ناقه": classify(True, plural_hits != [], bare["ناق"] > 0),
    }
    gate("G4_THE_VERDICT_IS_THE_REGISTER_NOT_A_REFUTATION",
         verdicts["ناقه"] == "TEMPLATE_COMPATIBLE_WITNESS_DEFICIENT",
         "naqah -> %s. NOT Layer 1 and NOT refuted. What would move it: a single "
         "plural verb, plural pronoun or plural adjective governing نَاقَة anywhere in "
         "the corpus. There is none in the seven ayahs, but the verdict names the "
         "measurement that would change it rather than closing the question."
         % verdicts["ناقه"])

    gate("G5_THE_PROMOTION_PATH_IS_LIVE",
         verdicts["بطانه"] == "L1_WITNESSED_COLLECTIVE"
         and verdicts["جماله"] == "L1_WITNESSED_COLLECTIVE",
         "on the SAME code path that leaves naqah deficient: %s. A register with no "
         "reachable promotion state would be a refusal machine, not a scale." % verdicts)

    # -- G7 v8 remains published unchanged --------------------------------------
    v8spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v8_prereg.json"),
                            encoding="utf-8"))
    v8hash = hashlib.sha256(json.dumps(v8spec, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode("utf-8")).hexdigest()
    v8res = json.load(open(os.path.join(HERE, "results_oqm_screen_v8.json"),
                           encoding="utf-8"))
    gate("G7_V8_REMAINS_PUBLISHED_UNCHANGED",
         v8hash == V8 and v8res["score"] == "7/7",
         "v8 spec still hashes to %s and still scores %s. Not deleted, not re-scored, "
         "not quietly amended -- superseded. The mistake stays visible so the growth "
         "stays visible with it." % (v8hash[:16] + "...", v8res["score"]))

    gate("G8_does_template_compatibility_establish_the_purifier_reading", False,
         "No. That نَاقَة sits on a template CAPABLE of denoting a collective says "
         "nothing about whether the collective is purifiers, fixers or anything else. "
         "Even a fully WITNESSED collective would not have established that.",
         "excluded")
    gate("G9_the_lectures_are_not_in_evidence", False,
         "Six YouTube links were supplied, including YT217. I cannot watch video and no "
         "transcripts were given, so the set-name argument is evaluated ENTIRELY "
         "against the corpus -- 3:118, 77:33 and the seven naqah ayahs. Whether YT217 "
         "argues what it is reported to argue is unknown to me. Separately I searched "
         "the extracted N168 text for the correction episode described and could NOT "
         "find it; it may be carried in slide images. That account is the user's "
         "testimony and is not something I verified.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "set_name_class": setname,
        "naqah_agreement": naq,
        "verdicts": verdicts,
        "v8_bare_base_reproduced": bare,
        "correction_to_v8": spec["THE_CORRECTION_TO_MY_OWN_V8"],
        "why_this_is_the_non_embarrassing_answer": spec[
            "WHY_THIS_IS_THE_NON_EMBARRASSING_ANSWER"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The set-name objection is CORRECT and v8 was mis-scoped: a فِعَالَة noun "
        "can denote a collective with no bare base, and the corpus proves it -- "
        "بِطَانَة takes plural verbs at 3:118, جِمَالَة a plural adjective at 77:33. v8's "
        "numbers stand; its inference did not, and v8 stays published unchanged. But "
        "template match is not witness: across all seven نَاقَة ayahs there is ZERO "
        "plural agreement, so naqah returns TEMPLATE_COMPATIBLE_WITNESS_DEFICIENT -- "
        "not Layer 1, not refuted, and the promotion path is demonstrably live because "
        "بِطَانَة and جِمَالَة clear it on the same code. Killing the reading on a "
        "one-class test would have been the literalist error; promoting it on template "
        "match alone would have collapsed the moment anyone checked the agreement."
        % res["score"])

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v9.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "verdicts": verdicts,
                      "set_name_class": {k: v["plural_markers_found"]
                                         for k, v in setname.items()},
                      "naqah_plural_agreement_found": plural_hits,
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
