import pytest
from src.core.centric_intelligence import CentricIntelligenceCore

def test_run_pilot_test_calculation():
    """
    Test that run_pilot_test calculates c_dev correctly with a given density.
    """
    ci = CentricIntelligenceCore()
    input_data = {'density': 1.5}
    result = ci.run_pilot_test("Test Pilot", input_data)

    # Check that c_dev is calculated
    assert result.c_dev is not None
    assert isinstance(result.c_dev, float)

    # Check that c_dev is positive (assuming density 1.5 yields positive c_dev)
    assert result.c_dev > 0

    # Verify context
    assert result.context == "Test Pilot"

    print(f"Test Output - c_dev: {result.c_dev}")
