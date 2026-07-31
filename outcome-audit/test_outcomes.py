"""
test_outcomes.py — locks the outcome-panel audit: 2/5.

CREDIT FIRST, AND IT IS REAL. The earlier audit (02e6bbba) found three contract SCHEDULES
could not discriminate risk-sharing from debt because they contained no adverse event, and
named the remedy: asset values marked over time, arrears, write-downs, defaults, recovery.
These panels contain ALL FIVE. O1 passes. That is a genuine advance and it is recorded.

THE CLAIM TESTED. It was put to this programme that MSH-2026-007 is "mathematical proof of
loss absorption" because Write_Down_Loss 315,775.0 exactly equals the fall in the bank's
balance from 371,500.0 to 55,725.0, and that this is the Gate A6 divergence.

THE ARITHMETIC IS CORRECT AND IS NOT DISPUTED. 371,500.0 - 55,725.0 = 315,775.0 exactly.
What it does not establish is what A6 tested: whether the financier's position falls WITH
THE ASSET.

  O2 FAILED, PRIMARY. Across all 5 write-down events the bank's balance falls -85.0% every
     time, while the asset moves -1.10%, +1.61%, -0.37%, +0.90%, +0.18%. Median ratio of
     financier loss to asset loss is 94.9 against a declared band of 3. IN 3 OF 5 EVENTS
     THE ASSET ROSE WHILE THE FINANCIER WROTE DOWN. Over the whole episode the asset gains
     +1.20% while the bank goes from 371,500 to 28.21.

  O3 FAILED. The customer balance changes by exactly 0.00 in all five write-down months.
     The co-owner's stake is untouched while the financier absorbs 100% of the loss.
     Proportional co-ownership impairs BOTH owners by their shares; bearing the entire
     loss is a guarantee structure, not musharakah proportionality.

  O4 PASSED ONLY ON A ROUNDING ARTEFACT, DISCLOSED AS MARGINAL. Locked threshold sd < 1e-6;
     measured 1.03e-6, above it by 3%. The CSV stores balances to 2 decimal places and that
     rounding is the entire source of the variation -- the successive ratios are identical
     to 4dp (0.1500 0.1500 0.1500 0.1500). The balance is multiplied by a fixed 0.15 every
     period. Threshold NOT moved, gate NOT re-scored, marginality recorded.

  O5 FAILED. Five accounts carry an identical status label in month 1 and month 24 despite
     the adverse event occurring mid-life: MSH-2026-007 is "Written-off" from month 1 though
     the write-down begins in month 20; MSH-2026-005 is "Default (90d+)" from month 1 though
     the flag flips in month 15. LABEL LEAKAGE -- the outcome is already in the row, so the
     panel cannot be used to predict outcomes from state.

  O6 FAILED (excluded). Both arrears series accumulate by an exactly constant amount every
     month, second-difference sd 0.00e+00. Arithmetic sequences, not recorded arrears.

WHAT THIS DOES AND DOES NOT MEAN. It does NOT mean the contracts are debt, and it does NOT
mean the panels are worthless -- panels recording impairment policy are useful for testing
provisioning behaviour, cascade timing and recovery. It means these panels cannot settle the
risk-sharing question either, for a MORE SPECIFIC reason than the schedules: the schedules
lacked events; these contain events whose magnitude is set by policy rather than by the asset.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "caacef8454a34242164a7228befe79305a466981d72e16791fa21d0b09559588"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "audit_outcomes.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_outcomes.json")))


def test_spec_locked_and_declined_the_confirmation_script():
    spec = json.load(open(os.path.join(HERE, "prereg", "outcome_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    assert "will confirm it" in spec["why_a_confirmation_script_was_declined"]
    assert "THIRTEENTH appearance" in spec["the_simulation_trap_being_avoided_again"]
    # the spec had to concede the arithmetic before testing it
    assert "IS NOT IN DISPUTE" in spec["the_claim_actually_under_test"]
    for g in ("O2", "O3", "O4", "O5"):
        assert "EXPECTED TO FAIL" in spec["predictions_recorded_in_advance"][g]


def test_the_panels_do_contain_the_five_remedies():
    """O1: credit where it is due, and it is due."""
    r = _r()
    assert all(r["five_remedies_present"].values())
    assert "O1_the_panels_contain_the_five_named_outcome_types" not in r["gates_not_met"]
    assert r["rows"] == {"musharakah": 240, "ijarah": 240, "murabahah": 240}


def test_the_supplied_arithmetic_is_conceded_exactly():
    """371,500.0 - 55,725.0 = 315,775.0. Not in dispute."""
    assert abs((371500.0 - 55725.0) - 315775.0) < 1e-9


def test_write_downs_do_not_track_the_asset():
    """O2, the primary gate — and the reason the supplied arithmetic doesn't settle A6."""
    r = _r()
    assert "O2_WRITE_DOWNS_TRACK_THE_ASSET_VALUE" in r["gates_not_met"]
    assert r["median_loss_to_asset_ratio"] > 50, "median ratio 94.9 against a band of 3"
    assert r["n_events_where_asset_rose"] == 3 and r["n_write_down_events"] == 5
    for e in r["write_down_events"]:
        assert abs(e["bank_pct"] + 85.0) < 1e-3, \
            "every event is a flat -85% (to CSV rounding precision)"
        assert abs(e["asset_pct"]) < 2.0, "while the asset moves under 2%"


def test_the_customer_stake_never_moves():
    """O3: 100% of the loss on one side is a guarantee, not proportional co-ownership."""
    r = _r()
    assert "O3_the_customer_stake_moves_when_the_financier_stake_does" in r["gates_not_met"]
    assert r["customer_balance_moved_in_n_events"] == 0


def test_the_decay_is_a_fixed_factor_and_the_pass_is_disclosed_as_marginal():
    """O4 passes on the locked threshold by 3%; the ratios are identical to 4dp."""
    r = _r()
    assert "O4_write_downs_are_not_a_closed_form_decay" not in r["gates_not_met"]
    assert r["decay_identical_to_4dp"] == ["MSH-2026-007"]
    assert "rounding artefact" in r["o4_marginal_pass_disclosed"]
    ratios = r["decay_ratios"]["MSH-2026-007"]["ratios"]
    assert all(abs(x - 0.15) < 1e-4 for x in ratios), "a fixed 0.15 multiplier every period"


def test_outcome_labels_are_stamped_from_row_one():
    """O5: label leakage across all three contract types."""
    r = _r()
    assert "O5_outcome_labels_are_DERIVED_from_state_not_stamped_in_advance" \
        in r["gates_not_met"]
    assert set(r["label_leakage_accounts"]) == {
        "MSH-2026-007", "IJR-2026-005", "IJR-2026-007", "MRB-2026-003", "MRB-2026-007"}


def test_arrears_are_arithmetic_sequences():
    r = _r()
    assert r["perfectly_linear_arrears"] == ["MSH-2026-003", "MSH-2026-005"]


def test_the_score_is_two_of_five():
    r = _r()
    assert r["score"] == "2/5"
    assert sorted(r["gates_not_met"]) == sorted([
        "O2_WRITE_DOWNS_TRACK_THE_ASSET_VALUE",
        "O3_the_customer_stake_moves_when_the_financier_stake_does",
        "O5_outcome_labels_are_DERIVED_from_state_not_stamped_in_advance"])
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
