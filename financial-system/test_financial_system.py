#!/usr/bin/env python3
"""
test_financial_system.py
========================
Rigorous pytest suite validating the full-reserve Sovereign Mudaraba Risk-Sharing
Ledger and the OQM Sabbath Lock Verifier state-machine.
"""

import os
import sys
import pytest

# Add current directory to python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sovereign_mudaraba_ledger import SovereignMudarabaLedger, UnderwritingGuard
from sabbath_lock_verifier import SabbathLockVerifier

def test_underwriting_guard():
    guard = UnderwritingGuard(tau_v_max=15.0, sigma_max=0.15)

    # Healthy active node
    ok, risk = guard.evaluate({"tau_v": 4.3, "sigma": 0.05})
    assert ok is True
    assert risk < 1.0

    # Famous zombie Pharaoh node (high prestige but massive latency)
    ok, risk = guard.evaluate({"tau_v": 121.7, "sigma": 0.02})
    assert ok is False
    assert risk > 1.0

    # Dishonest node (high say-do dissonance)
    ok, risk = guard.evaluate({"tau_v": 3.0, "sigma": 0.45})
    assert ok is False


def test_sovereign_mudaraba_ledger_rules():
    # Segregate a 100% full-reserve pool of 1,000,000 capital
    ledger = SovereignMudarabaLedger(total_reserves=1000000)

    # Rule 1: Reject synthetic Tawarruq interest wrapper
    res = ledger.deploy_capital(
        mudarib_id="mudarib_1",
        contract_type="Tawarruq",
        capital_req=100000,
        asset_value=100000,
        telemetry={"tau_v": 3.0, "sigma": 0.02}
    )
    assert res["success"] is False
    assert "Tawarruq" in res["reason"]

    # Rule 2: Accept healthy Mudaraba note with physical asset backing
    res = ledger.deploy_capital(
        mudarib_id="mudarib_2",
        contract_type="Mudaraba",
        capital_req=200000,
        asset_value=250000,
        telemetry={"tau_v": 4.5, "sigma": 0.05}
    )
    assert res["success"] is True
    assert ledger.allocated_capital == 200000

    # Rule 3: Reject under-collateralized/unbacked note
    res = ledger.deploy_capital(
        mudarib_id="mudarib_3",
        contract_type="Diminishing_Musharakah",
        capital_req=300000,
        asset_value=150000, # asset value less than capital requested
        telemetry={"tau_v": 2.0, "sigma": 0.02}
    )
    assert res["success"] is False
    assert "backed" in res["reason"] or "collateralized" in res["reason"]

    # Rule 4: Reject credit creation beyond 100% full reserves (fractional reserve block)
    res = ledger.deploy_capital(
        mudarib_id="mudarib_4",
        contract_type="Mudaraba",
        capital_req=900000, # Exceeds remaining reserves (800,000)
        asset_value=950000,
        telemetry={"tau_v": 1.0, "sigma": 0.01}
    )
    assert res["success"] is False
    assert "reserves" in res["reason"]


def test_mudaraba_pool_pnl_distribution():
    ledger = SovereignMudarabaLedger(total_reserves=500000)

    # Deploy to two healthy Mudaribs
    ledger.deploy_capital("m_1", "Mudaraba", 100000, 120000, {"tau_v": 2.0, "sigma": 0.04})
    ledger.deploy_capital("m_2", "Diminishing_Musharakah", 150000, 180000, {"tau_v": 4.0, "sigma": 0.08})

    # Simulate distributions under standard conditions
    sim = ledger.simulate_pnl_distribution(revenue_shock_factor=1.0)
    assert sim["total_capital_deployed"] == 250000
    assert len(sim["distributions"]) == 2

    # Diminishing Musharakah has equity buyback distribution
    m2_dist = [d for d in sim["distributions"] if d["mudarib_id"] == "m_2"][0]
    assert m2_dist["equity_buyback"] > 0


def test_sabbath_lock_verifier_state_machine():
    verifier = SabbathLockVerifier(n_nodes=5)

    # Cycle 1: Standard cycle, nodes perform normal utility-seeking writes
    actions_cycle1 = {
        "node_0": {"type": "write", "capture_net": False},
        "node_1": {"type": "read", "capture_net": False},
    }
    res1 = verifier.execute_cycle("standard", actions_cycle1)
    assert res1["cycle_type"] == "standard"
    assert res1["network_noise"] >= 0.50
    assert res1["feedback"]["node_0"]["status"] == "active"
    assert res1["feedback"]["node_0"]["D"] == 0.6 # noise degrades write fidelity

    # Cycle 2: Sabbath state-pause, node_0 obeys read-only, node_1 transgresses (Yuzh'oon)
    actions_cycle2 = {
        "node_0": {"type": "read", "capture_net": False}, # Honest Sabbath pause
        "node_1": {"type": "write", "capture_net": False}, # Transgression
        "node_2": {"type": "read", "capture_net": True},  # Sneaky capture net (transgression)
    }
    res2 = verifier.execute_cycle("sabbath", actions_cycle2)
    assert res2["cycle_type"] == "sabbath"
    assert res2["network_noise"] == 0.01 # Noise minimized

    # Node_0 has maximized encoding fidelity (D -> 1.0) and receives insights
    assert res2["feedback"]["node_0"]["status"] == "active"
    assert res2["feedback"]["node_0"]["D"] == 1.0
    assert res2["feedback"]["node_0"]["insight_pockets"] == 5

    # Node_1 is flagged as stagnant Qiradah and quarantined (D -> 0)
    assert res2["feedback"]["node_1"]["status"] == "stagnant (Qiradah)"
    assert res2["feedback"]["node_1"]["D"] == 0.0

    # Node_2 is also flagged as stagnant Qiradah and quarantined due to capture net
    assert res2["feedback"]["node_2"]["status"] == "stagnant (Qiradah)"
    assert res2["feedback"]["node_2"]["D"] == 0.0

    # Cycle 3: Quarantined nodes remain locked
    actions_cycle3 = {
        "node_1": {"type": "read", "capture_net": False}
    }
    res3 = verifier.execute_cycle("standard", actions_cycle3)
    assert res3["feedback"]["node_1"]["status"] == "quarantined"
    assert res3["feedback"]["node_1"]["D"] == 0.0
