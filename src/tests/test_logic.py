import pytest
from src.core.adge import ADGE, ASGE
from src.core.tqg_cfe import TQGCFE
from src.core.nere import NERE
from src.core.ecosystem import IHCEIEcosystem

class TestADGE:
    def test_calculate_metrics(self):
        adge = ADGE()
        metrics = adge.calculate_metrics(coherence_level=0.8, intention_alignment=0.9)

        assert "c_dev" in metrics
        assert "ricci_scalar" in metrics
        assert isinstance(metrics["c_dev"], float)
        assert isinstance(metrics["ricci_scalar"], float)

        # Expected C_dev = 1.0 * (0.8 * 0.9) = 0.72
        assert metrics["c_dev"] == pytest.approx(0.72)
        # Expected Ricci = log(1 + 0.72)
        assert metrics["ricci_scalar"] > 0

    def test_asge_alias(self):
        """Test that ASGE alias works as expected."""
        asge = ASGE()
        assert isinstance(asge, ADGE)

class TestTQGCFE:
    def test_calculate_field_potential(self):
        engine = TQGCFE()
        potential = engine.calculate_field_potential(mass_energy=1000, radius=10)
        assert isinstance(potential, float)
        assert potential < 0  # Gravitational potential is negative

    def test_integrate_forces(self):
        engine = TQGCFE()
        forces = [10.0, 20.0, 5.0]
        net_force = engine.integrate_forces(forces)
        assert net_force == 35.0

class TestNERE:
    def test_audit_compliant(self):
        nere = NERE()
        # High transparency and fairness
        decision = {'transparency': 0.95, 'fairness': 0.95, 'utility': 0.8}
        audit = nere.audit_decision(decision)

        assert audit['is_compliant'] is True
        assert audit['shirk_level'] < 0.1
        assert audit['riba_level'] < 0.1

    def test_audit_non_compliant_shirk(self):
        nere = NERE()
        # Low transparency -> High Shirk
        decision = {'transparency': 0.1, 'fairness': 0.9, 'utility': 0.8}
        audit = nere.audit_decision(decision)

        assert audit['is_compliant'] is False
        assert audit['shirk_level'] > 0.8

    def test_audit_non_compliant_riba(self):
        nere = NERE()
        # High utility, Low fairness -> High Riba
        decision = {'transparency': 0.9, 'fairness': 0.1, 'utility': 0.9}
        audit = nere.audit_decision(decision)

        assert audit['is_compliant'] is False
        assert audit['riba_level'] > 0.5  # Approximate check

class TestEcosystem:
    def test_process_state(self):
        ecosystem = IHCEIEcosystem()
        state_data = {
            'coherence': 0.9,
            'alignment': 0.9,
            'mass_energy': 500.0,
            'radius': 5.0
        }

        result = ecosystem.process_state(state_data)

        assert "adge_metrics" in result
        assert "field_potential" in result
        assert "nere_audit" in result

        assert result['adge_metrics']['c_dev'] == pytest.approx(0.81)
        assert result['nere_audit']['is_compliant'] is True
