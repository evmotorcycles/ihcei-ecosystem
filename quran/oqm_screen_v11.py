"""
oqm_screen_v11.py -- checking the YT169 corrected table against the corpus it cites.

The corrected Appendix A table carries a 'Quranic Evidence' column with three rows.
A citation column is checkable, and checking citations is what this screen is for.

What is NOT checked: the morphological ARGUMENT -- that a triliteral under semantic
shift is treated as a quadriliteral فَعْلَل, that the alif of أَبَابِيل is intrinsic
rather than an إِفْعَال augment. That is morphological theory, not distribution. No
instrument here reaches it and no position is taken on it.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os

from oqm_screen_v5 import wings
from oqm_screen_v6 import key
from qtext import defective, load_voc

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "65748aa3c47ab15a5d8719e088d518fa0ef57889980db37d22b70bfceea2b411"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

MASDAR_KIDHDHAAB = {"كذابا"}                 # فِعَّال maṣdar of Form II
ADJ_KADHDHAAB = {"كذاب", "الكذاب"}           # فَعَّال intensive adjective -- different
SIKKEER = {"سكير", "السكير", "سكيرا"}         # the form the table names
SUKKIRAT = {"سكرت"}                          # the Form II verb that actually occurs
INTOX = {"سكاري", "سكرتهم", "سكرا", "سكره"}


def find(rows, forms):
    return sorted({r["ref"] for r in rows if any(t in forms for t in r["tokens"])},
                  key=key)


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v11_prereg.json"),
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

    # -- J1 row 1: abaabeel ------------------------------------------------------
    ab = find(rows, {"ابابيل"})
    abl = sorted({r["ref"] for r in rows for t in r["tokens"]
                  if defective(t[2:] if t.startswith("ال") else t) == "ابل"}, key=key)
    row1 = ("UNTESTABLE_BY_OQM" if len(ab) < 2 and not abl else "screenable")
    gate("J1_ABAABEEL_IS_A_HAPAX_WITH_AN_UNATTESTED_ROOT",
         ab == ["105:3"] and abl == [] and row1 == "UNTESTABLE_BY_OQM",
         "أبابيل -> %s (%d ayah). Bare root أ-ب-ل -> %d ayahs. Under N159's coverage "
         "rule -- the same rule that made فسح and جلس untestable at 58:11 -- a form "
         "attested once, whose root has no other attestation, cannot be nested: there "
         "is nothing to nest it into. Row 1 -> %s. This does NOT say the correction is "
         "wrong; it says the corpus cannot adjudicate it, which is exactly the verdict "
         "N159 reaches about 58:11 and treats as the methodology behaving correctly."
         % (ab, len(ab), len(abl), row1))

    # -- J2 / J3 / J4 row 2: kidhdhaab ------------------------------------------
    masdar = find(rows, MASDAR_KIDHDHAAB)
    adj = find(rows, ADJ_KADHDHAAB)
    cited = ["78:28"]
    gate("J2_THE_TABLE_UNDER_CITES_ROW_2",
         masdar == ["78:28", "78:35"] and cited == ["78:28"],
         "the Form II maṣdar occurs at %s; the table cites %s. Under-citation, reported "
         "the same way over-citation was for ع-ب-س: a finding about the CITATION, not "
         "about the reading. The extra witness helps the row." % (masdar, cited))

    gate("J3_THE_MASDAR_IS_NOT_MERGED_WITH_THE_INTENSIVE_ADJECTIVE",
         set(masdar).isdisjoint(adj) and len(adj) == 5,
         "maṣdar كِذَّابًا %s kept separate from the فَعَّال intensive adjective كَذَّاب "
         "'a great liar' at %s -- same consonants, different template, different "
         "function. Collapsing them would inflate this row's evidence from %d to %d."
         % (masdar, adj, len(masdar), len(masdar) + len(adj)))

    old_rule = len({x.split(":")[0] for x in masdar})      # surah-identity, v3/v4
    new_rule, merges, _g = wings(idx, masdar)              # context rule, v5
    gate("J4_V5s_RULE_CHANGES_THE_VERDICT_ON_ROW_2",
         old_rule == 1 and new_rule == 2 and merges == [],
         "78:28 and 78:35 -> surah-identity gives %d wing (ONE_WING, verdict withheld); "
         "the v5 context rule gives %d wings (CLEARS), since they are 7 ayahs apart, "
         "outside the 3-ayah adjacency window, and not formulaic. Here v5's correction "
         "changes the verdict on someone ELSE's claim, in the direction of SUPPORTING "
         "it -- the surah proxy would have withheld a verdict the evidence supports."
         % (old_rule, new_rule))

    # -- J5 / J6 row 3: sikkeer --------------------------------------------------
    sk = find(rows, SIKKEER)
    verb = find(rows, SUKKIRAT)
    intox = find(rows, INTOX)
    gate("J5_SIKKEER_IS_NOT_ATTESTED_AT_ALL",
         sk == [] and verb == ["15:15"],
         "the form سِكِّير named in row 3 -> %d attestations. What IS attested is the "
         "Form II passive verb سُكِّرَتْ at %s, once. That cell of the table has no "
         "Quranic witness for the form it names. Any attestation of سكير would have "
         "failed this gate." % (len(sk), verb))

    gate("J6_THE_SKR_DISTINCTION_IS_REAL_BUT_SINGLE_WITNESSED",
         set(verb).isdisjoint(intox) and len(intox) == 5 and len(verb) == 1,
         "the intoxication family is separately attested at %s, distinct from سُكِّرَتْ "
         "at %s -- so the distinction row 3 draws IS visible in the corpus. But it "
         "rests on ONE attestation, which is ONE_WING under the Janah rule and settles "
         "nothing on its own." % (intox, verb))

    gate("J7_does_this_evaluate_the_morphological_ARGUMENT", False,
         "No. Whether a triliteral under semantic shift is treated as a quadriliteral "
         "فَعْلَل, and whether the alif of أَبَابِيل is intrinsic or an إِفْعَال augment, "
         "are claims about morphological theory. This screen counts distributions. It "
         "has no instrument for the argument and takes no position on it.", "excluded")
    gate("J8_is_a_hapax_verdict_a_criticism", False,
         "No. UNTESTABLE_BY_OQM on أَبَابِيل is not a mark against the correction. N159 "
         "reaches the same verdict about 58:11 and treats it as the methodology working "
         "as intended. A correction can be a real improvement in reasoning and still "
         "land somewhere the evidence rule cannot certify.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "row1_abaabeel": {"ayahs": ab, "bare_root_ayahs": abl, "verdict": row1},
        "row2_kidhdhaab": {"masdar": masdar, "cited_by_table": cited,
                           "intensive_adjective": adj,
                           "wings_surah_rule": old_rule, "wings_context_rule": new_rule,
                           "verdict": "CLEARS" if new_rule >= 2 else "ONE_WING"},
        "row3_sikkeer": {"named_form_ayahs": sk, "verb_ayahs": verb,
                         "intoxication_family": intox,
                         "verdict": "FORM_UNATTESTED_VERB_ONE_WING"},
        "not_checked": spec["WHAT_IS_BEING_CHECKED_AND_WHAT_IS_NOT"]["NOT_checked"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The corrected table's three rows come back DIFFERENT, which is the useful "
        "result. أَبَابِيل is a hapax at 105:3 with its bare root أ-ب-ل attested zero "
        "times, so under OQM's own coverage rule the corrected derivation is "
        "UNTESTABLE_BY_OQM -- not wrong, just not adjudicable by the corpus, exactly as "
        "N159 says of 58:11. كِذَّاب is BETTER evidenced than the table claims: the "
        "Form II maṣdar occurs at 78:28 AND 78:35, and under v5's context rule those "
        "are two independent wings, so the row CLEARS -- where the older surah-identity "
        "rule would have withheld it. And سِكِّير, the form row 3 names, is attested "
        "ZERO times; only the verb سُكِّرَتْ occurs, once, so the 'closing off' sense is "
        "real and visible against the intoxication family but rests on ONE_WING."
        % res["score"])

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v11.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "row1_abaabeel", "row2_kidhdhaab",
                       "row3_sikkeer", "primary_verdict")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
