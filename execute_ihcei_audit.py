import requests
import json

def execute_ihcei_audit(query: str, domain: str) -> str:
    """
    Executes the physical HTTP call to the local IHCEI FastAPI server.
    Jules will run this function when it triggers the press_ihcei_data_packet tool.
    """
    print(f"\n[JULES SYSTEM] Routing '{domain}' packet to Moral TCP/IP for Governance Audit...")

    url = "http://127.0.0.1:8000/api/v1/press"
    payload = {
        "query": query,
        "domain": domain
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("[JULES SYSTEM] Audit complete. Feeding variables back to LLM context.")

            # Return the exact mathematical output back to Jules as a string
            return json.dumps(result, indent=2)
        else:
            error_msg = f"IHCEI Engine Error: {response.status_code} - {response.text}"
            print(f"[JULES SYSTEM] {error_msg}")
            return error_msg

    except requests.exceptions.ConnectionError:
        fatal_error = "FATAL: Cannot connect to Moral TCP/IP. Ensure the IHCEI FastAPI server is actively running on port 8000."
        print(f"[JULES SYSTEM] {fatal_error}")
        return fatal_error

# Example of how Jules's internal logic binds the schema to this function:
# available_tools = {
#     "press_ihcei_data_packet": execute_ihcei_audit
# }
