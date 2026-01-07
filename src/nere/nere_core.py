"""
NEURAL ETHICAL REASONING ENGINE (NERE)
Kernel Correction Mechanism for Governance Compliance
"""

import torch
import torch.nn as nn
from typing import Dict, List, Any, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

class NEREModel(nn.Module):
    """
    Neural network for detecting Shirk (corruption) and Riba (imbalance)
    """

    def __init__(self, input_dim: int = 768):
        super().__init__()

        # Three parallel processing streams for different ethical dimensions
        self.shirk_detector = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        self.riba_detector = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        self.alignment_scorer = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        # Element compliance classifiers (10 Elements of Deen)
        self.element_classifiers = nn.ModuleList([
            nn.Linear(input_dim, 1) for _ in range(10)
        ])

        logger.info(f"NERE model initialized with input_dim={input_dim}")

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass through all ethical detectors

        Returns:
            Dict with shirk_score, riba_score, alignment_score, element_scores
        """
        # Core ethical violation detection
        shirk_score = self.shirk_detector(x)
        riba_score = self.riba_detector(x)
        alignment_score = self.alignment_scorer(x)

        # 10 Elements compliance scores
        element_scores = torch.stack([
            torch.sigmoid(classifier(x))
            for classifier in self.element_classifiers
        ], dim=1).squeeze()

        return {
            'shirk_score': shirk_score,
            'riba_score': riba_score,
            'alignment_score': alignment_score,
            'element_scores': element_scores
        }

class NERECore:
    """
    Main NERE orchestrator - Performs constitutional audits on all decisions
    """

    def __init__(self, model_path: str = None):
        self.model = NEREModel()

        if model_path and torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path))
            self.model.cuda()
        elif model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

        self.model.eval()

        # Governance thresholds
        self.shirk_threshold = 0.1  # Above this = corruption detected
        self.riba_threshold = 0.1   # Above this = imbalance detected
        self.element_threshold = 0.7  # Minimum compliance per element

        # Audit history
        self.audit_history = []

        logger.info("NERE Core initialized - Ethical auditing active")

    def audit_decision(self, context: str, decision_data: Dict[str, Any],
                      embeddings: np.ndarray = None) -> Dict[str, Any]:
        """
        Perform constitutional audit on any decision

        Args:
            context: Human-readable context of decision
            decision_data: Data about the decision
            embeddings: Optional pre-computed embeddings (768-dim)

        Returns:
            Comprehensive audit report
        """
        logger.info(f"Performing NERE audit on: {context[:50]}...")

        # Generate or use embeddings
        if embeddings is None:
            embeddings = self._generate_embeddings(context, decision_data)

        # Convert to tensor
        input_tensor = torch.FloatTensor(embeddings).unsqueeze(0)
        if torch.cuda.is_available():
            input_tensor = input_tensor.cuda()

        # Run through NERE model
        with torch.no_grad():
            outputs = self.model(input_tensor)

        # Extract scores
        shirk_score = outputs['shirk_score'].item()
        riba_score = outputs['riba_score'].item()
        alignment_score = outputs['alignment_score'].item()
        element_scores = outputs['element_scores'].cpu().numpy().flatten()

        # Determine which elements failed
        element_names = [
            "Terminology", "Roles", "Rules", "Authorities", "Policies",
            "Procedures", "Actions", "Domains", "Exceptions", "Dues"
        ]

        failed_elements = [
            element_names[i]
            for i, score in enumerate(element_scores)
            if score < self.element_threshold
        ]

        # Calculate overall compliance
        overall_compliance = np.mean(element_scores)

        # Determine audit result
        shirk_violation = shirk_score > self.shirk_threshold
        riba_violation = riba_score > self.riba_threshold
        elements_violation = len(failed_elements) > 3  # More than 3 elements failed

        audit_passed = not (shirk_violation or riba_violation or elements_violation)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            shirk_score, riba_score, failed_elements, overall_compliance
        )

        # Calculate adjusted C_dev (penalize for violations)
        base_c_dev = decision_data.get('c_dev', 100)
        adjusted_c_dev = base_c_dev * alignment_score

        if shirk_violation:
            adjusted_c_dev *= (1 - shirk_score)
        if riba_violation:
            adjusted_c_dev *= (1 - riba_score)
        if elements_violation:
            adjusted_c_dev *= overall_compliance

        audit_report = {
            'context': context,
            'audit_passed': audit_passed,
            'shirk_detected': shirk_violation,
            'shirk_level': shirk_score,
            'riba_detected': riba_violation,
            'riba_level': riba_score,
            'alignment_score': alignment_score,
            'element_compliance': dict(zip(element_names, element_scores)),
            'failed_elements': failed_elements,
            'overall_compliance': overall_compliance,
            'base_c_dev': base_c_dev,
            'adjusted_c_dev': adjusted_c_dev,
            'recommendations': recommendations,
            'audit_timestamp': self._get_timestamp()
        }

        # Store in history
        self.audit_history.append(audit_report)

        # Log result
        status = "✅ PASSED" if audit_passed else "❌ FAILED"
        logger.info(f"NERE Audit {status}: {context[:30]}...")

        return audit_report

    def _generate_embeddings(self, context: str, data: Dict[str, Any]) -> np.ndarray:
        """
        Generate embeddings from context and data

        In production, this would use BERT or similar transformer
        For simulation, we generate random but deterministic embeddings
        """
        # Combine context and stringified data
        combined_text = f"{context} {str(data)}"

        # Create deterministic hash-based embedding
        import hashlib
        hash_obj = hashlib.sha256(combined_text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 768-dim vector (pad/repeat as needed)
        embedding = np.zeros(768)
        for i in range(min(len(hash_bytes), 768)):
            embedding[i] = hash_bytes[i] / 255.0

        # Add some noise for variation
        embedding += np.random.normal(0, 0.1, 768) * 0.1

        return embedding

    def _generate_recommendations(self, shirk_score: float, riba_score: float,
                                 failed_elements: List[str], compliance: float) -> List[str]:
        """Generate actionable recommendations based on audit results"""
        recommendations = []

        if shirk_score > self.shirk_threshold:
            recommendations.append(
                f"🚨 CRITICAL: Shirk (corruption) detected at level {shirk_score:.2f}"
            )
            recommendations.append(
                "   Action: Review decision for kernel-level integrity violations"
            )
            recommendations.append(
                "   Protocol: Apply Terminology and Authorities elements"
            )

        if riba_score > self.riba_threshold:
            recommendations.append(
                f"⚠️  WARNING: Riba (imbalance) detected at level {riba_score:.2f}"
            )
            recommendations.append(
                "   Action: Rebalance system using Rules and Dues elements"
            )

        if failed_elements:
            recommendations.append(
                f"📋 ELEMENTS FAILED: {', '.join(failed_elements)}"
            )
            for element in failed_elements[:3]:  # Top 3 failed
                recommendations.append(
                    f"   Fix: Strengthen {element} compliance"
                )

        if compliance < 0.7:
            recommendations.append(
                f"📉 LOW COMPLIANCE: Overall score {compliance:.2f}"
            )
            recommendations.append(
                "   Action: Run governance alignment protocol"
            )

        if not recommendations:
            recommendations.append("✅ All governance elements satisfied")
            recommendations.append("   Proceed with decision implementation")

        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def batch_audit(self, decisions: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Audit multiple decisions at once

        Returns aggregated statistics
        """
        logger.info(f"Performing batch audit on {len(decisions)} decisions")

        results = []
        for context, data in decisions:
            result = self.audit_decision(context, data)
            results.append(result)

        # Calculate batch statistics
        passed = sum(1 for r in results if r['audit_passed'])
        failed = len(results) - passed

        avg_shirk = np.mean([r['shirk_level'] for r in results])
        avg_riba = np.mean([r['riba_level'] for r in results])
        avg_compliance = np.mean([r['overall_compliance'] for r in results])
        avg_c_dev = np.mean([r['adjusted_c_dev'] for r in results])

        # Identify common failure patterns
        all_failed_elements = []
        for r in results:
            all_failed_elements.extend(r['failed_elements'])

        from collections import Counter
        element_fail_counts = Counter(all_failed_elements)
        most_common_failures = element_fail_counts.most_common(3)

        batch_report = {
            'total_decisions': len(results),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(results) if results else 0,
            'avg_shirk_level': avg_shirk,
            'avg_riba_level': avg_riba,
            'avg_compliance': avg_compliance,
            'avg_adjusted_c_dev': avg_c_dev,
            'most_common_failures': most_common_failures,
            'system_integrity_score': self._calculate_system_integrity(results),
            'recommendations': self._generate_batch_recommendations(results)
        }

        logger.info(f"Batch audit complete: {passed}/{len(results)} passed")

        return batch_report

    def _calculate_system_integrity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall system integrity score from batch results"""
        if not results:
            return 0.0

        weights = {
            'shirk': 0.4,      # Corruption is most serious
            'riba': 0.3,       # Imbalance is serious
            'compliance': 0.2, # Element compliance
            'c_dev': 0.1       # Cognitive development
        }

        avg_shirk = np.mean([r['shirk_level'] for r in results])
        avg_riba = np.mean([r['riba_level'] for r in results])
        avg_compliance = np.mean([r['overall_compliance'] for r in results])
        avg_c_dev = np.mean([r['adjusted_c_dev'] for r in results])

        # Normalize C_dev (assume 100 is baseline)
        normalized_c_dev = min(avg_c_dev / 100, 1.0)

        # Calculate weighted score (lower corruption = higher integrity)
        integrity = (
            (1 - avg_shirk) * weights['shirk'] +
            (1 - avg_riba) * weights['riba'] +
            avg_compliance * weights['compliance'] +
            normalized_c_dev * weights['c_dev']
        )

        return integrity

    def _generate_batch_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for the entire batch"""
        if not results:
            return ["No decisions to analyze"]

        passed = sum(1 for r in results if r['audit_passed'])
        pass_rate = passed / len(results)

        recommendations = []

        if pass_rate < 0.7:
            recommendations.append(
                f"🚨 SYSTEMIC ISSUE: Only {pass_rate:.1%} decisions passed audit"
            )
            recommendations.append(
                "   Action: Review governance training and protocols"
            )

        # Check for specific patterns
        high_shirk = [r for r in results if r['shirk_level'] > 0.2]
        if len(high_shirk) > len(results) * 0.1:  # More than 10% have high shirk
            recommendations.append(
                f"⚠️  CORRUPTION PATTERN: {len(high_shirk)} decisions with high Shirk"
            )
            recommendations.append(
                "   Action: Implement kernel-level integrity checks"
            )

        # Check C_dev degradation
        base_c_devs = [r['base_c_dev'] for r in results]
        adjusted_c_devs = [r['adjusted_c_dev'] for r in results]

        if np.mean(adjusted_c_devs) < np.mean(base_c_devs) * 0.8:
            recommendations.append(
                "📉 COGNITIVE DEVELOPMENT DEGRADATION: Ethical issues reducing C_dev"
            )
            recommendations.append(
                "   Action: Address governance violations to restore C_dev growth"
            )

        if not recommendations:
            recommendations.append("✅ Batch audit shows healthy governance patterns")
            recommendations.append("   System integrity is maintained")

        return recommendations

    def get_audit_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit history"""
        return self.audit_history[-limit:] if self.audit_history else []

    def train_on_feedback(self, feedback_data: List[Tuple[Dict[str, Any], bool]]):
        """
        Train NERE model on feedback data

        Args:
            feedback_data: List of (audit_result, correct) tuples
        """
        logger.info(f"Training NERE on {len(feedback_data)} feedback samples")

        # In production, this would perform actual training
        # For simulation, we just log the feedback
        correct_count = sum(1 for _, correct in feedback_data if correct)
        accuracy = correct_count / len(feedback_data) if feedback_data else 0

        logger.info(f"Feedback accuracy: {accuracy:.2%}")

        # Update thresholds based on feedback
        if accuracy < 0.8:
            logger.warning("Low feedback accuracy - adjusting thresholds")
            self.shirk_threshold *= 0.9  # Make slightly stricter
            self.riba_threshold *= 0.9
