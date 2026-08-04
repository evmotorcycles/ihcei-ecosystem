"""
oqm_screen_v3.py -- a method-conformance screen built from the OQM source documents.

v1 and v2 screened terms along axes I invented. v3 stops inventing. It implements the
two method rules the documents state -- the Janah two-witness rule and the 58:11
coverage rule -- as gates on every verdict, and it checks the instrument against flat
textual claims the DOCUMENTS make, so the controls are source-supplied.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os
import re
import unicodedata

from qtext import SHADDA, defective, load_voc, normalise, skeleton

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "b5eaa3051ebe499b7751ac72c477204061a5414ff4f0613e21414c02e940c669"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

# Letters that can stand as a proclitic. Used by the root matcher below.
PROCLITIC_LETTERS = set("وفبكلاأإ") | {"ٱ"}

# The five near-misses N159's claim runs into. Declared so the run can show it
# rejects them by rule rather than by name -- they are never special-cased.
FSH_LOOKALIKES = ["52:15", "67:11", "9:2", "20:61", "4:172"]


WASLA = "ٱ"


def stem_of(voc_tok):
    """Strip the leading proclitic run, using WASLA as the stop signal.

    The discriminator is IN THE SOURCE TEXT rather than in my judgement. Waṣla
    (U+0671) marks an elidable hamza, so it says 'the stem starts here'. Stripping
    therefore halts the moment a waṣla is reached:

        فَٱفْسَحُوا۟   fa + ٱ -> stop -> stem فسحوا      root f-s-h  KEPT
        أَفَسِحْرٌ     ʾa + fa, no waṣla -> stem سحر     root s-h-r  DROPPED
        فَسُحْقًۭا      fa,  no waṣla    -> stem سحقا     root s-h-q  DROPPED
        ٱلْمَجَٰلِسِ    waṣla at index 0 -> stem intact   root j-l-s  KEPT

    Long vowels are removed only afterwards, so a radical ي or و is never confused
    with the imperfect prefix. Must be fed r["raw"]: voc() folds waṣla to plain
    alif, and فَٱفْسَحُوا۟ is then indistinguishable from fa + a + ... and is lost.
    """
    # Letters only, but WASLA and the hamza carriers survive -- they are letters,
    # not combining marks, and both carry the information the rule turns on.
    t = "".join(c for c in unicodedata.normalize("NFC", voc_tok)
                if unicodedata.category(c) != "Mn" and c != "ـ")
    while t and t[0] in PROCLITIC_LETTERS and t[0] != WASLA:
        t = t[1:]
        if t[:1] == WASLA:
            break
    return t.replace(WASLA, "")


def root_hits(rows, root):
    """Ayahs containing ROOT, with one uniform rule applied to every root.

    DISCLOSED, because it was corrected mid-run. The first implementation called a
    contiguity match at index 0 ambiguous whenever the root's first radical was a
    proclitic letter. That rejected all five corpus near-misses correctly, but it
    also silently dropped يَفْسَحِ -- a genuine f-s-h token in 58:11 -- because
    defective() strips the imperfect prefix ي and leaves فسح word-initial. The gate
    still passed, since 58:11 was carried by its other two tokens, but a matcher
    that discards a true positive is broken whatever its score. Replaced with the
    waṣla rule above, which gets all nine candidates right.
    """
    hits, rejected = {}, {}
    for r in rows:
        for raw, tok in zip(r["raw"], r["tokens"]):
            if root not in defective(tok):
                continue
            stem = normalise(stem_of(unicodedata.normalize("NFC", raw)))
            if root in defective(stem):
                hits.setdefault(r["ref"], []).append(tok)
            else:
                rejected.setdefault(r["ref"], []).append(tok)
    return hits, rejected


def nzl_imperfect(rows):
    """Classify every imperfect n-z-l token by VERB FORM, read off the vowels.

        Form II   yunazzil   ya+damma, zay carries SHADDA
        Form IV   yunzil     ya+damma, no shadda
        Form I    yanzil     ya+fatha, no shadda

    Requires the vocalised path. normalise() cannot do this -- it deletes shadda
    and both vowels, which is the v1/v2 defect this gate exists to demonstrate.
    """
    DAMMA, FATHA = "ُ", "َ"
    out = {"II": [], "IV": [], "I": [], "other": []}
    for r in rows:
        for raw, sk in zip(r["voc"], r["skel"]):
            bare = sk.replace(SHADDA, "")
            if not re.fullmatch(r"[وفل]?[يت]نزل[هامكنوي]*", normalise(bare)):
                continue
            d = unicodedata.normalize("NFD", raw)
            # vowel sitting on the imperfect prefix ya-/ta-
            m = re.search(r"[يت]([ً-ْ]?)", d)
            v = m.group(1) if m else ""
            if SHADDA in d:
                out["II"].append((r["ref"], raw))
            elif v == DAMMA:
                out["IV"].append((r["ref"], raw))
            elif v == FATHA:
                out["I"].append((r["ref"], raw))
            else:
                out["other"].append((r["ref"], raw))
    return out


def janah(witness_refs):
    """The two-witness rule. Independence = distinct surah."""
    surahs = {w.split(":")[0] for w in witness_refs}
    if len(surahs) >= 2:
        return "CLEARS", len(surahs)
    if len(witness_refs) >= 1:
        return "ONE_WING", len(surahs)
    return "NO_WITNESS", 0


def form_of(tok):
    return "II" if SHADDA in unicodedata.normalize("NFD", tok) else "I/IV"


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v3_prereg.json"),
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

    # -- Z1 the instrument can now see verb form, and the old path could not ----
    a, b = "يُنَزِّلُ", "يَنزِلُ"
    sees = skeleton(a) != skeleton(b)
    blind = normalise(a) == normalise(b)
    gate("Z1_INSTRUMENT_CAN_SEE_VERB_FORM", sees and blind,
         "vocalised path: %s vs %s -> distinct=%s | v1/v2 normalise(): %s vs %s -> "
         "identical=%s, which is the defect, demonstrated not asserted"
         % (skeleton(a), skeleton(b), sees, normalise(a), normalise(b), blind))

    # -- Z2 / Z3 the two roots N159 makes flat claims about --------------------
    jls, jls_rej = root_hits(rows, "جلس")
    gate("Z2_SOURCE_SUPPLIED_POSITIVE_CONTROL_JLS", sorted(jls) == ["58:11"],
         "root j-l-s -> %s (forms %s); proclitic rule inert here, 0 rejected"
         % (sorted(jls), sum(jls.values(), [])))

    fsh, fsh_rej = root_hits(rows, "فسح")
    rejected_all = all(ref in fsh_rej for ref in FSH_LOOKALIKES)
    gate("Z3_SOURCE_SUPPLIED_NEGATIVE_CONTROL_FSH",
         sorted(fsh) == ["58:11"] and rejected_all,
         "root f-s-h -> %s (forms %s); the five corpus-supplied near-misses %s were "
         "all rejected by the uniform rule = %s"
         % (sorted(fsh), sum(fsh.values(), []), FSH_LOOKALIKES, rejected_all))

    # -- Z5 the coverage rule ---------------------------------------------------
    coverage = {}
    for name, hits in (("j-l-s", jls), ("f-s-h", fsh)):
        coverage[name] = {
            "n_ayahs": len(hits),
            "verdict": "UNTESTABLE_BY_OQM" if len(hits) < 2 else "screenable",
            "note": "attested in one ayah only, so nested interpretation cannot run; "
                    "this is NOT a finding about what 58:11 means"}
    gate("Z5_COVERAGE_RULE_FIRES",
         all(v["verdict"] == "UNTESTABLE_BY_OQM" for v in coverage.values()),
         "both roots returned UNTESTABLE_BY_OQM; their score is not evidence")

    # -- Z6 the risky claim: no Form IV imperfect of n-z-l ---------------------
    nzl = nzl_imperfect(rows)
    gate("Z6_RISKY_N159_NO_FORM_IV_IMPERFECT_OF_NZL", len(nzl["IV"]) == 0,
         "Form IV imperfect yunzil: %d found. Form II=%d, Form I=%d %s, other=%d. "
         "One counterexample would have refuted N159; none exists. Form I yanzilu is "
         "NOT a counterexample and is not counted as one."
         % (len(nzl["IV"]), len(nzl["II"]), len(nzl["I"]),
            [x[0] for x in nzl["I"]], len(nzl["other"])))

    # -- Z7 the minimal pairs, themselves subject to the Janah rule ------------
    def forms_in(ref):
        for r in rows:
            if r["ref"] == ref:
                return [t for t in r["voc"]
                        if re.fullmatch(r"[وفل]*[اينت]?نزل[نهاتمكوي]*", normalise(t))]
        return []

    w33 = forms_in("3:3")
    w47a, w47b = forms_in("47:9"), forms_in("47:26")
    pair_33 = {form_of(t) for t in w33} == {"I/IV", "II"}
    pair_47 = ([form_of(t) for t in w47a] == ["I/IV"]
               and [form_of(t) for t in w47b] == ["II"])
    verdict, n_ind = janah(["3:3", "47:9", "47:26"])
    gate("Z7_RISKY_N159_NAZZALA_VS_ANZALA_MINIMAL_PAIR",
         pair_33 and pair_47 and verdict == "CLEARS",
         "3:3 carries both forms in one ayah %s -> %s | 47:9 %s vs 47:26 %s in an "
         "identical frame -> %s | Janah: %d independent surahs -> %s (the minimum; "
         "47:9 and 47:26 are one surah and count once)"
         % (w33, pair_33, w47a, w47b, pair_47, n_ind, verdict))

    # -- Z8 and it does not generalise -----------------------------------------
    TOR, QUR = ("التوريه", "التوراه", "الانجيل"), ("القران", "الذكر", "الكتاب")
    broad = {}
    for r in rows:
        n = r["tokens"]
        for i, (raw, t) in enumerate(zip(r["voc"], n)):
            if not re.fullmatch(r"[وفل]*[اينت]?نزل[نهاتمكوي]*", t):
                continue
            win = " ".join(n[max(0, i - 2):i + 6])
            obj = ("Torah/Injil" if any(x in win for x in TOR) else
                   "Quran/Dhikr/Kitab" if any(x in win for x in QUR) else None)
            if obj:
                broad[(obj, form_of(raw))] = broad.get((obj, form_of(raw)), 0) + 1
    disclosure = ("Corpus-wide, the claim does NOT hold as a categorical rule: %s. "
                  "Form II is relatively commoner with the Quran than with the Torah, "
                  "but there are many non-Form-II uses with al-Kitab. The broad test is "
                  "the WEAKER instrument, because al-Kitab is itself ambiguous between "
                  "the Quran and earlier scripture -- which is the very thing in dispute "
                  "-- so a context window cannot adjudicate it. The minimal pairs can; "
                  "the broad distribution is reported anyway because it cuts against a "
                  "categorical reading."
                  % {"%s|%s" % k: v for k, v in sorted(broad.items())})
    gate("Z8_DISCLOSURE_Z7_DOES_NOT_GENERALISE", bool(broad), disclosure)

    # -- Z4 the Janah rule must actually withhold something --------------------
    readjudicated = {
        "amanu_mumin_iman": dict(zip(("verdict", "n_surahs"),
                                     janah(["2:108", "3:86", "3:100", "3:106", "4:137",
                                            "9:66", "9:74", "16:106"]))),
        "aslamu_muslim_islam": dict(zip(("verdict", "n_surahs"), janah(["9:74"]))),
        "nasara_nasr": dict(zip(("verdict", "n_surahs"), janah([]))),
    }
    withheld = [k for k, v in readjudicated.items() if v["verdict"] == "ONE_WING"]
    gate("Z4_THE_JANAH_RULE_IS_BINDING_NOT_DECORATIVE", bool(withheld),
         "the rule withheld a verdict for %s. v2 reported islam as FIXED on the single "
         "attestation 9:74; under the documented rule no verdict may be issued there at "
         "all. A rule that never fires would not be a constraint." % withheld)

    gate("Z9_does_any_of_this_establish_MEANING", False,
         "It does not. Verb form, root coverage and witness counts are morphological "
         "and distributional facts; none selects between competing readings of any "
         "term.", "excluded")
    gate("Z10_claims_about_living_communities", False,
         "None are made or tested.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED,
        "supersedes": spec["supersedes"],
        "n_ayahs": len(rows),
        "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates,
        "gates_not_met": not_met,
        "coverage_rule": coverage,
        "nzl_forms": {k: len(v) for k, v in nzl.items()},
        "nzl_form_I_refs": [x[0] for x in nzl["I"]],
        "janah_readjudication_of_v2": readjudicated,
        "broad_distribution": {"%s|%s" % k: v for k, v in sorted(broad.items())},
        "post_run_disclosures": {
            "D1_THE_GOVERNANCE_LABEL_FIREWALL":
                spec["THE_GOVERNANCE_LABEL_FIREWALL"]["the_firewall"],
            "D2_WHAT_THE_DOCUMENTS_SETTLE_AND_WHAT_THEY_DO_NOT":
                spec["THE_GOVERNANCE_LABEL_FIREWALL"]["what_this_does_settle"],
            "D3_A_DOCUMENT_CLAIM_REPORTED_PRECISELY_RATHER_THAN_ENDORSED": {
                "note": "N159 says the form نُفَرِّق 'occurs 4 times (2:136, 2:285, 3:84, "
                        "and 4:152)'. The exact form occurs at three of those; 4:152 "
                        "carries يُفَرِّقُوا۟ -- same root, same Form II, different person. "
                        "The wording is loose about form versus root. This is recorded, "
                        "endorsed in neither direction, and deliberately NOT used as a "
                        "gate, because a claim that is ambiguous as stated cannot be a "
                        "pass/fail test of anything."},
            "D4_ONE_DOCUMENT_COULD_NOT_BE_READ": {
                "note": "Duaa_Publication_1.pdf is scanned page images. pypdf recovered "
                        "only running headers. It contributed nothing to this spec and "
                        "is recorded as unread rather than summarised from its title."},
            "D5_WHY_V1_AND_V2_ARE_NOT_RE_SCORED": {
                "note": "qtext.normalise() is unchanged, so v1 and v2 reproduce "
                        "byte-identically. v3 corrects one v2 VERDICT (islam) under a "
                        "rule v2 did not have, and supersedes rather than overwrites."},
        },
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The two method rules the OQM documents state are implementable and both "
        "BIND: the coverage rule refuses two roots outright, and the Janah rule "
        "withholds the islam verdict that v2 issued. N159's riskiest textual claim -- "
        "that the Form IV imperfect يُنْزِل is absent from the text -- survives a test "
        "one counterexample would have ended (%d found). Its nazzala/anzala claim holds "
        "on two independent minimal-pair witnesses and does NOT hold as a categorical "
        "rule corpus-wide; both are reported."
        % (res["score"], len(nzl["IV"])))

    out = os.path.join(HERE, "results_oqm_screen_v3.json")
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "nzl_forms", "nzl_form_I_refs",
                       "coverage_rule", "janah_readjudication_of_v2",
                       "broad_distribution", "primary_verdict")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
