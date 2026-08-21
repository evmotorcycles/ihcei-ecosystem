"""
test_riba.py -- the N182 pipeline applied to Riba: 5/5, and the rule LOST.

THE PIPELINE YOU ASKED FOR, RUN END TO END.
  STEP 1  L1  what 2:275 / 3:130 / 30:39 measurably contain
  STEP 2  L3  the schema — a reading, not a result
  STEP 3  L2  the rule the schema generates, stated so anyone can test it
  STEP 4  L1  the rule tested on the supplied panels, and allowed to lose

STEP 1 HOLDS, AND IT IS THE STRONGEST PART. The metaphor is supplied BY THE TEXT, not
imported onto it: 2:275 says those who consume riba لَا يَقُومُونَ إِلَّا كَمَا يَقُومُ ٱلَّذِى
يَتَخَبَّطُهُ ٱلشَّيْطَٰنُ مِنَ ٱلْمَسِّ — a physical gait standing for a condition. That IS the
N182 abstraction pattern occurring inside the aya. The same aya records and rejects an
objection — إِنَّمَا ٱلْبَيْعُ مِثْلُ ٱلرِّبَوٰا۟ — so the text asserts a DISCRIMINABLE difference
between two things that look alike. And 30:39 supplies two ledgers that diverge:
لِّيَرْبُوَا۟ فِىٓ أَمْوَٰلِ ٱلنَّاسِ فَلَا يَرْبُوا۟ عِندَ ٱللَّهِ.

A HOMOGRAPH REJECTED BY HAND. 6:164 رَبًّا is root ر-ب-ب, "a Lord", not riba ر-ب-و. A
naive form list accepts it. R2 requires it to appear in the candidates AND in the
printed rejections — the same discipline the قري collision forced in v10.

STEP 3'S RULE, STATED SO IT CAN LOSE. Riba-likeness = the financier's carried position
is DECOUPLED from the realised outcome of the underlying asset. Prediction:
coupling(musharakah) > coupling(murabahah), since musharakah is an equity partnership
where the financier is said to share asset risk. Refuted if musharakah's financier
position turns out to be a fixed schedule too.

IT WAS REFUTED. In 6 of 10 supplied musharakah accounts the bank's position steps by a
flat −1500 every month regardless of what the asset does — zero variance, a fixed
ladder. In the 4 where it varies, rho(Δasset, Δbank) = −0.142, −0.145, +0.178, +0.161:
near zero and INCONSISTENT IN SIGN. Murabahah's panel has no asset market-value column
at all. So the contract labelled risk-sharing is not measurably more coupled than the
cost-plus debt contract.

R5 MATTERS AS MUCH AS R4. A zero-variance series has no correlation with anything. Those
6 accounts are counted as fixed ladders and NO rho is reported for them — nan is not a
small number, and averaging it in would have manufactured a result.

R4 IS ABOUT REPORTING, NOT WINNING. It passes because the refutation is stated, not
because the prediction survived. A gate that only passed on success would make every
future run an advertisement.

TWO THINGS THIS EMPHATICALLY DOES NOT SHOW — both weight:excluded.
  R6  A surviving rule would NOT have validated the metaphor. Many schemas generate the
      same rule; the metaphor gains nothing downstream, and would have gained nothing
      even if every prediction had held. Steps 2 and 3 cannot inherit credibility from
      step 4.
  R7  The FAILING rule does not refute the Qur'anic text. Three candidates remain and
      this run cannot separate them: the schema is wrong, OR the rule is a poor
      operationalisation of it, OR the supplied schedules are not what their labels say.
      It does not get to pick the flattering one.

PROVENANCE, STATED PLAINLY. The manifests say these panels were "supplied for audit".
They do NOT say the data is real-world; I did not collect it and cannot verify its
origin. Every sentence above is about THESE SUPPLIED SCHEDULES, not about musharakah as
practised anywhere. A flat monthly step may be a modelling simplification by whoever
wrote the file.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "0937cf450ce157ff0b971bcb23916712f3efc504a15c7a3c2da11ccdb49aaada"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "riba.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_riba.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_is_locked():
    s = json.load(open(os.path.join(HERE, "prereg", "riba_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_STEP1_the_text_supplies_its_own_metaphor():
    r = _r()
    assert "R1_THE_TEXT_SUPPLIES_ITS_OWN_METAPHOR" not in r["gates_not_met"]
    s = r["step1_text"]
    for tok in ("يتخبطه", "الشيطان", "المس"):
        assert tok in s["metaphor_tokens"]
    assert "البيع" in s["contrast_tokens"]
    assert len(s["two_ledger_tokens"]) >= 3, "30:39's diverging ledgers"


def test_the_riba_homograph_is_rejected_by_hand():
    r = _r()
    assert "R2_THE_HOMOGRAPH_IS_REJECTED_BY_HAND" not in r["gates_not_met"]
    assert "6:164" in r["step1_text"]["rejected_homograph"]
    assert "6:164" not in r["step1_text"]["riba_ayahs_accepted"]
    assert "ر-ب-ب" in r["step1_text"]["rejected_homograph"]["6:164"]


def test_the_rule_was_stated_so_it_COULD_come_out_backwards():
    r = _r()
    d = _gate("R3_THE_SCHEMA_GENERATES_A_RULE_THAT_COULD_COME_OUT_BACKWARDS")["detail"]
    assert "It is REFUTED IF" in d
    assert "before the result is reported" in d


def test_PRIMARY_the_prediction_was_REFUTED_and_the_run_says_so():
    r = _r()
    s = r["step4"]
    assert s["verdict"] == "REFUTED"
    assert s["musharakah"]["fixed_ladder"] == 6
    assert s["musharakah"]["n_accounts"] == 10
    assert s["murabahah_has_asset_value_column"] is False
    d = _gate("R4_PRIMARY_THE_PREDICTION_IS_TESTED_AND_THE_RESULT_REPORTED_EITHER_WAY")["detail"]
    assert "INCONSISTENT IN SIGN" in d
    assert "about REPORTING, not winning" in d


def test_the_four_varying_accounts_have_near_zero_inconsistent_correlation():
    rhos = _r()["step4"]["musharakah"]["rhos"]
    assert len(rhos) == 4
    assert min(rhos) < 0 < max(rhos), "signs disagree, so there is no coupling direction"
    assert all(abs(x) < 0.25 for x in rhos)


def test_a_fixed_ladder_reports_NO_correlation_because_nan_is_not_a_small_number():
    r = _r()
    assert "R5_A_FIXED_LADDER_IS_IDENTIFIED_AS_SUCH" not in r["gates_not_met"]
    for a in r["step4"]["musharakah"]["accounts"]:
        if not a["financier_varies"]:
            assert a["rho_delta"] is None
    assert "nan is not a small number" in \
        _gate("R5_A_FIXED_LADDER_IS_IDENTIFIED_AS_SUCH")["detail"]


def test_a_surviving_rule_would_NOT_have_validated_the_metaphor():
    g = _gate("R6_does_a_SURVIVING_rule_validate_the_metaphor")
    assert g["weight"] == "excluded"
    assert "would have gained nothing even if every prediction had held" in g["detail"]


def test_the_failing_rule_does_NOT_refute_the_text():
    g = _gate("R7_does_a_FAILING_rule_refute_the_Quranic_text")
    assert g["weight"] == "excluded"
    assert "cannot distinguish those three" in g["detail"]
    assert "does not get to pick the flattering" in g["detail"]


def test_the_schema_is_labelled_as_a_reading_not_a_result():
    s = _r()["step2_schema"]
    assert "NOT MEASURED AND NOT MEASURABLE" in s["layer"]
    assert "can still evaluate Step 3" in s["THE_FIREWALL"]


def test_provenance_of_the_panels_is_not_overstated():
    p = _r()["provenance_caveat"]
    assert "do NOT say the data is real-world" in p
    assert "not about musharakah as practised anywhere" in p


def test_score_is_five_of_five_and_nothing_simulated():
    r = _r()
    assert r["score"] == "5/5" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0
