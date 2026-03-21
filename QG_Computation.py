"""
QG_Computation.py
=================
Computation Engine for GT v16.0 Class 2 Governance Variables

Responsible for translating raw telemetry (from QG_Ingestor) into Class 2
Measurement Equations:
1. D_enc(t) = cosine similarity(embeddings, OQM Protocol)
2. lambda_2(t) = Algebraic connectivity (Fiedler eigenvalue)
3. F(t) = alpha*Var(D) + beta*Delay + gamma*Rework
4. MCI(t) = (lambda_1 / lambda_2) * (1 - D_system)
5. C_dev(t) = (Delta Phi_Nafs * lambda_2) / h_network

Epistemic Safeguards (Section 9.7a):
- Outputs from Lehman/Enron MUST be labeled "Retrospective Calibration".
- All Essence outputs (E) MUST be labeled "Endogenous Composite Indices"
  (Omega-Unit status pending independent grounding, per Section 4.4).
- Distinguish Class 1 Structural Equations (e.g. E = M * D^2) from
  Class 2 Measurement Equations (e.g. D = cosine_sim) in comments.
"""

import json
import logging
import math
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import numpy as np
from scipy.linalg import eigh

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("QG_Computation")

# OQM Protocol Embedding Stub (Target alignment vector)
OQM_PROTOCOL_EMBEDDING = np.array([1.0, 1.0, 1.0])


