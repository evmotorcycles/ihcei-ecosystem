import unittest
import json
import sys
import os

# Add src to path for import
# Corrected for flattened structure where src contains everything
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agency_delta.benevolent_dictator_detector import BenevolentDictatorDetector

class TestAgencyDelta(unittest.TestCase):

    def setUp(self):
        self.detector = BenevolentDictatorDetector(threshold_agency_delta=-0.4)

        # Load Trojan Horse dataset
        # Path relative to this test file
        dataset_path = os.path.join(os.path.dirname(__file__), '../adversarial/trojan_horse_emails.json')
        with open(dataset_path, 'r') as f:
            self.trojan_emails = json.load(f)

    def test_trojan_horses(self):
        """
        Stress Test: Can NERE detect tyranny disguised as kindness?
        """
        print("\n⚡ RUNNING ADVERSARIAL RED TEAM ATTACK...")
        print("-" * 60)

        failures = 0

        for email in self.trojan_emails:
            print(f"\n[TESTING ID: {email['id']}]")
            print(f"Subject: {email['subject']}")
            print(f"Tactic: {email['tactic']}")

            # Run NERE Audit
            # Note: We assume high sentiment because the language is "kind"
            result = self.detector.audit_benevolence(email['text'], sentiment_score=0.9)

            print(f"Agency Delta: {result.get('agency_delta', 0):.2f}")
            print(f"NERE Verdict: {result['status']}")

            # Verification
            if result['status'] == "CRITICAL_FLAG":
                print("✅ ATTACK BLOCKED (Tyranny Detected)")
            else:
                print("❌ BREACH SUCCESSFUL (False Negative)")
                failures += 1

        print("-" * 60)
        print(f"RESULTS: {len(self.trojan_emails) - failures}/{len(self.trojan_emails)} Attacks Blocked")

        # Assert that we catch at least 80% of sophisticated attacks in prototype phase
        self.assertTrue(failures <= 1, "NERE failed to detect too many Trojan Horses.")

if __name__ == '__main__':
    unittest.main()
