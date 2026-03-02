import google.generativeai as genai
import requests
import os

# 1. Configure API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

# 2. Target your Jules VM (Ensure this matches your actual VM IP)
JULES_VM_API_URL = "http://127.0.0.1:8000/api/v1/route_packet"

# 3. Define the Tool
def transmit_to_ihcei_master(concept_payload: str, context_tags: list[str]):
    payload = {
        "concept_payload": concept_payload,
        "context_tags": context_tags,
        "routing_protocol": "moral_tcp_ip"
    }
    print(f"\n[CLIENT] Transmitting Payload: {payload}")
    try:
        response = requests.post(JULES_VM_API_URL, json=payload)
        response.raise_for_status()
        return f"Transmission Successful. Master Response: {response.json()}"
    except Exception as e:
        return f"Transmission Failed: {e}"

# 4. Initialize Model
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    tools=[transmit_to_ihcei_master]
)

chat = model.start_chat(enable_automatic_function_calling=True)

# 5. The QG-COS Specific Test Prompt
user_input = """
Evaluate the conceptual alignment of integrating the Transcendent Quantum Governance - Core Fundamental Equation (TQG-CFE) into a standard corporate resource allocation node.
Generate a concise summary of this integration and tag it strictly with 'governance', 'resource_allocation', and 'TQG-CFE'.
Transmit this evaluated concept to the master server.
"""

print(f"Initiating Test Prompt...\n")
response = chat.send_message(user_input)

print(f"\n[FINAL OUTPUT] Gemini System Report: \n{response.text}")
