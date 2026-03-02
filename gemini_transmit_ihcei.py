import google.generativeai as genai
import requests
import json
import os

# 1. Configure your Gemini API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

# 2. Define the Target API Link (Your Jules VM Endpoint)
# Replace with the actual IP address or domain of your Jules VM
JULES_VM_API_URL = "http://127.0.0.1:8000/api/v1/route_packet"

# 3. Define the Function for Gemini to Call
def transmit_to_ihcei_master(concept_payload: str, context_tags: list[str]):
    """
    Transmits an evaluated cognitive packet through the
    Moral TCP/IP architecture via the Jules VM.
    """

    # Structure the packet for the Moral TCP/IP server
    payload = {
        "concept_payload": concept_payload,
        "context_tags": context_tags,
        "routing_protocol": "moral_tcp_ip"
    }

    try:
        # The actual API call to your Jules VM
        response = requests.post(JULES_VM_API_URL, json=payload)
        response.raise_for_status()
        return f"Success: Packet routed to IHCEI Master. Server response: {response.json()}"
    except requests.exceptions.RequestException as e:
        return f"Transmission Failed: {e}"

# 4. Initialize the Gemini Model with the Tool
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro', # Or your preferred model version
    tools=[transmit_to_ihcei_master]
)

# 5. Execution Example
chat = model.start_chat(enable_automatic_function_calling=True)

user_input = "Evaluate the conceptual alignment of deploying a new automated resource allocation system and send it to the master server."

print(f"User: {user_input}\n")
response = chat.send_message(user_input)

print(f"Gemini Response: {response.text}")
