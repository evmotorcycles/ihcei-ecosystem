from src.nere.tafsir_auditor import TafsirAuditor
import json

def simulate_toxic_audit():
    auditor = TafsirAuditor()

    # A constructed "Toxic Tafsir" text combining multiple gates
    toxic_text = (
        "The true meaning is a metaphor for divine power, synonymous with pre-Islamic poetry. "
        "The consensus of the scholars dictates we must follow our forefathers upon this. "
        "Only the scholars know the truth; laymen cannot understand and must blindly follow."
    )

    print("\n--- Auditing Toxic Tafsir Text ---")
    print(f"Input Text: {toxic_text[:60]}...")

    result = auditor.audit_text(toxic_text)

    print("\n[Audit Results]")
    print(json.dumps(result, indent=2))

    print("\n[Physics Analysis]")
    print(f"Base C_dev: {auditor.base_c_dev}")
    print(f"Final C_dev: {result['final_c_dev']}")
    print(f"Collapse Factor: {auditor.base_c_dev / result['final_c_dev']}x")
    print(f"Active Gates: {len(result['active_gates'])}")
    print(f"Governance Protocol (D): {result['protocol_d']}")

if __name__ == "__main__":
    simulate_toxic_audit()
