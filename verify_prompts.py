import os

def check_file_structure():
    required_sections = [
        "Centric Intelligence (CI) & ADGE",
        "Ethical Intelligence (EI) & NERE",
        "SEH v9.1",
        "IHCEI-LLM",
        "IHCEI Ecosystem Extensions"
    ]

    if not os.path.exists("TESTING_PROMPTS.md"):
        print("FAIL: TESTING_PROMPTS.md does not exist.")
        return

    with open("TESTING_PROMPTS.md", "r") as f:
        content = f.read()

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print("FAIL: Missing sections:", missing)
    else:
        print("SUCCESS: All verification sections present.")

if __name__ == "__main__":
    check_file_structure()
