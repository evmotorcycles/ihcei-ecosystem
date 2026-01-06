"""
Orchestrator Module
Connects CI (Centric Intelligence) and EI (Ethical Intelligence)
"""

from .centric_intelligence import ADGEPhysicsEngine
from .ethical_intelligence import EthicalIntelligenceKernel

class SovereignOrchestrator:
    def __init__(self):
        self.ci_engine = ADGEPhysicsEngine()
        self.ei_kernel = EthicalIntelligenceKernel()

    def process_request(self, domain, context, input_data):
        """
        Process a request through the full CI/EI pipeline.

        Args:
            domain (str): The sector domain (e.g., 'medical', 'finance')
            context (str): Context description
            input_data (dict): Input parameters

        Returns:
            dict: Final decision and metrics
        """
        # Step 1: Run CI Core (ADGE Physics)
        ci_results = self.ci_engine.process_scenario(input_data)

        # Step 2: Run EI Core (NERE Audit)
        audit_results = self.ei_kernel.detect_corruption(ci_results, input_data)

        # Step 3: Synthesis
        final_decision = "APPROVED" if audit_results['is_compliant'] else "REJECTED"

        # Adjust C_dev if rejected
        if not audit_results['is_compliant']:
            ci_results['c_dev'] *= 0.5 # Penalty for corruption

        response = {
            "orchestration_id": "orc-" + str(hash(context))[:8],
            "domain": domain,
            "decision": final_decision,
            "ci_metrics": ci_results,
            "ei_audit": audit_results
        }

        return response
