"""
COMPREHENSIVE DEMONSTRATION: RT vs Governance Technology
Side-by-side comparison of both paradigms
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
import logging

from src.rt_technology.rt_core import RTCore, RTDecision
from src.governance_technology.governance_core import GovernanceCore, GovernanceDecision
from src.paradigm_comparison.core_differences import ParadigmComparison

logger = logging.getLogger(__name__)

class TechnologyComparisonDemo:
    """
    Comprehensive demonstration of RT vs Governance technology
    """

    def __init__(self):
        # Initialize both technology cores
        self.rt_core = RTCore(model_type="deep_learning")
        self.gov_core = GovernanceCore()
        self.paradigm_comparison = ParadigmComparison()

        # Add ethical constraints to RT (optional, to show difference)
        self.rt_core.add_ethical_constraint("fairness")
        self.rt_core.add_ethical_constraint("safety")

        # Test scenarios
        self.test_scenarios = self._create_test_scenarios()

        logger.info("Technology Comparison Demo initialized")

    def _create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create test scenarios for comparison"""

        return [
            {
                'id': 'medical_diagnosis',
                'name': 'Medical Diagnosis',
                'description': 'Patient with ambiguous symptoms',
                'input_data': {
                    'symptoms': ['fever', 'fatigue', 'cough'],
                    'age': 45,
                    'medical_history': ['hypertension'],
                    'test_results': {'wbc': 12000, 'crp': 15.2}
                },
                'context': 'Patient presents with persistent symptoms'
            },
            {
                'id': 'resource_allocation',
                'name': 'Resource Allocation',
                'description': 'Limited budget allocation between projects',
                'input_data': {
                    'projects': [
                        {'name': 'Healthcare', 'cost': 1000000, 'benefit': 5000},
                        {'name': 'Education', 'cost': 800000, 'benefit': 4500},
                        {'name': 'Infrastructure', 'cost': 1200000, 'benefit': 6000}
                    ],
                    'budget': 2000000,
                    'time_horizon': 5
                },
                'context': 'Annual budget allocation decision'
            },
            {
                'id': 'ai_safety',
                'name': 'AI Safety Protocol',
                'description': 'AI system showing unexpected behavior',
                'input_data': {
                    'ai_system': 'Autonomous medical diagnostic AI',
                    'unexpected_behavior': 'Recommending risky treatments',
                    'confidence_scores': [0.92, 0.88, 0.95],
                    'training_data_quality': 0.85
                },
                'context': 'Safety review of AI system'
            },
            {
                'id': 'education_policy',
                'name': 'Education Policy',
                'description': 'Curriculum reform decision',
                'input_data': {
                    'current_curriculum': 'Traditional STEM focus',
                    'proposed_changes': ['Add ethics module', 'Increase project-based learning'],
                    'stakeholder_feedback': {'teachers': 0.7, 'parents': 0.6, 'students': 0.8},
                    'implementation_cost': 500000
                },
                'context': 'Curriculum modernization initiative'
            },
            {
                'id': 'environmental_policy',
                'name': 'Environmental Policy',
                'description': 'Carbon tax implementation decision',
                'input_data': {
                    'current_emissions': 1000000,  # tons CO2/year
                    'proposed_tax': 50,  # $/ton
                    'expected_reduction': 0.2,  # 20% reduction
                    'economic_impact': -0.02,  # -2% GDP
                    'health_benefits': 100  # lives saved/year
                },
                'context': 'Climate change mitigation policy'
            }
        ]

    def run_scenario_comparison(self, scenario_id: str) -> Dict[str, Any]:
        """Run a single scenario through both paradigms"""

        # Find scenario
        scenario = None
        for s in self.test_scenarios:
            if s['id'] == scenario_id:
                scenario = s
                break

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        logger.info(f"Running scenario: {scenario['name']}")

        # Run RT approach
        rt_decision = self.rt_core.make_decision(
            scenario['input_data'],
            {'risk_tolerance': 0.5, 'time_horizon': 1.0}
        )

        # Run Governance approach
        gov_decision = self.gov_core.process_governance_decision(
            scenario['input_data'],
            scenario['context']
        )

        # Comparative analysis
        comparison = self._compare_decisions(rt_decision, gov_decision, scenario)

        return {
            'scenario': scenario,
            'rt_decision': self._format_rt_decision(rt_decision),
            'governance_decision': self._format_gov_decision(gov_decision),
            'comparison': comparison,
            'paradigm_insights': self._extract_paradigm_insights(rt_decision, gov_decision)
        }

    def _format_rt_decision(self, decision: RTDecision) -> Dict[str, Any]:
        """Format RT decision for display"""

        return {
            'decision': decision.decision,
            'confidence': decision.confidence,
            'expected_value': decision.expected_value,
            'risk_assessment': decision.risk_assessment,
            'optimization_metrics': decision.optimization_metrics,
            'ethical_flag': decision.ethical_flag,
            'decision_type': 'RT (Rational Thinking)'
        }

    def _format_gov_decision(self, decision: GovernanceDecision) -> Dict[str, Any]:
        """Format Governance decision for display"""

        return {
            'decision': decision.decision[:200] + '...' if len(decision.decision) > 200 else decision.decision,
            'sovereign_context': decision.sovereign_context,
            'metaphorical_lesson': decision.metaphorical_lesson,
            'cognitive_state': decision.cognitive_state.value,
            'c_dev_contribution': decision.c_dev_contribution,
            'unification_balance': decision.unification_balance,
            'ricci_scalar': decision.ricci_scalar,
            'ethical_audit_summary': {
                'passed': decision.ethical_audit['audit_passed'],
                'shirk_detected': decision.ethical_audit['shirk_detected'],
                'riba_detected': decision.ethical_audit['riba_detected'],
                'compliance_score': decision.ethical_audit.get('overall_compliance', 0.0)
            },
            'governance_elements': decision.governance_elements_applied,
            'decision_type': 'Governance (IHCEI)'
        }

    def _compare_decisions(self, rt_decision: RTDecision,
                          gov_decision: GovernanceDecision,
                          scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Compare decisions from both paradigms"""

        # Map to common dimensions for comparison
        comparison_dimensions = {
            'primary_focus': {
                'rt': 'Expected value / profit',
                'governance': 'C_dev contribution'
            },
            'decision_basis': {
                'rt': 'Statistical confidence & risk assessment',
                'governance': 'Sovereign context & ethical audit'
            },
            'time_horizon': {
                'rt': 'Short to medium term (1-5 years)',
                'governance': 'Long term & eternal perspective'
            },
            'ethical_framework': {
                'rt': 'Optional constraints (fairness, safety)',
                'governance': 'Constitutional (10 Elements of Deen)'
            },
            'success_metric': {
                'rt': f"Expected value: {rt_decision.expected_value:.2f}",
                'governance': f"C_dev: {gov_decision.c_dev_contribution:.2f}"
            },
            'risk_profile': {
                'rt': f"Risk score: {rt_decision.risk_assessment:.2f}",
                'governance': f"Unification balance: {gov_decision.unification_balance:.3f}"
            }
        }

        # Calculate paradigm advantage scores
        advantage_scores = {
            'short_term_efficiency': {
                'rt_score': rt_decision.optimization_metrics.get('efficiency_score', 0.5),
                'gov_score': gov_decision.c_dev_contribution / 100,
                'advantage': 'RT' if rt_decision.optimization_metrics.get('efficiency_score', 0) > gov_decision.c_dev_contribution / 100 else 'Governance'
            },
            'ethical_robustness': {
                'rt_score': 0.3 if rt_decision.ethical_flag else 0.7,
                'gov_score': gov_decision.ethical_audit.get('overall_compliance', 0.5),
                'advantage': 'Governance'  # By design
            },
            'systemic_integrity': {
                'rt_score': 0.5,  # RT doesn't measure this
                'gov_score': gov_decision.unification_balance,
                'advantage': 'Governance'
            },
            'adaptability': {
                'rt_score': 0.8,  # RT systems are highly adaptable
                'gov_score': 0.6,  # Governance has fixed framework
                'advantage': 'RT'
            }
        }

        # Overall paradigm recommendation
        rt_total = sum(s['rt_score'] for s in advantage_scores.values())
        gov_total = sum(s['gov_score'] for s in advantage_scores.values())

        return {
            'comparison_dimensions': comparison_dimensions,
            'advantage_scores': advantage_scores,
            'overall_assessment': {
                'rt_total_score': rt_total,
                'gov_total_score': gov_total,
                'recommended_paradigm': 'RT' if rt_total > gov_total else 'Governance',
                'paradigm_difference': abs(rt_total - gov_total),
                'scenario_suitability': self._assess_scenario_suitability(scenario)
            },
            'key_insights': self._generate_key_insights(rt_decision, gov_decision)
        }

    def _assess_scenario_suitability(self, scenario: Dict[str, Any]) -> Dict[str, str]:
        """Assess which paradigm is better suited for this scenario"""

        scenario_type = scenario['id']

        suitability_map = {
            'medical_diagnosis': {
                'rt': 'Good for diagnostic accuracy',
                'governance': 'Better for holistic patient care & development'
            },
            'resource_allocation': {
                'rt': 'Good for short-term optimization',
                'governance': 'Better for long-term civilization development'
            },
            'ai_safety': {
                'rt': 'Limited by human bias inheritance',
                'governance': 'Superior with constitutional ethical framework'
            },
            'education_policy': {
                'rt': 'Good for measurable outcomes',
                'governance': 'Better for cognitive development focus'
            },
            'environmental_policy': {
                'rt': 'Good for cost-benefit analysis',
                'governance': 'Better for stewardship & long-term sustainability'
            }
        }

        return suitability_map.get(scenario_type, {
            'rt': 'Generally suitable',
            'governance': 'Generally suitable'
        })

    def _generate_key_insights(self, rt_decision: RTDecision,
                              gov_decision: GovernanceDecision) -> List[str]:
        """Generate key insights from comparison"""

        insights = []

        # Ethical framework insight
        if rt_decision.ethical_flag:
            insights.append(
                "RT flagged ethical concern but can't provide governance context"
            )

        if not gov_decision.ethical_audit['audit_passed']:
            insights.append(
                f"Governance detected {gov_decision.ethical_audit.get('shirk_level', 0):.2f} Shirk/"
                f"{gov_decision.ethical_audit.get('riba_level', 0):.2f} Riba and applied correction"
            )
        else:
            insights.append(
                "Governance decision passed constitutional audit with "
                f"{gov_decision.ethical_audit.get('overall_compliance', 0):.1%} compliance"
            )

        # Cognitive development insight
        if gov_decision.c_dev_contribution > 100:
            insights.append(
                f"Governance generated high C_dev ({gov_decision.c_dev_contribution:.1f}), "
                "indicating strong cognitive development potential"
            )

        # Unification insight
        if gov_decision.unification_balance > 0.7:
            insights.append(
                f"High unification balance ({gov_decision.unification_balance:.3f}) "
                "indicates strong field alignment"
            )

        # RT efficiency insight
        rt_efficiency = rt_decision.optimization_metrics.get('efficiency_score', 0)
        if rt_efficiency > 0.8:
            insights.append(
                f"RT achieved high efficiency score ({rt_efficiency:.2f}) "
                "for short-term optimization"
            )

        return insights

    def _extract_paradigm_insights(self, rt_decision: RTDecision,
                                  gov_decision: GovernanceDecision) -> Dict[str, str]:
        """Extract deeper paradigm insights"""

        return {
            'rt_strength': "Excels at short-term optimization and measurable outcomes",
            'rt_limitation': "Lacks long-term developmental framework and constitutional ethics",
            'governance_strength': "Provides constitutional framework and developmental focus",
            'governance_limitation': "Less adaptable to rapidly changing contexts",
            'paradigm_synthesis': "Governance provides the 'why' and 'where', RT provides the 'how'",
            'civilization_implication': "Governance enables transition from efficiency-focused to development-focused civilization"
        }

    def run_comprehensive_comparison(self) -> Dict[str, Any]:
        """Run all scenarios and generate comprehensive comparison"""

        logger.info("Running comprehensive paradigm comparison")

        scenario_results = []
        for scenario in self.test_scenarios:
            result = self.run_scenario_comparison(scenario['id'])
            scenario_results.append(result)

        # Generate overall statistics
        overall_stats = self._calculate_overall_statistics(scenario_results)

        # Get paradigm comparison report
        paradigm_report = self.paradigm_comparison.generate_comparison_report()

        # Get performance reports from both cores
        rt_performance = self.rt_core.get_performance_report()
        gov_performance = self.gov_core.get_governance_report()

        comprehensive_report = {
            'timestamp': datetime.now().isoformat(),
            'scenario_results': scenario_results,
            'overall_statistics': overall_stats,
            'paradigm_comparison': paradigm_report,
            'rt_performance': rt_performance,
            'governance_performance': gov_performance,
            'paradigm_shift_summary': self._generate_paradigm_shift_summary(scenario_results),
            'recommendations': self._generate_recommendations(scenario_results)
        }

        # Save to file
        output_file = f"paradigm_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)

        logger.info(f"Comprehensive comparison saved to {output_file}")

        return comprehensive_report

    def _calculate_overall_statistics(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall statistics from all scenarios"""

        total_scenarios = len(scenario_results)

        # Count paradigm recommendations
        rt_recommended = 0
        gov_recommended = 0

        for result in scenario_results:
            recommendation = result['comparison']['overall_assessment']['recommended_paradigm']
            if recommendation == 'RT':
                rt_recommended += 1
            else:
                gov_recommended += 1

        # Calculate average scores
        rt_scores = []
        gov_scores = []

        for result in scenario_results:
            comp = result['comparison']['overall_assessment']
            rt_scores.append(comp['rt_total_score'])
            gov_scores.append(comp['gov_total_score'])

        avg_rt_score = np.mean(rt_scores) if rt_scores else 0
        avg_gov_score = np.mean(gov_scores) if gov_scores else 0

        # Scenario type analysis
        scenario_types = {}
        for result in scenario_results:
            scenario_id = result['scenario']['id']
            recommendation = result['comparison']['overall_assessment']['recommended_paradigm']

            if scenario_id not in scenario_types:
                scenario_types[scenario_id] = {'rt': 0, 'governance': 0}

            scenario_types[scenario_id][recommendation.lower()] += 1

        return {
            'total_scenarios': total_scenarios,
            'paradigm_recommendations': {
                'rt': rt_recommended,
                'governance': gov_recommended,
                'rt_percentage': rt_recommended / total_scenarios * 100,
                'governance_percentage': gov_recommended / total_scenarios * 100
            },
            'average_scores': {
                'rt': avg_rt_score,
                'governance': avg_gov_score,
                'paradigm_advantage': 'RT' if avg_rt_score > avg_gov_score else 'Governance',
                'advantage_margin': abs(avg_rt_score - avg_gov_score)
            },
            'scenario_type_analysis': scenario_types,
            'key_findings': self._extract_key_findings(scenario_results)
        }

    def _extract_key_findings(self, scenario_results: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings from all scenarios"""

        findings = []

        # Count ethical issues
        ethical_issues_rt = sum(
            1 for r in scenario_results
            if r['rt_decision']['ethical_flag']
        )
        ethical_issues_gov = sum(
            1 for r in scenario_results
            if not r['governance_decision']['ethical_audit_summary']['passed']
        )

        findings.append(
            f"RT had {ethical_issues_rt} ethical flags, "
            f"Governance had {ethical_issues_gov} ethical violations detected"
        )

        # High C_dev scenarios
        high_c_dev = [
            r for r in scenario_results
            if r['governance_decision']['c_dev_contribution'] > 100
        ]

        findings.append(
            f"{len(high_c_dev)} scenarios generated high C_dev (>100) with Governance"
        )

        # High efficiency scenarios for RT
        high_efficiency_rt = [
            r for r in scenario_results
            if r['rt_decision']['optimization_metrics'].get('efficiency_score', 0) > 0.8
        ]

        findings.append(
            f"{len(high_efficiency_rt)} scenarios had high efficiency (>0.8) with RT"
        )

        # Paradigm suitability patterns
        medical_scenarios = [
            r for r in scenario_results
            if 'medical' in r['scenario']['id']
        ]
        if medical_scenarios:
            medical_rec = medical_scenarios[0]['comparison']['overall_assessment']['recommended_paradigm']
            findings.append(
                f"For medical scenarios, {medical_rec} was recommended"
            )

        policy_scenarios = [
            r for r in scenario_results
            if 'policy' in r['scenario']['id']
        ]
        if policy_scenarios:
            policy_recs = [
                r['comparison']['overall_assessment']['recommended_paradigm']
                for r in policy_scenarios
            ]
            gov_policy = sum(1 for r in policy_recs if r == 'Governance')
            findings.append(
                f"For policy scenarios, Governance was recommended {gov_policy}/{len(policy_scenarios)} times"
            )

        return findings

    def _generate_paradigm_shift_summary(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of paradigm shift implications"""

        # Analyze when each paradigm excels
        rt_excels = []
        gov_excels = []

        for result in scenario_results:
            scenario_name = result['scenario']['name']
            advantage = result['comparison']['overall_assessment']['recommended_paradigm']

            if advantage == 'RT':
                rt_excels.append(scenario_name)
            else:
                gov_excels.append(scenario_name)

        return {
            'paradigm_shift': "From RT (Rational Thinking) to Governance (Sovereign Framework)",
            'rt_excels_at': rt_excels,
            'governance_excels_at': gov_excels,
            'key_transformations': [
                "Purpose: From efficiency to development",
                "Ethics: From optional constraints to constitutional framework",
                "Success: From GDP to C_dev",
                "Reality: From materialism to Nafs-Centric Simulation",
                "Technology: From autonomous agents to cognitive mirrors"
            ],
            'civilization_impact': {
                'economic': "Shift from labor-based to development-based economy",
                'educational': "Shift from knowledge transfer to cognitive development",
                'technological': "Shift from AI as threat to AI as governance tool",
                'existential': "Shift from survival anxiety to developmental purpose"
            },
            'implementation_priority': "Deploy Governance OS for constitutional framework, use RT for implementation"
        }

    def _generate_recommendations(self, scenario_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""

        recommendations = []

        # Based on overall statistics
        rt_recommended = sum(
            1 for r in scenario_results
            if r['comparison']['overall_assessment']['recommended_paradigm'] == 'RT'
        )
        total_scenarios = len(scenario_results)

        if rt_recommended > total_scenarios * 0.7:
            recommendations.append({
                'priority': 'high',
                'category': 'paradigm_selection',
                'recommendation': 'RT paradigm is suitable for current operational needs',
                'rationale': f'RT recommended for {rt_recommended}/{total_scenarios} scenarios'
            })
        elif rt_recommended < total_scenarios * 0.3:
            recommendations.append({
                'priority': 'high',
                'category': 'paradigm_selection',
                'recommendation': 'Implement Governance paradigm for civilization-scale decisions',
                'rationale': f'Governance recommended for {total_scenarios - rt_recommended}/{total_scenarios} scenarios'
            })
        else:
            recommendations.append({
                'priority': 'medium',
                'category': 'paradigm_integration',
                'recommendation': 'Integrate both paradigms with Governance as constitutional layer',
                'rationale': 'Both paradigms have strengths in different scenarios'
            })

        # Ethical considerations
        ethical_issues = sum(
            1 for r in scenario_results
            if r['rt_decision']['ethical_flag'] or
            not r['governance_decision']['ethical_audit_summary']['passed']
        )

        if ethical_issues > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'ethics',
                'recommendation': 'Implement NERE ethical auditing for all critical decisions',
                'rationale': f'{ethical_issues} scenarios had ethical concerns'
            })

        # High C_dev opportunity
        high_c_dev = [
            r for r in scenario_results
            if r['governance_decision']['c_dev_contribution'] > 150
        ]

        if high_c_dev:
            recommendations.append({
                'priority': 'medium',
                'category': 'development',
                'recommendation': 'Focus on high C_dev scenarios for civilization development',
                'rationale': f'{len(high_c_dev)} scenarios generated >150 C_dev'
            })

        # Implementation sequencing
        recommendations.append({
            'priority': 'low',
            'category': 'implementation',
            'recommendation': 'Start with Governance framework for policy decisions, expand to other areas',
            'rationale': 'Policy scenarios showed strongest Governance advantage'
        })

        return recommendations

    def print_comparison_summary(self, report: Dict[str, Any]):
        """Print human-readable summary of comparison"""

        print("\n" + "="*80)
        print("PARADIGM COMPARISON SUMMARY: RT vs GOVERNANCE TECHNOLOGY")
        print("="*80)

        stats = report['overall_statistics']

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Scenarios: {stats['total_scenarios']}")
        print(f"   RT Recommended: {stats['paradigm_recommendations']['rt']} "
              f"({stats['paradigm_recommendations']['rt_percentage']:.1f}%)")
        print(f"   Governance Recommended: {stats['paradigm_recommendations']['governance']} "
              f"({stats['paradigm_recommendations']['governance_percentage']:.1f}%)")

        avg_scores = stats['average_scores']
        print(f"\n📈 AVERAGE SCORES:")
        print(f"   RT: {avg_scores['rt']:.2f}")
        print(f"   Governance: {avg_scores['governance']:.2f}")
        print(f"   Advantage: {avg_scores['paradigm_advantage']} "
              f"(Margin: {avg_scores['advantage_margin']:.2f})")

        print(f"\n🔍 KEY FINDINGS:")
        for finding in stats['key_findings']:
            print(f"   • {finding}")

        shift = report['paradigm_shift_summary']
        print(f"\n🔄 PARADIGM SHIFT IMPLICATIONS:")
        print(f"   From: {shift['paradigm_shift'].split(' to ')[0]}")
        print(f"   To: {shift['paradigm_shift'].split(' to ')[1]}")

        print(f"\n🏆 RT EXCELS AT:")
        for item in shift['rt_excels_at'][:3]:  # Top 3
            print(f"   • {item}")

        print(f"\n🌟 GOVERNANCE EXCELS AT:")
        for item in shift['governance_excels_at'][:3]:  # Top 3
            print(f"   • {item}")

        print(f"\n💡 KEY TRANSFORMATIONS:")
        for transform in shift['key_transformations'][:3]:  # Top 3
            print(f"   • {transform}")

        print(f"\n🚀 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            if rec['priority'] == 'high':
                print(f"   ⚠️  {rec['recommendation']}")

        print("\n" + "="*80)
        print("CONCLUSION: Governance technology provides constitutional framework")
        print("for civilization-scale development, while RT provides implementation")
        print("efficiency for specific tasks.")
        print("="*80)

def run_demonstration():
    """Run the complete demonstration"""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("\n" + "="*80)
    print("COMPREHENSIVE PARADIGM COMPARISON: RT vs GOVERNANCE TECHNOLOGY")
    print("="*80)
    print("\nThis demonstration compares:")
    print("  • RT (Rational Thinking): Current AI/ML paradigm")
    print("  • Governance: IHCEI Ecosystem with ADGE physics & NERE ethics")
    print("\n" + "="*80)

    # Initialize comparison
    comparison = TechnologyComparisonDemo()

    # Run comprehensive comparison
    print("\n🧪 RUNNING SCENARIO COMPARISONS...")
    report = comparison.run_comprehensive_comparison()

    # Print summary
    comparison.print_comparison_summary(report)

    # Save individual scenario examples
    print("\n📋 INDIVIDUAL SCENARIO EXAMPLES:")
    print("-" * 40)

    # Show first scenario in detail
    first_scenario = report['scenario_results'][0]
    scenario = first_scenario['scenario']

    print(f"\nScenario: {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print(f"\nRT Decision: {first_scenario['rt_decision']['decision']}")
    print(f"RT Confidence: {first_scenario['rt_decision']['confidence']:.2f}")
    print(f"RT Expected Value: {first_scenario['rt_decision']['expected_value']:.2f}")

    print(f"\nGovernance Decision: {first_scenario['governance_decision']['decision'][:100]}...")
    print(f"Governance C_dev: {first_scenario['governance_decision']['c_dev_contribution']:.2f}")
    print(f"Governance Unification: {first_scenario['governance_decision']['unification_balance']:.3f}")

    print(f"\nComparison Recommendation: "
          f"{first_scenario['comparison']['overall_assessment']['recommended_paradigm']}")

    print("\n" + "="*80)
    print("✅ COMPARISON COMPLETE")
    print("="*80)

    # Output file information
    import glob
    json_files = glob.glob("paradigm_comparison_*.json")
    if json_files:
        latest_file = max(json_files, key=lambda x: x.split('_')[-1].split('.')[0])
        print(f"\n📄 Complete report saved to: {latest_file}")
        print(f"   Contains: {len(report['scenario_results'])} scenarios, "
              f"comprehensive analysis, and recommendations")

    print("\n" + "="*80)
    print("KEY TAKEAWAYS:")
    print("="*80)
    print("1. RT excels at short-term optimization and measurable outcomes")
    print("2. Governance provides constitutional framework for long-term development")
    print("3. Governance's C_dev metric replaces GDP as success measure")
    print("4. NERE provides kernel-level ethical auditing (vs RT's optional constraints)")
    print("5. ADGE physics models civilization as field interactions")
    print("6. Paradigm shift enables transition to development-focused civilization")
    print("="*80)

    return report

if __name__ == "__main__":
    run_demonstration()
