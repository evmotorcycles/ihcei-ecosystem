import json
import os
import unittest
import numpy as np
from QG_Computation import (
    compute_cosine_similarity,
    compute_D_enc,
    compute_laplacian_eigenvalues,
    compute_F_t,
    compute_MCI,
    compute_C_dev,
    ComputationEngine
)

class TestPrivacyGuarantee(unittest.TestCase):

    def setUp(self):
        self.data_dir = "data/calibration"
        self.enron_file = os.path.join(self.data_dir, "enron_edges.json")
        self.lehman_file = os.path.join(self.data_dir, "lehman_proxy.json")

    def test_no_raw_text_in_enron_edges(self):
        """Asserts no raw text strings exist in the data/calibration output files."""
        if not os.path.exists(self.enron_file):
            self.skipTest(f"File {self.enron_file} not found. Run ingestor first.")

        with open(self.enron_file, "r") as f:
            edges = json.load(f)

        for edge in edges:
            self.assertNotIn("text_content", edge)
            self.assertNotIn("content", edge)
            self.assertNotIn("description", edge)

            # Ensure identifiers are hashed
            self.assertTrue(edge["source_id"].startswith("NODE_"))
            self.assertTrue(edge["target_id"].startswith("NODE_"))
            self.assertNotIn("@", edge["source_id"])
            self.assertNotIn("@", edge["target_id"])

    def test_no_raw_text_in_lehman_proxy(self):
        if not os.path.exists(self.lehman_file):
            self.skipTest(f"File {self.lehman_file} not found. Run ingestor first.")

        with open(self.lehman_file, "r") as f:
            periods = json.load(f)

        for period in periods:
            self.assertNotIn("text_content", period)
            self.assertNotIn("description", period)


class TestComputationEngine(unittest.TestCase):

    def test_cosine_similarity(self):
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        v3 = np.array([0.0, 1.0, 0.0])

        self.assertAlmostEqual(compute_cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(compute_cosine_similarity(v1, v3), 0.0)
        self.assertAlmostEqual(compute_cosine_similarity(v1, np.array([0,0,0])), 0.0)

    def test_D_enc(self):
        embeddings = [
            [1.0, 1.0, 1.0], # sim = 1.0 -> norm = 1.0
            [-1.0, -1.0, -1.0] # sim = -1.0 -> norm = 0.0
        ]
        # Avg = 0.5
        self.assertAlmostEqual(compute_D_enc(embeddings), 0.5)

    def test_laplacian_eigenvalues(self):
        # Create a simple line graph: A-B-C
        edges = [
            {"source_id": "A", "target_id": "B", "weight": 1.0},
            {"source_id": "B", "target_id": "C", "weight": 1.0}
        ]
        lambda_1, lambda_2, mean_degree = compute_laplacian_eigenvalues(edges)

        # Expected eigenvalues for P3 graph: 0, 1, 3
        # lambda_2 = 1, lambda_1 = 3
        self.assertAlmostEqual(lambda_2, 1.0)
        self.assertAlmostEqual(lambda_1, 3.0)

        # Degrees: A=1, B=2, C=1 -> mean = 4/3
        self.assertAlmostEqual(mean_degree, 4/3)

    def test_F_t(self):
        f = compute_F_t(var_D=0.6, delay=3.0, rework=0.3)
        # 1/3 * (0.6 + 3.0 + 0.3) = 1/3 * 3.9 = 1.3
        self.assertAlmostEqual(f, 1.3)

    def test_MCI(self):
        mci = compute_MCI(lambda_1=3.0, lambda_2=1.0, D_system=0.5)
        # (3/1) * (1 - 0.5) = 1.5
        self.assertAlmostEqual(mci, 1.5)

        # Disconnected graph test
        self.assertEqual(compute_MCI(3.0, 0.0, 0.5), float('inf'))

    def test_C_dev(self):
        c_dev = compute_C_dev(delta_phi_nafs=0.1, lambda_2=2.0, h_network=0.5)
        # (0.1 * 2) / 0.5 = 0.4
        self.assertAlmostEqual(c_dev, 0.4)

        # Zero friction test
        self.assertEqual(compute_C_dev(0.1, 2.0, 0.0), float('inf'))


if __name__ == '__main__':
    unittest.main()