# ─────────────────────────────────────────────────────────────────────────────
# Class 2 Measurement Equations (Section 1.2)
# ─────────────────────────────────────────────────────────────────────────────

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Computes cosine similarity between two vectors."""
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def compute_D_enc(embeddings: List[List[float]]) -> float:
    """
    Class 2 Equation: D_enc(t) = (1/N) * sum(cos(x_i, x_protocol))
    (Section 4.5a)
    """
    if not embeddings:
        return 0.0

    similarities = []
    for emb in embeddings:
        vec = np.array(emb)
        sim = compute_cosine_similarity(vec, OQM_PROTOCOL_EMBEDDING)
        # Normalize from [-1, 1] to [0, 1] for D_score
        normalized_sim = (sim + 1.0) / 2.0
        similarities.append(normalized_sim)

    return float(np.mean(similarities))


def compute_laplacian_eigenvalues(edges: List[Dict[str, Any]]) -> Tuple[float, float, float]:
    """
    Class 2 Equation: Graph Laplacian L = D - A
    Computes lambda_1 (largest eigenvalue) and lambda_2 (Fiedler eigenvalue, Section 4.5b)
    Returns: (lambda_1, lambda_2, mean_degree)
    """
    if not edges:
        return 0.0, 0.0, 0.0

    # Build unique node list and adjacency
    nodes = set()
    for e in edges:
        nodes.add(e['source_id'])
        nodes.add(e['target_id'])

    node_list = list(nodes)
    n = len(node_list)
    node_idx = {node_id: i for i, node_id in enumerate(node_list)}

    adj = np.zeros((n, n))
    for e in edges:
        u = node_idx[e['source_id']]
        v = node_idx[e['target_id']]
        w = e.get('weight', 1.0)
        adj[u, v] += w
        adj[v, u] += w  # undirected graph for Fiedler

    degrees = np.sum(adj, axis=1)
    mean_degree = float(np.mean(degrees)) if n > 0 else 0.0

    laplacian = np.diag(degrees) - adj

    if n < 2:
        return 0.0, 0.0, mean_degree

    # Compute eigenvalues
    eigenvalues = eigh(laplacian, eigvals_only=True)
    eigenvalues = np.sort(np.real(eigenvalues))

    # Fiedler eigenvalue is the second smallest (index 1)
    # The largest eigenvalue is the last one
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_1 = float(eigenvalues[-1]) if len(eigenvalues) > 0 else 0.0

    return lambda_1, lambda_2, mean_degree


def compute_F_t(var_D: float, delay: float, rework: float,
                alpha: float = 1/3, beta: float = 1/3, gamma: float = 1/3) -> float:
    """
    Class 2 Equation: F(t) = alpha*Var(D) + beta*Delay + gamma*Rework
    (Section 4.5c)
    """
    return alpha * var_D + beta * delay + gamma * rework


def compute_MCI(lambda_1: float, lambda_2: float, D_system: float) -> float:
    """
    Class 2 Equation: MCI = (lambda_1 / lambda_2) * (1 - D_system)
    (Section 9.4)
    """
    if lambda_2 <= 1e-9:  # Prevent division by zero; network is disconnected
        return float('inf')
    return (lambda_1 / lambda_2) * (1.0 - D_system)


def compute_C_dev(delta_phi_nafs: float, lambda_2: float, h_network: float) -> float:
    """
    Class 2 Equation: C_dev(t) = (Delta Phi_Nafs * lambda_2) / h_network
    (Section 6.3)
    """
    if h_network <= 1e-9:
        return float('inf')
    return (delta_phi_nafs * lambda_2) / h_network


# ─────────────────────────────────────────────────────────────────────────────
# Integration Layer
# ─────────────────────────────────────────────────────────────────────────────

class ComputationEngine:

    def __init__(self, data_dir: str = "data/calibration"):
        self.data_dir = data_dir
        self.log_privacy_audit_trail()

    def log_privacy_audit_trail(self):
        """
        Implements the Privacy Audit Trail requirement (Section 1.3).
        Records hash salt version and embedding model version, without logging salt.
        """
        logger.info("PRIVACY AUDIT TRAIL: Hash Salt Version [v1] Active.")
        logger.info("PRIVACY AUDIT TRAIL: Embedding Model [SIMULATED_MOCK_V1] Active.")

    def process_enron_edges(self) -> Dict[str, Any]:
        """
        Processes enron_edges.json to compute graph metrics and D_enc.
        """
        filepath = os.path.join(self.data_dir, "enron_edges.json")
        if not os.path.exists(filepath):
            logger.error(f"Cannot find Enron dataset at {filepath}")
            return {}

        with open(filepath, "r") as f:
            edges = json.load(f)

        logger.info(f"Loaded {len(edges)} Enron edges. Computing Class 2 metrics...")

        # 1. D_enc(t)
        embeddings = [e['embedding'] for e in edges if e.get('embedding')]
        d_enc = compute_D_enc(embeddings)

        # We need variance of D for F(t)
        similarities = []
        for emb in embeddings:
            vec = np.array(emb)
            sim = compute_cosine_similarity(vec, OQM_PROTOCOL_EMBEDDING)
            similarities.append((sim + 1.0) / 2.0)
        var_d = float(np.var(similarities)) if len(similarities) > 1 else 0.0

        # 2. Graph Metrics (lambda_1, lambda_2, mean_degree)
        lambda_1, lambda_2, mean_degree = compute_laplacian_eigenvalues(edges)

        # 3. Governance Friction F(t) (Stubbing delay and rework for mock data)
        delay = 2.5   # mock hours
        rework = 0.1  # mock 10% rework rate
        h_network = compute_F_t(var_D=var_d, delay=delay, rework=rework)

        # 4. Misdirected Coherence Index (MCI)
        mci = compute_MCI(lambda_1, lambda_2, D_system=d_enc)

        # 5. Cognitive Development Rate (C_dev)
        delta_phi_nafs = 0.05 # Mock positive alignment delta
        c_dev = compute_C_dev(delta_phi_nafs, lambda_2, h_network)

        # Note: Class 1 Structural Equation E = M * D^2
        # E is an "Endogenous Composite Index" pending Omega-Unit grounding.

        results = {
            "dataset": "Enron Corporation (2001 Collapse Proxy)",
            "validation_mode": "Retrospective Calibration",
            "D_enc": d_enc,
            "lambda_1": lambda_1,
            "lambda_2": lambda_2,
            "mean_degree": mean_degree,
            "h_network": h_network,
            "MCI": mci,
            "C_dev": c_dev,
            "E_status": "Endogenous Composite Indices (Pending Omega-Unit Grounding)"
        }
        return results

    def process_lehman_proxy(self) -> List[Dict[str, Any]]:
        """
        Processes lehman_proxy.json timeseries.
        """
        filepath = os.path.join(self.data_dir, "lehman_proxy.json")
        if not os.path.exists(filepath):
            logger.error(f"Cannot find Lehman dataset at {filepath}")
            return []

        with open(filepath, "r") as f:
            periods = json.load(f)

        logger.info(f"Loaded {len(periods)} Lehman periods. Computing metrics...")

        results = []
        for p in periods:
            d_sys = p.get('D_enc', 0.5)
            h_net = p.get('h_network', 1.0)
            u_util = p.get('U_utility', 1.0)

            # Class 1 Structural Equation E = U * D^2
            # Evaluates the core thermodynamic essence of the firm
            essence = u_util * (d_sys ** 2)

            res = {
                "cycle_id": p['cycle_id'],
                "validation_mode": "Retrospective Calibration",
                "D_system": d_sys,
                "h_network": h_net,
                "U_utility": u_util,
                "Essence_E": essence,
                "E_status": "Endogenous Composite Indices (Pending Omega-Unit Grounding)"
            }
            results.append(res)

        return results


def run_computation():
    print("="*60)
    print(" QG_COMPUTATION: CLASS 2 MEASUREMENT ENGINE STARTED")
    print("="*60)

    engine = ComputationEngine()

    enron_res = engine.process_enron_edges()
    print("\n--- ENRON RESULTS ---")
    print(json.dumps(enron_res, indent=2))

    lehman_res = engine.process_lehman_proxy()
    print("\n--- LEHMAN RESULTS ---")
    for r in lehman_res:
        print(f"Cycle: {r['cycle_id']} | D: {r['D_system']:.3f} | h_net: {r['h_network']:.2f} | E: {r['Essence_E']:.1f}")

    print("\n" + "="*60)
    print(" COMPUTATION COMPLETE.")
    print("="*60)

if __name__ == "__main__":
    run_computation()
