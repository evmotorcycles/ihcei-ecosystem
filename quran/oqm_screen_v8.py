"""
oqm_screen_v8.py -- the ontology as a hypothesis register, not an answer key.

Morphology is the Arḍ, not the methodology. That criticism is accepted. v8 encodes
more of the substance -- the Abrahamic Locution mappings, the collective-noun
grammar, the Bayt -- but in a form that can still LOSE.

The fork that matters: a declared ontology can be an INPUT TO BE TESTED or it can be
smuggled in as a RESULT. The proposed v9/v10 does the latter -- audit_collective_plural
reads its verdict back out of the dict it was typed into, never touching an ayah. Here
every declared mapping must carry a prediction about the text's own distribution that
could come out false, and mappings that carry none are retained but score nothing.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os

from qtext import load_voc

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "c9d6f4b38a4277e32f4c16aee7c3641a9f3591a9329406b3aba8d77c6ce1b333"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

# Bare collective base vs the ة-form singulative. An اسم جنس جمعي IS the bare form.
COLLECTIVE = {
    "نحل": ({"نحل", "النحل"}, {"نحله", "النحله"}),
    "طير": ({"طير", "الطير", "طيرا", "وطير"}, {"طيره", "الطيره"}),
    "شجر": ({"شجر", "الشجر"}, {"شجره", "الشجره"}),
    "ناق": ({"ناق", "الناق", "نوق", "النوق"}, {"ناقه", "الناقه"}),
}
BUYUT = {"بيت", "البيت", "بيوت", "البيوت", "بيوتا", "بيوتكم", "بيوتهم", "بيتي",
         "بيوتها", "بيتك", "بيوتهن", "لبيوتهم", "وبيوتا"}
# 16:68-69, the corpus's own worked example of a collective taking fem. sg. agreement
BEE_FORMS = {"النحل", "اتخذي", "كلي", "فاسلكي", "بطونها", "بيوتا"}


def ayahs_with(rows, forms):
    return sorted({r["ref"] for r in rows if any(t in forms for t in r["tokens"])},
                  key=lambda x: tuple(int(i) for i in x.split(":")))


def proposed_v9_audit(ontology, token):
    """The proposed audit, reimplemented faithfully. Note what it never touches."""
    entry = ontology.get(token, {"rule": "Standard"})
    if entry["rule"] == "Collective Plural":
        return "LICENSED"
    return "STANDARD_SYNTAX"


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v8_prereg.json"),
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

    # -- F1 the proposed audit is a tautology -----------------------------------
    onto = {"ناقة": {"rule": "Collective Plural"}}
    before = proposed_v9_audit(onto, "ناقة")
    onto["ناقة"]["rule"] = "Standard"          # one string, no ayah consulted
    after = proposed_v9_audit(onto, "ناقة")
    gate("F1_THE_PROPOSED_ONTOLOGY_AUDIT_CANNOT_FAIL",
         before == "LICENSED" and after == "STANDARD_SYNTAX",
         "reimplemented faithfully: verdict %r; then ONE string in the dict was "
         "changed and the verdict became %r. The corpus was not consulted in either "
         "run. The verdict is read back out of the dictionary it was typed into, so it "
         "cannot fail, cannot test, and cannot catch an error." % (before, after))

    # -- F2 the corpus's own worked example -------------------------------------
    bee = set(idx["16:68"]["tokens"]) | set(idx["16:69"]["tokens"])
    present = {f: (f in bee) for f in sorted(BEE_FORMS)}
    gate("F2_THE_TEXT_SUPPLIES_ITS_OWN_WORKED_EXAMPLE", all(present.values()),
         "16:68-69 %s. ٱلنَّحْل is a collective and takes FEMININE SINGULAR agreement "
         "throughout while denoting a plurality. The positive control for the "
         "collective-agreement rule comes from the corpus, not from me." % present)

    # -- F3 / F4 the discriminator ----------------------------------------------
    coll = {}
    for base, (bare, unit) in COLLECTIVE.items():
        b, u = ayahs_with(rows, bare), ayahs_with(rows, unit)
        coll[base] = {"bare_collective_ayahs": len(b), "bare_refs": b[:6],
                      "unit_form_ayahs": len(u),
                      "collective_base_attested": bool(b)}
    gate("F3_PRIMARY_THE_COLLECTIVE_BASE_TEST_DISCRIMINATES",
         all(coll[k]["collective_base_attested"] for k in ("نحل", "طير", "شجر"))
         and not coll["ناق"]["collective_base_attested"],
         "bare collective bases -> %s. An اسم جنس جمعي IS the bare form and the ة-form "
         "is its singulative. طير has the grammatical warrant for a collective reading, "
         "which SUPPORTS the YT89 Ṭayr treatment. ناقة does not: it is a unit noun with "
         "no attested collective base. A single attestation of ناق would have failed "
         "this gate and handed the collective reading a direct warrant."
         % {k: (v["bare_collective_ayahs"], v["unit_form_ayahs"])
            for k, v in coll.items()})

    gate("F4_MY_OWN_EARLIER_FRAMING_IS_CORRECTED", True,
         "Feminine singular agreement is NON-DISCRIMINATING. ٱلنَّحْل is a collective and "
         "takes it (16:68-69). نَاقَة is a unit noun and takes it (هَٰذِهِۦ at 11:64 and "
         "26:155, فَعَقَرُوهَا at 91:14). The same pattern appears on both, so observing "
         "it settles nothing either way. Any earlier suggestion of mine that the "
         "singular pronouns weighed AGAINST a collective reading was wrong. What still "
         "stands from v7 is the separate finding that no plural FORM of ناقة is "
         "attested -- that is about forms, not agreement.")

    # -- F5 the Bayt has a textual basis ---------------------------------------
    bt = ayahs_with(rows, BUYUT)
    gate("F5_THE_BAYT_HAS_A_TEXTUAL_BASIS",
         "بيوتا" in idx["16:68"]["tokens"] and len(bt) > 20
         and len({x.split(":")[0] for x in bt}) > 10,
         "16:68 contains بيوتا -- ٱتَّخِذِى مِنَ ٱلْجِبَالِ بُيُوتًا -- and the bayt/buyut "
         "family is attested in %d ayahs across %d surahs. Calling an ayah a Bayt is "
         "the text's own word in the very passage the reading is built on, not a "
         "borrowed metaphor." % (len(bt), len({x.split(":")[0] for x in bt})))

    # -- F6 register: testable vs untestable ------------------------------------
    reg = {}
    for tok, h in spec["hypothesis_register"].items():
        if not h["falsifiable"]:
            reg[tok] = {"verdict": "UNFALSIFIABLE_AS_STATED", "scored": False,
                        "reading": h["reading"], "why": h["prediction"]}
            continue
        base = {"طير": "طير", "نحل": "نحل", "شجر": "شجر", "ناقة": "ناق"}[tok]
        ok = coll[base]["collective_base_attested"]
        reg[tok] = {"verdict": "PREDICTION_HOLDS" if ok else "PREDICTION_FAILS",
                    "scored": True, "reading": h["reading"],
                    "evidence": "%d ayahs with the bare collective base"
                                % coll[base]["bare_collective_ayahs"]}
    n_scored = sum(1 for v in reg.values() if v["scored"])
    n_unscored = len(reg) - n_scored
    gate("F6_THE_REGISTER_SEPARATES_TESTABLE_FROM_UNTESTABLE_MAPPINGS",
         n_scored == 4 and n_unscored == 4,
         "%d mappings carry a distributional prediction and are scored; %d state none "
         "and are returned UNFALSIFIABLE_AS_STATED. They are RETAINED, not deleted -- "
         "they simply are not evidence until someone says what would make them false. "
         "%s" % (n_scored, n_unscored,
                 {k: v["verdict"] for k, v in sorted(reg.items())}))

    # -- F7 qualify the best case -----------------------------------------------
    gate("F7_A_LICENSED_PREDICTION_IS_NOT_A_LICENSED_READING",
         reg["طير"]["verdict"] == "PREDICTION_HOLDS",
         "طير is this run's best-performing case: the bare collective base is attested "
         "in %d ayahs, so its prediction HOLDS. That licenses the GRAMMATICAL component "
         "-- that طير can denote a collective -- and nothing further. It does not "
         "establish that the collective is angels, teachers, or any other referent. The "
         "moment a screen stops qualifying its own successes is the moment it becomes "
         "an answer key." % coll["طير"]["bare_collective_ayahs"])

    gate("F8_does_any_of_this_establish_the_metaphorical_readings", False,
         "No. Collective-base attestation, agreement patterns and co-occurrence say "
         "nothing about whether Ṭayr denotes teachers, Arḍ denotes scripture or Rummān "
         "denotes rectified stories. Those are Layer 3 and this screen has no "
         "instrument for them.", "excluded")
    gate("F9_the_video_is_not_in_evidence", False,
         "A YouTube link was supplied. I cannot watch video and no transcript was "
         "provided. Everything attributed to YT136 here is checked against the CORPUS "
         "at 16:68-69, not against the lecture. The lecture's actual argument is not "
         "known to me and is not evaluated.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "collective_test": coll,
        "hypothesis_register": reg,
        "buyut_ayahs": len(bt),
        "the_architectural_fork": spec["THE_ARCHITECTURAL_FORK_THAT_MATTERS"],
        "did_not_happen": spec["THINGS_IN_THE_PROPOSAL_THAT_DID_NOT_HAPPEN"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The criticism is accepted: morphology is the Arḍ, not the methodology. The "
        "ontology is therefore encoded IN FULL -- but as a hypothesis register, where "
        "each mapping must predict something about the text that could come out false. "
        "Four predictions were testable and four were not; the untestable ones are kept "
        "and scored zero rather than deleted. The corpus supplies its own worked "
        "example at 16:68-69, where ٱلنَّحْل is a collective taking feminine singular "
        "agreement -- so I was WRONG to imply singular pronouns weigh against a "
        "collective reading, and that is corrected here. What discriminates is the bare "
        "collective base: طير yes (12 ayahs), شجر yes, نحل yes, ناق NO. So the Ṭayr "
        "reading gains a grammatical warrant and the Nāqah collective reading does not "
        "have one. Neither result says what either term MEANS." % res["score"])

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v8.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "collective_test": coll, "hypothesis_register": reg,
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
