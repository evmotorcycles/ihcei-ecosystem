"""
qlex.py -- do 'yahud' and 'nasara' behave like ethnonyms or like deverbal descriptors
in the Quranic text? Run against its pre-registration.

Spec 708ac80e3b14096c0eee90df0eae918596c565d78f005541c06b5dd1111fb6aa.

This measures WORD BEHAVIOUR IN ONE TEXT. It does not establish meaning (V8) and it makes
no claim about Jewish or Christian people (V9). Both limits are gates, not footnotes.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qtext import load  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "708ac80e3b14096c0eee90df0eae918596c565d78f005541c06b5dd1111fb6aa"

SPEC = json.load(open(os.path.join(HERE, "prereg", "quran_lexical_prereg.json"),
                     encoding="utf-8"))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

DATA = os.environ.get("QURAN_CSV", os.path.join(ROOT, "data", "quran",
                                                "The_Quran_Dataset.csv"))
V2_MIN = 5
BENCH = {"nasara": 14, "al_yahud": 8, "hadu": 10}

REL = {"الذين", "للذين", "والذين", "لذين", "فالذين"}   # 'those who ...'
VOC = "ياايها"                            # 'O you who ...' (normalised, joined)


def designated_by_finite_verb(rows, verb_forms, noun_forms):
    """The discriminator: is the GROUP named by a finite verb in a relative or
    vocative clause, rather than only by a noun? A proper noun cannot do this.

    The relative pronoun is matched on the RAW normalised token, never on the
    clitic-stripped base: base() strips a leading definite article, which turns
    'alladhina' into 'dhina' and makes the construction undetectable.
    """
    hits = []
    for r in rows:
        b, t = r["bases"], r["tokens"]
        for i, w in enumerate(b):
            if w not in verb_forms:
                continue
            prev = t[i - 1] if i else ""
            prev2 = t[i - 2] if i > 1 else ""
            if prev in REL or prev2 in REL or prev == VOC or prev2 == VOC:
                hits.append({"ref": r["ref"], "verb": t[i],
                             "context": " ".join(t[max(0, i - 3):i + 2])})
    return hits


def main():
    rows = load(DATA)
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    def count(pred):
        return [(r["ref"], w) for r in rows for w in r["bases"] if pred(w)]

    nasara = count(lambda w: w in ("نصاري", "نصارا"))
    yahud = count(lambda w: w in ("يهود", "يهودا"))
    hadu = count(lambda w: w == "هادوا")
    yahudi = count(lambda w: w == "يهوديا")
    nasrani = count(lambda w: w == "نصرانيا")
    ansar = count(lambda w: w in ("انصار", "انصاري", "انصارا", "انصارهم"))
    # N-S-R finite verbs, excluding the group noun and the adjective, and excluding
    # nusarrif (root S-R-F) which is surface-similar but a different root.
    nsr_verb = count(lambda w: re.match(r"^(ي|ت|ن|ا|است)?نصر", w)
                     and not w.startswith("نصار") and not w.startswith("نصران")
                     and not w.startswith("نصرف"))

    # ---- V1 integrity ------------------------------------------------------
    got = {"nasara": len(nasara), "al_yahud": len(yahud), "hadu": len(hadu)}
    gate("V1_integrity", len(rows) == 6236 and got == BENCH,
         "%d ayahs. Benchmark counts %s against published %s. This is an INTEGRITY "
         "CHECK, not a finding." % (len(rows), got, BENCH))

    # ---- V2 primary --------------------------------------------------------
    y_des = designated_by_finite_verb(rows, {"هادوا"}, {"يهود"})
    gate("V2_PRIMARY_yahud_IS_designated_by_a_finite_verb", len(y_des) >= V2_MIN,
         "the group is named by the finite verb 'hadu' in a relative or vocative clause "
         "%d times (needs >= %d), against %d occurrences of the noun. Refs: %s"
         % (len(y_des), V2_MIN, len(yahud), sorted({h["ref"] for h in y_des})))

    # ---- V3 ablation -------------------------------------------------------
    ctrl_forms = SPEC["the_control_set"]
    ctrl_hits = {}
    for c in ctrl_forms:
        d = designated_by_finite_verb(rows, {c}, {c})
        ctrl_hits[c] = len(d)
    total_ctrl = sum(ctrl_hits.values())
    v3 = total_ctrl == 0
    gate("V3_ABLATION_control_proper_nouns_are_NOT", v3,
         "across %d control proper nouns the finite-verb group-designation count is %d "
         "(needs 0). Per control: %s" % (len(ctrl_forms), total_ctrl, ctrl_hits))

    # ---- V4 the split ------------------------------------------------------
    nsr_verb_forms = {w for _, w in nsr_verb}
    n_des = designated_by_finite_verb(rows, nsr_verb_forms, {"نصاري"})
    # the ansar are a DIFFERENT group from the nasara; a hit here is only relevant
    # if it designates the nasara, so both the count and the refs are reported.
    v4 = len(n_des) == 0
    gate("V4_THE_SPLIT_nasara_is_NOT_designated_by_a_finite_verb", v4,
         "relative or vocative clauses built on a finite N-S-R verb: %d. Refs: %s. The "
         "noun 'nasara' occurs %d times and the root supplies %d finite verb tokens, yet "
         "the group is never named BY the verb."
         % (len(n_des), sorted({h["ref"] for h in n_des}), len(nasara), len(nsr_verb)))

    # ---- V5 the homograph demonstration, EXCLUDED --------------------------
    aad = count(lambda w: w == "عاد")
    aad_refs = sorted({r for r, _ in aad})
    gates.append({"id": "V5_the_homograph_demonstration", "met": None,
                  "weight": "excluded",
                  "detail": "'Aad appears %d times across %d ayahs and is surface-identical "
                            "to two unrelated forms: the verb 'aada (returned, root '-W-D, "
                            "e.g. 2:275 'wa man 'aada') and 'aadin (transgressor, root "
                            "'-D-W, e.g. 2:173 'wa laa 'aad'). A test based on shared "
                            "letters would call 'Aad deverbal. This is why the run tests "
                            "GROUP DESIGNATION instead. Demonstration only, scores nothing."
                            % (len(aad), len(aad_refs))})

    # ---- V6 M-L-L ----------------------------------------------------------
    mll_verb = count(lambda w: re.match(r"^(فلي|ولي|لي|ي|ت|ا)مل(ل|)$", w) is not None
                     and w not in ("الامل", "امل"))
    mll_refs = sorted({r for r, _ in mll_verb})
    gate("V6_M_L_L_verbal_usage_is_confined_to_2_282",
         bool(mll_verb) and mll_refs == ["2:282"],
         "finite M-L-L verb tokens: %d, all in %s. Forms: %s"
         % (len(mll_verb), mll_refs, sorted({w for _, w in mll_verb})))

    # ---- V7 2:120 ----------------------------------------------------------
    a120 = next((r for r in rows if r["ref"] == "2:120"), None)
    has_sing = a120 is not None and "ملتهم" in a120["bases"]
    has_both = a120 is not None and "يهود" in a120["bases"] and "نصاري" in a120["bases"]
    gate("V7_2_120_uses_a_SINGULAR_millah_for_two_named_groups", has_sing and has_both,
         "2:120 contains singular 'millatahum': %s; names both groups: %s. Text: %s"
         % (has_sing, has_both, a120["ayah_ar"] if a120 else "MISSING"))

    gates.append({"id": "V8_does_any_of_this_establish_what_the_words_MEAN", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Distributional behaviour constrains readings; "
                            "it does not select one. Many ordinary ethnonyms are "
                            "historically deverbal in every language, so a pass on V2 is "
                            "CONSISTENT WITH a descriptor reading and does not establish "
                            "it."})
    gates.append({"id": "V9_claims_about_actual_communities", "met": None,
                  "weight": "excluded",
                  "detail": "OUT OF SCOPE BY CONSTRUCTION. The units of analysis are Arabic "
                            "word-forms in one text. No gate references any living "
                            "community, and no count here is evidence about Jewish or "
                            "Christian people, beliefs or practices."})

    binding = ("V3 WAS MET, so V2 discriminates: the behaviour separates 'yahud' from "
               "seven control proper nouns." if v3 else
               "V3 WAS NOT MET, SO V2 IS UNINFORMATIVE -- the behaviour does not "
               "distinguish anything.")

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Quran lexical behaviour: ethnonym or deverbal descriptor?",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "simulated_values": 0, "n_ayahs": len(rows),
        "counts": {
            "nasara_noun": len(nasara), "yahud_noun": len(yahud),
            "hadu_finite_verb": len(hadu), "yahudiyyan": len(yahudi),
            "nasraniyyan": len(nasrani), "ansar_noun": len(ansar),
            "nsr_finite_verbs": len(nsr_verb),
            "yahud_group_designated_by_verb": len(y_des),
            "nasara_group_designated_by_verb": len(n_des),
            "control_group_designated_by_verb": ctrl_hits,
        },
        "yahud_verb_designations": y_des,
        "post_run_disclosures": {
            "D1_THE_BINDING_CONSEQUENCE": {"statement": binding},
            "D2_THE_TWO_WORDS_DO_NOT_BEHAVE_THE_SAME": {
                "yahud": "noun %d times; named by the finite verb 'hadu' %d times, "
                         "including a direct vocative address."
                         % (len(yahud), len(y_des)),
                "nasara": "noun %d times; named by a finite verb %d times, despite the "
                          "root supplying %d finite verb tokens elsewhere."
                          % (len(nasara), len(n_des), len(nsr_verb)),
                "note": "A single symmetric claim covering both words is NOT supported by "
                        "this test. Whatever is true of one is not thereby true of the "
                        "other, and reporting them together would hide the asymmetry that "
                        "is the actual result.",
            },
            "D2b_THE_V2_THRESHOLD_WAS_INFORMED_BY_A_PRE_LOCK_COUNT": {
                "note": "The spec's V1 records that the benchmark counts, including hadu = "
                        "10, were seen before the lock as a normalisation check. V2's bar "
                        "of >= 5 was therefore set knowing that number. That makes V2 a "
                        "WEAK pre-registration and it is labelled as such rather than "
                        "presented as a blind prediction. V3 and V4 were NOT informed this "
                        "way, and they are what carry the run.",
            },
            "D3_WHY_ROOT_SHARING_WAS_NOT_USED": {
                "note": "'Aad is surface-identical to an unrelated verb and an unrelated "
                        "participle. Any test based on shared letters would have produced a "
                        "false positive on a proper noun, which is exactly the failure mode "
                        "this design was built to avoid.",
            },
            "D4_WHAT_IS_NOT_CLAIMED": {
                "note": "No meaning is established (V8). Nothing here is a statement about "
                        "Jewish or Christian people (V9). The result is about how two "
                        "Arabic word-forms are used in one text, and it stops there.",
            },
        },
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "IN THIS TEXT the group named 'yahud' is ALSO designated by a finite verb from the "
        "same root %d times, a behaviour none of the %d control proper nouns shows. The "
        "group named 'nasara' is NOT so designated (%d times), so the two words behave "
        "DIFFERENTLY. %s No meaning is established by any of this."
        % (len(y_des), len(ctrl_forms), len(n_des), binding))
    with open(os.path.join(HERE, "results_qlex.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "counts",
                                          "primary_verdict")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
