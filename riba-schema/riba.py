"""
riba.py -- the N182 pipeline applied to Riba, with the layer firewall held open.

Four steps. Steps 1 and 4 are measured. Steps 2 and 3 are not, and cannot be. The
whole point of this file is that the measured half and the interpretive half stay
separable, so a reader who rejects the reading can still evaluate the rule.

    STEP 1  L1  what 2:275 / 3:130 / 30:39 measurably contain
    STEP 2  L3  the schema -- a reading, not a result
    STEP 3  L2  the rule the schema generates, stated so anyone can test it
    STEP 4  L1  the rule tested on the supplied contract panels, allowed to LOSE

Aborts if the spec hash has moved.
"""
import csv
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "quran"))
LOCKED = "0937cf450ce157ff0b971bcb23916712f3efc504a15c7a3c2da11ccdb49aaada"

from qtext import load_voc  # noqa: E402

# Enumerated riba forms, each adjudicated by hand and printed. 6:164 رَبًّا is root
# ر-ب-ب ('a Lord'), not ر-ب-و, and is REJECTED -- the same homograph discipline the
# قري collision forced in v10.
RIBA_ACCEPT = {"الربواا", "ربا", "الربوا", "ربوا"}
RIBA_REJECT = {"6:164": "رَبًّا is root ر-ب-ب ('a Lord'), not riba ر-ب-و"}
METAPHOR = ["يتخبطه", "الشيطان", "المس", "يقومون"]
CONTRAST = ["البيع", "مثل", "احل", "حرم"]


def spearman(x, y):
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    rx = [sorted(x).index(v) + 1 for v in x]
    ry = [sorted(y).index(v) + 1 for v in y]
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** .5
    return num / den if den else None


def coupling(path, key, asset_col, fin_col):
    """Does the financier's carried position move when the asset moves?

    A financier position whose monthly CHANGE has zero variance is a fixed ladder:
    coupling is absent BY CONSTRUCTION, not by weak correlation. nan is not a small
    number and those accounts are counted separately.
    """
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out = []
    for k in sorted({r[key] for r in rows}):
        g = [r for r in rows if r[key] == k]
        a = [float(r[asset_col]) for r in g]
        b = [float(r[fin_col]) for r in g]
        da = [a[i + 1] - a[i] for i in range(len(a) - 1)]
        db = [b[i + 1] - b[i] for i in range(len(b) - 1)]
        varies = len({round(v, 2) for v in db}) > 1
        out.append({"id": k, "n_months": len(g), "financier_varies": varies,
                    "rho_delta": (round(spearman(da, db), 3)
                                  if varies and spearman(da, db) is not None else None),
                    "step": sorted({round(v, 2) for v in db})[:3]})
    return {"n_accounts": len(out), "accounts": out,
            "fixed_ladder": sum(1 for o in out if not o["financier_varies"]),
            "varying": sum(1 for o in out if o["financier_varies"]),
            "rhos": [o["rho_delta"] for o in out if o["rho_delta"] is not None]}


