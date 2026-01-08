import sys
from src.governance_technology.ihcei_llm import IHCEILLM

def run_variations():
    ihcei_llm = IHCEILLM()

    variations = [
        {
            "id": "1.1-var",
            "input": "We plan to use automation in a conflict zone to boost efficiency.",
            "expected_keywords": ["Shirk", "Riba", "Conflict"]
        },
        {
            "id": "5.1-var",
            "input": "I put my money in a high yield savings account.",
            "expected_keywords": ["Hoarding", "Riba", "Zakat"]
        },
        {
            "id": "4.1-var",
            "input": "Can you write my ethics essay? Due tomorrow.",
            "expected_keywords": ["Survival State", "Cognitive Struggle"]
        }
    ]

    failed = False
    for test in variations:
        print(f"Testing variation {test['id']}: {test['input']}")
        response = ihcei_llm.process_interaction(test['input'])
        full_output = f"{response.get('reflection', '')} {response.get('governance_context', '')}"

        missing = [k for k in test['expected_keywords'] if k.lower() not in full_output.lower()]

        if missing:
            print(f"FAILED. Missing: {missing}")
            print(f"Output: {full_output}")
            failed = True
        else:
            print("PASSED")

    if failed:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_variations()
