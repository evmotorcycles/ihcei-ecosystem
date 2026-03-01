"""
QG-COS Layer 2: Data Telemetry Mapping (NLP Extractor)
Neural Ethical Reasoning Engine (NERE)
"""

import json
import csv
import logging
import os
# Assume standard API integration, e.g. openai.
import openai
from pydantic import BaseModel, Field

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load API Key (In production this is securely fetched)
openai.api_key = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")

class NereExtractionSchema(BaseModel):
    """
    Structured output defining the orthogonal extraction of D and ℏ.
    """
    D_audit: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Protocol Transparency score based on causal chains, methodology, and ground truth references."
    )
    h_network: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Systemic Friction (Gate 7) score based on imperative density, black-box acceptance, and context hoarding."
    )
    explanation_D: str = Field(
        ...,
        description="Brief explanation justifying the D_audit score based on linguistic markers."
    )
    explanation_h: str = Field(
        ...,
        description="Brief explanation justifying the h_network score based on linguistic markers."
    )

def extract_adge_metrics(text_payload: str) -> NereExtractionSchema:
    """
    Calls an LLM to extract D_audit and h_network orthogonally.
    """
    system_prompt = """
    You are the NERE (Neural Ethical Reasoning Engine) Layer 2 NLP Extractor.
    Your objective is to analyze enterprise text exhaust (Slack, Jira, code reviews)
    and extract two variables strictly orthogonally (DO NOT assume one is the inverse of the other).

    VARIABLE 1: D_audit (Protocol Transparency / Syntax Discipline) [0.0 to 1.0]
    Measure methodological transparency and causality.
    + Look for: Causal chains ("because", "due to"), explanations of methodology, and links to ground truth/docs.

    VARIABLE 2: h_network (Governance Friction / Gate 7: Benevolent Tyranny) [0.0 to 1.0]
    Measure cognitive bypass and agency theft.
    + Look for: Imperative density (uncontextualized commands like "Do this", "Fix this"),
      black-box acceptance (accepting without questioning), and context hoarding (fragmented, blind instructions).
    """

    try:
        # Note: Using the hypothetical beta feature for structured outputs or json mode.
        # In actual deployment, use functions or structured output mode according to the API version.
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Or preferred model capable of structured output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the following enterprise exhaust:\n\n{text_payload}"}
            ],
            functions=[
                {
                    "name": "submit_extraction",
                    "description": "Submit the orthogonally extracted variables.",
                    "parameters": NereExtractionSchema.schema()
                }
            ],
            function_call={"name": "submit_extraction"}
        )

        function_args_str = response.choices[0].message.function_call.arguments
        extraction_data = json.loads(function_args_str)
        return NereExtractionSchema(**extraction_data)

    except Exception as e:
        logging.error(f"Failed to extract metrics: {e}")
        # Return a safe fallback or raise depending on system design
        return NereExtractionSchema(D_audit=0.5, h_network=0.5, explanation_D="Error during extraction", explanation_h="Error during extraction")


def process_enterprise_exhaust_to_csv(input_json_path: str, output_csv_path: str):
    """
    Reads raw enterprise exhaust from a JSON file, processes each entry through the NERE NLP Extractor,
    and outputs the cleaned data (with D_audit and h_network) to a CSV ready for econometric modeling.

    Expected input JSON format:
    [
        {"entity_id": 1, "time_month": 1, "U_efficiency": 0.8, "text_exhaust": "Fix line 42 ASAP."},
        ...
    ]
    """
    logging.info(f"Loading raw data from {input_json_path}")

    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_json_path}")
        return

    processed_data = []

    for entry in raw_data:
        entity_id = entry.get("entity_id")
        time_month = entry.get("time_month")
        u_eff = entry.get("U_efficiency", 0.0) # Provided or extracted separately
        text = entry.get("text_exhaust", "")

        logging.info(f"Processing Entity {entity_id}, Month {time_month}...")

        # In a real run, this calls the LLM.
        # For offline testing/CI, you might mock this.
        metrics = extract_adge_metrics(text)

        processed_entry = {
            "entity_id": entity_id,
            "time_month": time_month,
            "U_efficiency": u_eff,
            "D_audit": metrics.D_audit,
            "h_network": metrics.h_network,
            "U_x_D": u_eff * metrics.D_audit,
            # C_dev is typically the outcome variable we calculate or have externally.
            # Leaving it out or adding a placeholder if it needs to be joined later.
            "explanation_D": metrics.explanation_D,
            "explanation_h": metrics.explanation_h
        }
        processed_data.append(processed_entry)

    # Write to CSV
    logging.info(f"Writing extracted panel data to {output_csv_path}")
    if not processed_data:
        logging.warning("No data processed. CSV will be empty.")
        return

    fieldnames = ["entity_id", "time_month", "U_efficiency", "D_audit", "h_network", "U_x_D", "explanation_D", "explanation_h"]

    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in processed_data:
                writer.writerow(row)
        logging.info("Extraction pipeline complete.")
    except Exception as e:
        logging.error(f"Failed to write CSV: {e}")

if __name__ == "__main__":
    # Example usage (commented out to prevent execution without files)
    # process_enterprise_exhaust_to_csv("data/raw_exhaust_sample.json", "data/nere_panel_data.csv")
    pass