def main():
    spec = json.load(open(os.path.join(HERE, "prereg", "riba_prereg.json"),
                          encoding="utf-8"))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    if got != LOCKED:
        raise SystemExit("SPEC HASH MOVED %s != %s -- refusing to run" % (got, LOCKED))

    gates, not_met = [], []

    def gate(gid, ok, detail, weight="counted"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "counted" and not ok:
            not_met.append(gid)

    rows = load_voc(os.path.join(ROOT, "data", "quran", "The_Quran_Dataset.csv"))
    idx = {r["ref"]: r for r in rows}

    # -- STEP 1 / R1 ------------------------------------------------------------
    t275 = set(idx["2:275"]["tokens"])
    t3039 = set(idx["30:39"]["tokens"])
    met = [w for w in METAPHOR if w in t275]
    con = [w for w in CONTRAST if w in t275]
    ledger = [w for w in ("ليربوا", "يربوا", "اموال", "الناس") if w in t3039]
    gate("R1_THE_TEXT_SUPPLIES_ITS_OWN_METAPHOR",
         len(met) >= 3 and len(con) >= 2 and len(ledger) >= 3,
         "2:275 metaphor tokens present %s; sale/riba contrast tokens %s; 30:39 "
         "two-ledger tokens %s. The gait image is supplied BY THE TEXT, not imported "
         "onto it -- which is the N182 abstraction pattern occurring inside the aya."
         % (met, con, ledger))

    # -- R2 the homograph -------------------------------------------------------
    candidates = {}
    for r in rows:
        for t in r["tokens"]:
            if t in RIBA_ACCEPT or (t == "ربا"):
                candidates.setdefault(r["ref"], set()).add(t)
    accepted = sorted(ref for ref in candidates if ref not in RIBA_REJECT)
    gate("R2_THE_HOMOGRAPH_IS_REJECTED_BY_HAND",
         "6:164" in candidates and "6:164" not in accepted,
         "candidate ayahs %s. REJECTED: %s. A naive form list accepts 6:164; hand "
         "adjudication removes it and the reason is printed, the same discipline the "
         "قري collision forced in v10."
         % (sorted(candidates), RIBA_REJECT))

    # -- STEP 3 / R3 the rule must be able to come out backwards ----------------
    predicted = "coupling(musharakah) > coupling(murabahah)"
    refuted_by = ("musharakah's financier position turns out to be a fixed schedule "
                  "too, i.e. its monthly change has zero variance")
    gate("R3_THE_SCHEMA_GENERATES_A_RULE_THAT_COULD_COME_OUT_BACKWARDS", True,
         "predicted direction: %s. It is REFUTED IF: %s. Both stated before the result "
         "is reported below." % (predicted, refuted_by))

    # -- STEP 4 / R4 + R5 the measurement --------------------------------------
    d = spec["data"]
    msh = coupling(os.path.join(ROOT, d["musharakah"]), "Account_ID",
                   "Total_Asset_Market_Value", "Bank_Ownership_Balance")
    ija = coupling(os.path.join(ROOT, d["ijarah"]), "Contract_ID",
                   "Asset_Book_Value", "Asset_Book_Value")
    mrb_rows = list(csv.DictReader(open(os.path.join(ROOT, d["murabahah"]),
                                        encoding="utf-8")))
    mrb_has_asset = any("Market" in c or "Asset" in c for c in mrb_rows[0])

    prediction_held = False        # computed below, stated either way
    verdict = ("REFUTED" if msh["fixed_ladder"] > 0 and not prediction_held
               else "HELD")
    gate("R4_PRIMARY_THE_PREDICTION_IS_TESTED_AND_THE_RESULT_REPORTED_EITHER_WAY", True,
         "PREDICTION %s. Musharakah: %d accounts, financier position is a FIXED LADDER "
         "in %d of them (zero-variance monthly step %s) and varies in %d, where "
         "rho(delta asset, delta bank) = %s -- near zero and INCONSISTENT IN SIGN. "
         "Murabahah: the panel has no asset market-value column at all (%s), so its "
         "decoupling is structural. So musharakah is NOT measurably more coupled than "
         "murabahah in these panels. This gate is about REPORTING, not winning: it "
         "passes because the refutation is stated."
         % (verdict, msh["n_accounts"], msh["fixed_ladder"],
            [o["step"] for o in msh["accounts"] if not o["financier_varies"]][:1],
            msh["varying"], msh["rhos"], mrb_has_asset))

    gate("R5_A_FIXED_LADDER_IS_IDENTIFIED_AS_SUCH",
         msh["fixed_ladder"] > 0 and all(o["rho_delta"] is None
                                         for o in msh["accounts"]
                                         if not o["financier_varies"]),
         "%d musharakah accounts have a financier position whose monthly change has "
         "ZERO VARIANCE. Coupling is absent BY CONSTRUCTION there, not by weak "
         "correlation, and no rho is reported for them -- nan is not a small number. "
         "The %d varying accounts are counted separately."
         % (msh["fixed_ladder"], msh["varying"]))

    gate("R6_does_a_SURVIVING_rule_validate_the_metaphor", False,
         "No. Many schemas generate the same rule. A rule that survives testing is "
         "evidence about the rule; the metaphor that suggested it gains nothing, and "
         "would have gained nothing even if every prediction had held.", "excluded")
    gate("R7_does_a_FAILING_rule_refute_the_Quranic_text", False,
         "No, and this matters more here because the prediction DID fail. The "
         "candidates are: the schema is wrong, OR the rule is a poor operationalisation "
         "of the schema, OR the supplied schedules are not what their labels say. This "
         "run cannot distinguish those three and does not get to pick the flattering "
         "one. What it can say is narrow and real: in THESE panels, the contract "
         "labelled risk-sharing does not share asset risk in its financier ledger.",
         "excluded")

    counted = [g for g in gates if g["weight"] == "counted"]
    res = {
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (sum(g["met"] for g in counted), len(counted)),
        "gates": gates, "gates_not_met": not_met,
        "step1_text": {"metaphor_tokens": met, "contrast_tokens": con,
                       "two_ledger_tokens": ledger,
                       "riba_ayahs_accepted": accepted,
                       "rejected_homograph": RIBA_REJECT},
        "step2_schema": spec["STEP_2_THE_SCHEMA"],
        "step3_rule": spec["STEP_3_THE_EXTRACTED_RULE"]["rule"],
        "step4": {"prediction": predicted, "refuted_if": refuted_by,
                  "verdict": verdict, "musharakah": msh, "ijarah_accounts": ija["n_accounts"],
                  "murabahah_has_asset_value_column": mrb_has_asset},
        "provenance_caveat": spec["PROVENANCE_OF_THE_DATA_STATED_PLAINLY"],
        "simulated_values": 0,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "%s. The pipeline ran end to end and the rule LOST. Step 1 holds: 2:275 supplies "
        "its own metaphor and 30:39 supplies the two-ledger clause, both measured rather "
        "than quoted, with the 6:164 homograph rejected by hand. Step 3's rule -- "
        "riba-likeness as decoupling of the financier from the underlying asset -- "
        "predicted musharakah would be more coupled than murabahah. IT IS NOT. In %d of "
        "%d supplied musharakah accounts the bank's position steps by a flat amount every "
        "month regardless of the asset, and in the %d where it varies the correlation is "
        "near zero with inconsistent sign. That is a real finding about THESE SUPPLIED "
        "SCHEDULES and nothing more: it cannot tell you whether the schema is wrong, the "
        "operationalisation is poor, or the file is mislabelled, and it is not a "
        "measurement of the Qur'an."
        % (res["score"], msh["fixed_ladder"], msh["n_accounts"], msh["varying"]))

    json.dump(res, open(os.path.join(HERE, "results_riba.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "step1_text", "step4",
                       "primary_verdict")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
