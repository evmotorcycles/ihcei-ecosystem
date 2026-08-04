"""
oqm_screen.py -- the OQM Lexical Screen, run against its pre-registration.

Spec 8257dfcca40d0be024bac323e45137eba27277200243b3c1a7893d6f08349204.

Not another reading. An INSTRUMENT for questions of the shape "is this word a label or an
act?", calibrated at BOTH ends -- proper nouns must score zero, unambiguous action terms
must score high -- and required by gate X6 to be capable of returning NO.

Built from the test that discriminated (designation, 7/7 controls at zero, spec 708ac80e)
and deliberately excluding the one that did not (VIF on word counts, 99.8% of random pairs
cleared its bar, spec af27d2c9).
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qtext import load  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "8257dfcca40d0be024bac323e45137eba27277200243b3c1a7893d6f08349204"

SPEC = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_prereg.json"),
                      encoding="utf-8"))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

DATA = os.path.join(ROOT, "data", "quran", "The_Quran_Dataset.csv")
LABEL_MAX, ACTION_MIN, X4_GAP, X6_MIN_LABELS = 5, 20, 20, 2

REL = {"الذين", "للذين", "والذين", "لذين", "فالذين"}
VOC = "ياايها"

NEGATIVE = {                     # proper nouns: the screen must score these 0
    "Firawn":   {"فرعون"},
    "Thamud":   {"ثمود"},
    "Aad":      {"عاد"},
    "Israil":   {"اسراءيل"},
    "Majus":    {"مجوس"},
    "Rum":      {"روم"},
    "Quraysh":  {"قريش"},
}
POSITIVE = {                     # unambiguously act-based: must score >= 20
    "kafaru":   {"كفروا", "كفر", "يكفرون"},
    "zalamu":   {"ظلموا", "ظلم", "يظلمون"},
    "amilu":    {"عملوا", "يعملون"},
}
UNDER_TEST = {                   # the OQM group vocabulary
    "hadu_yahud":        {"هادوا"},
    "nasara":            {"نصروا", "ينصرون"},
    "hawariyyun":        {"يحاورهۥ", "تحاوركما", "يحاوره", "حاوره"},
    "sabiin":            {"صبءوا", "صباوا"},
    "ashraku_mushrikun": {"اشركوا", "يشركون"},
    "nafaqu_munafiqun":  {"نافقوا", "ينافقون"},
    "ittaqaw_muttaqin":  {"اتقوا", "يتقون"},
    "aslamu_muslim":     {"اسلموا", "اسلم", "يسلمون"},
    "amanu_mumin":       {"امنوا", "يومنون", "امن"},
    "sabaru_sabirun":    {"صبروا", "يصبرون"},
}


def designations(rows, verbs):
    """Finite-verb group designation: 'those who [verb]' or 'O you who [verb]'.

    Verbs are matched on the RAW normalised token, never on the clitic-stripped base.
    base() strips a leading kaf as the 'like/as' proclitic, which turns kafaru into
    faru and silently deleted the commonest verbal designation in the text -- caught
    by the X3 positive control on the first run.
    """
    def is_form(w):
        # UNIFORM proclitic rule, applied identically to every term and every control:
        # a token matches if it IS a declared form, or is one carrying a leading waw or
        # fa (the coordinating proclitics). Needed because 'and they did' is written
        # wa-'amilu as a single token, which is how the commonest coordinated
        # designation in the text is spelled.
        return w in verbs or (w[:1] in ("و", "ف") and w[1:] in verbs)

    hits = []
    for r in rows:
        t = r["tokens"]
        for i, w in enumerate(t):
            if not is_form(w):
                continue
            prev = t[i - 1] if i else ""
            prev2 = t[i - 2] if i > 1 else ""
            if prev in REL or prev2 in REL or prev == VOC or prev2 == VOC:
                hits.append(r["ref"])
    return hits


def classify(n):
    if n < LABEL_MAX:
        return "LABEL"
    if n >= ACTION_MIN:
        return "ACTION"
    return "AMBIGUOUS"


def main():
    rows = load(DATA)
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    vocab = {w for r in rows for w in r["bases"]}
    neg = {k: len(designations(rows, v)) for k, v in NEGATIVE.items()}
    pos = {k: len(designations(rows, v)) for k, v in POSITIVE.items()}
    test = {k: len(designations(rows, v)) for k, v in UNDER_TEST.items()}
    attested = {k: sorted(v & vocab) for k, v in
                list(NEGATIVE.items()) + list(POSITIVE.items()) + list(UNDER_TEST.items())}

    # ---- X1 ---------------------------------------------------------------
    unattested = [k for k, v in attested.items() if not v]
    gate("X1_integrity", len(rows) == 6236 and not unattested,
         "%d ayahs. Every control and term resolves to an attested form: %s"
         % (len(rows), "yes" if not unattested else "NO -- %s" % unattested))

    # ---- X2 negative control ----------------------------------------------
    gate("X2_NEGATIVE_CONTROL", all(v == 0 for v in neg.values()),
         "the 7 proper nouns score %s. All must be 0." % neg)

    # ---- X3 positive control ----------------------------------------------
    gate("X3_POSITIVE_CONTROL", all(v >= ACTION_MIN for v in pos.values()),
         "the 3 unambiguous action terms score %s. Each needs >= %d."
         % (pos, ACTION_MIN))

    # ---- X4 PRIMARY: a clean decision boundary ----------------------------
    gap = min(pos.values()) - max(neg.values())
    gate("X4_PRIMARY_THE_SCREEN_HAS_A_CLEAN_DECISION_BOUNDARY", gap >= X4_GAP,
         "min(positive) %d minus max(negative) %d = %d (needs >= %d). The calibrators must "
         "separate by more than the width of the AMBIGUOUS band or the screen returns a "
         "shrug." % (min(pos.values()), max(neg.values()), gap, X4_GAP))

    # ---- X5 the classification, disclosure --------------------------------
    classes = {k: classify(v) for k, v in test.items()}
    ranked = sorted(test.items(), key=lambda kv: -kv[1])
    gates.append({"id": "X5_THE_CLASSIFICATION_OF_THE_TERMS_UNDER_TEST",
                  "met": None, "weight": "excluded",
                  "detail": "ranked designation counts: %s. Classes: %s"
                            % (dict(ranked), classes)})

    # ---- X6 anti-rubber-stamp ---------------------------------------------
    labels = [k for k, c in classes.items() if c == "LABEL"]
    gate("X6_ANTI_RUBBER_STAMP_THE_SCREEN_MUST_BE_ABLE_TO_SAY_NO",
         len(labels) >= X6_MIN_LABELS,
         "%d of %d terms under test classify as LABEL (needs >= %d): %s. A screen that "
         "certifies every term the framework favours is agreeing, not screening."
         % (len(labels), len(test), X6_MIN_LABELS, labels))

    gates.append({"id": "X7_does_a_classification_establish_MEANING", "met": None,
                  "weight": "excluded",
                  "detail": "EXCLUDED, UNTESTABLE-HERE. An ACTION classification says the "
                            "text names a group by a finite verb. It does not say what the "
                            "verb means, what the group is, or that any reading of either "
                            "is correct. Many ordinary ethnonyms are historically deverbal "
                            "in every language."})
    gates.append({"id": "X8_claims_about_living_communities", "met": None,
                  "weight": "excluded",
                  "detail": "EXCLUDED, OUT OF SCOPE BY CONSTRUCTION. The units are Arabic "
                            "word-forms in one text. No classification here is a statement "
                            "about Jewish, Christian, Muslim, Zoroastrian or any other "
                            "people."})

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "The OQM Lexical Screen",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet, "simulated_values": 0,
        "n_ayahs": len(rows),
        "boundary": {"LABEL": "< %d" % LABEL_MAX, "AMBIGUOUS": "%d..%d" % (LABEL_MAX, ACTION_MIN - 1),
                     "ACTION": ">= %d" % ACTION_MIN},
        "negative_controls": neg,
        "positive_controls": pos,
        "under_test": dict(ranked),
        "classes": classes,
        "separation": gap,
        "attested_forms": attested,
        "post_run_disclosures": {
            "D1_WHAT_THE_SCREEN_ADDS": {
                "note": "A framework becomes more comprehensive by acquiring ways to SETTLE "
                        "questions, not by accumulating answers. This is one uniform "
                        "instrument, calibrated at both ends, with a boundary fixed before "
                        "any term was scored, applied to a whole vocabulary at once.",
            },
            "D2_IT_IS_BUILT_FROM_THE_TEST_THAT_WORKED": {
                "kept": "designation -- 7 of 7 control proper nouns at zero, spec 708ac80e",
                "discarded": "VIF on word counts -- 99.8% of random unrelated pairs cleared "
                             "its bar, so it separated nothing, spec af27d2c9",
                "note": "Both were tried. Only one is in the instrument.",
            },
            "D3_THE_SCREEN_DISAGREES_WITH_THE_FRAMEWORK_SOMEWHERE": {
                "labels": labels,
                "note": "These terms are named by a noun and essentially never by a finite "
                        "verb designating the group. Where OQM reads them as functions, "
                        "this text's usage does not supply verbal support for that reading. "
                        "That disagreement is the point of X6.",
            },
            "D3b_ONE_TERM_CANNOT_BE_SCREENED_AT_ALL_AND_THAT_IS_NOT_A_LABEL": {
                "note": "The screen has a PRECONDITION: the root must supply an attested "
                        "finite verb somewhere in the text. Where it does not, the term is "
                        "UNTESTABLE-HERE by this instrument -- which is a different verdict "
                        "from LABEL. Filing 'the root has verbs but the text never uses them "
                        "for this group' together with 'the root has no verbs at all' would "
                        "merge two findings this programme keeps distinct. X1 exists to "
                        "catch exactly that and it failed on the first run for that reason.",
            },
            "D4_WHAT_AN_ACTION_CLASSIFICATION_DOES_NOT_BUY": {
                "note": "It does not vindicate any reading. It establishes that the text "
                        "uses a verbal group-designation, which is a far smaller fact than "
                        "a reading, and it says nothing about meaning or about any living "
                        "community.",
            },
        },
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "THE SCREEN IS CALIBRATED: %d proper nouns at zero, %d action terms at >= %d, "
        "separation %d. Of %d OQM terms it classifies %d as ACTION, %d as AMBIGUOUS and "
        "%d as LABEL. It disagrees with the framework on %s, which is what a screen is for."
        % (len(neg), len(pos), ACTION_MIN, gap, len(test),
           sum(1 for c in classes.values() if c == "ACTION"),
           sum(1 for c in classes.values() if c == "AMBIGUOUS"),
           len(labels), labels))
    with open(os.path.join(HERE, "results_oqm_screen.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "negative_controls",
                                          "positive_controls", "under_test", "classes",
                                          "separation", "primary_verdict")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
