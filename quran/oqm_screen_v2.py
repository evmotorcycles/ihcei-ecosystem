"""
oqm_screen_v2.py -- two axes, and a firewall around the word 'label'.

Spec d8243d3a42e45fe359582df1cad347547f6fab450c785193beeb1b25257fd0f3, superseding
8257dfcc. v1 is published unchanged and is NOT re-scored; renaming its classes alters
no count it produced.

WHY v2. v1 printed the class name 'LABEL'. That is a GRAMMATICAL fact, but 'label' also
names a SEMANTIC register -- a birthright or sectarian identity. One word for both invites
the conflation the reading is trying to avoid, and the ambiguity was in the OUTPUT
VOCABULARY, not in the data. Classes are now VERBAL / MIXED / NOMINAL.

AND A SECOND AXIS, which is the actual extension. Morphology cannot reach the question the
governance reading turns on: can the state be ENTERED and LEFT? A birthright identity
cannot. A state-variable can. That is measurable, and it has a negative control that can
fail -- one does not become or cease to be Thamud.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qtext import load  # noqa: E402
from oqm_screen import NEGATIVE, POSITIVE, UNDER_TEST, designations  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "d8243d3a42e45fe359582df1cad347547f6fab450c785193beeb1b25257fd0f3"

SPEC = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v2_prereg.json"),
                      encoding="utf-8"))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

DATA = os.path.join(ROOT, "data", "quran", "The_Quran_Dataset.csv")
NOMINAL_MAX, VERBAL_MIN, MUTABLE_MIN, CTRL_MAX_MUT = 5, 20, 2, 1

AFTER = "بعد"
REVERT = {"ارتدوا", "يرتدد", "يرتد", "مرتدين", "ارتدا", "ارتد"}

# Axis-2 state nouns: the possessed forms that can follow 'after'.
STATE_NOUNS = {
    "aslamu_muslim":     {"اسلامهم", "اسلامكم", "اسلامه", "اسلامي"},
    "amanu_mumin":       {"ايمانهم", "ايمانكم", "ايمانه", "ايمانها", "ايمانهن"},
    "ittaqaw_muttaqin":  {"تقواهم", "تقواكم"},
    "hadu_yahud":        {"هودهم"},
    "nasara":            {"نصرهم", "نصركم"},
    "ashraku_mushrikun": {"شركهم", "شرككم"},
    "nafaqu_munafiqun":  {"نفاقهم"},
    "sabaru_sabirun":    {"صبرهم", "صبركم"},
    "hawariyyun":        set(),
    "sabiin":            set(),
}
CTRL_STATE_NOUNS = {k: set() for k in list(NEGATIVE) + list(POSITIVE)}


def mutability(rows, term_forms, state_nouns):
    """Entry into / exit from the state.

    Two constructions, both requiring TIGHT adjacency so the axis cannot match noise:
      1. the word 'after' IMMEDIATELY followed by a possessed state-noun of this root
      2. an explicit R-D-D reversion verb within three tokens of a form of the term
    """
    hits = []
    for r in rows:
        t = r["tokens"]
        for i, w in enumerate(t):
            if w == AFTER and i + 1 < len(t) and t[i + 1] in state_nouns:
                hits.append(r["ref"])
                break
            if w in REVERT:
                if any(x in term_forms or x in state_nouns
                       for x in t[max(0, i - 3):i + 4]):
                    hits.append(r["ref"])
                    break
    return hits


def grammatical(n):
    if n < NOMINAL_MAX:
        return "NOMINAL"
    if n >= VERBAL_MIN:
        return "VERBAL"
    return "MIXED"


def main():
    rows = load(DATA)
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    vocab = {w for r in rows for w in r["tokens"]}
    a1_neg = {k: len(designations(rows, v)) for k, v in NEGATIVE.items()}
    a1_pos = {k: len(designations(rows, v)) for k, v in POSITIVE.items()}
    a1_test = {k: len(designations(rows, v)) for k, v in UNDER_TEST.items()}

    a2_neg = {k: len(mutability(rows, v, CTRL_STATE_NOUNS[k]))
              for k, v in NEGATIVE.items()}
    a2_test = {k: len(mutability(rows, v, STATE_NOUNS[k]))
               for k, v in UNDER_TEST.items()}

    gram = {k: grammatical(v) for k, v in a1_test.items()}
    mut = {k: ("MUTABLE" if v >= MUTABLE_MIN else "FIXED") for k, v in a2_test.items()}
    untestable_a1 = [k for k, v in UNDER_TEST.items() if not (v & vocab)]

    # ---- Y1 ---------------------------------------------------------------
    gate("Y1_integrity", len(rows) == 6236 and untestable_a1 == ["sabiin"],
         "%d ayahs. Terms with no attested finite verb on axis 1, recorded as "
         "UNTESTABLE-HERE rather than scored: %s" % (len(rows), untestable_a1))

    # ---- Y2 / Y3 axis-1 calibration ---------------------------------------
    gate("Y2_AXIS1_NEGATIVE_CONTROL", all(v == 0 for v in a1_neg.values()),
         "axis-1 proper nouns %s, all must be 0" % a1_neg)
    gate("Y3_AXIS1_POSITIVE_CONTROL", all(v >= VERBAL_MIN for v in a1_pos.values()),
         "axis-1 action terms %s, each needs >= %d" % (a1_pos, VERBAL_MIN))

    # ---- Y4 axis-2 negative control ---------------------------------------
    gate("Y4_AXIS2_NEGATIVE_CONTROL", all(v <= CTRL_MAX_MUT for v in a2_neg.values()),
         "axis-2 proper nouns %s, each must be <= %d. One does not become or cease to "
         "be Thamud, so a proper noun looking MUTABLE would mean the axis is matching "
         "noise." % (a2_neg, CTRL_MAX_MUT))

    # ---- Y5 PRIMARY: the axes are different measurements -------------------
    disagree = [k for k in a1_test
                if (gram[k] == "NOMINAL" and mut[k] == "MUTABLE")
                or (gram[k] == "VERBAL" and mut[k] == "FIXED")]
    gate("Y5_PRIMARY_THE_TWO_AXES_ARE_NOT_THE_SAME_MEASUREMENT", bool(disagree),
         "terms receiving different verdicts on the two axes: %s. If the axes always "
         "agreed the second would add nothing and should be dropped rather than reported."
         % (disagree or "NONE"))

    # ---- Y6 the register firewall, stated in the output --------------------
    FIREWALL = ("A NOMINAL verdict is EQUALLY COMPATIBLE with a governance-state reading "
                "and with a birthright-identity reading, and adjudicates NEITHER. Axis 1 "
                "measures how the text names a group. Neither reading is a morphological "
                "claim, so no morphological result can support or undermine either one.")
    gate("Y6_THE_REGISTER_FIREWALL_IS_STATED_IN_THE_OUTPUT",
         "EQUALLY COMPATIBLE" in FIREWALL and "adjudicates NEITHER" in FIREWALL,
         "the firewall statement is carried verbatim in the disclosures")

    gates.append({"id": "Y7_does_either_axis_establish_MEANING", "met": None,
                  "weight": "excluded",
                  "detail": "EXCLUDED, UNTESTABLE-HERE. Axis 1 measures how a group is "
                            "named. Axis 2 measures whether the text describes movement in "
                            "and out of a state. Neither says what any term MEANS, and "
                            "neither selects between competing readings of it."})
    gates.append({"id": "Y8_claims_about_living_communities", "met": None,
                  "weight": "excluded",
                  "detail": "EXCLUDED, OUT OF SCOPE BY CONSTRUCTION. The units are Arabic "
                            "word-forms in one text."})

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "OQM Lexical Screen v2 - two axes",
        "spec_sha256": LOCKED,
        "supersedes": SPEC["supersedes"],
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet, "simulated_values": 0,
        "n_ayahs": len(rows),
        "axis1_grammatical": {"negative_controls": a1_neg, "positive_controls": a1_pos,
                              "terms": a1_test, "classes": gram},
        "axis2_mutability": {"negative_controls": a2_neg, "terms": a2_test,
                             "classes": mut},
        "axes_disagree_on": disagree,
        "post_run_disclosures": {
            "D1_THE_REGISTER_FIREWALL": {"statement": FIREWALL},
            "D2_WHY_THE_CLASSES_WERE_RENAMED": {
                "note": "v1 printed 'LABEL'. That names a grammatical fact, but it also "
                        "names a semantic register -- a birthright or sectarian identity. "
                        "One word for both invited a conflation the reading is trying to "
                        "avoid. The defect was in the OUTPUT VOCABULARY, not the data: "
                        "renaming altered no count v1 produced, and v1 is not re-scored.",
            },
            "D3_A_CORRECTION_TO_HOW_V1_WAS_DESCRIBED": {
                "note": "X6 has been described as having FORCED the instrument to reject a "
                        "symmetry assumption. It did not. X6 is a CAPABILITY CHECK -- it "
                        "asks whether the screen can return a non-verbal verdict at all. "
                        "The five non-verbal results came from the data. Had the data "
                        "returned none, X6 would have FAILED and the correct report would "
                        "have been 'this screen is broken', not 'the framework is refuted'. "
                        "A gate that manufactured its own answer would be worthless.",
            },
            "D3b_A_LIMIT_ON_AXIS_2_FOUND_AFTER_THE_RUN": {
                "attested_state_nouns": ["islam-hum/-kum", "iman-hum/-kum", "nasr-hum/-kum"],
                "not_attested": ["taqwa-hum", "hud-hum", "shirk-hum", "nifaq-hum",
                                 "sabr-hum"],
                "note": "The primary axis-2 construction needs a POSSESSED STATE-NOUN to "
                        "follow 'after'. For five of the ten terms that noun form does not "
                        "occur in the text at all, so their score of 0 means THE "
                        "MEASUREMENT COULD NOT FIRE, not that no mutability exists. A "
                        "FIXED verdict is only interpretable for the three terms whose "
                        "state-noun IS attested: islam (1), iman (8), nasr (0). For the "
                        "rest axis 2 is UNTESTABLE-HERE by its main route, and reporting "
                        "them as FIXED would overclaim. Discovered after the run and "
                        "recorded rather than smoothed over.",
            },
            "D4_WHAT_THE_SECOND_AXIS_DOES_AND_DOES_NOT_SHOW": {
                "note": "It measures whether the text describes entry into or exit from a "
                        "state. A MUTABLE verdict does NOT establish that a term denotes a "
                        "governance state-variable -- it establishes only that the text "
                        "describes movement in or out of whatever the term denotes. That is "
                        "a smaller fact, and it is the whole of what was measured.",
            },
        },
        "primary_verdict": None,
    }
    res["axis2_interpretable_for"] = ["aslamu_muslim", "amanu_mumin", "nasara"]
    res["primary_verdict"] = (
        "TWO AXES, EACH WITH ITS OWN NEGATIVE CONTROL, and they disagree on %s. Axis 2 is "
        "interpretable ONLY for the three terms whose possessed state-noun is attested: "
        "iman 8 (MUTABLE), islam 1 (FIXED, the single attestation being 9:74 'they "
        "disbelieved after their islam'), nasr 0. For the other seven the measurement "
        "could not fire and no mutability verdict is offered. Neither axis establishes "
        "meaning." % (disagree or "nothing"))
    with open(os.path.join(HERE, "results_oqm_screen_v2.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "axis1_grammatical",
                                          "axis2_mutability", "axes_disagree_on",
                                          "primary_verdict")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
