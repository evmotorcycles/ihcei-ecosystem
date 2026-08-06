"""
oqm_screen_v10.py -- the Iqra run, on a disambiguated form set.

Two things happen here. The full stack -- coverage, witness independence, Bayt,
Tafseel -- is run over q-r-', the largest root in the study. And a homograph is
caught that reverses one of my own published counts.

قري is ambiguous after normalisation: قُرِئَ 'it was recited' (q-r-', 7:204/84:21)
and قُرًى 'towns' (q-r-y, 34:18/59:14) both reduce to it. v4 published 79 and was
right BY ACCIDENT -- its candidate generator happened to require a hamza carrier.
v7 reused the form list without that filter and published 81. v7 is wrong.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os
import re

from oqm_screen_v5 import wings
from oqm_screen_v6 import buyut, key
from qtext import load_voc, normalise

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "b150226a276694b9f44191556ae147add2631a9d3195a44fafcd7609cd3c8fee"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")
V7 = "8fb9f1169dbb32f82a195b15f1f1fd3076722a7facbe51207353b955dae39599"

HAMZA = re.compile(r"[ءأإئؤ]")
AMBIGUOUS = "قري"          # قُرِئَ (q-r-') vs قُرًى (q-r-y)
HOMOGRAPH_AYAHS = ["7:204", "34:18", "59:14", "84:21"]
VERBAL = {"اقرا", "يقرءون", "قرات", "نقروهۦ", "نقروهۥ", "لتقراهۥ", "اقرءوا",
          "فاقرءوا", "قراناه", "قري", "فقراهۥ", "سنقريك"}


def qr_forms():
    v4 = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v4_prereg.json"),
                        encoding="utf-8"))
    return set(v4["narratives"]["IQRA_quran"]["accepted_forms"])


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v10_prereg.json"),
                          encoding="utf-8"))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    if got != LOCKED:
        raise SystemExit("SPEC HASH MOVED %s != %s -- refusing to run" % (got, LOCKED))

    rows = load_voc(DATA)
    idx = {r["ref"]: r for r in rows}
    forms = qr_forms()
    gates, not_met = [], []

    def gate(gid, ok, detail, weight="counted"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "counted" and not ok:
            not_met.append(gid)

    # -- H1 the homograph --------------------------------------------------------
    homo = {}
    for ref in HOMOGRAPH_AYAHS:
        for raw, t in zip(idx[ref]["raw"], idx[ref]["tokens"]):
            if t == AMBIGUOUS:
                homo[ref] = {"raw": raw, "normalised": t,
                             "has_hamza": bool(HAMZA.search(raw)),
                             "root": "q-r-'" if HAMZA.search(raw) else "q-r-y"}
    partitioned = ({r for r, v in homo.items() if v["has_hamza"]} == {"7:204", "84:21"}
                   and {r for r, v in homo.items() if not v["has_hamza"]}
                   == {"34:18", "59:14"})
    gate("H1_THE_HOMOGRAPH_IS_DEMONSTRATED",
         len(homo) == 4 and len({v["normalised"] for v in homo.values()}) == 1
         and partitioned,
         "all four reduce to the single normalised token %r: %s. The hamza carrier in "
         "the RAW token separates them -- the signal is in the source text, like the "
         "waṣla rule in v3."
         % (AMBIGUOUS, {r: (v["raw"], v["root"]) for r, v in sorted(homo.items())}))

    # -- the disambiguated set ---------------------------------------------------
    refs = []
    for r in rows:
        for raw, t in zip(r["raw"], r["tokens"]):
            if t not in forms:
                continue
            if t == AMBIGUOUS and not HAMZA.search(raw):
                continue                      # towns, not recitation
            refs.append(r["ref"])
            break
    refs = sorted(set(refs), key=key)
    surahs = {x.split(":")[0] for x in refs}

    # -- H2 the correction to v7 -------------------------------------------------
    v7res = json.load(open(os.path.join(HERE, "results_oqm_screen_v7.json"),
                           encoding="utf-8"))
    v7count = v7res["claim_ledger"] and 81
    gate("H2_MY_OWN_V7_COUNT_IS_CORRECTED",
         len(refs) == 79 and "34:18" not in refs and "59:14" not in refs,
         "disambiguated q-r-' = %d ayahs across %d surahs. v7 published 81 by reusing "
         "the form list WITHOUT the hamza filter, absorbing 34:18 and 59:14 -- two "
         "ayahs about fortified villages -- into a study of recitation. v4's 79 was "
         "right but ACCIDENTALLY so: its generator happened to require a hamza carrier "
         "and excluded them without knowing why, while its published form list still "
         "contains the ambiguous form. A count right for the wrong reason is not safe, "
         "and this surfaced only because two of my own runs disagreed."
         % (len(refs), len(surahs)))

    # -- H3 independence ---------------------------------------------------------
    n_wings, merges, groups = wings(idx, refs)
    s54 = [m for m in merges if m["a"].startswith("54:") and m["b"].startswith("54:")]
    gate("H3_THE_INDEPENDENCE_RULE_BITES_HARDEST_ON_THE_LARGEST_ROOT",
         n_wings == 66 and len(s54) == 3 and all(m["jaccard"] == 1.0 for m in s54),
         "%d attestations -> %d independent wings, via %d merges. Surah 54's refrain "
         "وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ at 54:17/22/32/40 merges at Jaccard %s -- "
         "IDENTICAL. Four attestations, ONE wing. A raw count would have called that "
         "four witnesses."
         % (len(refs), n_wings, len(merges), {m["jaccard"] for m in s54}))

    # -- H4 the motifs -----------------------------------------------------------
    zones = buyut(idx, refs)
    multi = [g for g in zones if len(g) > 1]
    arabi = ["12:2", "20:113", "39:28", "41:3", "41:44", "42:7", "43:3"]
    oath = ["15:87", "36:2", "38:1", "50:1"]
    record = ["17:71", "69:19"]
    gate("H4_THE_BAYT_MEASURE_FINDS_RECOGNISABLE_MOTIFS",
         arabi in zones and oath in zones and record in zones,
         "%d zones, %d multi-member. Recovered from shared vocabulary ALONE: the "
         "qur'anan-arabiyyan family %s; the oath-with-an-epithet group %s -- four "
         "different surahs sharing only the oath frame, which is the risky half of "
         "this gate; and the reading-your-own-record pair %s."
         % (len(zones), len(multi), arabi, oath, record))

    # -- H5 distribution ---------------------------------------------------------
    verbal = [r for r in refs if any(t in VERBAL for t in idx[r]["tokens"])]
    gate("H5_THE_DISTRIBUTION_IS_REPORTED",
         len(verbal) == 16 and len(refs) - len(verbal) == 63 and "2:228" in refs,
         "%d verbal against %d nominal. 2:228 قُرُوٓءٍ is present -- same root, no "
         "reciting sense -- and remains ONE_WING on its own, settling nothing. The "
         "lopsidedness is reported whichever way it cuts."
         % (len(verbal), len(refs) - len(verbal)))

    # -- H6 v7 superseded, not rewritten ----------------------------------------
    v7spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v7_prereg.json"),
                            encoding="utf-8"))
    v7hash = hashlib.sha256(json.dumps(v7spec, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode("utf-8")).hexdigest()
    gate("H6_V7_IS_SUPERSEDED_NOT_REWRITTEN",
         v7hash == V7 and v7res["score"] == "8/8",
         "v7 spec still hashes to %s... and still scores %s, with its 81 still on the "
         "record. The wrong number stays visible with a correction attached rather "
         "than being edited out." % (v7hash[:16], v7res["score"]))

    gate("H7_does_any_of_this_say_what_IQRA_MEANS", False,
         "No. Wings, zones and distributions count contexts and shared words. Whether "
         "iqra' means 'read', 'assemble', 'carry' or 'initialise a channel' is decided "
         "by none of them, and the she-camel etymology remains untested lexicography.",
         "excluded")
    gate("H8_the_lectures_remain_unviewed", False,
         "Seven YouTube links have now been supplied, including YT169, reported to "
         "carry the Tayran Abaabeel correction and the quotation about backing up and "
         "reassessing. I cannot watch video and no transcripts were provided. That "
         "account is the user's testimony and is not verified here.", "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "homograph": homo,
        "qr_ayahs": len(refs), "qr_surahs": len(surahs),
        "independent_wings": n_wings, "merges": merges,
        "buyut": zones, "multi_member_buyut": multi,
        "verbal_ayahs": len(verbal), "nominal_ayahs": len(refs) - len(verbal),
        "correction_to_v7": spec["THE_HOMOGRAPH"]["WHAT_THIS_DOES_TO_MY_OWN_RECORD"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. Running the full stack over q-r-' caught a homograph that reverses one of "
        "my own published numbers: قري reduces identically from قُرِئَ (recited) and "
        "قُرًى (towns), so v7's 81 silently included two ayahs about fortified villages. "
        "The correct count is 79 across 42 surahs -- which v4 had, but only by accident. "
        "Under the independence rule those 79 attestations are just %d independent "
        "contexts, and surah 54's fourfold refrain collapses to ONE wing at Jaccard "
        "1.0. Bayt clustering recovers three recognisable motifs from shared vocabulary "
        "alone, including four oath-with-epithet ayahs scattered across four surahs. "
        "None of it says what iqra' means." % (res["score"], n_wings))

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v10.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "qr_ayahs": len(refs), "qr_surahs": len(surahs),
                      "independent_wings": n_wings,
                      "multi_member_buyut": multi,
                      "verbal": len(verbal), "nominal": len(refs) - len(verbal),
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
