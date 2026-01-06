"""
Tests for Paradigm Comparison Module
"""
import pytest
from src.paradigm_comparison.core_differences import (
    RTCore, GovernanceCore, ParadigmComparison, RealityModel, PurposeOfLife, TechnologyConstruction
)

def test_rt_core_initialization():
    rt = RTCore()
    assert RealityModel.RT_MATERIALISM in rt.reality_model
    assert PurposeOfLife.RT_SURVIVAL in rt.purpose
    assert rt.ai_model == TechnologyConstruction.INDEPENDENT_AGENT

def test_rt_core_optimization():
    rt = RTCore()
    metrics = {"gdp": 100, "engagement": 50, "efficiency": 80}
    optimized = rt.optimize(metrics)

    # RT should increase these metrics
    assert optimized["gdp"] > 100
    assert optimized["engagement"] > 50
    assert optimized["addiction_risk"] == "HIGH"
    assert optimized["governance_layer"] == "VACUUM"

def test_governance_core_initialization():
    gov = GovernanceCore()
    assert RealityModel.GOVERNANCE_NAFS_CENTRIC in gov.reality_model
    assert PurposeOfLife.GOVERNANCE_DEVELOPMENT in gov.purpose
    assert gov.ai_model == TechnologyConstruction.COGNITIVE_MIRROR

def test_governance_process_apparition():
    gov = GovernanceCore()
    # High unification scenario
    nafs_state_high = {"phi": 0.8, "chi": 0.8, "psi": 0.8}
    result_high = gov.process_apparition({"event": "test"}, nafs_state_high)

    assert result_high["unification_balance"] == 1.0
    assert result_high["c_dev_gained"] == 100.0

    # Low unification scenario
    nafs_state_low = {"phi": 0.2, "chi": 0.8, "psi": 0.5}
    result_low = gov.process_apparition({"event": "test"}, nafs_state_low)

    assert result_low["unification_balance"] < 1.0
    assert result_low["c_dev_gained"] < 100.0

def test_paradigm_comparison_analysis():
    comparison = ParadigmComparison()
    analysis = comparison.analyze_divergence()

    assert "Materialism" in analysis["ontology"]["RT"][0]
    assert "Nafs-Centric" in analysis["ontology"]["Governance"][0]
    assert analysis["technological_consequence"]["RT"] == TechnologyConstruction.INDEPENDENT_AGENT.value
    assert analysis["technological_consequence"]["Governance"] == TechnologyConstruction.COGNITIVE_MIRROR.value
