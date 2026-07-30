"""
test_three.py — locks the three-proposal comparison: 4/5, and the one that failed is the
one that matters most.

THE SETUP. Three named positions on what Islamic banking should be, put on one engine with
one committed event sequence, plus a required control:

  irfan        100% full reserve, every claim a participation note (extinguishes on loss)
  alqudah_m3   asset-backed + diminishing co-ownership on the FRACTIONAL substrate the
               position accepts as regulatory reality
  alqudah_m1   the SAME contracts at full reserve — separates contract from substrate
  tworegister  full reserve, fixed 25/75 containment/recovery mix, no routing model

THE RESULT

  distribution OFF          shortfall   secondary
    irfan                      4103.2         135
    alqudah_m3                 6621.6         616
    alqudah_m1                 3321.2         166
    tworegister                2983.7         177

  distribution ON
    irfan                       128.3         123
    alqudah_m3                  237.0         672
    alqudah_m1                   88.5         142
    tworegister                  96.7         151

B4 FAILED, AND IT WAS PREDICTED TO. The spread between best and worst arm collapses from
3,637.8 to 148.5 once continuous distribution is switched on everywhere — only 4.1%
survives. **A payment-timing rule that none of the three positions argues about dominates
the dispute between them.** This is uncomfortable for all three, and it is the reason B4
was made primary rather than a footnote.

AND OUR OWN ARM LOSES ONCE DISTRIBUTION IS ON. With it enabled, alqudah_m1 scores 88.5
against tworegister's 96.7. Our arm wins B2 only in the distribution-OFF comparison, and
by a modest margin over the same contracts at full reserve (2,983.7 vs 3,321.2). That is
reported here rather than omitted.

WHAT PASSED
  B1  the substrate difference is real, not nominal: the fractional arm carries 1,585.9 of
      unbacked claims while all three full-reserve arms carry exactly 0.0.
  B3  Irfan's all-participation arm records the FEWEST cascades (135). The contagion-control
      finding therefore generalises to an architecture that is not ours — full
      extinguishment stops propagation best, on someone else's design.
  B5  the practitioner critique is correct on measurement. IDENTICAL contracts score 6,621.6
      at m=3 against 3,321.2 at m=1 — a 1.99x penalty attributable to the substrate alone,
      with the contract design held fixed. The label was never the problem; the substrate was.

WHAT THIS CANNOT SETTLE. Nothing here adjudicates a jurisprudential question. An arm
scoring better on settlement outcomes is not thereby permissible, and one scoring worse is
not thereby impermissible. The spec says so and so does the README.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "0b2328c54836ec5281c54e4c1ff0afdb6a779172a51975ed5703d020a13c6402"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "three.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_three.json")))


def test_spec_locked_and_controls_the_confound_in_advance():
    spec = json.load(open(os.path.join(HERE, "prereg", "three_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    c = spec["the_confound_that_would_wreck_this_test_if_left_alone"]
    assert "INDEPENDENT FACTOR" in c
    assert "guarantee our arm wins" in c, "the spec had to name the confound as ours"
    assert "EXPECTED TO FAIL" in spec["predictions_recorded_in_advance"]["B4"]
    # the previous run's objective mistake must not be repeated
    assert "NO COMBINED OBJECTIVE" in spec["the_two_objective_trap_closed_again"]
    assert "TENTH appearance" in spec["the_simulation_trap_being_avoided_again"]
    # and the test must disclaim jurisprudential authority
    assert "not thereby permissible" in spec["what_this_test_cannot_settle"]


def test_all_four_arms_ran_on_the_same_committed_sequence():
    r = _r()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["n_events"] == 10000
    assert r["arms"] == ["irfan", "alqudah_m3", "alqudah_m1", "tworegister"]


def test_the_substrate_difference_is_real_not_nominal():
    """B1: full reserve means full reserve; the constrained arm genuinely creates claims."""
    r = _r()
    off = r["distribution_off"]
    for a in ("irfan", "alqudah_m1", "tworegister"):
        assert off[a]["unbacked"] < 1e-6
    assert off["alqudah_m3"]["unbacked"] > 1000


def test_the_practitioner_critique_holds_on_measurement():
    """B5: identical contracts, different substrate — the substrate costs 2x."""
    r = _r()
    off = r["distribution_off"]
    assert off["alqudah_m3"]["shortfall"] > off["alqudah_m1"]["shortfall"]
    assert r["alqudah_substrate_ratio"] > 1.9, \
        "the same contracts are ~2x worse on the fractional substrate"


def test_full_extinguishment_stops_cascade_best_on_someone_elses_architecture():
    """B3: the contagion-control finding generalises beyond our own design."""
    r = _r()
    assert r["fewest_cascades_arm"] == "irfan"
    off = r["distribution_off"]
    assert off["irfan"]["secondary"] < off["tworegister"]["secondary"]
    assert off["irfan"]["secondary"] < off["alqudah_m1"]["secondary"]


def test_the_doctrinal_spread_collapses_under_a_payment_timing_rule():
    """B4, the primary gate, failed as predicted. This is the headline."""
    r = _r()
    assert "B4_DOES_THE_DOCTRINAL_DIFFERENCE_SURVIVE_CONTINUOUS_DISTRIBUTION" \
        in r["gates_not_met"]
    assert r["spread_retained"] < 0.10, \
        "under 10% of the three-way difference survives continuous distribution"
    assert r["spread_off"] > 3000 and r["spread_on"] < 200


def test_our_own_arm_loses_once_distribution_is_switched_on():
    """Reported, not omitted: tworegister is beaten by the same contracts at full reserve."""
    r = _r()
    on = r["distribution_on"]
    assert on["alqudah_m1"]["shortfall"] < on["tworegister"]["shortfall"], \
        "with distribution on, Al-Qudah's contracts at full reserve beat our arm"
    off = r["distribution_off"]
    # and our B2 win is by a modest margin over the same comparator
    margin = off["alqudah_m1"]["shortfall"] / off["tworegister"]["shortfall"]
    assert 1.0 < margin < 1.25, "the distribution-OFF win is modest, not decisive"


def test_the_score_is_four_of_five_and_the_failure_is_the_primary_gate():
    r = _r()
    assert r["score"] == "4/5"
    assert r["gates_not_met"] == [
        "B4_DOES_THE_DOCTRINAL_DIFFERENCE_SURVIVE_CONTINUOUS_DISTRIBUTION"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
    assert len([g for g in r["gates"] if g["weight"] == "excluded"]) == 2
