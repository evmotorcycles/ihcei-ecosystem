"""
test_audit.py — locks the peer review of the Colab "Hybrid Sovereign Mesh" run.

Verdict: 7/14 scored gates. 4 REPRODUCED · 2 NOT_REPRODUCED · 3 INVALID · 1 CIRCULAR.

WHAT SURVIVED. The simple arithmetic is honest and reproduces exactly: 4,886 debits with
400 above the 30% threshold; all four Meezan headline figures; the executive-order counts
(112/132/907/1061); the hearing counts (3567/8245/11404/15738).

WHAT DID NOT.
  A7  The cohort labelled "Risk-Sharing (Data)" contains ZERO risk-sharing contracts.
      The file holds only Murabaha (3,837), Ijara (3,764) and Salam (3,647) — cost-plus
      sale, lease and forward purchase. Under Harris Irfan's own critique these ARE the
      synthetic-debt wrappers. The comparison was debt-like data vs tuned debt-like sim.
  A8  The "Synthetic Debt" arm is not measured. Capacity is set to a "Target Mean
      Capacity", fidelity to a "Tuned" 0.75 against the comparator's 0.95. Two arms with
      different fidelity constants cannot be compared; the winner is fixed before any
      data is read.
  A9  The "Zombie Breach Rate" is algebraically P(Risk_Score > 13.513) and recomputes to
      26.64% — identical to the reported figure. It is a renamed percentile of an input
      column, not a finding.
  A10 The legislative D values (up to 2,245,229) cannot be fidelities. In E = U*D, D must
      lie in [0,1]; these are character-count times hearing-count, so the reported yields
      up to 2.03e9 have no units.
  A6  D_enc does not recompute: [88.46, 107.40, 98.36, 92.79] against the claimed
      [117.59, 91.05, 196.88, 91.31] — different values AND a different rank order.
  A3  The Kenya index recomputes to 12.23%, not 11.24%, on a denominator that counts
      spreadsheet rows rather than respondents.

THE CORRECTION THAT MATTERS MOST (C6): the Colab's D_dec was a RAW COUNT of hearings,
which ranks with capacity at spearman +1.00 — a perfect rank correlation. So E = U*D was
approximately U-SQUARED, and "Govt Operations has the highest yield" reduced to "Govt
Operations is the biggest domain." Rebuilding D_dec as hearings PER ENACTED LAW breaks
that (rho = -0.80) and REVERSES the substantive conclusion: Banking & Finance turns out to
have the HIGHEST fidelity (0.9978), not the lowest.

C4 FAILED its own gate, and that is reported rather than softened: the real median
introduction-to-signature latency is 171-288 days (refuting the asserted "69 days"), but
Macroeconomics has only n=15 dated laws, below the pre-registered floor of 100.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "9a3e4a3e1ef4c219d026725f7e1eb743d82d19935ff1486f69c901bbd184f3eb"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "audit.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_audit.json")))


def test_spec_locked_and_expected_failures_declared_in_advance():
    spec = json.load(open(os.path.join(HERE, "prereg", "audit_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    for g in ("A3_kenya_index_reproduces", "A6_legislative_D_enc_reproduces",
              "A7_the_risk_sharing_cohort_actually_contains_risk_sharing",
              "A8_the_debt_comparison_is_not_rigged",
              "A9_zombie_breach_is_not_a_relabelled_quantile",
              "A10_legislative_fidelity_is_dimensionally_valid"):
        assert "EXPECTED TO FAIL" in spec["audit_gates"][g], \
            "%s must be declared as an expected failure BEFORE the run" % g
    assert "does not claim the Colab author acted in bad faith" in \
        spec["what_this_review_does_not_do"]


def test_the_datasets_are_committed_and_hash_pinned():
    man = json.load(open(os.path.join(ROOT, "data", "colab-audit", "MANIFEST.json")))
    assert len(man["sha256"]) == 9
    for f in man["sha256"]:
        rel = os.path.join("data", "colab-audit", f)
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                                 cwd=ROOT, capture_output=True, text=True)
        assert tracked.returncode == 0, "%s is not git-tracked" % rel


def test_the_honest_arithmetic_reproduces_exactly():
    """Where the Colab did simple counting, it was right. Say so."""
    r = _r()
    assert r["A1"] == {"debits": 4886, "high_risk": 400}
    assert r["A2"]["n"] == 11248
    assert abs(r["A2"]["mean_U"] - 238959.66) < 0.01
    assert abs(r["A2"]["breach_pct"] - 26.64) < 0.01
    assert abs(r["A2"]["mean_E"] - 104378.76) < 0.01
    assert list(r["A4_U"].values()) == [112, 132, 907, 1061]
    assert list(r["A5_hearings"].values()) == [3567, 8245, 11404, 15738]


def test_there_are_no_risk_sharing_contracts_in_the_risk_sharing_cohort():
    r = _r()
    comp = r["A7_contract_composition"]
    assert set(comp) == {"Murabaha", "Ijara", "Salam"}
    assert not ({"Mudarabah", "Musharakah"} & set(comp)), \
        "the cohort named 'Risk-Sharing' must be shown to contain none"
    assert sum(comp.values()) == 11248


def test_the_zombie_breach_rate_is_exactly_a_relabelled_percentile():
    r = _r()
    assert abs(r["A9_threshold"] - 13.513) < 0.01
    assert abs(r["A9_quantile_pct"] - r["A2"]["breach_pct"]) < 0.01, \
        "the breach rate and the raw quantile must be shown to be the same number"


def test_the_legislative_fidelity_was_dimensionally_impossible():
    r = _r()
    assert all(d > 1.0 for d in r["A10_claimed_D"])
    assert max(r["A10_claimed_D"]) > 1e6


def test_d_enc_does_not_reproduce_and_the_rank_order_differs():
    r = _r()
    got, claimed = r["A6_D_enc"], r["A6_claimed"]
    assert got != claimed
    # Defense was claimed as by far the most specific; it is not
    assert claimed["Defense & Security"] > 190
    assert got["Defense & Security"] < 110
    assert max(got, key=got.get) != max(claimed, key=claimed.get), \
        "the recomputed rank order differs from the claimed one"


def test_the_political_finding_was_circular_and_the_fix_reverses_it():
    """C6 is the most consequential correction in the whole review."""
    r = _r()
    assert abs(r["C6_spearman_U_vs_rawcount"] - 1.00) < 1e-9, \
        "the raw hearing count ranks PERFECTLY with capacity — E = U*D was U-squared"
    assert abs(r["C6_spearman_U_vs_intensity"]) < 0.90
    D = r["C3_D_rebuilt"]
    assert all(0.0 < v <= 1.0 for v in D.values())
    # the Colab said Banking had among the LOWEST fidelity; rebuilt, it is the highest
    assert max(D, key=D.get) == "Banking & Finance"


def test_the_69_day_latency_claim_is_refuted_and_its_own_gate_failed():
    r = _r()
    lat = r["C4_median_latency_days"]
    assert all(v > 100 for v in lat.values()), "every domain far exceeds the asserted 69d"
    assert min(lat.values()) > 150
    # and the correction is not oversold: one domain is underpowered, so C4 FAILED
    assert r["C4_n_dated"]["Macroeconomics"] < 100
    assert "C4_a_real_legislative_tau_v_is_measured_not_asserted" in r["gates_not_met"]


def test_the_fair_comparison_is_computed_not_targeted():
    r = _r()
    assert r["C2_equity_mean"] > r["C2_debt_mean"], \
        "on matched transactions with a shared fidelity input, equity beats debt"
    # but it must not be sold as vindication of the original claim
    c2 = [g for g in r["gates"] if g["gate"].startswith("C2")][0]
    assert "no risk-sharing contracts are present" in c2["detail"]


def test_the_overall_verdict_is_not_softened():
    r = _r()
    verdicts = [g["verdict"] for g in r["gates"]]
    assert verdicts.count("REPRODUCED") == 4
    assert verdicts.count("NOT_REPRODUCED") == 2
    assert verdicts.count("INVALID") == 3
    assert verdicts.count("CIRCULAR") == 1
    assert len(r["gates_not_met"]) == 7
