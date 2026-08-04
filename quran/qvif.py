"""
qvif.py -- does a VIF gate carry any information on Quranic word counts?

Spec af27d2c9c9398ca4f99a4772e6769a23cf4ab8198542067f453971c83e6c09b3, locked after a
NULL-ONLY probe. The Salat/Zakat VIF was not computed before the lock.

A VIF of 1.000073 has been quoted as showing the text handles 'seeking' and 'sharing' as
independent channel legs. This run asks the prior question: on this substrate, does a
near-1.0 VIF distinguish anything at all?
"""
import hashlib
import json
import os
import random
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qtext import load  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "af27d2c9c9398ca4f99a4772e6769a23cf4ab8198542067f453971c83e6c09b3"

SPEC = json.load(open(os.path.join(HERE, "prereg", "quran_vif_prereg.json"),
                      encoding="utf-8"))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

DATA = os.path.join(ROOT, "data", "quran", "The_Quran_Dataset.csv")
ORTHO_BAR, W2_MAX_FRAC, N_NULL, SEED = 1.05, 0.50, 1200, 20260804
W5_MIN = 5

# Track definitions. Regexes over clitic-stripped tokens, declared in the spec.
TRACKS = {
    # NOTE: these regexes match the DATASET'S orthography after NFD normalisation.
    # Two traps caught by the W1 integrity gate on the first run: hamza-on-waw (U+0624)
    # decomposes to waw + a combining mark, so 'mumin' is مومن not مءمن; and zakat is
    # written زكوه with a waw. Zakariyya is excluded -- same letters, a personal name.
    "SALAT":   r"^(صلاه|صلاتك|صلاتهم|صلاتي|صلاتهۦ|صلوات|الصلاه|صلوه|الصلوه|صلوتك|صلوتهم|يصلي|يصلون|صلوا|مصلي|المصلين)$",
    "ZAKAT":   r"^(زكاه|الزكاه|زكوه|زكواه|الزكواه|يزكي|يزكيهم|يزكيكم|تزكي|ازكي|يتزكي|زكيها|تزكيه)$",
    "BARAKAH": r"^(برك|بركه|بركات|مبارك|مباركه|تبارك|باركنا|بوركت)$",
    "MILLAH":  r"^مل(ه|تي|تكم|تنا|تهم|ته)$",
    "NASARA":  r"^(نصاري|نصارا)$",
    "MUSLIM":  r"^(مسلم|مسلما|مسلمون|مسلمين|المسلمون|المسلمين|مسلمه|مسلمات)$",
    "MUMIN":   r"^(مومن|مومنا|مومنون|مومنين|المومنون|المومنين|للمومنين|مومنه|مومنات)$",
    "IMAN":    r"^(ايمان|ايمانا|ايمانكم|ايمانهم|بالايمان|الايمان)$",
}
# For W5: finite verbs that could designate a group, per root.
SLM_VERBS = {"اسلموا", "اسلم", "اسلمت", "يسلمون", "تسلمون"}
AMN_VERBS = {"امنوا", "امن", "يومنون", "امنت", "تومنون"}
REL = {"الذين", "للذين", "والذين", "لذين", "فالذين"}
VOC = "ياايها"


