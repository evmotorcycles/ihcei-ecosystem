"""
RATIONAL THINKING (RT) TECHNOLOGY CORE
Implementation of standard AI/ML paradigm optimized for efficiency and profit
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class RTDecision:
    """Standard RT-based decision output"""
    decision: str
    confidence: float
    expected_value: float
    risk_assessment: float
    optimization_metrics: Dict[str, float]
    ethical_flag: bool = False

class RTCore:
    """
    Rational Thinking Core - Implements standard AI/ML paradigm

    Characteristics:
    - Optimizes for efficiency, profit, accuracy
    - Treats data as objective facts
    - Uses statistical models and neural networks
    - Ethical considerations as optional constraints
    """

    def __init__(self, model_type: str = "deep_learning"):
        self.model_type = model_type
        self.optimization_goal = "maximize_efficiency"
        self.primary_metric = "accuracy" if model_type == "classification" else "mse"

        # Training parameters
        self.learning_rate = 0.001
        self.batch_size = 32
        self.epochs = 100

        # Performance tracking
        self.training_history = []
        self.inference_count = 0
        self.total_value_generated = 0.0

        # Ethical constraints (optional)
        self.ethical_constraints = []
        self.constraint_violations = 0

        logger.info(f"RT Core initialized with {model_type} model")

    def make_decision(self, input_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> RTDecision:
        """
        Make a decision using RT paradigm

        Args:
            input_data: Raw input data
            context: Optional context information

        Returns:
            RTDecision with confidence and metrics
        """
        self.inference_count += 1

        # Extract features
        features = self._extract_features(input_data)

        # Apply model (simplified)
        prediction = self._apply_model(features)

        # Calculate expected value (profit/efficiency)
        expected_value = self._calculate_expected_value(prediction, context)

        # Risk assessment
        risk = self._assess_risk(prediction, expected_value)

        # Optimization metrics
        metrics = self._calculate_metrics(prediction, expected_value, risk)

        # Check ethical constraints (optional)
        ethical_flag = self._check_ethical_constraints(prediction, context)
        if ethical_flag:
            self.constraint_violations += 1
            logger.warning(f"Ethical constraint violation in decision #{self.inference_count}")

        # Update value tracking
        self.total_value_generated += expected_value

        decision = RTDecision(
            decision=self._format_decision(prediction),
            confidence=prediction.get('confidence', 0.8),
            expected_value=expected_value,
            risk_assessment=risk,
            optimization_metrics=metrics,
            ethical_flag=ethical_flag
        )

        # Store in history
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'input_summary': str(input_data)[:100]
        })

        logger.info(f"RT Decision made: {decision.decision[:50]}... (Value: {expected_value:.2f})")

        return decision

    def _extract_features(self, input_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Extract features for model processing"""
        # Simplified feature extraction
        features = {}

        for key, value in input_data.items():
            if isinstance(value, (int, float)):
                features[key] = np.array([float(value)])
            elif isinstance(value, str):
                # Simple text feature: length and word count
                features[f"{key}_length"] = np.array([float(len(value))])
                features[f"{key}_words"] = np.array([float(len(value.split()))])
            elif isinstance(value, list):
                # Filter strictly numeric values
                numeric_values = []
                for v in value[:10]:
                    if isinstance(v, (int, float)):
                        numeric_values.append(float(v))
                if numeric_values:
                    features[key] = np.array(numeric_values)
            elif isinstance(value, dict):
                # Extract numeric values from dict
                numeric_values = []
                for v in value.values():
                    if isinstance(v, (int, float)):
                        numeric_values.append(float(v))
                if numeric_values:
                    features[key] = np.array(numeric_values)

        return features

    def _apply_model(self, features: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Apply the ML model to features"""

        # Simplified model simulation
        if self.model_type == "deep_learning":
            # Simulate neural network
            prediction_values = []
            for feat in features.values():
                if len(feat) > 0:
                    prediction_values.append(np.mean(feat))

            if prediction_values:
                avg_prediction = np.mean(prediction_values)
                confidence = min(0.95, 0.7 + 0.3 * (1 - np.std(prediction_values)))
            else:
                avg_prediction = 0.5
                confidence = 0.5

            return {
                'prediction': avg_prediction,
                'confidence': confidence,
                'model_type': 'deep_learning',
                'feature_importance': {k: np.mean(v) for k, v in features.items()}
            }

        elif self.model_type == "regression":
            # Simulate regression model
            coefficients = np.random.randn(len(features))
            feature_values = np.array([np.mean(v) for v in features.values()])

            prediction = np.dot(coefficients, feature_values)
            confidence = 0.8 - 0.3 * abs(prediction)  # Less confident for extreme predictions

            return {
                'prediction': prediction,
                'confidence': max(0.3, confidence),
                'model_type': 'regression',
                'coefficients': coefficients.tolist()
            }

        else:
            # Default prediction
            return {
                'prediction': 0.5,
                'confidence': 0.5,
                'model_type': self.model_type
            }

    def _calculate_expected_value(self, prediction: Dict[str, Any],
                                 context: Optional[Dict[str, Any]]) -> float:
        """Calculate expected value (profit/efficiency)"""

        base_value = prediction.get('prediction', 0.5)
        confidence = prediction.get('confidence', 0.5)

        # Adjust based on context
        if context:
            risk_tolerance = context.get('risk_tolerance', 0.5)
            time_horizon = context.get('time_horizon', 1.0)
            scaling_factor = context.get('scaling_factor', 1.0)

            expected_value = base_value * confidence * scaling_factor

            # Adjust for risk and time
            if risk_tolerance < 0.3:  # Risk averse
                expected_value *= 0.7
            elif risk_tolerance > 0.7:  # Risk seeking
                expected_value *= 1.3

            # Time horizon adjustment
            expected_value *= min(2.0, time_horizon)
        else:
            expected_value = base_value * confidence

        return float(expected_value)

    def _assess_risk(self, prediction: Dict[str, Any], expected_value: float) -> float:
        """Assess risk of the decision"""

        confidence = prediction.get('confidence', 0.5)
        prediction_value = prediction.get('prediction', 0.5)

        # Risk increases with uncertainty and extreme predictions
        uncertainty_risk = 1.0 - confidence
        extremity_risk = abs(prediction_value - 0.5) * 2  # 0-1 scale

        # Combined risk score
        risk = 0.6 * uncertainty_risk + 0.4 * extremity_risk

        # Adjust based on expected value
        if expected_value < 0:
            risk *= 1.5  # Higher risk for negative expected value

        return min(1.0, risk)

    def _calculate_metrics(self, prediction: Dict[str, Any],
                          expected_value: float, risk: float) -> Dict[str, float]:
        """Calculate optimization metrics"""

        confidence = prediction.get('confidence', 0.5)

        return {
            'efficiency_score': expected_value / max(0.1, risk),
            'confidence_score': confidence,
            'risk_adjusted_return': expected_value * (1 - risk),
            'uncertainty': 1 - confidence,
            'decision_quality': confidence * (1 - risk)
        }

    def _check_ethical_constraints(self, prediction: Dict[str, Any],
                                  context: Optional[Dict[str, Any]]) -> bool:
        """Check if decision violates ethical constraints"""

        if not self.ethical_constraints:
            return False

        # Simplified ethical check
        prediction_value = prediction.get('prediction', 0.5)

        # Check each constraint
        violations = 0
        for constraint in self.ethical_constraints:
            if constraint == "fairness" and abs(prediction_value - 0.5) > 0.4:
                violations += 1
            elif constraint == "safety" and prediction_value > 0.8:
                violations += 1
            elif constraint == "privacy" and context and context.get('sensitive', False):
                violations += 1

        return violations > 0

    def _format_decision(self, prediction: Dict[str, Any]) -> str:
        """Format the decision for output"""

        pred_value = prediction.get('prediction', 0.5)
        confidence = prediction.get('confidence', 0.5)

        if pred_value > 0.7:
            decision = "APPROVE/IMPLEMENT"
        elif pred_value > 0.4:
            decision = "MONITOR/REVIEW"
        else:
            decision = "REJECT/DEFER"

        return f"{decision} (Score: {pred_value:.2f}, Confidence: {confidence:.2f})"

    def train_on_data(self, training_data: List[Dict[str, Any]],
                     labels: List[Any]) -> Dict[str, Any]:
        """
        Train the model on data

        Args:
            training_data: List of training examples
            labels: Corresponding labels/targets

        Returns:
            Training results
        """
        logger.info(f"Training RT model on {len(training_data)} examples")

        # Simplified training simulation
        loss_history = []
        accuracy_history = []

        for epoch in range(self.epochs):
            # Simulate training loss
            base_loss = 0.5 * np.exp(-epoch / 20)
            noise = np.random.normal(0, 0.1)
            loss = max(0.01, base_loss + noise)

            # Simulate accuracy improvement
            accuracy = min(0.95, 0.6 + 0.4 * (1 - np.exp(-epoch / 10)))

            loss_history.append(loss)
            accuracy_history.append(accuracy)

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: loss={loss:.4f}, accuracy={accuracy:.4f}")

        training_result = {
            'final_loss': loss_history[-1],
            'final_accuracy': accuracy_history[-1],
            'loss_history': loss_history,
            'accuracy_history': accuracy_history,
            'training_samples': len(training_data),
            'model_improvement': accuracy_history[-1] - accuracy_history[0]
        }

        logger.info(f"Training complete. Final accuracy: {accuracy_history[-1]:.4f}")

        return training_result

    def add_ethical_constraint(self, constraint: str):
        """Add an ethical constraint (optional)"""
        if constraint not in self.ethical_constraints:
            self.ethical_constraints.append(constraint)
            logger.info(f"Added ethical constraint: {constraint}")

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""

        if self.training_history:
            recent_decisions = self.training_history[-10:]
            avg_confidence = np.mean([d['decision'].confidence for d in recent_decisions])
            avg_value = np.mean([d['decision'].expected_value for d in recent_decisions])
        else:
            avg_confidence = 0.5
            avg_value = 0.0

        return {
            'inference_count': self.inference_count,
            'total_value_generated': self.total_value_generated,
            'constraint_violations': self.constraint_violations,
            'violation_rate': self.constraint_violations / max(1, self.inference_count),
            'average_confidence': avg_confidence,
            'average_value_per_decision': avg_value,
            'ethical_constraints': self.ethical_constraints.copy(),
            'model_type': self.model_type,
            'optimization_status': 'active'
        }
