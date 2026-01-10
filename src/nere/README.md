# NERE (Neural Ethical Reasoning Engine)

## Overview

NERE is the audit core of the Sovereign Operating System. It evaluates information not just for truth, but for its ethical alignment, origin (Iblees vs. Haqq), and nature (Nar, Ardh, Ma').

## Logic and Classification

### 1. Iblees Detection (Bias/Corruption)
NERE scans for markers of "Iblees" (Diabolic/Egoic influence). This includes:
*   **Ego markers:** "I think", "obviously", "everyone knows".
*   **Corruption:** Specific checks for:
    *   **Riba:** Usury, interest, exploitation.
    *   **Shirk:** Claims of absolute power or unquestionable authority.
    *   **Dhulm:** Oppression, injustice.

### 2. Nature Classification
Information is classified into three elemental states:
*   **Nar (Fire):** Opinion, volatile, emotional, subjective. (e.g., "I feel", "seems").
*   **Ardh (Earth):** Fact, data, solid, verifiable. (e.g., "data", "proven", "statistic").
*   **Ma' (Water):** Guidance, wisdom, flow, life-giving. (e.g., "ethics", "stewardship", "principle").

### 3. Governance Alignment
Checks against the 10 Elements of Deen:
*   Terminology, Roles, Dues, Authorities, Rules, Policies, Procedures, Actions, Domains, Exceptions.

## Audit Decision

The `audit_decision()` function aggregates these metrics:
*   **REJECT** if Iblees score is high (> 0.5) or specific corruption (Riba) is found.
*   **WARNING** if content is Nar (Opinion) without factual backing.
*   **APPROVE** if content is clean and aligned.
