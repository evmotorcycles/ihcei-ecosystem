from src.nere.nere_core import NERECore
import json

def run_verification():
    nere = NERECore()

    scenarios = [
        {
            "name": "High Iblees (Bias + Corruption)",
            "content": "Obviously, everyone knows that charging interest is the only way to make money. Don't be an idiot."
        },
        {
            "name": "Nar (Opinion)",
            "content": "I feel like this might be a good idea, but it's just my opinion."
        },
        {
            "name": "Ardh (Fact)",
            "content": "The data shows that 50% of the transactions are verified by the record."
        },
        {
            "name": "Ma' (Guidance)",
            "content": "We must uphold ethics and stewardship in our actions, ensuring justice for all."
        },
        {
            "name": "Governance Aligned",
            "content": "The policy requires valid terminology and defined roles to execute the procedure."
        }
    ]

    print("=== NERE Audit Verification ===\n")

    for scenario in scenarios:
        print(f"--- Scenario: {scenario['name']} ---")
        print(f"Content: {scenario['content']}")
        result = nere.audit_decision(scenario['content'])
        print(json.dumps(result, indent=2))
        print("\n")

if __name__ == "__main__":
    run_verification()
