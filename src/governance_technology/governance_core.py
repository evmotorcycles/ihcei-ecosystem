"""
GOVERNANCE TECHNOLOGY CORE
Implementation of IHCEI Ecosystem with Absolute Divine Governance Equation (ADGE) and NERE ethics
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from src.paradigm_comparison.core_differences import PurposeOfLife, SuccessMetric
from src.seh.seh_v9_1 import SEHCore, CognitiveEssenceState
from src.nere.nere_core import NERECore

logger = logging.getLogger(__name__)

@dataclass
class GovernanceDecision:
    """Governance-based decision output"""
    decision: str
    sovereign_context: str
    metaphorical_lesson: str
    cognitive_state: CognitiveEssenceState
    c_dev_contribution: float
    unification_balance: float
    ricci_scalar: float
    ethical_audit: Dict[str, Any]
    governance_elements_applied: List[str]

class GovernanceCore:
    """
    Governance Technology Core - Implements IHCEI Ecosystem

    Characteristics:
    - Optimizes for Cognitive Development (C_dev)
    - Treats data as Apparitions to be "pressed"
    - Uses ADGE physics and NERE ethics
    - Constitutional framework via 10 Elements of Deen
    """

    def __init__(self):
        # Initialize SEH and NERE cores
        self.seh_core = SEHCore()
        self.nere_core = NERECore()

        # Purpose and metrics
        self.purpose_of_life = PurposeOfLife.GOVERNANCE_DEVELOPMENT
        self.primary_metric = SuccessMetric.GOVERNANCE_C_DEV

        # Field states for ADGE
        self.field_history = []
        self.c_dev_history = []

        # Civilization tracking
        self.civilization_decisions = []
        self.total_c_dev_generated = 0.0
        self.ethical_violations_prevented = 0

        # Extension registry
        self.extensions = self._initialize_extensions()

        logger.info("Governance Core initialized with SEH v9.1 and NERE")

    def _initialize_extensions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the 33 IHCEI extensions"""

        extensions = {}
        categories = [
            ('governance', ['policy', 'legal', 'compliance', 'audit']),
            ('health', ['medical', 'mental_health', 'wellness', 'diagnostics']),
            ('education', ['primary', 'secondary', 'higher', 'vocational']),
            ('infrastructure', ['energy', 'water', 'transport', 'communication']),
            ('environment', ['climate', 'agriculture', 'conservation', 'sustainability']),
            ('economy', ['finance', 'trade', 'manufacturing', 'services']),
            ('social', ['community', 'family', 'culture', 'justice']),
            ('technology', ['ai', 'blockchain', 'quantum', 'biotech'])
        ]

        for category, subcategories in categories:
            for subcat in subcategories:
                ext_name = f"gov_{category}_{subcat}"
                extensions[ext_name] = {
                    'category': category,
                    'subcategory': subcat,
                    'c_dev_contribution': 0,
                    'usage_count': 0,
                    'last_used': None
                }

        return extensions

    def process_governance_decision(self, input_data: Dict[str, Any],
                                   context: Optional[str] = None) -> GovernanceDecision:
        """
        Make a decision using Governance paradigm

        Args:
            input_data: Input data (treated as Apparition)
            context: Optional context string

        Returns:
            GovernanceDecision with full governance context
        """

        # Convert input to string for SEH processing
        input_text = self._format_input_for_seh(input_data, context)

        # Step 1: SEH Apparition Analysis
        seh_analysis = self.seh_core.process_apparition(input_text, context or "")

        # Step 2: NERE Ethical Audit
        audit_data = {
            'c_dev': seh_analysis.c_dev_potential,
            'unification_balance': seh_analysis.unification_balance,
            'ricci_scalar': seh_analysis.ricci_scalar,
            'cognitive_state': seh_analysis.cognitive_essence_state.value,
            'context': context
        }

        nere_audit = self.nere_core.audit_decision(
            context=f"Governance decision: {input_text[:100]}",
            decision_data=audit_data
        )

        # Step 3: Calculate C_dev contribution (adjust for ethical violations)
        base_c_dev = seh_analysis.c_dev_potential
        if not nere_audit['audit_passed']:
            self.ethical_violations_prevented += 1
            # Apply penalty for ethical violations
            penalty = max(nere_audit['shirk_level'], nere_audit['riba_level'])
            c_dev_contribution = base_c_dev * (1 - penalty)
        else:
            c_dev_contribution = base_c_dev

        # Step 4: Route to appropriate extension
        extension = self._route_to_extension(input_text, seh_analysis)
        self._update_extension_metrics(extension['name'], c_dev_contribution)

        # Step 5: Generate governance-contextualized decision
        decision_text = self._generate_governance_decision(
            seh_analysis, nere_audit, extension
        )

        # Step 6: Update tracking
        self.total_c_dev_generated += c_dev_contribution
        self.c_dev_history.append(c_dev_contribution)

        # Record field states
        self.field_history.append({
            'phi': seh_analysis.phi_series[-1] if seh_analysis.phi_series else 0.7,
            'chi': seh_analysis.chi_series[-1] if seh_analysis.chi_series else 0.88,
            'psi': seh_analysis.psi_series[-1] if seh_analysis.psi_series else 0.6,
            'timestamp': datetime.now().isoformat()
        })

        # Store decision
        decision = GovernanceDecision(
            decision=decision_text,
            sovereign_context=seh_analysis.sovereign_context,
            metaphorical_lesson=seh_analysis.metaphorical_lesson,
            cognitive_state=seh_analysis.cognitive_essence_state,
            c_dev_contribution=c_dev_contribution,
            unification_balance=seh_analysis.unification_balance,
            ricci_scalar=seh_analysis.ricci_scalar,
            ethical_audit=nere_audit,
            governance_elements_applied=[
                # e.value if isinstance(e, Enum) else e for e in seh_analysis.governance_elements_applied
                # Assuming simple strings for now based on mock SEH
                e for e in seh_analysis.governance_elements_applied
            ]
        )

        self.civilization_decisions.append({
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'input_summary': input_text[:100],
            'extension': extension['name']
        })

        logger.info(f"Governance Decision made. C_dev: {c_dev_contribution:.2f}, "
                   f"Unification: {seh_analysis.unification_balance:.3f}")

        return decision

    def _format_input_for_seh(self, input_data: Dict[str, Any],
                             context: Optional[str]) -> str:
        """Format input data for SEH processing"""

        if isinstance(input_data, str):
            return input_data

        # Convert dict to descriptive string
        parts = []
        for key, value in input_data.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                parts.append(f"{key}: {len(value)} items")
            elif isinstance(value, dict):
                parts.append(f"{key}: dict with {len(value)} keys")

        formatted = ", ".join(parts)
        if context:
            formatted = f"{context}: {formatted}"

        return formatted

    def _route_to_extension(self, input_text: str,
                           seh_analysis: Any) -> Dict[str, Any]:
        """Route to appropriate IHCEI extension"""

        text_lower = input_text.lower()

        # Simple keyword-based routing
        keyword_mapping = {
            'health': 'gov_health_medical',
            'medical': 'gov_health_medical',
            'doctor': 'gov_health_medical',
            'hospital': 'gov_health_medical',

            'policy': 'gov_governance_policy',
            'law': 'gov_governance_policy',
            'regulation': 'gov_governance_policy',

            'education': 'gov_education_primary',
            'school': 'gov_education_primary',
            'learn': 'gov_education_primary',

            'energy': 'gov_infrastructure_energy',
            'power': 'gov_infrastructure_energy',
            'electric': 'gov_infrastructure_energy',

            'climate': 'gov_environment_climate',
            'environment': 'gov_environment_climate',
            'sustain': 'gov_environment_climate',

            'finance': 'gov_economy_finance',
            'money': 'gov_economy_finance',
            'bank': 'gov_economy_finance',

            'ai': 'gov_technology_ai',
            'artificial': 'gov_technology_ai',
            'machine': 'gov_technology_ai'
        }

        # Find matching extension
        matched_extension = None
        for keyword, ext_name in keyword_mapping.items():
            if keyword in text_lower:
                matched_extension = self.extensions.get(ext_name)
                if matched_extension:
                    break

        # Default to governance policy
        if not matched_extension:
            matched_extension = self.extensions.get('gov_governance_policy', {
                'name': 'gov_governance_policy',
                'category': 'governance',
                'subcategory': 'policy'
            })
            # If not found in self.extensions (because get returned default dict which has name but isn't in extensions map)
            # Actually self.extensions.get returns reference to dict in map if exists.
            # If not exists, I constructed a new dict but it's not in self.extensions.
            # Better to fallback to a known key.
            if 'gov_governance_policy' in self.extensions:
                 matched_extension = self.extensions['gov_governance_policy']

        # Add name if missing (from my logic above)
        if 'name' not in matched_extension:
            # Reverse lookup or just use logic
            matched_extension['name'] = [k for k, v in self.extensions.items() if v is matched_extension][0]

        # Update usage
        matched_extension['last_used'] = datetime.now().isoformat()

        return matched_extension

    def _update_extension_metrics(self, extension_name: str, c_dev: float):
        """Update extension metrics"""

        if extension_name in self.extensions:
            self.extensions[extension_name]['c_dev_contribution'] += c_dev
            self.extensions[extension_name]['usage_count'] += 1

    def _generate_governance_decision(self, seh_analysis: Any,
                                     nere_audit: Dict[str, Any],
                                     extension: Dict[str, Any]) -> str:
        """Generate governance-contextualized decision text"""

        cognitive_state = seh_analysis.cognitive_essence_state
        state_name = cognitive_state.value.lower()

        templates = {
            'infant': [
                "Based on governance principles for cognitive development: {context}. "
                "The metaphorical lesson is: {lesson}. This contributes {c_dev:.1f} C_dev."
            ],
            'guidable': [
                "The governance framework interprets this as: {context}. "
                "Key lesson: {lesson}. This advances cognitive development by {c_dev:.1f} C_dev."
            ],
            'insight holder': [
                "Within the Nafs-Centric Simulation: {context}. "
                "The sovereign insight: {lesson}. This generates {c_dev:.1f} C_dev for the network."
            ]
        }

        # Select template based on cognitive state
        if 'infant' in state_name:
            template_group = 'infant'
        elif 'guidable' in state_name:
            template_group = 'guidable'
        else:
            template_group = 'insight holder'

        template = np.random.choice(templates[template_group])

        # Apply ethical corrections if needed
        if not nere_audit['audit_passed']:
            correction = "[ETHICAL CORRECTION APPLIED: "
            if nere_audit['shirk_detected']:
                correction += f"Shirk detected at level {nere_audit['shirk_level']:.2f}. "
            if nere_audit['riba_detected']:
                correction += f"Riba detected at level {nere_audit['riba_level']:.2f}. "
            correction += "Governance protocols enforced.]\n\n"
        else:
            correction = ""

        decision_text = template.format(
            context=seh_analysis.sovereign_context,
            lesson=seh_analysis.metaphorical_lesson,
            c_dev=seh_analysis.c_dev_potential
        )

        return correction + decision_text

    def batch_process_decisions(self, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple decisions in batch"""

        logger.info(f"Batch processing {len(inputs)} governance decisions")

        results = []
        for input_data in inputs:
            result = self.process_governance_decision(input_data)
            results.append(result)

        # Calculate batch metrics
        total_c_dev = sum(r.c_dev_contribution for r in results)
        avg_c_dev = total_c_dev / len(results) if results else 0

        unification_scores = [r.unification_balance for r in results]
        avg_unification = np.mean(unification_scores) if unification_scores else 0

        ethical_violations = sum(
            1 for r in results if not r.ethical_audit['audit_passed']
        )

        # Extension usage analysis
        extension_usage = {}
        for r in results:
            # Find which extension was used
            # This is tricky because result doesn't explicitly store extension name, but we can infer or we should have stored it in result or logging
            # For this implementation I will iterate extensions and match last_used or usage count, but usage count is cumulative.
            # However, I stored extension name in civilization_decisions with timestamp.
            # Let's use the assumption that we can retrieve it or just skip precise extension reporting for this batch function logic
            # OR better, since I implemented _route_to_extension updating 'last_used', I can check that if timestamps match.
            # But simpler:
            pass
            # I will just skip extension_usage logic here for batch or simplify it.

        # Re-implementing extension usage properly:
        # In process_governance_decision, I added to civilization_decisions.
        # I can look at the last N decisions.

        batch_decisions = self.civilization_decisions[-len(results):]
        for d in batch_decisions:
            ext_name = d['extension']
            extension_usage[ext_name] = extension_usage.get(ext_name, 0) + 1


        batch_report = {
            'total_decisions': len(results),
            'total_c_dev_generated': total_c_dev,
            'average_c_dev': avg_c_dev,
            'average_unification': avg_unification,
            'ethical_violations': ethical_violations,
            'compliance_rate': 1 - (ethical_violations / len(results)) if results else 1.0,
            'extension_usage': dict(sorted(
                extension_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            'field_stability': self._calculate_field_stability(),
            'civilization_health': self._calculate_civilization_health(results)
        }

        logger.info(f"Batch processing complete. Generated {total_c_dev:.1f} total C_dev")

        return batch_report

    def _calculate_field_stability(self) -> float:
        """Calculate stability of ADGE fields"""

        if len(self.field_history) < 2:
            return 1.0

        recent_fields = self.field_history[-10:]  # Last 10 measurements

        # Calculate variance for each field
        phi_values = [f['phi'] for f in recent_fields]
        chi_values = [f['chi'] for f in recent_fields]
        psi_values = [f['psi'] for f in recent_fields]

        phi_variance = np.var(phi_values) if len(phi_values) > 1 else 0
        chi_variance = np.var(chi_values) if len(chi_values) > 1 else 0
        psi_variance = np.var(psi_values) if len(psi_values) > 1 else 0

        # Stability is inverse of average variance
        avg_variance = (phi_variance + chi_variance + psi_variance) / 3
        stability = 1.0 - min(avg_variance * 10, 0.9)  # Scale appropriately

        return stability

    def _calculate_civilization_health(self, results: List[GovernanceDecision]) -> float:
        """Calculate overall civilization health score"""

        if not results:
            return 0.5

        # Components of health score
        c_dev_score = min(np.mean([r.c_dev_contribution for r in results]) / 100, 1.0)
        unification_score = np.mean([r.unification_balance for r in results])

        # Ethical compliance
        compliance_rate = sum(
            1 for r in results if r.ethical_audit['audit_passed']
        ) / len(results)

        # Field stability
        field_stability = self._calculate_field_stability()

        # Weighted health score
        health_score = (
            c_dev_score * 0.4 +
            unification_score * 0.3 +
            compliance_rate * 0.2 +
            field_stability * 0.1
        )

        return health_score

    def get_governance_report(self) -> Dict[str, Any]:
        """Get comprehensive governance report"""

        # Recent decisions analysis
        recent_decisions = self.civilization_decisions[-10:] if self.civilization_decisions else []

        if recent_decisions:
            recent_c_dev = np.mean([d['decision'].c_dev_contribution for d in recent_decisions])
            recent_unification = np.mean([d['decision'].unification_balance for d in recent_decisions])
            recent_compliance = np.mean([
                1 if d['decision'].ethical_audit['audit_passed'] else 0
                for d in recent_decisions
            ])
        else:
            recent_c_dev = 0.0
            recent_unification = 0.0
            recent_compliance = 1.0

        # Top extensions by C_dev contribution
        top_extensions = sorted(
            self.extensions.items(),
            key=lambda x: x[1]['c_dev_contribution'],
            reverse=True
        )[:5]

        # Cognitive state distribution
        cognitive_states = {}
        for decision in self.civilization_decisions[-50:]:  # Last 50 decisions
            state = decision['decision'].cognitive_state.value
            cognitive_states[state] = cognitive_states.get(state, 0) + 1

        # Normalize to percentages
        total_states = sum(cognitive_states.values())
        if total_states > 0:
            cognitive_distribution = {
                state: count / total_states
                for state, count in cognitive_states.items()
            }
        else:
            cognitive_distribution = {}

        return {
            'total_decisions': len(self.civilization_decisions),
            'total_c_dev_generated': self.total_c_dev_generated,
            'ethical_violations_prevented': self.ethical_violations_prevented,
            'recent_performance': {
                'avg_c_dev': recent_c_dev,
                'avg_unification': recent_unification,
                'compliance_rate': recent_compliance
            },
            'field_states': self.field_history[-1] if self.field_history else {},
            'top_extensions': [
                {
                    'name': name,
                    'c_dev_contribution': data['c_dev_contribution'],
                    'usage_count': data['usage_count']
                }
                for name, data in top_extensions
            ],
            'cognitive_distribution': cognitive_distribution,
            'civilization_health': self._calculate_civilization_health(
                [d['decision'] for d in self.civilization_decisions[-10:]]
            ) if self.civilization_decisions else 0.5,
            'system_status': 'active' if self.total_c_dev_generated > 0 else 'inactive'
        }
