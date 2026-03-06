import requests
import json

def audit_proposal_with_ihcei(proposal_text: str, domain_context: str) -> dict:
    url = "http://127.0.0.1:8000/api/v1/press"

    payload = {
        "query": proposal_text,
        "domain": domain_context
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error communicating with Moral TCP/IP: {response.text}")
        return {}

# ---------------------------------------------------------
# Example LLM Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    # The LLM generates a proposal for a client
    proposed_solution = (
        "To reduce customer churn and address the borrowing limit reductions "
        "following the recent internet shutdown, we will use data storytelling "
        "to clearly outline the algorithm's decisions to MoSente users."
    )

    print("Sending proposal to IHCEI Engine for Governance Audit...\n")
    audit_results = audit_proposal_with_ihcei(proposed_solution, "Economics")

    print(json.dumps(audit_results, indent=2))

    # The LLM can now be programmed to automatically revise its proposal
    # if C_dev drops below a certain threshold or if specific Gates are triggered.
