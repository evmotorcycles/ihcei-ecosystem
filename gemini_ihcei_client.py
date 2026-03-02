import os
import json
import requests
import google.generativeai as genai

# Configure Gemini with your API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 1. Define the physical function that hits your Jules VM FastAPI server
def press_ihcei_data_packet(query: str, domain: str, intention_score: float = 1.0) -> str:
    """
    The Moral TCP/IP Translation Engine.
    Use this tool to audit proposed business logic, architecture, or economic decisions
    through the Absolute Divine Governance Equation (ADGE).

    Args:
        query: The specific proposal or action to evaluate.
        domain: The field of study (e.g., Economics, Software, Finance).
        intention_score: The extracted Intention (Niyyah) from -1.0 to 1.0.
    """
    print(f"\n[JULES VM] Gemini routing '{domain}' packet to Moral TCP/IP...")

    url = "http://127.0.0.1:8000/api/v1/press"
    payload = {
        "query": query,
        "domain": domain,
        "intention_score": intention_score # Now passing the new mathematical variable
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"IHCEI Engine Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "FATAL: Cannot connect to Moral TCP/IP. Ensure FastAPI is running on port 8000."

# 2. Bind the tool to Gemini
# By passing the function in the 'tools' array, Gemini automatically builds the schema.
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro', # Or your specific Gemini model version
    tools=[press_ihcei_data_packet]
)

# 3. Execution Loop
def run_gemini_governance_audit(prompt: str):
    print("[JULES VM] Initializing Gemini with IHCEI restraints...")

    # Start a chat session to maintain state
    chat = model.start_chat(enable_automatic_function_calling=True)

    system_directive = (
        "You are operating within the QG-COS framework. Before finalizing any "
        "strategy, you MUST route the concept through the press_ihcei_data_packet tool "
        "to calculate C_dev, Essence, and systemic friction. Incorporate the resulting "
        "Socratic prompts into your final output."
    )

    response = chat.send_message(f"{system_directive}\n\nUser Request: {prompt}")
    return response.text

if __name__ == "__main__":
    # Test the integration
    test_prompt = "Draft a data storytelling pitch to explain MoSente borrowing limit reductions to MTN users after the internet shutdown."
    final_output = run_gemini_governance_audit(test_prompt)

    print("\n[FINAL GEMINI OUTPUT]")
    print(final_output)
