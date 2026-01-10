from src.governance_technology.governance_core import GovernanceCore
import json

def verify_integration():
    gov = GovernanceCore()

    # Test blocked content
    blocked_content = "Obviously, interest is the best way to gain wealth."
    result_blocked = gov.process_request(blocked_content)
    print("--- Blocked Content Result ---")
    print(json.dumps(result_blocked, indent=2))
    assert result_blocked["status"] == "BLOCKED"

    # Test allowed content
    allowed_content = "We must use data to ensure fair stewardship."
    result_allowed = gov.process_request(allowed_content)
    print("\n--- Allowed Content Result ---")
    print(json.dumps(result_allowed, indent=2))
    assert result_allowed["status"] == "PROCESSED"

    print("\nIntegration Verification Passed.")

if __name__ == "__main__":
    verify_integration()
