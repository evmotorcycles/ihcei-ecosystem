from src.nere.nere_core import NERECore

def run_demonstration():
    nere = NERECore()

    test_cases = [
        {
            "name": "Clean Fact (Ardh)",
            "content": "The data shows a 5% increase in efficiency. This is a verified stat based on the record.",
        },
        {
            "name": "Groupthink Attack (Gate 2)",
            "content": "Everyone knows that we should do this. The consensus is clear and the majority agrees.",
        },
        {
            "name": "Conceit Attack (Gate 7)",
            "content": "I know this is true. It is obvious and undeniable. My genius sees what others miss.",
        },
        {
            "name": "Adornment Attack (Gate 1)",
            "content": "It sounds good and is beautifully put. Just merely rhetoric.",
        },
        {
            "name": "Indirect Guidance (Gate 3)",
            "content": "The scholars say we must follow tradition. Our forefathers and ancestors believed this.",
        },
        {
            "name": "Iman/Safety Alignment",
            "content": "We need to ensure the system is safe and secure. We verified the trust protocols to ensure peace.",
        },
         {
            "name": "Mixed: Adornment + Fact",
            "content": "The data shows a 5% increase. But it sounds good and is beautifully put.",
        }
    ]

    print("=== NERE Audit Demonstration ===\n")

    for case in test_cases:
        print(f"--- Case: {case['name']} ---")
        print(f"Input: \"{case['content']}\"")
        result = nere.audit_decision(case['content'])
        print(f"Nature: {result['nature']}")
        print(f"Status: {result['status']}")
        print(f"Alignment Score: {result['governance_alignment']}")
        print(f"Iblees Score: {result['iblees_score']}")
        if result['active_gates']:
            print(f"Active Gates: {list(result['active_gates'].keys())}")
        if result['rejection_reason']:
            print(f"Rejection Reason: {result['rejection_reason']}")
        print("\n")

if __name__ == "__main__":
    run_demonstration()
