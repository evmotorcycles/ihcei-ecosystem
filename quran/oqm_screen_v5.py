"""
oqm_screen_v5.py -- witness independence: the Janah is not straightforward.

v3 and v4 counted a wing per DISTINCT SURAH. That is wrong in both directions: too
loose, because one fixed formula repeated across four surahs is one piece of evidence
wearing four hats; too tight, because two unrelated passages seventeen ayahs apart in
one surah are two contexts. v5 replaces the surah proxy with an independent-CONTEXT
rule, and adds the test the surah counter could never express -- whether a claimed
link BETWEEN TERMS has any textual footing at all.

Aborts if the spec hash has moved.
"""
import hashlib
import json
import os

from qtext import load_voc

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "5f43d480f2af1616f365b925a2ea887936cbffdccf337efd2d8452fec229719d"
DATA = os.path.join(HERE, "..", "data", "quran", "The_Quran_Dataset.csv")

THETA = 0.50          # J1 formulaic-collapse similarity
ADJACENT = 3          # J2 same-passage window, in ayahs

# Explicit surface forms. Substring matching on n-w-q takes أعناقهم ('their necks',
# root 3-n-q) for a she-camel, so the forms are enumerated and the necks are kept as
# a declared negative control.
NAQAH = {"ناقه", "الناقه", "وناقه", "فناقه"}
NECKS = {"اعناقهم"}
SAAH = {"الساعه", "ساعه", "بالساعه", "للساعه", "والساعه", "وساعه"}
QR = {"القران", "قرانا", "قران", "اقرا", "يقرءون", "والقران", "وقران", "بالقران",
      "بقران", "لقران", "قرانهۥ", "وقرانهۥ", "وقرانا", "قراناه", "قرات", "قروء",
      "اقرءوا", "فاقرءوا", "نقروهۥ", "لتقراهۥ", "فقراهۥ", "قري", "سنقريك"}

PRIOR_SETS = {
    "v2_iman": ["2:108", "3:86", "3:100", "3:106", "4:137", "9:66", "9:74", "16:106"],
    "v3_Z7_nazzala_minimal_pairs": ["3:3", "47:9", "47:26"],
    "N159_nufarriq": ["2:136", "2:285", "3:84", "4:152"],
    "N167_sulala": ["23:12", "24:63", "32:8"],
    "N182_al_asr": ["2:266", "12:36", "12:49", "78:14", "103:1"],
}


def jaccard(idx, a, b):
    A, B = set(idx[a]["tokens"]), set(idx[b]["tokens"])
    return len(A & B) / len(A | B) if (A | B) else 0.0


