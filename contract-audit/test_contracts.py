"""
test_contracts.py — locks the contract audit: 3/6. The datasets cannot audit the claim
they were supplied to audit, and the reason is specific and fixable.

THE PRIOR QUESTION. Al-Qudah's position was previously modelled from a written
description because no contract data existed. Three schedules were supplied. This audit
asks whether they can DISCRIMINATE the claim that separates these contracts from debt --
not whether they perform well.

WHAT WAS FOUND

  A1 PASS   all 20 rows reconcile to within 0.01 USD. The schedules are clean arithmetic.

  A2 PASS, and it is a SURPRISE that cuts AGAINST the usual critique.
            flat markup      10.00 10.00 10.00 10.00 10.00   (sd 0.0000)
            implied annual   10.0  20.0  10.0  40.0  20.0    (sd 10.9545)
            A constant-rate loan in disguise would hold the ANNUALISED rate fixed and
            vary the flat markup. This schedule does the opposite: the trade margin is
            flat and the implied annual rate swings 4x with tenor. That is what a price
            that does NOT price time looks like. The gate scores no verdict either way,
            and the finding is recorded because it runs against the expected direction.

  A3 FAIL   the bank holds legal title in all 5 periods while the lessee pays every
            maintenance charge -- 3,000 USD billed into the lessee's payment. The
            ownership BURDEN moved; the ownership RISK did not.

  A4 FAIL   the musharakah property value has standard deviation 0.0000 across 10 months.
            IT NEVER MOVES. A co-ownership schedule with a constant asset value cannot
            exhibit co-ownership risk, because no event occurs for the co-owner to share in.

  A5 FAIL   PRIMARY. All three schedules are CASH-FLOW IDENTICAL to their matched debt
            twins -- maximum per-period difference 0.003 USD against a 0.01 tolerance. The
            musharakah rental is exactly 0.6250% per month of the financier's outstanding
            stake in every period, which is the definition of a declining-balance interest
            schedule.

  A6 PASS   and this is the constructive half. Apply the pre-declared 25% value fall and
            the positions separate immediately: co-owner 120,000 against lender 160,000,
            maximum divergence 40,000 USD.

WHAT THIS DOES AND DOES NOT MEAN. It does NOT show these contracts are debt -- A6 shows
the contracts genuinely differ the moment an adverse event occurs. It shows THE SUPPLIED
DATA CANNOT TELL THE DIFFERENCE, because it contains no such event. The remedy is a
different dataset, not a different contract: one with realised outcomes -- value
movements, arrears, early settlements, defaults, write-downs -- rather than a planned
schedule.

N = 5, 5, 10. Contract SCHEDULES, not outcome records. No statistical inference is
licensed and none is emitted. Declared in the spec before the files were analysed.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "02e6bbba5bdbe31ec6fd9d888399b39b6ee91bf75ca6d9bc8ae5d768e534fed0"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "audit_contracts.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_contracts.json")))


def test_spec_locked_and_declares_its_limits_before_analysis():
    spec = json.load(open(os.path.join(HERE, "prereg", "contract_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    d = spec["sample_size_declaration_made_before_looking"]
    assert "No statistical inference" in d and "CONTRACT SCHEDULES" in d
    assert "EXPECTED TO FAIL" in spec["predictions_recorded_in_advance"]["A5"]
    assert "TWELFTH appearance" in spec["the_simulation_trap_being_avoided_again"]
    # the clause must cut BOTH ways
    ai = spec["anti_immunisation_clause"]
    assert "may not be inflated" in ai and "disguised debt" in ai


def test_all_twenty_rows_are_used_and_hash_pinned():
    r = _r()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["n_rows"] == {"murabahah": 5, "ijarah": 5, "musharakah": 10}


def test_the_schedules_are_clean_arithmetic():
    r = _r()
    assert "A1_the_schedules_are_internally_consistent" not in r["gates_not_met"]


def test_the_murabahah_markup_does_not_price_time():
    """A2 cuts AGAINST the disguised-interest reading — recorded because it surprised us."""
    r = _r()
    assert r["murabahah_flat_sd"] < 1e-9, "flat markup is constant at 10%"
    assert r["murabahah_annualised_sd"] > 5.0, "implied annual rate swings with tenor"
    assert max(r["murabahah_implied_annualised_pct"]) == 40.0
    assert min(r["murabahah_implied_annualised_pct"]) == 10.0
    assert r["markup_prices_time_not_rate"] is True


def test_the_lease_moves_the_burden_but_not_the_risk():
    r = _r()
    assert "A3_the_ijarah_places_ownership_risk_with_the_owner" in r["gates_not_met"]
    assert r["ijarah_legal_owners"] == ["Bank"]
    assert r["ijarah_maintenance_billed_to_lessee"] is True


def test_the_asset_value_never_moves():
    """A4: the single most important property of the data."""
    r = _r()
    assert "A4_the_musharakah_asset_value_moves" in r["gates_not_met"]
    assert r["musharakah_value_sd"] == 0.0
    assert r["musharakah_value_moves"] is False


def test_no_dataset_can_distinguish_risk_sharing_from_debt():
    """A5, the primary gate. A fact about the data, not about the contracts."""
    r = _r()
    assert "A5_ANY_DATASET_CAN_DISTINGUISH_RISK_SHARING_FROM_DEBT" in r["gates_not_met"]
    assert r["any_dataset_discriminates"] is False
    for k, v in r["debt_twin_max_diff"].items():
        assert v <= 0.01, "%s is cash-flow identical to its debt twin" % k
    # the musharakah rental is a constant rate on the outstanding stake
    assert abs(r["musharakah_implied_monthly_rate_pct"] - 0.625) < 1e-6


def test_an_adverse_event_separates_them_immediately():
    """A6: the contracts DO differ — the data just never records the moment."""
    r = _r()
    assert "A6_the_adverse_event_separates_them" not in r["gates_not_met"]
    assert r["shock_separation_usd"] > 1000, \
        "under a 25% fall the co-owner and the lender diverge by 40,000 USD"


def test_the_score_is_three_of_six_and_emits_no_statistics():
    r = _r()
    assert r["score"] == "3/6"
    assert len(r["gates_not_met"]) == 3
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
    # scope the check to the DATA keys, not the prose: the disclaimers legitimately
    # contain the words "p-value" and "confidence interval" while denying making one
    data_keys = {k for k in r if k not in ("gates", "gates_not_met")}
    blob = json.dumps({k: r[k] for k in data_keys}).lower()
    for banned in ("p_value", "pvalue", "confidence_interval", "ci_low", "ci_high",
                   "significant", "z_score", "t_stat"):
        assert banned not in blob, \
            "N = 5, 5, 10 licenses no statistical claim — found %r" % banned
