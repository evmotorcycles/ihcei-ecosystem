"""
test_network.py -- locks the interbank 2016Q1->Q2 result: 3/5.

WHAT THIS IS. A directed, weighted interbank exposure network, 4,548 institutions, two
consecutive quarters of 2016, with a 74-column balance-sheet panel on the Q1 nodes. The
outcome is realised: 3,811 of 11,631 Q1 exposures are absent in Q2 and 3,812 new ones
appear. Nothing in the scored gates is simulated.

THE SIMULATION THAT WAS DECLINED, FOR THE FOURTEENTH TIME. The proposal was to re-route
the 11,631 real edges under participation mechanics, cascade both wirings, and report the
delta as the measurement. That delta is the output of the re-routing rule, and a real
topology does not make a chosen mechanism an observation. It is carried as N6 at weight
'excluded' and its own result is degenerate -- 1 default in 1 round under BOTH wirings,
because the highest-leverage node's three counterparties absorb the shock without
exhausting equity. The two rules never diverge, so even as illustration it shows nothing.
That is reported rather than repaired by re-seeding, because choosing a seed that produces
a cascade is precisely the tuning move the pre-registration exists to prevent.

THE PRIMARY GATE MISSED, AND IT MISSED AGAINST LISM.

  N3 FAILED. E = U*D_enc*D_dec scored AUC 0.6090. The symmetric quadratic rival
     E = U*D^2 scored 0.6109. THE RIVAL WON, by 0.0019. In yeast, in the GitHub cohort
     and in the 10,000-institution financial cohort the asymmetric form won. On this
     network it did not. Separating encoding distance from decoding distance bought
     nothing here, and the margin was declared at 0.02 before any AUC existed.

  N4 FAILED, as predicted in writing. LISM 0.6090 against total assets alone 0.5920, a
     gap of +0.0170 against a declared bar of 0.05. It does beat size -- it does not beat
     size by enough to matter to a supervisor.

  N5 PASSED, AGAINST THE WRITTEN PREDICTION. srisk_ratio was pre-declared as expected to
     WIN and scored 0.4921, indistinguishable from chance, against LISM's 0.5653 on the
     204-node subsample carrying 72 events. This is NOT evidence that SRISK is a poor
     measure: SRISK estimates capital shortfall under a market-wide equity crash, a
     different quantity from one-quarter interbank funding withdrawal. Recorded as a pass
     because the gate was locked, and qualified because the qualification is true.

DATA DEFECT FOUND AND DISCLOSED. The Q2 edge file carries 57 NEGATIVE exposure weights,
minimum -7,080,587; the Q1 file carries none. N1 did not test edge sign because the locked
spec did not declare it, and N1 is NOT re-scored. The labels are unaffected -- a negative
Q2 inflow satisfies the withdrawal threshold regardless of magnitude -- so every AUC
stands. The intensity figure does not: it reads 556.7 as computed, which is impossible for
a fraction lost, and the corrected figure excluding the 21 affected events is 0.908.

SCOPE. One network, one quarter transition, one banking system, 2016, node identities
unknown. 3,199 of 4,548 nodes receive no Q1 interbank exposure and are excluded by the
locked rule, so every number describes the 1,349-node funded core. Nothing here concerns
Islamic finance: no column in these files distinguishes a fixed claim from a
participation, which is recorded as N7, UNTESTABLE-HERE -- not refuted, not blocked,
invisible.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "db8c3a4f0454f9d73a97a5e03159b3525e13d62d13e7e104183940ae074b718b"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "network.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_network.json")))


def test_spec_locked_and_declined_the_reroute_simulation():
    spec = json.load(open(os.path.join(HERE, "prereg", "network_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    trap = spec["the_simulation_trap_being_avoided_again"]
    assert "FOURTEENTH" in trap["occurrence"]
    assert "output of the re-routing rule" in trap["why_it_was_declined"]
    # the spec had to concede, in advance, that this data supersedes nothing
    assert "They do not" in spec["why_this_dataset_supersedes_nothing"]["claim_being_corrected"]


def test_the_primary_gate_missed_and_the_quadratic_rival_won():
    """N3. The result that goes against the programme's own model."""
    r = _r()
    assert "N3_LISM_BEATS_THE_QUADRATIC_RIVAL" in r["gates_not_met"]
    a = r["auc"]
    assert a["arm_Q_quadratic"] > a["arm_L_LISM"], \
        "the symmetric quadratic form outscored the asymmetric LISM form"
    assert abs(a["arm_L_LISM"] - 0.6090) < 5e-4 and abs(a["arm_Q_quadratic"] - 0.6109) < 5e-4
    assert "MISSED" in r["primary_verdict"] and "rival won" in r["primary_verdict"]


