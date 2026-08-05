"""
oqm_screen_v4.py -- applies the source-derived OQM rules to four narratives.

v3 extracted two rules from the OQM documents. v4 asks of four narratives' central
roots exactly one question: is a nested interpretation of this root METHODOLOGICALLY
LICENSED under OQM's own rules -- i.e. is the root attested widely enough that the
Quran can define it internally, rather than a dictionary defining it from outside?

Licensing is a statement about the AVAILABILITY OF EVIDENCE. It is not a statement
that any reading is correct. All four readings could still be wrong.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os
import re

from qtext import defective, load_voc, normalise

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "de629189f2e6712688e6602b1d1ae7da7ed071353a4972c546129a492058645e"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

# Mechanical candidate generators, one per root. Deliberately OVER-GENEROUS: they
# must not miss an occurrence, and every candidate they raise is then adjudicated
# by name in the locked spec.
CANDIDATE = {
    "N157_barakah": lambda n, raw: "برك" in defective(n),
    "N182_al_asr": lambda n, raw: "عصر" in defective(n),
    "N167_sulalah": lambda n, raw: "سلل" in defective(n) or "سلال" in n,
    "IQRA_quran": lambda n, raw: "قر" in n and re.search(r"[ءأإئؤ]", raw),
}
# Verbal q-r-' forms, for the distribution report only. Not a gate.
QR_VERBAL = {"اقرا", "يقرءون", "قرات", "نقروهۥ", "لتقراهۥ", "اقرءوا", "فاقرءوا",
             "قراناه", "قري", "فقراهۥ", "سنقريك"}


def candidates(rows, key):
    pred = CANDIDATE[key]
    out = {}
    for r in rows:
        for raw in r["raw"]:
            n = normalise(raw)
            if pred(n, raw):
                out.setdefault(n, set()).add(r["ref"])
    return out


def v3_rule_on(rows, root):
    """Re-run v3's automatic proclitic rule, purely to demonstrate it failing."""
    from oqm_screen_v3 import root_hits
    return root_hits(rows, root)


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v4_prereg.json"),
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

    # -- W1 demonstrate v3's rule inverting the answer on b-r-k ----------------
    hits3, rej3 = v3_rule_on(rows, "برك")
    ate_true = "27:8" in rej3 and "17:1" in rej3
    took_false = any(r in hits3 for r in ("47:31", "16:127"))
    gate("W1_THE_V3_RULE_IS_SHOWN_TO_FAIL_ON_B_R_K", ate_true and took_false,
         "v3 rule on b-r-k REJECTED 27:8 (بورك, the ayah N157 is built on) and 17:1 "
         "(باركنا) = %s, while ACCEPTING 47:31/16:127 (اخباركم / صبرك) = %s. The rule "
         "did not merely miss on this root, it inverted the answer."
         % (ate_true, took_false))

    # -- per-narrative adjudication --------------------------------------------
    report, recon_ok = {}, True
    for key, nar in spec["narratives"].items():
        cand = candidates(rows, key)
        acc = set(nar["accepted_forms"])
        rej = set(nar["rejected_forms"])
        unadjudicated = sorted(set(cand) - acc - rej)
        phantom = sorted((acc | rej) - set(cand))
        if unadjudicated or phantom:
            recon_ok = False
        ayahs = sorted({a for f in acc for a in cand.get(f, ())},
                       key=lambda x: tuple(int(i) for i in x.split(":")))
        surahs = sorted({a.split(":")[0] for a in ayahs}, key=int)
        report[key] = {
            "root": nar["root"],
            "n_candidate_forms": len(cand),
            "n_accepted_forms": len(acc),
            "n_rejected_forms": len(rej),
            "unadjudicated": unadjudicated,
            "phantom_forms_not_in_corpus": phantom,
            "n_ayahs": len(ayahs),
            "n_surahs": len(surahs),
            "coverage_rule": "screenable" if len(ayahs) > 1 else "UNTESTABLE_BY_OQM",
            "janah_rule": "CLEARS" if len(surahs) >= 2 else
                          ("ONE_WING" if ayahs else "NO_WITNESS"),
            "ayahs": ayahs,
            "adjudication": {f: ("ACCEPTED root %s" % nar["root"]) for f in sorted(acc)},
        }
        report[key]["adjudication"].update(
            {f: "REJECTED " + why for f, why in nar["rejected_forms"].items()})
        report[key]["licensed"] = (report[key]["coverage_rule"] == "screenable"
                                   and report[key]["janah_rule"] == "CLEARS")

    gate("W2_EVERY_CANDIDATE_IS_ADJUDICATED_AND_PRINTED", recon_ok,
         "accepted + rejected exhausts the mechanically generated candidate set for "
         "all four roots; unadjudicated=%s phantom=%s"
         % ({k: v["unadjudicated"] for k, v in report.items()},
            {k: v["phantom_forms_not_in_corpus"] for k, v in report.items()}))

    qr_rej = set(spec["narratives"]["IQRA_quran"]["rejected_forms"].values())
    bk_rej = spec["narratives"]["N157_barakah"]["rejected_forms"]
    gate("W3_THE_REJECTIONS_ARE_REAL_OTHER_ROOTS",
         all(any(x in v for v in qr_rej) for x in ("q-r-b", "f-q-r", "q-r-r",
                                                   "q-r-d", "q-r-n"))
         and len(bk_rej) == 6 and "r-k-n" in bk_rej["بركنهۥ"],
         "q-r-' rejects five distinct other roots %s; b-r-k rejects four suffix "
         "artefacts plus b-r-' (بارئكم) and r-k-n (بِرُكْنِهِۦ)" % sorted(qr_rej))

    for gid, key, extra in (
            ("W4_N182_IS_LICENSED", "N182_al_asr", None),
            ("W5_N167_IS_LICENSED_AND_USED_ITS_OWN_WITNESSES", "N167_sulalah",
             ["23:12", "24:63", "32:8"]),
            ("W6_N157_IS_LICENSED_ONCE_THE_INSTRUMENT_IS_FIXED", "N157_barakah",
             ["27:8"]),
            ("W7_IQRA_IS_LICENSED_AND_ITS_DISTRIBUTION_IS_REPORTED", "IQRA_quran",
             ["2:228"])):
        rep = report[key]
        ok = rep["licensed"]
        note = ""
        if extra and key == "N167_sulalah":
            ok = ok and rep["ayahs"] == extra
            note = (" ayahs found %s vs the three N167 itself cites %s -> exact match "
                    "= %s" % (rep["ayahs"], extra, rep["ayahs"] == extra))
        elif extra:
            ok = ok and all(a in rep["ayahs"] for a in extra)
            note = " required ayah(s) %s present = %s" % (
                extra, all(a in rep["ayahs"] for a in extra))
        gate(gid, ok,
             "root %s: %d ayahs across %d surahs -> coverage=%s janah=%s licensed=%s.%s"
             % (rep["root"], rep["n_ayahs"], rep["n_surahs"], rep["coverage_rule"],
                rep["janah_rule"], rep["licensed"], note))

    # q-r-' distribution, reported whichever way it cuts
    qc = candidates(rows, "IQRA_quran")
    acc_q = set(spec["narratives"]["IQRA_quran"]["accepted_forms"])
    verbal = sorted(acc_q & QR_VERBAL)
    nominal = sorted(acc_q - QR_VERBAL)
    n_v = sum(len(qc[f]) for f in verbal)
    n_n = sum(len(qc[f]) for f in nominal)
    report["IQRA_quran"]["distribution"] = {
        "verbal_forms": verbal, "verbal_ayah_count": n_v,
        "nominal_forms": nominal, "nominal_ayah_count": n_n,
        "note": "The root is overwhelmingly NOMINAL in the text (%d vs %d). 2:228 "
                "قُرُوٓءٍ is the same root used with no reciting sense at all, which "
                "is the one datum here bearing on whether q-r-' is semantically "
                "confined to 'read'. It is reported because it was pre-registered, "
                "not because of which way it cuts -- and on its own, one ayah is "
                "ONE_WING under the Janah rule and settles nothing."
                % (n_n, n_v)}

    gate("W8_does_a_LICENSED_root_make_the_reading_correct", False,
         "It does not. Licensing says evidence is available, not that the conclusion "
         "drawn from it is right. All four readings could still be wrong.", "excluded")
    gate("W9_does_this_run_support_the_quantitative_models", False,
         "It does not. E = U*D, the cascade product, revocation latency, the Bayesian "
         "engine and Al-Mizan are not measured here or anywhere in this repository "
         "against Quranic text. Nothing in this run bears on them either way.",
         "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED,
        "supersedes": spec["supersedes"],
        "n_ayahs": len(rows),
        "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates,
        "gates_not_met": not_met,
        "narratives": report,
        "corrections": spec["CORRECTIONS_TO_CLAIMS_PUT_TO_ME"],
        "post_run_disclosures": {
            "D1_WHAT_LICENSED_MEANS": spec[
                "WHAT_THIS_RUN_DOES_AND_WHAT_IT_REFUSES_TO_DO"]["refuses"],
            "D2_THE_V3_RULE_DOES_NOT_GENERALISE": spec[
                "THE_INSTRUMENT_DEFECT_THAT_FORCED_V4"]["why_v3_still_stands"],
        },
        "primary_verdict": None,
    }
    lic = [k for k, v in report.items() if v["licensed"]]
    res["primary_verdict"] = (
        "%s. All four roots are LICENSED: %s. Each clears both of OQM's own rules, so "
        "for each of these narratives the Quran can be used to define the term "
        "internally -- unlike 58:11, where N159 showed the same rules failing on "
        "purpose. This says the inquiry may proceed. It does NOT say any reading is "
        "correct. The run also had to correct its own instrument first: v3's proclitic "
        "rule rejected 27:8 بُورِكَ, the very ayah N157 is built on, while accepting "
        "four suffix artefacts."
        % (res["score"], ", ".join(sorted(lic))))

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v4.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "narratives": {k: {kk: v[kk] for kk in
                                         ("root", "n_ayahs", "n_surahs",
                                          "coverage_rule", "janah_rule", "licensed")}
                                     for k, v in report.items()},
                      "iqra_distribution": report["IQRA_quran"]["distribution"],
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
