"""
test_stewardship.py — locks the first banking design that mostly worked, and the
pre-registered prediction of mine that was WRONG.

Result: 4/5 scored gates (SC1 and SC6 excluded — they cannot fail).

  SC4 FAILED — and it was MY prediction that failed, not the design's. I pre-registered
      that risk-sharing would cost the institution capital. It did the opposite:
      equity -361,440 vs debt -430,640. The reason is economic, not a coding artifact:
      a priority claim is only worth having if the asset can actually be recovered. At
      phi=0.40 the lender still eats 600 per failure AND gives up all upside, while
      proportional participation captures the 20% gain on every survivor.

  SC7 PASSED — tau_v earned a narrow, real second life. It failed as an ADMISSION SCREEN
      (four times). As a MONITORING COVENANT it made money: +42,840 over hold-everything,
      while paying a full 30% haircut on all 204 exits including 17 false positives.
      Screening and monitoring are different problems and the same signal can lose one
      and win the other.

  SC5 PASSED — a full-reserve risk-sharing institution retained 59.5% of capital over a
      75.6%-default population. It survives; it is not unscathed.

This suite exists so none of that can drift — in either direction. It asserts the
failure stands AND that the successes are not overstated beyond the declared substrate.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "8bac3099bb472b40bb51300ff287d177f8a1e8f2f60b5e8c825ca31d3c05e773"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "stewardship_test.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_stewardship.json")))


def test_spec_locked_and_still_names_its_own_hazards():
    spec = json.load(open(os.path.join(HERE, "prereg", "stewardship_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    # the retreat from selection must stay explicitly guarded against
    h = spec["the_immunisation_hazard_again"]
    assert "makes the framework unfalsifiable" in h
    assert "conceded explicitly and mechanically" in h
    # the substrate limitation must stay in the spec, not be discovered later
    lim = spec["data"]["declared_substrate_limitation"]
    assert "poor analogue" in lim and "NOT a claim about credit markets" in lim


def test_selection_really_is_held_fixed():
    """The whole result is meaningless if a selection advantage leaked back in."""
    r = _r()
    rec = json.load(open(os.path.join(ROOT, "cohort-audit", "results_992_recovery.json")))
    assert r["csv_sha256"] == rec["csv_sha256"]
    assert r["N"] == 992 and r["defaults"] == 750
    sc1 = [g for g in r["gates"] if g["gate"].startswith("SC1")][0]
    assert sc1["weight"] == "excluded", "an honesty gate must not inflate the score"


def test_my_own_prediction_failed_and_stays_failed():
    """SC4 is the author's pre-registered prediction. It was wrong. Keep it wrong."""
    r = _r()
    assert r["gates_not_met"] == ["SC4_risk_sharing_costs_the_institution_capital"]
    assert r["equity_institution_pnl"] > r["debt_institution_pnl"], \
        "equity outperformed debt; the predicted cost did not materialise"
    assert abs(r["equity_institution_pnl"] - (-361440)) < 1
    assert abs(r["debt_institution_pnl"] - (-430640)) < 1


def test_the_posthoc_sweep_is_labelled_and_never_scored():
    """The recovery sweep was written AFTER seeing SC4 fail. It explains; it cannot confirm."""
    r = _r()
    assert "posthoc_recovery_sweep_NOT_A_GATE" in r
    sweep = r["posthoc_recovery_sweep_NOT_A_GATE"]
    assert len(sweep) == 5
    # it must not have been quietly promoted into the gate list
    assert all(not g["gate"].lower().startswith("posthoc") for g in r["gates"])
    # and it must show the honest boundary: equity wins across the whole scanned range
    assert all(s["debt_wins"] is False for s in sweep), \
        "if this ever flips, the SC4 explanation must be rewritten, not the gate"


def test_the_borrower_side_gains_are_real_but_correctly_weighted():
    r = _r()
    assert r["borrower_stdev_equity"] < r["borrower_stdev_debt"]
    assert (r["borrower_stdev_debt"] / r["borrower_stdev_equity"]) > 10
    # no-recourse caps the worst case at the stake
    assert r["borrower_worst_equity"] == -60.0
    assert r["borrower_worst_debt"] < -700
    sc3 = [g for g in r["gates"] if g["gate"].startswith("SC3")][0]
    assert sc3["weight"] == "supporting", \
        "no-recourse is definitional; it cannot count as independent confirmation"


def test_solvency_is_reported_without_rounding_up():
    r = _r()
    assert r["equity_terminal_capital"] > 0
    assert 0.55 < r["capital_retained_fraction"] < 0.65, \
        "59.5% retained — solvent, not unscathed; do not restate this as robustness"


def test_tau_v_works_as_a_covenant_and_the_cost_stays_visible():
    """The signal's second life is real, and its false positives are part of the record."""
    r = _r()
    assert r["covenant_pnl"] > r["equity_institution_pnl"]
    assert r["covenant_exits"] == 204
    assert r["covenant_false_positive_exits"] == 17, \
        "the exits charged on non-defaulters must stay in the reported result"


def test_full_reserve_leverage_scan_is_correct_and_excluded():
    r = _r()
    sc6 = [g for g in r["gates"] if g["gate"].startswith("SC6")][0]
    assert sc6["weight"] == "excluded", "definitional; never scored"
    scan = {s["multiplier"]: s["depositor_shortfall"] for s in r["leverage_scan"]}
    # m=1 IS full reserve: no depositor funds the book, so none can be short
    assert scan[1.0] == 0
    # and shortfall must GROW with leverage (the earlier inverted model was a bug)
    order = [s["depositor_shortfall"] for s in r["leverage_scan"]]
    assert order == sorted(order), "depositor shortfall must be monotone in leverage"
    assert r["first_insolvent_multiplier"] == 3.0