def test_lism_beats_size_but_not_by_the_declared_margin():
    """N4, predicted in writing to fail, and it failed."""
    r = _r()
    assert "N4_LISM_BEATS_THE_SIZE_BASELINE" in r["gates_not_met"]
    d = r["auc"]["arm_L_LISM"] - r["auc"]["arm_B_size"]
    assert 0 < d < 0.05, "beats size by %.4f, short of the locked 0.05 bar" % d


def test_the_random_arm_sits_at_chance():
    """Every AUC in the file is readable against a known null."""
    assert abs(_r()["auc"]["arm_R_random"] - 0.5) < 0.02


def test_srisk_pass_is_recorded_with_its_qualification():
    """N5 passed against the written prediction; the qualification is asserted present."""
    r = _r()
    assert "N5_LISM_BEATS_THE_PUBLISHED_SRISK_MEASURE" not in r["gates_not_met"]
    s = r["auc_srisk_subsample"]
    assert s["n"] == 204 and s["events"] == 72
    assert s["arm_S_srisk"] < 0.51, "srisk scored at chance on THIS outcome"
    assert "different quantity" in r["post_run_disclosures"]["D4_what_N5_does_and_does_not_show"]["note"]


def test_the_realised_outcome_is_not_generated_here():
    r = _r()
    assert r["shape"]["Q1_only"] == 3811 and r["shape"]["Q2_only"] == 3812
    assert r["withdrawal_events"] == 291 and r["eligible"] == 1349
    assert r["simulation_count_in_scored_gates"] == 0


def test_the_cascade_is_excluded_and_says_so():
    r = _r()
    n6 = [g for g in r["gates"] if g["id"] == "N6_cascade_on_real_topology"][0]
    assert n6["weight"] == "excluded" and n6["met"] is None
    assert "not evidence" in n6["detail"]
    assert "not an observation" in r["cascade_is_not_evidence"]
    # and it was degenerate, which is disclosed rather than fixed by re-seeding
    assert "re-seeding" in r["post_run_disclosures"]["D2_the_cascade_did_essentially_nothing"]["note"]


def test_the_negative_weight_defect_is_disclosed_not_repaired():
    r = _r()
    d = r["post_run_disclosures"]["D1_negative_edge_weights_in_Q2"]
    assert d["found"] == 57 and d["events_with_negative_Q2_inflow"] == 21
    assert "NOT" in d["note"] and "re-scored" in d["note"]
    assert r["mean_intensity_of_loss_among_events"] > 1.0, "left in as computed"
    assert abs(d["mean_intensity_excluding_negative_inflow"] - 0.908394) < 1e-5


def test_the_forward_looking_label_is_read_by_no_arm():
    """rank_next_quarter is in the panel and would leak. No arm touches it."""
    src = open(os.path.join(HERE, "network.py")).read()
    body = src.split("def main(")[1]
    assert "rank_next_quarter" not in body.split('"rank_next_quarter_excluded"')[0]
    assert _r()["too_perfect_flag"] == []


def test_no_islamic_contract_claim_is_made():
    r = _r()
    n7 = [g for g in r["gates"] if g["id"] == "N7_islamic_contract_discrimination"][0]
    assert n7["weight"] == "excluded" and "UNTESTABLE-HERE" in n7["detail"]
    assert "Not refuted, not blocked" in n7["detail"]


def test_the_score_is_three_of_five():
    r = _r()
    assert r["score"] == "3/5"
    assert sorted(r["gates_not_met"]) == [
        "N3_LISM_BEATS_THE_QUADRATIC_RIVAL", "N4_LISM_BEATS_THE_SIZE_BASELINE"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
