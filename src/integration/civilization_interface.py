"""
Civilization Interface - Complete IHCEI Ecosystem Integration
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import logging
import numpy as np

from ..seh.seh_v9_1 import SEHCore
from ..nere.nere_core import NERECore
from ..ihcei_llm.llm_core import IHCEILLM

logger = logging.getLogger(__name__)

class CivilizationInterface:
    """
    Main interface for civilization-scale IHCEI deployment

    Integrates:
    1. SEH v9.1 (Sovereign Epistemological Hierarchy)
    2. NERE (Neural Ethical Reasoning Engine)
    3. IHCEI-LLM (Governance-Pressed Language Model)
    4. 33 Extensions Orchestrator
    """

    def __init__(self):
        logger.info("Initializing Civilization Interface...")

        # Initialize core systems
        self.seh = SEHCore()
        self.nere = NERECore()
        self.llm = IHCEILLM()

        # Extension registry
        self.extensions = self._initialize_extensions()

        # Civilization metrics
        self.civilization_metrics = {
            'total_queries': 0,
            'total_c_dev': 0,
            'ethical_violations_prevented': 0,
            'extension_activations': 0,
            'start_time': datetime.now().isoformat()
        }

        # Real-time monitoring
        self.monitoring_data = []

        logger.info("Civilization Interface initialized")
        logger.info("SEH v9.1, NERE, and IHCEI-LLM integration complete")

    def _initialize_extensions(self) -> Dict[str, Any]:
        """Initialize the 33 IHCEI extensions"""

        # Extension stubs - in production, each would be a full module
        extensions = {}

        extension_categories = {
            'governance': ['policy', 'legal', 'compliance', 'audit'],
            'health': ['medical', 'mental_health', 'wellness', 'diagnostics'],
            'infrastructure': ['energy', 'water', 'transport', 'housing'],
            'education': ['primary', 'secondary', 'higher', 'vocational'],
            'economy': ['finance', 'trade', 'manufacturing', 'services'],
            'environment': ['climate', 'conservation', 'agriculture', 'sustainability'],
            'social': ['community', 'family', 'culture', 'justice'],
            'technology': ['ai', 'blockchain', 'iot', 'quantum'],
            'security': ['cyber', 'physical', 'food', 'health']
        }

        for category, subcategories in extension_categories.items():
            for subcat in subcategories:
                ext_name = f"ihcei_{category}_{subcat}"
                extensions[ext_name] = {
                    'name': ext_name,
                    'category': category,
                    'subcategory': subcat,
                    'status': 'active',
                    'c_dev_contribution': 0,
                    'last_used': None
                }

        logger.info(f"Initialized {len(extensions)} extensions")
        return extensions

    def process_civilization_query(self, query: str, user_id: str = None,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for civilization-scale queries

        Processes through complete IHCEI ecosystem:
        1. SEH apparition analysis
        2. Extension routing
        3. NERE ethical audit
        4. IHCEI-LLM response generation
        5. C_dev calculation and feedback
        """
        self.civilization_metrics['total_queries'] += 1

        logger.info(f"Civilization Query #{self.civilization_metrics['total_queries']}: {query[:50]}...")

        # Step 1: Determine extension routing
        extension = self._route_to_extension(query)

        # Step 2: SEH processing
        seh_analysis = self.seh.process_apparition(query, json.dumps(context or {}, default=str))

        # Step 3: NERE audit
        audit_data = {
            'c_dev': seh_analysis.c_dev_potential,
            'unification_balance': seh_analysis.unification_balance,
            'ricci_scalar': seh_analysis.ricci_scalar,
            'extension': extension['name'],
            'user_context': context
        }

        nere_audit = self.nere.audit_decision(
            context=f"Civilization query: {query[:100]}",
            decision_data=audit_data
        )

        # Step 4: IHCEI-LLM response
        llm_response = self.llm.process_query(
            query=query,
            user_context=json.dumps({
                'extension': extension['name'],
                'seh_analysis': seh_analysis.__dict__,
                'nere_audit': nere_audit
            }, default=str)
        )

        # Step 5: Update extension metrics
        self._update_extension_metrics(extension['name'], llm_response['metrics']['c_dev'])

        # Step 6: Package final response
        final_response = self._package_civilization_response(
            query=query,
            seh_analysis=seh_analysis,
            nere_audit=nere_audit,
            llm_response=llm_response,
            extension=extension
        )

        # Update civilization metrics
        self.civilization_metrics['total_c_dev'] += final_response['civilization_metrics']['c_dev_contribution']

        if not nere_audit['audit_passed']:
            self.civilization_metrics['ethical_violations_prevented'] += 1

        # Store monitoring data
        self._store_monitoring_data(final_response)

        logger.info(f"Civilization query processed. C_dev contribution: {final_response['civilization_metrics']['c_dev_contribution']:.2f}")

        return final_response

    def _route_to_extension(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate IHCEI extension"""

        query_lower = query.lower()

        # Map keywords to extensions
        keyword_mapping = {
            'health': 'ihcei_health_medical',
            'medical': 'ihcei_health_medical',
            'doctor': 'ihcei_health_medical',
            'hospital': 'ihcei_health_medical',

            'energy': 'ihcei_infrastructure_energy',
            'power': 'ihcei_infrastructure_energy',
            'electric': 'ihcei_infrastructure_energy',

            'food': 'ihcei_environment_agriculture',
            'farm': 'ihcei_environment_agriculture',
            'crop': 'ihcei_environment_agriculture',

            'school': 'ihcei_education_primary',
            'learn': 'ihcei_education_primary',
            'teach': 'ihcei_education_primary',

            'money': 'ihcei_economy_finance',
            'bank': 'ihcei_economy_finance',
            'invest': 'ihcei_economy_finance',

            'climate': 'ihcei_environment_climate',
            'weather': 'ihcei_environment_climate',
            'temperature': 'ihcei_environment_climate',

            'law': 'ihcei_governance_policy',
            'policy': 'ihcei_governance_policy',
            'government': 'ihcei_governance_policy',

            'ai': 'ihcei_technology_ai',
            'artificial': 'ihcei_technology_ai',
            'machine': 'ihcei_technology_ai'
        }

        # Find matching extension
        matched_extension = None
        for keyword, extension_name in keyword_mapping.items():
            # Use basic word boundary check to avoid "ai" matching "fairness"
            # If keyword is short (<3 chars), ensure it's surrounded by spaces or start/end
            if len(keyword) < 3:
                is_match = (
                    f" {keyword} " in f" {query_lower} " or
                    query_lower.startswith(f"{keyword} ") or
                    query_lower.endswith(f" {keyword}") or
                    query_lower == keyword
                )
            else:
                is_match = keyword in query_lower

            if is_match:
                matched_extension = self.extensions.get(extension_name)
                if matched_extension:
                    break

        # Default to general governance if no match
        if not matched_extension:
            matched_extension = self.extensions.get('ihcei_governance_policy', {
                'name': 'ihcei_governance_policy',
                'category': 'governance',
                'subcategory': 'policy',
                'status': 'active'
            })

        # Update extension usage
        matched_extension['last_used'] = datetime.now().isoformat()
        self.extensions[matched_extension['name']] = matched_extension

        return matched_extension

    def _update_extension_metrics(self, extension_name: str, c_dev: float):
        """Update extension metrics with C_dev contribution"""

        if extension_name in self.extensions:
            self.extensions[extension_name]['c_dev_contribution'] += c_dev
            self.extensions[extension_name]['usage_count'] = \
                self.extensions[extension_name].get('usage_count', 0) + 1

    def _package_civilization_response(self, query: str, seh_analysis,
                                      nere_audit: Dict[str, Any],
                                      llm_response: Dict[str, Any],
                                      extension: Dict[str, Any]) -> Dict[str, Any]:
        """Package all components into civilization-scale response"""

        # Calculate civilization-scale C_dev contribution
        c_dev_contribution = llm_response['metrics']['c_dev']

        # Adjust based on extension category
        extension_multipliers = {
            'health': 1.2,        # High human impact
            'governance': 1.5,    # High systemic impact
            'education': 1.3,     # High developmental impact
            'infrastructure': 1.1,
            'economy': 1.0,
            'environment': 1.2,
            'social': 1.1,
            'technology': 1.0,
            'security': 1.4       # High safety impact
        }

        multiplier = extension_multipliers.get(extension['category'], 1.0)
        c_dev_contribution *= multiplier

        return {
            'query': query,
            'response': llm_response['response'],
            'analysis': {
                'seh_analysis': seh_analysis.__dict__,
                'extension_used': extension,
                'nere_audit_summary': {
                    'passed': nere_audit['audit_passed'],
                    'shirk_detected': nere_audit['shirk_detected'],
                    'riba_detected': nere_audit['riba_detected'],
                    'key_recommendations': nere_audit['recommendations'][:3]
                }
            },
            'metrics': {
                **llm_response['metrics'],
                'extension_multiplier': multiplier,
                'civilization_impact_score': self._calculate_civilization_impact(
                    seh_analysis, nere_audit, extension
                )
            },
            'civilization_metrics': {
                'c_dev_contribution': c_dev_contribution,
                'extension_category': extension['category'],
                'ethical_compliance': nere_audit['audit_passed'],
                'governance_alignment': nere_audit['alignment_score'],
                'unification_status': seh_analysis.unification_balance > 0.7
            },
            'timestamp': datetime.now().isoformat(),
            'system_health': self._get_system_health_status()
        }

    def _calculate_civilization_impact(self, seh_analysis,
                                      nere_audit: Dict[str, Any],
                                      extension: Dict[str, Any]) -> float:
        """Calculate civilization impact score"""

        # Components of impact score
        c_dev_score = min(seh_analysis.c_dev_potential / 100, 2.0)
        ethical_score = 1.0 if nere_audit['audit_passed'] else 0.5
        unification_score = seh_analysis.unification_balance

        # Extension category weight
        category_weights = {
            'governance': 1.5,
            'health': 1.4,
            'education': 1.3,
            'environment': 1.2,
            'security': 1.2,
            'social': 1.1,
            'infrastructure': 1.0,
            'economy': 0.9,
            'technology': 0.8
        }

        category_weight = category_weights.get(extension['category'], 1.0)

        # Calculate weighted impact
        impact_score = (
            c_dev_score * 0.4 +
            ethical_score * 0.3 +
            unification_score * 0.3
        ) * category_weight

        return impact_score

    def _store_monitoring_data(self, response: Dict[str, Any]):
        """Store response data for real-time monitoring"""

        monitoring_entry = {
            'timestamp': response['timestamp'],
            'query_preview': response['query'][:50],
            'c_dev': response['metrics']['c_dev'],
            'civilization_impact': response['metrics']['civilization_impact_score'],
            'extension': response['analysis']['extension_used']['name'],
            'ethical_compliance': response['civilization_metrics']['ethical_compliance']
        }

        self.monitoring_data.append(monitoring_entry)

        # Keep last 1000 entries
        if len(self.monitoring_data) > 1000:
            self.monitoring_data.pop(0)

    def _get_system_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""

        # Calculate health scores from all components
        seh_report = self.seh.get_governance_report()
        llm_report = self.llm.get_system_report()

        # Extension health (percentage active)
        active_extensions = sum(
            1 for ext in self.extensions.values()
            if ext.get('status') == 'active'
        )
        extension_health = active_extensions / len(self.extensions)

        # Overall system health
        system_health = (
            seh_report.get('system_integrity', 0.5) * 0.3 +
            llm_report.get('system_health', 0.5) * 0.3 +
            extension_health * 0.2 +
            (self.civilization_metrics['total_c_dev'] /
             max(self.civilization_metrics['total_queries'] * 100, 1)) * 0.2
        )

        return {
            'system_health_score': system_health,
            'seh_integrity': seh_report.get('system_integrity', 0),
            'llm_health': llm_report.get('system_health', 0),
            'extension_coverage': extension_health,
            'c_dev_efficiency': (
                self.civilization_metrics['total_c_dev'] /
                max(self.civilization_metrics['total_queries'], 1)
            ),
            'ethical_compliance_rate': (
                1.0 - (self.civilization_metrics['ethical_violations_prevented'] /
                      max(self.civilization_metrics['total_queries'], 1))
            )
        }

    def get_civilization_report(self) -> Dict[str, Any]:
        """Get comprehensive civilization development report"""

        # Calculate extension contributions
        extension_contributions = []
        for name, ext in self.extensions.items():
            if ext.get('c_dev_contribution', 0) > 0:
                extension_contributions.append({
                    'name': name,
                    'category': ext['category'],
                    'c_dev_contribution': ext.get('c_dev_contribution', 0),
                    'usage_count': ext.get('usage_count', 0)
                })

        # Sort by contribution
        extension_contributions.sort(key=lambda x: x['c_dev_contribution'], reverse=True)

        # Calculate civilization development index
        total_queries = self.civilization_metrics['total_queries']
        if total_queries == 0:
            civ_dev_index = 0
        else:
            civ_dev_index = (
                self.civilization_metrics['total_c_dev'] / total_queries * 0.4 +
                self._get_system_health_status()['ethical_compliance_rate'] * 0.3 +
                self._get_system_health_status()['extension_coverage'] * 0.3
            )

        civilization_metrics = {
            **self.civilization_metrics,
            'civilization_development_index': civ_dev_index,
            'avg_c_dev_per_query': (
                self.civilization_metrics['total_c_dev'] /
                max(total_queries, 1)
            ),
            'operational_duration': self._get_operational_duration()
        }

        system_health = self._get_system_health_status()

        return {
            'civilization_metrics': civilization_metrics,
            'system_health': system_health,
            'top_extensions': extension_contributions[:10],
            'cognitive_state_distribution': self._get_cognitive_state_distribution(),
            'governance_patterns': self._analyze_governance_patterns(),
            'recommendations': self._generate_civilization_recommendations(civilization_metrics, system_health)
        }

    def _get_operational_duration(self) -> str:
        """Calculate how long system has been operational"""

        start_time = datetime.fromisoformat(self.civilization_metrics['start_time'])
        current_time = datetime.now()
        duration = current_time - start_time

        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        return f"{days}d {hours}h {minutes}m"

    def _get_cognitive_state_distribution(self) -> Dict[str, float]:
        """Get distribution of cognitive essence states in recent queries"""

        # This would query the actual distribution from monitoring data
        # For simulation, return estimated distribution

        return {
            'infant': 0.3,
            'guidable': 0.5,
            'insight_holder': 0.2
        }

    def _analyze_governance_patterns(self) -> Dict[str, Any]:
        """Analyze governance patterns from recent queries"""

        # This would analyze monitoring data for patterns
        # For simulation, return sample analysis

        return {
            'most_common_governance_elements': ['Terminology', 'Roles', 'Rules'],
            'ethical_violation_trend': 'decreasing',
            'c_dev_growth_rate': 'positive',
            'unification_stability': 'high',
            'recommended_focus': 'Expand insight-level queries'
        }

    def _generate_civilization_recommendations(self, metrics: Dict[str, Any], health: Dict[str, Any]) -> List[str]:
        """Generate civilization-scale recommendations"""

        recommendations = []

        # C_dev efficiency recommendations
        avg_c_dev = metrics['avg_c_dev_per_query']
        if avg_c_dev < 50:
            recommendations.append(
                "📉 LOW C_DEV EFFICIENCY: Average C_dev below 50"
            )
            recommendations.append(
                "   Action: Focus on governance-intensive queries"
            )
        elif avg_c_dev > 150:
            recommendations.append(
                f"🚀 HIGH C_DEV EFFICIENCY: Average C_dev {avg_c_dev:.1f}"
            )
            recommendations.append(
                "   Status: Civilization operating at high developmental level"
            )

        # Ethical compliance recommendations
        compliance_rate = health['ethical_compliance_rate']
        if compliance_rate < 0.8:
            recommendations.append(
                f"⚠️  ETHICAL COMPLIANCE: Only {compliance_rate:.1%} queries fully compliant"
            )
            recommendations.append(
                "   Action: Strengthen governance education and protocols"
            )

        # Extension coverage recommendations
        extension_coverage = health['extension_coverage']
        if extension_coverage < 0.9:
            recommendations.append(
                f"🔌 EXTENSION COVERAGE: {extension_coverage:.1%} extensions actively used"
            )
            recommendations.append(
                "   Action: Promote underutilized extensions"
            )

        if not recommendations:
            recommendations.append("✅ Civilization development is healthy")
            recommendations.append("   Continue current governance protocols")

        return recommendations

    def batch_process_civilization_queries(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple civilization queries in batch

        Returns aggregated civilization development report
        """
        logger.info(f"Batch processing {len(queries)} civilization queries")

        results = []
        for query_data in queries:
            query = query_data.get('query', '')
            user_id = query_data.get('user_id')
            context = query_data.get('context', {})

            result = self.process_civilization_query(query, user_id, context)
            results.append(result)

        # Calculate batch civilization metrics
        total_c_dev = sum(r['civilization_metrics']['c_dev_contribution'] for r in results)
        avg_c_dev = total_c_dev / len(results) if results else 0

        ethical_compliance = sum(
            1 for r in results if r['civilization_metrics']['ethical_compliance']
        ) / len(results) if results else 0

        # Extension usage distribution
        extension_usage = {}
        for r in results:
            ext_name = r['analysis']['extension_used']['name']
            extension_usage[ext_name] = extension_usage.get(ext_name, 0) + 1

        batch_report = {
            'total_queries_processed': len(results),
            'total_c_dev_generated': total_c_dev,
            'average_c_dev_per_query': avg_c_dev,
            'ethical_compliance_rate': ethical_compliance,
            'extension_usage_distribution': dict(sorted(
                extension_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            'civilization_impact_score': np.mean([
                r['metrics']['civilization_impact_score'] for r in results
            ]) if results else 0,
            'system_health_after_batch': self._get_system_health_status(),
            'recommendations': self._generate_batch_recommendations(results)
        }

        logger.info(f"Civilization batch processing complete. Generated {total_c_dev:.1f} total C_dev")

        return batch_report

    def _generate_batch_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on batch results"""

        if not results:
            return ["No queries to analyze"]

        recommendations = []

        # Check for query type patterns
        query_types = {}
        for r in results:
            ext_category = r['analysis']['extension_used']['category']
            query_types[ext_category] = query_types.get(ext_category, 0) + 1

        # Identify under-represented categories
        total_queries = len(results)
        for category, count in query_types.items():
            percentage = count / total_queries
            if percentage < 0.05:  # Less than 5%
                recommendations.append(
                    f"📊 UNDER-REPRESENTED: Only {percentage:.1%} {category} queries"
                )
                recommendations.append(
                    f"   Opportunity: Encourage {category}-focused queries"
                )

        # Check C_dev distribution
        c_dev_values = [r['civilization_metrics']['c_dev_contribution'] for r in results]
        c_dev_std = np.std(c_dev_values)

        if c_dev_std > np.mean(c_dev_values) * 0.5:
            recommendations.append(
                f"📈 VARIABLE C_DEV: High standard deviation ({c_dev_std:.1f})"
            )
            recommendations.append(
                "   Action: Standardize governance application across queries"
            )

        if not recommendations:
            recommendations.append("✅ Batch shows balanced civilization development")
            recommendations.append("   Governance application is consistent")

        return recommendations