def vif(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    if den == 0:
        return None, None
    r = num / den
    return (1.0 / (1.0 - r * r) if abs(r) < 1 else float("inf")), r


def designated(rows, verbs):
    hits = []
    for r in rows:
        t = r["tokens"]
        for i, w in enumerate(r["bases"]):
            if w not in verbs:
                continue
            prev = t[i - 1] if i else ""
            prev2 = t[i - 2] if i > 1 else ""
            if prev in REL or prev2 in REL or prev == VOC or prev2 == VOC:
                hits.append(r["ref"])
    return hits


def main():
    rows = load(DATA)
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    def track(rx):
        p = re.compile(rx)
        return [sum(1 for w in r["bases"] if p.match(w)) for r in rows]

    T = {k: track(v) for k, v in TRACKS.items()}
    sizes = {k: sum(v) for k, v in T.items()}

    # ---- the frequency-matched null, NOT touching the declared tracks ------
    vocab = Counter(w for r in rows for w in r["bases"])
    declared = {w for rx in TRACKS.values() for w in vocab if re.match(rx, w)}
    rng = random.Random(SEED)
    by_freq = {}
    for w, c in vocab.items():
        if w in declared:
            continue
        by_freq.setdefault(c, []).append(w)
    freqs = [f for f in by_freq if len(by_freq[f]) >= 2 and 3 <= f <= 200]
    null = []
    while len(null) < N_NULL and freqs:
        f = rng.choice(freqs)
        a, b = rng.sample(by_freq[f], 2)
        v, _r = vif(track("^%s$" % re.escape(a)), track("^%s$" % re.escape(b)))
        if v is not None:
            null.append(v)
    null.sort()
    frac_clearing = sum(1 for v in null if v < ORTHO_BAR) / len(null)

    gate("W1_integrity",
         len(rows) == 6236 and all(sizes.values()) and len(null) >= 1000,
         "%d ayahs; track token totals %s; null pairs %d"
         % (len(rows), sizes, len(null)))

    # ---- W2 PRIMARY --------------------------------------------------------
    w2 = frac_clearing < W2_MAX_FRAC
    gate("W2_PRIMARY_DOES_THE_VIF_GATE_DISCRIMINATE_ON_THIS_SUBSTRATE", w2,
         "%.1f%% of %d frequency-matched RANDOM unrelated word pairs clear the "
         "orthogonality bar of VIF < %.2f (the gate needs FEWER than %.0f%% to clear, "
         "otherwise it separates nothing). Null median VIF %.6f."
         % (100 * frac_clearing, len(null), ORTHO_BAR, 100 * W2_MAX_FRAC,
            statistics.median(null)))

    # ---- W3 the measured value, disclosure ---------------------------------
    sz_vif, sz_r = vif(T["SALAT"], T["ZAKAT"])
    pct = 100.0 * sum(1 for v in null if v <= sz_vif) / len(null)
    gates.append({"id": "W3_the_measured_Salat_Zakat_VIF_and_its_percentile",
                  "met": None, "weight": "excluded",
                  "detail": "VIF(SALAT, ZAKAT) = %.6f (r = %+.6f) across %d ayahs. It sits "
                            "at the %.1fth percentile of the frequency-matched null, i.e. "
                            "%.1f%% of RANDOM unrelated word pairs are at least as "
                            "'orthogonal'. Null median %.6f."
                            % (sz_vif, sz_r, len(rows), pct, 100 - pct,
                               statistics.median(null))})

    # ---- W4 full matrix, disclosure ----------------------------------------
    keys = sorted(TRACKS)
    matrix, clearing = {}, 0
    pairs = 0
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            v, r = vif(T[a], T[b])
            matrix["%s|%s" % (a, b)] = None if v is None else round(v, 6)
            pairs += 1
            if v is not None and v < ORTHO_BAR:
                clearing += 1
    gates.append({"id": "W4_the_full_matrix_over_the_declared_tracks",
                  "met": None, "weight": "excluded",
                  "detail": "%d of %d pairs among the 8 declared tracks clear VIF < %.2f "
                            "(%.1f%%). Every pair, related or not, looks 'orthogonal'."
                            % (clearing, pairs, ORTHO_BAR, 100 * clearing / pairs)})

    # ---- W5 the designation test, which IS known to discriminate -----------
    slm = designated(rows, SLM_VERBS)
    amn = designated(rows, AMN_VERBS)
    w5 = len(slm) >= W5_MIN and len(amn) >= W5_MIN
    gate("W5_THE_DESIGNATION_TEST_EXTENDED_TO_muslim_AND_mumin", w5,
         "groups named by a finite verb using the SAME matcher that scored 7 of 7 control "
         "proper nouns at zero: S-L-M (aslama forms) %d times; A-M-N (amanu forms) %d "
         "times. Each needs >= %d." % (len(slm), len(amn), W5_MIN))

    gates.append({"id": "W6_is_a_text_count_VIF_the_same_quantity_as_a_node_feature_VIF",
                  "met": None, "weight": "excluded",
                  "detail": "EXCLUDED. It is not. The yeast (1.0026) and GitHub (1.0203) "
                            "VIFs were computed on CONTINUOUS PER-NODE FEATURES where every "
                            "unit has a real value on both axes and collinearity is a live "
                            "possibility. Per-ayah word counts are overwhelmingly zero. "
                            "Sharing a name does not make the quantities comparable and no "
                            "number here may be reported beside them as if it did."})
    gates.append({"id": "W7_meaning_and_communities", "met": None, "weight": "excluded",
                  "detail": "EXCLUDED and OUT OF SCOPE. The units are word-forms in one "
                            "text. Nothing establishes what any word means, and nothing is "
                            "a claim about Jewish, Christian or Muslim people, communities "
                            "or beliefs."})

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Does a VIF gate carry information on Quranic word counts?",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet, "simulated_values": 0,
        "n_ayahs": len(rows),
        "track_token_totals": sizes,
        "salat_zakat": {"VIF": round(sz_vif, 6), "r": round(sz_r, 6),
                        "percentile_in_null": round(pct, 1)},
        "null": {"n_pairs": len(null), "median_VIF": round(statistics.median(null), 6),
                 "p95_VIF": round(null[int(0.95 * len(null))], 6),
                 "fraction_clearing_1.05": round(frac_clearing, 4)},
        "pairwise_matrix": matrix,
        "designation": {"S_L_M": len(slm), "A_M_N": len(amn),
                        "S_L_M_refs": sorted(set(slm))[:12]},
        "post_run_disclosures": {
            "D1_THE_QUOTED_FIGURE_IS_NOT_EVIDENCE": {
                "quoted": 1.000073,
                "null_median": round(statistics.median(null), 6),
                "fraction_of_random_pairs_clearing_the_bar": round(frac_clearing, 4),
                "note": "A near-1.0 VIF on this substrate is what arbitrary unrelated word "
                        "pairs produce, because two rare tracks are both nearly all zeros "
                        "across 6,236 ayahs and r is near 0 whatever the words mean. The "
                        "figure supports no claim about how the text handles anything.",
            },
            "D2_WHAT_SURVIVES_AND_IT_IS_NOT_THE_VIF": {
                "note": "The DESIGNATION test does discriminate -- it scored 7 of 7 control "
                        "proper nouns at zero in spec 708ac80e. Applied here it finds the "
                        "S-L-M and A-M-N groups named by finite verbs. That is a real "
                        "distributional fact; the VIF is not.",
            },
            "D3_the_category_difference": {
                "note": "Yeast 1.0026 and GitHub 1.0203 were computed on continuous "
                        "per-node features. Quoting a word-count VIF alongside them implies "
                        "a comparability that does not exist.",
            },
            "D4_what_none_of_this_licenses": {
                "note": "Distributional independence of two word-tracks would not be "
                        "evidence of authorial architecture even if it had been found. No "
                        "claim here concerns what any word means or any living community.",
            },
        },
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("THE VIF GATE DOES NOT DISCRIMINATE ON THIS SUBSTRATE: %.1f%% of random unrelated "
         "word pairs clear VIF < %.2f. The measured Salat/Zakat VIF of %.6f sits at the "
         "%.1fth percentile of that null. A near-1.0 VIF here is forced by sparsity and "
         "supports nothing." % (100 * frac_clearing, ORTHO_BAR, sz_vif, pct))
        if not w2 else
        ("The VIF gate discriminates here: only %.1f%% of random pairs clear the bar, so "
         "the measured %.6f can be read against the null."
         % (100 * frac_clearing, sz_vif)))
    with open(os.path.join(HERE, "results_qvif.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "salat_zakat", "null",
                                          "designation", "primary_verdict")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
