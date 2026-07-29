"""
test_tailrisk.py — locks the tail-risk result: 2/5, and the "wrong game" reframe loses
on the two parts that were checkable against this programme's own committed code.

THE ARGUMENT TESTED. The settlement mesh is not failing, the test suite is measuring the
wrong game: (1) the centralised arm posts zero routine failures ONLY because it creates
credit; (2) that is why full-reserve pooling was priced at 17-18% and not 90%; (3) the
centre is at single-point dependence 1.0000 and would melt down, while the mesh at k=2 is
"immune (blast quarantined)" at 0.0100.

WHAT THE ENGINE RETURNED

  C1 FAILED — THE CREDIT-CREATION EXPLANATION IS REFUTED.
      Centralised arm unbacked claims = 0.0. It is FULL RESERVE: it moves value from
      issuer to centre and never lends beyond it. Its zero routine failures were bought
      with POOLING, not with credit creation. One book meets obligations no single node
      could. This was predicted to fail in the spec, and it did.

  C2 FAILED — AND IT FAILED IN THE OPPOSITE DIRECTION TO THE PREDICTION.
      Leverage was expected to buy smoothness. Measured routine failures:
          m=1 (full reserve)     0
          m=3                 3262
          m=5                 3912
          m=10                4362      vs the full-reserve mesh's 2548
      Creating credit made settlement STRICTLY WORSE, monotonically in m, because the
      claims it manufactures still have to be paid. Full reserve was the smoothest
      configuration tested. "Fabricating liquidity is what produces smoothness" is not
      merely unsupported here — it is backwards.

  C3 PASSED. Losing half its value mid-flight, the centre cannot pay 100% of what it owes.

  C4 PASSED ON THE PRE-REGISTERED METRIC, AND THE PASS IS AN ARTEFACT. See below.

  C5 FAILED DECISIVELY. Combined ledger at the headline freeze: mesh 3,109 routine + 147
      tail = 3,256; central 71 + 2 = 73. There is NO strike point and NO freeze level in
      the whole 18-cell sweep where the mesh's combined ledger wins. The tail event never
      repays the routine premium.

  The "immune" claim FAILED as stated: mesh unmet fraction 0.5000, not below 0.05. Blast
  radius measures WHERE a failure starts, not how much value survives it.

THE C4 ARTEFACT, DISCLOSED AND NOT RE-SCORED. The gate turns on a FRACTION of outstanding
obligations. The two arms do not carry comparable books: the centre clears continuously
and holds 21.9 outstanding, while the mesh accumulates bilateral obligations and holds
4,345. So "mesh 50% unmet vs central 100% unmet" describes the mesh losing 2,172.5 units
against the centre's 21.9 — 99x MORE actual value from the same proportional shock. The
pre-registered threshold was NOT moved and the gate is NOT re-scored, but on the quantity
a creditor cares about this gate points the other way, and that is recorded in the source,
the results JSON and here.

THREE DISCLOSED HARNESS CORRECTIONS, none of which converted a mechanism failure into a
pass. (1) The freeze was first sized against the INITIAL base; after the replay drains the
system that removed 100% of everything left, and every level returned a meaningless 1.000.
(2) The strike first landed AFTER the whole replay, when the centralised book had cleared
to 0.0 — an empty book cannot be stressed. (3) Issuance ran once at seeding, so the centre
still carried nothing at strike time. Each fix was forced by a degenerate measurement, not
by a disliked answer: the mesh lost C5 before and after all three. Gate C6 was then turned
into a structural NON-EMPTY BOOK GUARD so the degeneracy cannot silently recur — and it
still FAILS, honestly reporting that the centralised book is empty at the 0.75 strike.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "bf5a27f012d2c926489e136b0fe5f24df968ee558e4e43e63ce555a8e0dedd4b"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "tailrisk.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_tailrisk.json")))


def test_spec_locked_and_names_the_seventh_simulation_refusal():
    spec = json.load(open(os.path.join(HERE, "prereg", "tailrisk_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    trap = spec["the_simulation_trap_being_avoided_again"]
    assert "SEVENTH appearance" in trap
    assert "test_catastrophic_center_meltdown.py" in trap
    # the spec had to predict C1's failure BEFORE the run to get credit for it
    assert "EXPECTED TO FAIL" in spec["predictions_recorded_in_advance"]["C1"]
    assert "anti_immunisation_clause" in spec


def test_it_runs_on_the_committed_real_shock_source():
    r = _r()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["n_shocks"] == 4886


def test_the_credit_creation_explanation_is_refuted():
    """C1: the central comparator is full reserve. It wins by pooling, not by dU > 0."""
    r = _r()
    assert "C1_the_centralised_arm_creates_credit" in r["gates_not_met"]
    assert r["central_unbacked"] == 0.0
    assert r["mesh_unbacked"] < 1e-6
    assert r["central_routine_failed"] == 0 and r["mesh_routine_failed"] == 2548


def test_leverage_made_settlement_worse_not_better():
    """C2 failed in the OPPOSITE direction to the prediction — monotonically in m."""
    r = _r()
    assert "C2_credit_creation_is_what_buys_smoothness" in r["gates_not_met"]
    lev = {int(k): v["failed"] for k, v in r["leverage_sweep"].items()}
    assert lev[1] == 0, "full reserve was the smoothest configuration tested"
    assert lev[3] < lev[5] < lev[10], "more leverage, strictly more failures"
    assert lev[5] > r["mesh_routine_failed"], "leverage is worse than the full-reserve mesh"


def test_the_mesh_is_not_immune_and_the_c4_pass_inverts_on_absolute_value():
    r = _r()
    assert r["mesh_is_immune"] is False
    assert r["mesh_unmet_fraction"] > 0.05, "the 'immune' claim fails as stated"
    # the pass is real on the locked metric...
    assert r["mesh_unmet_fraction"] <= 0.5 * r["central_unmet_fraction"] + 1e-9
    # ...and inverts by two orders of magnitude on the quantity that matters
    assert r["absolute_value_ratio_mesh_over_central"] > 50.0
    assert r["metric_confound_disclosed"].startswith("C4 passes")


def test_the_tail_event_never_repays_the_routine_premium():
    """C5 is the whole question, and the answer is no — at every cell in the sweep."""
    r = _r()
    assert "C5_the_mesh_wins_on_the_COMBINED_ledger" in r["gates_not_met"]
    assert r["mesh_combined"] > r["central_combined"]
    assert r["freeze_levels_where_mesh_wins_combined"] == [], \
        "no strike point and no freeze level in the 18-cell sweep favours the mesh"


def test_the_non_empty_book_guard_reports_its_own_limitation():
    """C6 is excluded from the score precisely so it can report bad news honestly."""
    r = _r()
    guard = r["non_empty_book_guard"]
    assert guard["central"] == 0.0, \
        "the guard must keep reporting that the centralised book empties at some strikes"
    assert guard["mesh"] > 0 and guard["fractional_m5"] > 0
    c6 = [g for g in r["gates"] if g["gate"].startswith("C6")][0]
    assert c6["pass"] is False and c6["weight"] == "excluded"


def test_the_score_is_two_of_five_and_is_not_inflated():
    r = _r()
    assert r["score"] == "2/5"
    assert len(r["gates_not_met"]) == 3
    full = [g for g in r["gates"] if g["weight"] == "full"]
    excluded = [g for g in r["gates"] if g["weight"] == "excluded"]
    assert len(full) == 5 and len(excluded) == 3
