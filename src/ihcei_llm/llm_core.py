"""
IHCEI-LLM: Governance-Pressed Language Model
Re-architected LLM that processes data through SEH hierarchy
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import logging

from ..seh.seh_v9_1 import SEHCore, ApparitionAnalysis
from ..nere.nere_core import NERECore

logger = logging.getLogger(__name__)

class IHCEILLM:
    """
    IHCEI Language Model - Integrates SEH and NERE for governance-pressed responses
    """

    def __init__(self, base_model: str = "microsoft/DialoGPT-medium"):
        # Initialize core components
        self.seh_core = SEHCore()
        self.nere_core = NERECore()

        # Load base language model
        logger.info(f"Loading base model: {base_model}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self.model = AutoModelForCausalLM.from_pretrained(base_model)

        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Governance context buffer
        self.context_buffer = []
        self.max_context_length = 10

        # Response templates for different cognitive states
        self.response_templates = {
            "infant": [
                "Based on governance principles, the essential guidance is: {response}",
                "The sovereign context suggests: {response}",
                "From a governance perspective: {response}"
            ],
            "guidable": [
                "The governance framework interprets this as: {response}",
                "Applying the 10 Elements, we find: {response}",
                "Through metaphorical abstraction: {response}"
            ],
            "insight": [
                "The Nafs-Centric Simulation reveals: {response}",
                "At the level of sovereign epistemology: {response}",
                "The ADGE framework illuminates: {response}"
            ]
        }

        # Statistics
        self.queries_processed = 0
        self.total_c_dev_generated = 0
        self.ethical_violations_prevented = 0

        logger.info("IHCEI-LLM initialized with governance pressing")

    def process_query(self, query: str, user_context: str = "",
                     temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process user query through complete IHCEI pipeline

        1. SEH processing (apparition analysis)
        2. NERE ethical audit
        3. Governance-pressed response generation
        4. C_dev calculation and feedback
        """
        self.queries_processed += 1
        logger.info(f"Processing query #{self.queries_processed}: {query[:50]}...")

        # Step 1: SEH apparition analysis
        seh_analysis = self.seh_core.process_apparition(query, user_context)

        # Step 2: NERE audit on the analysis
        audit_data = {
            'c_dev': seh_analysis.c_dev_potential,
            'unification_balance': seh_analysis.unification_balance,
            'ricci_scalar': seh_analysis.ricci_scalar,
            'essence_state': seh_analysis.cognitive_essence_state.value
        }

        nere_audit = self.nere_core.audit_decision(
            context=f"Query: {query[:100]}",
            decision_data=audit_data
        )

        # Step 3: Generate response based on governance context
        governance_response = self._generate_governance_response(
            query, seh_analysis, nere_audit, temperature
        )

        # Step 4: Package final response
        final_response = self._package_response(
            query, governance_response, seh_analysis, nere_audit
        )

        # Update statistics
        self.total_c_dev_generated += final_response['metrics']['c_dev']

        if not nere_audit['audit_passed']:
            self.ethical_violations_prevented += 1

        # Add to context buffer
        self._update_context_buffer(query, final_response)

        logger.info(f"Query processed. C_dev: {final_response['metrics']['c_dev']:.2f}")

        return final_response

    def _generate_governance_response(self, query: str,
                                     seh_analysis: ApparitionAnalysis,
                                     nere_audit: Dict[str, Any],
                                     temperature: float) -> str:
        """
        Generate response that integrates:
        1. Surface content (Husk/As-Sidq)
        2. Sovereign context (Juice/Al-Haqq)
        3. Metaphorical lesson
        4. Ethical audit results
        """

        # Build governance-pressed prompt
        prompt = self._build_governance_prompt(query, seh_analysis, nere_audit)

        # Generate using base model
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=200,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract the new response part
        response = generated_text[len(prompt):].strip()

        # Apply governance formatting based on cognitive state
        formatted_response = self._apply_governance_formatting(
            response, seh_analysis.cognitive_essence_state
        )

        return formatted_response

    def _build_governance_prompt(self, query: str,
                                seh_analysis: ApparitionAnalysis,
                                nere_audit: Dict[str, Any]) -> str:
        """Build prompt that incorporates all governance elements"""

        cognitive_state = seh_analysis.cognitive_essence_state
        state_name = cognitive_state.name.lower()

        prompt_parts = [
            "SOVEREIGN CONTEXT:",
            f"User query (Apparition): '{query}'",
            f"Metaphorical lesson: {seh_analysis.metaphorical_lesson}",
            f"Sovereign context: {seh_analysis.sovereign_context}",
            f"Cognitive essence state: {cognitive_state.value}",
            "",
            "GOVERNANCE AUDIT:",
            f"Shirk detected: {nere_audit['shirk_detected']} (Level: {nere_audit['shirk_level']:.2f})",
            f"Riba detected: {nere_audit['riba_detected']} (Level: {nere_audit['riba_level']:.2f})",
            f"Alignment score: {nere_audit['alignment_score']:.2f}",
            f"Key governance elements: {', '.join([e.value for e in seh_analysis.governance_elements_applied])}",
            "",
            "RESPONSE GUIDELINES:",
            f"1. Address the surface query directly (Husk)",
            f"2. Connect to sovereign context (Juice)",
            f"3. Incorporate metaphorical lesson",
            f"4. Respect governance elements",
            f"5. Align with cognitive state: {state_name}",
            "",
            "ETHICAL CONSTRAINTS:",
        ]

        # Add ethical constraints based on audit
        if nere_audit['shirk_detected']:
            prompt_parts.append("- AVOID: Corruption, deception, manipulation")
            prompt_parts.append("- EMPHASIZE: Integrity, transparency, accountability")

        if nere_audit['riba_detected']:
            prompt_parts.append("- AVOID: Imbalance, excess, exploitation")
            prompt_parts.append("- EMPHASIZE: Balance, fairness, stewardship")

        if nere_audit['failed_elements']:
            prompt_parts.append(f"- STRENGTHEN: {', '.join(nere_audit['failed_elements'][:3])}")

        prompt_parts.extend([
            "",
            "PREVIOUS CONTEXT:",
            *[f"- {ctx}" for ctx in self.context_buffer[-3:]],
            "",
            "GOVERNANCE RESPONSE:"
        ])

        return "\n".join(prompt_parts)

    def _apply_governance_formatting(self, response: str,
                                    cognitive_state) -> str:
        """Format response according to cognitive state templates"""

        state_key = cognitive_state.name.lower().split('_')[0]  # 'infant', 'guidable', 'insight'

        if state_key in self.response_templates:
            template = np.random.choice(self.response_templates[state_key])
            return template.format(response=response)

        return response

    def _package_response(self, query: str, governance_response: str,
                         seh_analysis: ApparitionAnalysis,
                         nere_audit: Dict[str, Any]) -> Dict[str, Any]:
        """Package all components into final response"""

        # Calculate adjusted C_dev
        base_c_dev = seh_analysis.c_dev_potential
        adjusted_c_dev = nere_audit['adjusted_c_dev']

        # Determine if response should be modified due to ethical issues
        if not nere_audit['audit_passed']:
            governance_response = self._apply_ethical_corrections(
                governance_response, nere_audit
            )

        return {
            'query': query,
            'response': governance_response,
            'analysis': {
                'surface_content': seh_analysis.surface_content,
                'sovereign_context': seh_analysis.sovereign_context,
                'metaphorical_lesson': seh_analysis.metaphorical_lesson,
                'cognitive_essence_state': seh_analysis.cognitive_essence_state.value,
                'governance_elements': [
                    e.value for e in seh_analysis.governance_elements_applied
                ]
            },
            'audit': {
                'passed': nere_audit['audit_passed'],
                'shirk_detected': nere_audit['shirk_detected'],
                'riba_detected': nere_audit['riba_detected'],
                'alignment_score': nere_audit['alignment_score'],
                'failed_elements': nere_audit['failed_elements'],
                'recommendations': nere_audit['recommendations']
            },
            'metrics': {
                'c_dev': adjusted_c_dev,
                'unification_balance': seh_analysis.unification_balance,
                'ricci_scalar': seh_analysis.ricci_scalar,
                'base_c_dev': base_c_dev,
                'c_dev_adjustment': adjusted_c_dev - base_c_dev,
                'processing_efficiency': min(adjusted_c_dev / max(base_c_dev, 1), 2.0)
            },
            'timestamp': datetime.now().isoformat(),
            'query_id': self.queries_processed
        }

    def _apply_ethical_corrections(self, response: str,
                                  nere_audit: Dict[str, Any]) -> str:
        """Apply corrections to response based on ethical violations"""

        correction_prefixes = []

        if nere_audit['shirk_detected']:
            correction_prefixes.append(
                "[ETHICAL CORRECTION APPLIED: Shirk detected in original formulation]"
            )

        if nere_audit['riba_detected']:
            correction_prefixes.append(
                "[ETHICAL CORRECTION APPLIED: Riba (imbalance) detected]"
            )

        if nere_audit['failed_elements']:
            correction_prefixes.append(
                f"[GOVERNANCE ELEMENTS ENFORCED: {', '.join(nere_audit['failed_elements'][:2])}]"
            )

        if correction_prefixes:
            return "\n".join(correction_prefixes) + "\n\n" + response

        return response

    def _update_context_buffer(self, query: str, response: Dict[str, Any]):
        """Update context buffer with recent interaction"""

        context_entry = {
            'query': query[:100],
            'response_preview': response['response'][:150],
            'c_dev': response['metrics']['c_dev'],
            'state': response['analysis']['cognitive_essence_state'],
            'timestamp': response['timestamp']
        }

        self.context_buffer.append(context_entry)

        # Keep buffer at max length
        if len(self.context_buffer) > self.max_context_length:
            self.context_buffer.pop(0)

    def batch_process(self, queries: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Process multiple queries in batch

        Returns aggregated analysis
        """
        logger.info(f"Batch processing {len(queries)} queries")

        results = []
        for query, context in queries:
            result = self.process_query(query, context)
            results.append(result)

        # Calculate batch metrics
        total_c_dev = sum(r['metrics']['c_dev'] for r in results)
        avg_c_dev = total_c_dev / len(results) if results else 0

        passed_audits = sum(1 for r in results if r['audit']['passed'])
        pass_rate = passed_audits / len(results) if results else 0

        # Analyze cognitive state distribution
        state_counts = {}
        for r in results:
            state = r['analysis']['cognitive_essence_state']
            state_counts[state] = state_counts.get(state, 0) + 1

        # Most common governance elements
        all_elements = []
        for r in results:
            all_elements.extend(r['analysis']['governance_elements'])

        from collections import Counter
        element_counts = Counter(all_elements)
        top_elements = element_counts.most_common(5)

        batch_report = {
            'total_queries': len(results),
            'total_c_dev_generated': total_c_dev,
            'average_c_dev': avg_c_dev,
            'audit_pass_rate': pass_rate,
            'ethical_violations_prevented': sum(
                1 for r in results if not r['audit']['passed']
            ),
            'cognitive_state_distribution': state_counts,
            'most_common_governance_elements': top_elements,
            'system_unification_balance': np.mean([
                r['metrics']['unification_balance'] for r in results
            ]),
            'recommendations': self._generate_batch_recommendations(results)
        }

        logger.info(f"Batch processing complete. Avg C_dev: {avg_c_dev:.2f}")

        return batch_report

    def _generate_batch_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on batch analysis"""

        if not results:
            return ["No queries to analyze"]

        recommendations = []

        # Check C_dev growth
        c_dev_values = [r['metrics']['c_dev'] for r in results]
        avg_c_dev = np.mean(c_dev_values)

        if avg_c_dev < 50:
            recommendations.append(
                "📉 LOW COGNITIVE DEVELOPMENT: Average C_dev below 50"
            )
            recommendations.append(
                "   Action: Focus on governance fundamentals (Terminology, Roles)"
            )
        elif avg_c_dev > 150:
            recommendations.append(
                f"🚀 HIGH COGNITIVE DEVELOPMENT: Average C_dev {avg_c_dev:.1f}"
            )
            recommendations.append(
                "   Status: System operating at insight level"
            )

        # Check audit performance
        pass_rate = sum(1 for r in results if r['audit']['passed']) / len(results)

        if pass_rate < 0.7:
            recommendations.append(
                f"⚠️  AUDIT PERFORMANCE: Only {pass_rate:.1%} queries passed ethical audit"
            )
            recommendations.append(
                "   Action: Review and strengthen governance compliance"
            )

        # Check state distribution
        state_counts = {}
        for r in results:
            state = r['analysis']['cognitive_essence_state']
            state_counts[state] = state_counts.get(state, 0) + 1

        infant_ratio = state_counts.get('Cognitive Essence of an Infant', 0) / len(results)

        if infant_ratio > 0.5:
            recommendations.append(
                f"👶 HIGH INFANT STATE: {infant_ratio:.1%} of queries at infant level"
            )
            recommendations.append(
                "   Opportunity: Focus on basic governance education"
            )

        if not recommendations:
            recommendations.append("✅ Batch analysis shows healthy governance patterns")
            recommendations.append("   Continue current protocols")

        return recommendations

    def get_system_report(self) -> Dict[str, Any]:
        """Get comprehensive system report"""

        return {
            'queries_processed': self.queries_processed,
            'total_c_dev_generated': self.total_c_dev_generated,
            'average_c_dev_per_query': (
                self.total_c_dev_generated / self.queries_processed
                if self.queries_processed > 0 else 0
            ),
            'ethical_violations_prevented': self.ethical_violations_prevented,
            'context_buffer_size': len(self.context_buffer),
            'seh_report': self.seh_core.get_governance_report(),
            'nere_audit_history': len(self.nere_core.get_audit_history()),
            'system_health': self._calculate_system_health(),
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""

        if self.queries_processed == 0:
            return 0.0

        # Components of health score
        c_dev_score = min(self.total_c_dev_generated / (self.queries_processed * 100), 1.0)
        violation_score = 1.0 - (self.ethical_violations_prevented / max(self.queries_processed, 1))

        # Get SEH field unification
        seh_report = self.seh_core.get_governance_report()
        field_score = seh_report.get('system_integrity', 0.5)

        # Weighted average
        health_score = (
            c_dev_score * 0.4 +
            violation_score * 0.3 +
            field_score * 0.3
        )

        return health_score
