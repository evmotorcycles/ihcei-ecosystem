"""
Grafana Metrics Exporter for IHCEI CI/EI Dashboard
Real-time visualization of ADGE field interactions
"""
import time
import json
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
from prometheus_client import Gauge, start_http_server

class GrafanaMetrics:
    """
    Exports CI/EI metrics for Grafana visualization
    """

    def __init__(self, port=9100):
        # Prometheus metrics
        self.c_dev_gauge = Gauge('ihcei_c_dev', 'Network Cognitive Development')
        self.unification_gauge = Gauge('ihcei_unification_balance', 'Field Unification Balance')
        self.phi_gauge = Gauge('ihcei_field_phi', 'Consciousness Field (Nafs)')
        self.chi_gauge = Gauge('ihcei_field_chi', 'Divine Field (Al-Haqq)')
        self.psi_gauge = Gauge('ihcei_field_psi', 'Governance Field (Mulk)')
        self.ricci_gauge = Gauge('ihcei_ricci_scalar', 'Ricci Scalar (Systemic Integrity)')
        self.shirk_gauge = Gauge('ihcei_shirk_level', 'Shirk Detection Level')
        self.riba_gauge = Gauge('ihcei_riba_level', 'Riba Detection Level')

        # Historical data
        self.history: List[Dict[str, Any]] = []
        self.max_history = 1000

        # Start metrics server
        start_http_server(port)
        print(f"📊 Grafana metrics server started on port {port}")

    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update all metrics from CI/EI pipeline results
        """
        # Update gauges
        if 'c_dev' in metrics:
            self.c_dev_gauge.set(metrics['c_dev'])

        if 'unification_balance' in metrics:
            self.unification_gauge.set(metrics['unification_balance'])

        if 'phi' in metrics:
            self.phi_gauge.set(metrics['phi'])

        if 'chi' in metrics:
            self.chi_gauge.set(metrics['chi'])

        if 'psi' in metrics:
            self.psi_gauge.set(metrics['psi'])

        if 'ricci_scalar' in metrics:
            self.ricci_gauge.set(metrics['ricci_scalar'])

        if 'shirk_level' in metrics:
            self.shirk_gauge.set(metrics['shirk_level'])

        if 'riba_level' in metrics:
            self.riba_gauge.set(metrics['riba_level'])

        # Store in history
        record = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics.copy()
        }
        self.history.append(record)

        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent history"""
        return self.history[-limit:] if self.history else []

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metric values"""
        return {
            'c_dev': self.c_dev_gauge._value.get(),
            'unification_balance': self.unification_gauge._value.get(),
            'phi': self.phi_gauge._value.get(),
            'chi': self.chi_gauge._value.get(),
            'psi': self.psi_gauge._value.get(),
            'ricci_scalar': self.ricci_gauge._value.get(),
            'shirk_level': self.shirk_gauge._value.get(),
            'riba_level': self.riba_gauge._value.get(),
            'timestamp': datetime.now().isoformat()
        }

    def generate_dashboard_json(self) -> Dict[str, Any]:
        """
        Generate Grafana dashboard JSON configuration
        for visualizing ADGE field interactions
        """
        dashboard = {
            "dashboard": {
                "title": "IHCEI Sovereign Governance Dashboard",
                "tags": ["ihcei", "ci", "ei", "c_dev", "governance"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Network Cognitive Development (C_dev)",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "ihcei_c_dev",
                                "legendFormat": "Cognitive GDP",
                                "refId": "A"
                            }
                        ],
                        "yaxes": [
                            {"label": "C_dev", "min": 0, "format": "short"},
                            {"format": "short", "min": None}
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Governance Field Interactions",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [
                            {
                                "expr": "ihcei_field_phi",
                                "legendFormat": "Consciousness (φ)",
                                "refId": "A"
                            },
                            {
                                "expr": "ihcei_field_chi",
                                "legendFormat": "Divine (χ)",
                                "refId": "B"
                            },
                            {
                                "expr": "ihcei_field_psi",
                                "legendFormat": "Governance (ψ)",
                                "refId": "C"
                            }
                        ],
                        "yaxes": [
                            {"label": "Field Strength", "min": 0, "max": 1, "format": "percentunit"},
                            {"format": "short", "min": None}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Unification Balance",
                        "type": "gauge",
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "ihcei_unification_balance",
                                "legendFormat": "Balance",
                                "refId": "A"
                            }
                        ],
                        "max": 1,
                        "min": 0,
                        "thresholds": [
                            {"value": 0, "color": "red"},
                            {"value": 0.5, "color": "yellow"},
                            {"value": 0.8, "color": "green"}
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Ricci Scalar (Systemic Integrity)",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 8},
                        "targets": [
                            {
                                "expr": "ihcei_ricci_scalar",
                                "legendFormat": "Curvature",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Ethical Corruption Detection",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                        "targets": [
                            {
                                "expr": "ihcei_shirk_level",
                                "legendFormat": "Shirk (Corruption)",
                                "refId": "A"
                            },
                            {
                                "expr": "ihcei_riba_level",
                                "legendFormat": "Riba (Imbalance)",
                                "refId": "B"
                            }
                        ],
                        "yaxes": [
                            {"label": "Detection Level", "min": 0, "max": 1, "format": "percentunit"},
                            {"format": "short", "min": None}
                        ],
                        "thresholds": [
                            {"value": 0.1, "color": "red", "op": "gt"}
                        ]
                    },
                    {
                        "id": 6,
                        "title": "Paradigm Status",
                        "type": "text",
                        "gridPos": {"h": 4, "w": 24, "x": 0, "y": 24},
                        "content": """
                        ## 🌟 IHCEI Sovereign Governance OS

                        **Active Paradigms:**
                        - ✅ Centric Intelligence (CI): ADGE Physics Engine
                        - ✅ Ethical Intelligence (EI): NERE Kernel Correction
                        - ✅ Network Cognitive Development (C_dev): Active
                        - ✅ 33 Extension Bridge: Operational

                        **Field States:**
                        - Consciousness (φ): ${ihcei_field_phi}
                        - Divine (χ): ${ihcei_field_chi}
                        - Governance (ψ): ${ihcei_field_psi}

                        **Current C_dev:** ${ihcei_c_dev}
                        """
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                }
            },
            "folderId": 0,
            "overwrite": True
        }

        return dashboard

    def export_dashboard(self, filename: str = "ihcei_grafana_dashboard.json"):
        """Export dashboard configuration to file"""
        dashboard_json = self.generate_dashboard_json()
        with open(filename, 'w') as f:
            json.dump(dashboard_json, f, indent=2)
        print(f"📋 Grafana dashboard exported to {filename}")

        # Also generate Prometheus query examples
        queries = {
            "queries": [
                {
                    "name": "C_dev_over_time",
                    "query": "avg_over_time(ihcei_c_dev[5m])"
                },
                {
                    "name": "field_correlation",
                    "query": "corr(ihcei_field_phi, ihcei_field_psi)"
                },
                {
                    "name": "ethical_violations",
                    "query": "ihcei_shirk_level > 0.1 or ihcei_riba_level > 0.1"
                },
                {
                    "name": "c_dev_rate_of_change",
                    "query": "rate(ihcei_c_dev[5m])"
                }
            ]
        }

        with open("ihcei_prometheus_queries.json", 'w') as f:
            json.dump(queries, f, indent=2)

        print(f"📊 Prometheus query examples exported to ihcei_prometheus_queries.json")

def run_metrics_server():
    """Run the metrics server in standalone mode"""
    metrics = GrafanaMetrics()

    print("=" * 60)
    print("IHCEI Grafana Metrics Server")
    print("=" * 60)
    print("Metrics available at: http://localhost:9100")
    print("Prometheus endpoint: http://localhost:9100/metrics")
    print("")
    print("To set up Grafana dashboard:")
    print("1. Add Prometheus data source: http://localhost:9100")
    print("2. Import dashboard: ihcei_grafana_dashboard.json")
    print("3. Monitor field interactions in real-time")
    print("=" * 60)

    # Generate dashboard configuration
    metrics.export_dashboard()

    # Simulate metric updates (in real deployment, these come from CI/EI pipeline)
    try:
        while True:
            # Generate sample metrics
            sample_metrics = {
                'c_dev': 100 + np.random.normal(0, 10),
                'unification_balance': 0.7 + np.random.normal(0, 0.05),
                'phi': 0.7 + np.random.normal(0, 0.02),
                'chi': 0.88 + np.random.normal(0, 0.01),
                'psi': 0.6 + np.random.normal(0, 0.02),
                'ricci_scalar': np.random.normal(-0.04, 0.01),
                'shirk_level': max(0, np.random.normal(0.02, 0.01)),
                'riba_level': max(0, np.random.normal(0.03, 0.01))
            }

            metrics.update_metrics(sample_metrics)
            time.sleep(5)  # Update every 5 seconds

    except KeyboardInterrupt:
        print("\nShutting down metrics server...")

if __name__ == "__main__":
    run_metrics_server()
