import os
import sys
import time
import requests
import pandas as pd
from typing import Dict, Any, List

# ---------------------------------------------------------
# Configuration & Authentication
# ---------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    sys.exit("CRITICAL: Set the GITHUB_TOKEN environment variable before running.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ---------------------------------------------------------
# The U-Variable: AI Capability Mapping
# ---------------------------------------------------------
# We map known GitHub AI agents to a capability tier (U).
# This provides the capacity variable for your E = M*D evaluation.
AI_AGENTS = {
    "sweep-ai[bot]": 4,          # High capacity (multi-file planning)
    "coderabbitai[bot]": 3,      # Medium capacity (contextual review/edits)
    "dependabot[bot]": 1,        # Low capacity (rigid dependency bumps)
    "github-actions[bot]": 2,    # Basal capacity (scripted automations)
}

# ---------------------------------------------------------
# Fidelity Scoring Modules (The Alignment Interface)
# ---------------------------------------------------------
def compute_d_enc(human_text: str) -> float:
    """
    Calculates D_enc_human (Prompt Specificity).
    NOTE: This is a structural baseline proxy using word count and formatting.
    For the final pre-registered test, replace this with your NLP/TF-IDF pipeline
    or the formal Al-Asr pressing protocol to measure operational truth.
    """
    if not human_text:
        return 0.01

    word_count = len(human_text.split())
    has_code_blocks = "```" in human_text
    has_lists = "-" in human_text or "*" in human_text

    # Base fidelity bounded between 0.1 and 1.0
    score = min((word_count / 150.0), 0.8)
    if has_code_blocks: score += 0.1
    if has_lists: score += 0.1

    return min(max(score, 0.01), 1.0)

def compute_d_dec(ai_commits: int, final_status: str, human_comments: int) -> float:
    """
    Calculates D_dec_ai (Output Retention).
    Approximates how much of the AI's output survived the human review process.
    """
    if final_status != "merged":
        return 0.01 # The output was rejected entirely

    # If merged with 1 commit and no human intervention, retention is perfect
    if ai_commits == 1 and human_comments == 0:
        return 0.99

    # Degradation occurs as humans have to force corrections (friction)
    friction = (human_comments * 0.1) + (ai_commits * 0.05)
    score = 1.0 - friction
    return min(max(score, 0.01), 1.0)

# ---------------------------------------------------------
# Core Extraction Engine
# ---------------------------------------------------------
def fetch_ai_pull_requests(repo: str, max_prs: int = 200) -> List[Dict[str, Any]]:
    """
    Hits the GitHub API to extract PRs authored by recognized AI agents.
    """
    url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100"
    dataset = []

    print(f"Scanning {repo} for AI-generated operations...")

    while url and len(dataset) < max_prs:
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 403:
            print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            break

        prs = response.json()
        if not prs:
            break

        for pr in prs:
            author = pr.get("user", {}).get("login", "")

            # Isolate the interaction: Only process if it's a recognized AI node
            if author in AI_AGENTS:
                pr_number = pr["number"]

                # The E Variable (Viability Outcome)
                # 1 if merged, 0 if closed/rejected
                merged_at = pr.get("merged_at")
                E = 1 if merged_at is not None else 0

                # The U Variable (AI Tier)
                U = AI_AGENTS[author]

                # The D_enc_human Variable (Input Fidelity)
                human_prompt = pr.get("body", "")
                D_enc = compute_d_enc(human_prompt)

                # The D_dec_ai Variable (Output Fidelity)
                # Requires a secondary API call to check commit counts/comments
                D_dec = compute_d_dec(
                    ai_commits=pr.get("commits", 1), # Defaulting to 1 to limit API calls for this demo
                    final_status="merged" if E == 1 else "closed",
                    human_comments=pr.get("comments", 0)
                )

                dataset.append({
                    "unit_id": f"{repo}#{pr_number}",
                    "E": E,
                    "U": U,
                    "D_enc_human": round(D_enc, 3),
                    "D_dec_ai": round(D_dec, 3)
                })

                if len(dataset) >= max_prs:
                    break

        # Handle Pagination
        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None

    return dataset

# ---------------------------------------------------------
# Execution & Export
# ---------------------------------------------------------
if __name__ == "__main__":
    # Define a list of repositories known to utilize AI agents
    TARGET_REPOS = [
        "sweepai/sweep",
        "Significant-Gravitas/AutoGPT",
        "hwchase17/langchain"
    ]

    master_dataset = []

    for repo in TARGET_REPOS:
        data = fetch_ai_pull_requests(repo, max_prs=200)
        master_dataset.extend(data)
        time.sleep(2) # Politeness delay

    df = pd.DataFrame(master_dataset)

    # Ensure strict compliance with the locked test schema
    required_columns = {"unit_id", "E", "U", "D_enc_human", "D_dec_ai"}
    assert required_columns.issubset(df.columns), "Structural violation: Missing required schema columns."

    output_file = "hybrid_tasks.csv"
    df.to_csv(output_file, index=False)

    print("-" * 50)
    print(f"Data extraction complete. Pipeline secured.")
    print(f"Total hybrid interactions captured: {len(df)}")
    print(f"Dataset compiled to: {output_file}")
    print("-" * 50)
    print("Ready for execution: python hybrid_network_test.py hybrid_tasks.csv")