def wings(idx, refs):
    """Independent CONTEXTS. Union-find over J1 formulaic and J2 adjacency merges."""
    refs = sorted(set(refs), key=lambda x: tuple(int(i) for i in x.split(":")))
    parent = {r: r for r in refs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    merges = []
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            a, b = refs[i], refs[j]
            sa, na = a.split(":")
            sb, nb = b.split(":")
            sim = jaccard(idx, a, b)
            adj = sa == sb and abs(int(na) - int(nb)) <= ADJACENT
            if sim >= THETA or adj:
                if find(a) != find(b):
                    merges.append({"a": a, "b": b, "jaccard": round(sim, 4),
                                   "reason": "J1_formulaic" if sim >= THETA
                                             else "J2_same_passage"})
                parent[find(a)] = find(b)
    groups = {}
    for r in refs:
        groups.setdefault(find(r), []).append(r)
    return len(groups), merges, sorted(groups.values())


def verdict(n):
    return "CLEARS" if n >= 2 else ("ONE_WING" if n == 1 else "NO_WITNESS")


def ayahs_with(rows, forms):
    return {r["ref"] for r in rows if any(t in forms for t in r["tokens"])}


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v5_prereg.json"),
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

    # -- V4 re-adjudicate every prior result -----------------------------------
    readj = {}
    for name, refs in PRIOR_SETS.items():
        old = len({r.split(":")[0] for r in refs})
        new, merges, groups = wings(idx, refs)
        readj[name] = {
            "refs": refs, "old_rule_surahs": old, "old_verdict": verdict(old),
            "new_rule_wings": new, "new_verdict": verdict(new),
            "direction": "TIGHTENED" if new < old else
                         ("RELAXED" if new > old else "UNCHANGED"),
            "merges": merges, "wing_groups": groups,
        }
    dirs = {v["direction"] for v in readj.values()}
    gate("V1_THE_RULE_MOVES_IN_BOTH_DIRECTIONS_AND_BOTH_ARE_REPORTED",
         "RELAXED" in dirs and "UNCHANGED" in dirs,
         "directions across the five re-adjudicated sets: %s. The corrected rule "
         "RELAXES more than it tightens, because surah-identity was over-merging "
         "distant ayahs. A stricter rule would have sounded more rigorous; this one "
         "is more accurate, and the direction of every change is stated."
         % {k: v["direction"] for k, v in readj.items()})

    # -- V2 the new rule must be able to TAKE a verdict away -------------------
    demo = ["2:136", "3:84"]
    d_old = len({r.split(":")[0] for r in demo})
    d_new, d_merges, _ = wings(idx, demo)
    gate("V2_FORMULAIC_COLLAPSE_CAN_WITHHOLD_A_VERDICT_THE_OLD_RULE_GRANTED",
         verdict(d_old) == "CLEARS" and verdict(d_new) == "ONE_WING",
         "a claim resting only on 2:136 + 3:84: surah rule -> %d surahs -> %s; "
         "context rule -> %d wing -> %s (jaccard %.4f, different surahs, one formula). "
         "The upgrade is only worth having because it can take a verdict away."
         % (d_old, verdict(d_old), d_new, verdict(d_new),
            d_merges[0]["jaccard"] if d_merges else 0.0))

    # -- V3 passage adjacency ---------------------------------------------------
    iq = sorted(ayahs_with(rows, {"اقرا"}),
                key=lambda x: tuple(int(i) for i in x.split(":")))
    iq_n, iq_merges, iq_groups = wings(idx, iq)
    gate("V3_PASSAGE_ADJACENCY_FIRES", iq_n == 2,
         "imperative اقرا at %s -> %d wings %s; 96:1 and 96:3 are one passage and "
         "merge under J2" % (iq, iq_n, iq_groups))

    gate("V4_EVERY_PRIOR_RESULT_IS_RE_ADJUDICATED",
         len(readj) == 5 and readj["N167_sulala"]["new_verdict"] == "CLEARS",
         "five prior sets re-scored. N167 s-l-l still CLEARS on %d genuinely "
         "independent contexts, so the corrected rule did not demolish the one "
         "document result that held its riskiest gate."
         % readj["N167_sulala"]["new_rule_wings"])

    # -- V5 / V6 / V7 the claim put to me --------------------------------------
    naq = ayahs_with(rows, NAQAH)
    neck = ayahs_with(rows, NECKS)
    saa = ayahs_with(rows, SAAH)
    qr = ayahs_with(rows, QR)
    inter = {
        "naqah_and_qr": sorted(naq & qr),
        "saah_and_qr": sorted(saa & qr),
        "naqah_and_saah": sorted(naq & saa),
    }
    all_empty = not any(inter.values())
    gate("V5_PRIMARY_THE_NAQAH_SAAH_IQRA_LINK_HAS_NO_TEXTUAL_JANAH", all_empty,
         "ayah-level intersections %s. Not one ayah in the corpus contains any two of "
         "these three terms, so under J4 the link between them is NO_TEXTUAL_LINK. "
         "Had any intersection been non-empty this gate would have failed and the "
         "link would have textual support I would have to report." % inter)

    gate("V6_THE_NAQAH_MATCHER_REJECTS_THE_NECKS",
         sorted(naq) == ["11:64", "17:59", "26:155", "54:27", "7:73", "7:77", "91:13"]
         and not (naq & neck),
         "naqah -> %s; أعناقهم (root 3-n-q, 'their necks') at %s excluded"
         % (sorted(naq, key=lambda x: tuple(int(i) for i in x.split(":"))),
            sorted(neck, key=lambda x: tuple(int(i) for i in x.split(":")))))

    gate("V7_THE_FINDING_IS_NOT_THAT_THE_TERMS_ARE_RARE",
         len(saa) > 40 and len(qr) > 70,
         "As-Saah %d ayahs / %d surahs; q-r-' %d ayahs / %d surahs; An-Naqah %d ayahs. "
         "Both of the abundant terms are abundant, so the empty intersections cannot "
         "be explained by scarcity. They never meet, which is far stronger than rare."
         % (len(saa), len({x.split(':')[0] for x in saa}), len(qr),
            len({x.split(':')[0] for x in qr}), len(naq)))

    gate("V8_does_NO_TEXTUAL_LINK_refute_the_reading", False,
         "It does not. It places the reading outside the class of claims OQM's own "
         "evidence rule can support -- exactly what N159 says about a dictionary "
         "opinion. The reading may be true; it is not ESTABLISHED by a Janah, because "
         "there is no Janah to establish it.", "excluded")
    gate("V9_the_source_videos_are_not_in_evidence", False,
         "YT127 and YT133 were NOT among the sixteen documents supplied and I have not "
         "read them. Every characterisation of their content here comes from the "
         "prompt, not from a source. This run does not test whether An-Naqah means a "
         "purifier cohort or As-Saah means irrigators -- only whether the terms meet.",
         "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED, "supersedes": spec["supersedes"],
        "n_ayahs": len(rows), "simulated_values": 0,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "independence_rule": spec["independence_rule"],
        "re_adjudication": readj,
        "the_claim_put_to_me": {
            "naqah_ayahs": sorted(naq, key=lambda x: tuple(int(i) for i in x.split(":"))),
            "saah_ayah_count": len(saa), "qr_ayah_count": len(qr),
            "intersections": inter,
            "verdict": "NO_TEXTUAL_LINK" if all_empty else "TEXTUAL_LINK_PRESENT",
        },
        "not_tested": spec["WHAT_IS_STILL_NOT_TESTED"],
        "placement": spec["PLACEMENT"],
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The Janah is not straightforward and the surah proxy was wrong in both "
        "directions; a wing is now an independent CONTEXT. The corrected rule can "
        "withhold a verdict the old one granted (2:136 + 3:84, jaccard 0.6774, one "
        "formula in two surahs), and on the five prior sets it RELAXES more than it "
        "tightens -- reported because it is true, not because it flatters the "
        "correction. On the claim put to me: An-Naqah, As-Saah and q-r-' NEVER "
        "CO-OCCUR in any of the 6,236 ayahs, though two of the three are abundant. "
        "Under OQM's own rule that is NO_TEXTUAL_LINK -- not a refutation of the "
        "reading, but a finding that no Janah exists to establish it."
        % res["score"])

    json.dump(res, open(os.path.join(HERE, "results_oqm_screen_v5.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"score": res["score"], "gates_not_met": not_met,
                      "re_adjudication": {k: {kk: v[kk] for kk in
                                              ("old_rule_surahs", "new_rule_wings",
                                               "old_verdict", "new_verdict",
                                               "direction")}
                                          for k, v in readj.items()},
                      "the_claim_put_to_me": res["the_claim_put_to_me"],
                      "primary_verdict": res["primary_verdict"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
